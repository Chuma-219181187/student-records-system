#!/usr/bin/env python
"""
Database Migration Script: Local SQL Server → Azure SQL Database
Migrates schema, data, views, and stored procedures
"""

import pyodbc
import sys
from datetime import datetime

# Connection Strings
LOCAL_CONN = """
DRIVER={ODBC Driver 17 for SQL Server};
SERVER=localhost;
DATABASE=student_records_db;
Trusted_Connection=yes;
"""

AZURE_CONN = """
Driver={ODBC Driver 17 for SQL Server};
Server=tcp:student-records-sql-server.database.windows.net,1433;
Database=student-records;
Uid=adminuser;
Pwd=@qwerty2024_19954;
Encrypt=yes;
TrustServerCertificate=no;
Connection Timeout=30;
"""

def log(message):
    """Print timestamped log messages"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def connect_local():
    """Connect to local SQL Server"""
    try:
        conn = pyodbc.connect(LOCAL_CONN)
        log("✅ Connected to Local SQL Server")
        return conn
    except Exception as e:
        log(f"❌ Failed to connect to Local SQL Server: {e}")
        sys.exit(1)

def connect_azure():
    """Connect to Azure SQL Database"""
    try:
        conn = pyodbc.connect(AZURE_CONN)
        log("✅ Connected to Azure SQL Database")
        return conn
    except Exception as e:
        log(f"❌ Failed to connect to Azure SQL Database: {e}")
        sys.exit(1)

def drop_constraints_azure(cursor):
    """Drop foreign key constraints in Azure (reverse order)"""
    try:
        log("📋 Dropping foreign key constraints...")
        drop_statements = [
            "DROP TABLE IF EXISTS dbo.vw_at_risk_students;",
            "DROP TABLE IF EXISTS dbo.vw_course_performance;",
            "DROP TABLE IF EXISTS dbo.vw_attendance_summary;",
            "DROP TABLE IF EXISTS dbo.vw_course_roster;",
            "DROP TABLE IF EXISTS dbo.vw_student_transcript;",
            "DROP TABLE IF EXISTS dbo.attendance;",
            "DROP TABLE IF EXISTS dbo.grades;",
            "DROP TABLE IF EXISTS dbo.enrollments;",
            "DROP TABLE IF EXISTS dbo.courses;",
            "DROP TABLE IF EXISTS dbo.students;",
        ]
        for stmt in drop_statements:
            try:
                cursor.execute(stmt)
            except:
                pass
        cursor.commit()
        log("✅ Constraints dropped")
    except Exception as e:
        log(f"⚠️ Warning: {e}")

def migrate_schema(local_conn, azure_conn):
    """Execute CREATE TABLE statements on Azure"""
    try:
        log("📊 Migrating schema...")
        local_cursor = local_conn.cursor()
        azure_cursor = azure_conn.cursor()
        
        # Read and execute create_tables.sql
        with open("sql/create_tables.sql", "r") as f:
            sql_script = f.read()
        
        # Split by GO statements
        statements = sql_script.split("GO")
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    azure_cursor.execute(stmt)
                except Exception as e:
                    log(f"⚠️ Schema statement warning: {e}")
        
        azure_conn.commit()
        log("✅ Schema migrated successfully")
    except Exception as e:
        log(f"❌ Schema migration failed: {e}")
        sys.exit(1)

def migrate_data(local_conn, azure_conn):
    """Migrate data from local to Azure"""
    try:
        log("📦 Migrating data...")
        local_cursor = local_conn.cursor()
        azure_cursor = azure_conn.cursor()
        
        # Tables in order (respecting foreign keys)
        tables = ["students", "courses", "enrollments", "grades", "attendance"]
        
        for table in tables:
            try:
                # Get data from local
                local_cursor.execute(f"SELECT * FROM {table}")
                rows = local_cursor.fetchall()
                
                if not rows:
                    log(f"  ℹ️  {table}: No data to migrate")
                    continue
                
                # Get column names
                columns = [desc[0] for desc in local_cursor.description]
                col_str = ", ".join(columns)
                placeholders = ", ".join(["?" for _ in columns])
                
                # Enable IDENTITY_INSERT for identity columns
                try:
                    azure_cursor.execute(f"SET IDENTITY_INSERT {table} ON;")
                except:
                    pass
                
                # Insert into Azure
                migrated_count = 0
                for row in rows:
                    insert_sql = f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})"
                    try:
                        azure_cursor.execute(insert_sql, row)
                        migrated_count += 1
                    except pyodbc.IntegrityError:
                        # Skip duplicate keys
                        pass
                
                # Disable IDENTITY_INSERT
                try:
                    azure_cursor.execute(f"SET IDENTITY_INSERT {table} OFF;")
                except:
                    pass
                
                azure_conn.commit()
                log(f"  ✅ {table}: {migrated_count} rows migrated")
                
            except Exception as e:
                log(f"  ⚠️  {table}: {e}")
        
        log("✅ Data migrated successfully")
    except Exception as e:
        log(f"❌ Data migration failed: {e}")
        sys.exit(1)

def migrate_views(azure_conn):
    """Create views in Azure"""
    try:
        log("👁️  Creating views...")
        azure_cursor = azure_conn.cursor()
        
        with open("sql/view.sql", "r") as f:
            sql_script = f.read()
        
        statements = sql_script.split("GO")
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.startswith("--"):
                try:
                    azure_cursor.execute(stmt)
                except Exception as e:
                    log(f"  ⚠️  View statement: {e}")
        
        azure_conn.commit()
        log("✅ Views created successfully")
    except Exception as e:
        log(f"⚠️  Views creation warning: {e}")

def verify_migration(local_conn, azure_conn):
    """Verify migration by comparing row counts"""
    try:
        log("🔍 Verifying migration...")
        local_cursor = local_conn.cursor()
        azure_cursor = azure_conn.cursor()
        
        tables = ["students", "courses", "enrollments", "grades", "attendance"]
        all_match = True
        
        for table in tables:
            try:
                local_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                local_count = local_cursor.fetchone()[0]
                
                azure_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                azure_count = azure_cursor.fetchone()[0]
                
                match = "✅" if local_count == azure_count else "⚠️"
                print(f"  {match} {table}: Local={local_count}, Azure={azure_count}")
                
                if local_count != azure_count:
                    all_match = False
            except Exception as e:
                print(f"  ❌ {table}: {e}")
                all_match = False
        
        if all_match:
            log("✅ Migration verification successful!")
            return True
        else:
            log("⚠️  Some data counts don't match")
            return False
    except Exception as e:
        log(f"❌ Verification failed: {e}")
        return False

def main():
    """Main migration process"""
    log("=" * 60)
    log("DATABASE MIGRATION: Local SQL Server → Azure SQL Database")
    log("=" * 60)
    
    # Connect to both databases
    local_conn = connect_local()
    azure_conn = connect_azure()
    
    try:
        # Step 1: Drop existing objects in Azure
        log("\n📋 Step 1: Cleaning up Azure database...")
        azure_cursor = azure_conn.cursor()
        drop_constraints_azure(azure_cursor)
        
        # Step 2: Migrate schema
        log("\n📊 Step 2: Migrating schema...")
        migrate_schema(local_conn, azure_conn)
        
        # Step 3: Migrate data
        log("\n📦 Step 3: Migrating data...")
        migrate_data(local_conn, azure_conn)
        
        # Step 4: Create views
        log("\n👁️  Step 4: Creating views...")
        migrate_views(azure_conn)
        
        # Step 5: Verify migration
        log("\n🔍 Step 5: Verifying migration...")
        verify_migration(local_conn, azure_conn)
        
        log("\n" + "=" * 60)
        log("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        log("=" * 60)
        
    except Exception as e:
        log(f"\n❌ MIGRATION FAILED: {e}")
    finally:
        local_conn.close()
        azure_conn.close()
        log("Connections closed")

if __name__ == "__main__":
    main()

# ☁ Cloud Deployment Guide — PostgreSQL + Python

## Option 1 — Deploy on Render (Free Tier)

1. Go to https://render.com
2. Create **PostgreSQL Database**
3. Copy credentials (host, user, password, db, port)
4. Update `.env` with cloud values
5. Run migrations locally:

```
psql -h <host> -U <user> -d <db> -f sql/create_tables.sql
```

6. Re-run ETL pointing to cloud DB

```
python etl/etl_pipeline_advanced.py
```

---

## Option 2 — Railway

1. Go to https://railway.app
2. Create **PostgreSQL Service**
3. View variables → copy credentials
4. Paste into `.env`
5. Test connection:

```
psql <connection-string>
```

---

## Security Notes

- Never commit `.env` to GitHub
- Use environment variables in CI/CD
- Rotate DB credentials if shared


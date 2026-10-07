import os

os.environ.setdefault("DEPLOYMENT_TYPE", "debug")
os.environ.setdefault("SECRET_KEY", "x" * 32)
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./.test_cdn.db")

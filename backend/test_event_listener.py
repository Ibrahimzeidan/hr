"""Test script to verify event listener is working."""
import logging
import socket
from urllib.parse import urlparse

from sqlalchemy import create_engine, event, text
from app.core.config import get_settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

settings = get_settings()
print(f"DATABASE_URL: {settings.database_url}")
print(f"SUPABASE_PROJECT_REF: {settings.supabase_project_ref}")

# Resolve pooler IPs
pooler_host = "aws-0-ap-southeast-1.pooler.supabase.com"
try:
    results = socket.getaddrinfo(pooler_host, 5432, socket.AF_INET)
    pooler_ips = list(set([r[4][0] for r in results]))
    print(f"Pooler IPs: {pooler_ips}")
except Exception as e:
    print(f"Failed to resolve pooler IPs: {e}")
    pooler_ips = []

if pooler_ips and settings.supabase_project_ref:
    db_hostname = f"db.{settings.supabase_project_ref}.supabase.co"
    print(f"DB hostname for SNI: {db_hostname}")

    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        connect_args={"sslmode": "require", "connect_timeout": 10}
    )

    @event.listens_for(engine, "do_connect")
    def override_pooler_connection(dialect, conn_rec, cargs, cparams):
        print(f"\n=== Event listener triggered ===")
        print(f"cparams before: {cparams}")
        cparams["host"] = db_hostname
        cparams["hostaddr"] = pooler_ips[0]
        cparams["sslmode"] = "require"
        print(f"cparams after: {cparams}")

    try:
        print("\nAttempting connection...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")
else:
    print("Cannot set up workaround - missing pooler IPs or project ref")
"""Test script to verify DNS patch is working correctly."""
import logging
import socket

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import settings first
from app.core.config import get_settings
settings = get_settings()

print(f"DATABASE_URL: {settings.database_url}")
print(f"SUPABASE_PROJECT_REF: {settings.supabase_project_ref}")

# Import and patch
from app.database.session import _enable_dns_patch, _pooler_ips, _resolve_pooler_ips

# Enable the patch
_enable_dns_patch()

print(f"Pooler IPs: {_pooler_ips}")

# Test DNS resolution
db_hostname = f"db.{settings.supabase_project_ref}.supabase.co"
print(f"\nTesting DNS resolution for: {db_hostname}")

try:
    result = socket.getaddrinfo(db_hostname, 5432, socket.AF_INET)
    print(f"Resolved to: {result}")
except Exception as e:
    print(f"Resolution failed: {e}")

# Now try to connect with psycopg
print("\nAttempting psycopg connection...")
import psycopg

try:
    conn = psycopg.connect(
        host=db_hostname,
        port=5432,
        user='postgres',
        password=settings.database_url.split('@')[1].split(':')[1].split('@')[0],  # Extract password
        dbname='postgres',
        sslmode='require'
    )
    print("Connected successfully!")
    conn.execute('SELECT 1')
    print("Query executed successfully!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
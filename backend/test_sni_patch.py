"""
Test script to patch psycopg3 SSL connection to set custom SNI hostname.
"""
import ssl
import socket
import psycopg
from psycopg import pq

# Store the original wrap_socket method
original_wrap_socket = ssl.SSLContext.wrap_socket

def patched_wrap_socket(self, sock, server_hostname=None, **kwargs):
    """Patch to override SNI hostname for Supabase pooler connections."""
    # If connecting to the pooler, override SNI hostname
    if server_hostname and 'pooler.supabase.com' in server_hostname:
        # Use the project's db hostname for SNI
        server_hostname = 'db.ybhezugsxaurfosujgci.supabase.co'
        print(f"Overriding SNI hostname to: {server_hostname}")
    return original_wrap_socket(self, sock, server_hostname=server_hostname, **kwargs)

# Apply the patch
ssl.SSLContext.wrap_socket = patched_wrap_socket

# Now try to connect
try:
    conn = psycopg.connect(
        'postgresql://postgres:PJh69AbuCgriio19@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres?sslmode=require'
    )
    print('Connected successfully!')
    conn.execute('SELECT 1')
    print('Query executed successfully!')
    conn.close()
except Exception as e:
    print(f'Error: {e}')
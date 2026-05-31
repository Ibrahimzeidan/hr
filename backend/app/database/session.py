import logging
import socket
from collections.abc import Generator
from urllib.parse import urlparse

from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class Base(DeclarativeBase):
    pass


# Supabase pooler configuration
SUPABASE_POOLER_HOST = "aws-0-ap-southeast-1.pooler.supabase.com"
_pooler_ips: list[str] = []
_original_getaddrinfo = socket.getaddrinfo


def _resolve_pooler_ips() -> list[str]:
    """Resolve Supabase pooler IP addresses."""
    global _pooler_ips
    if _pooler_ips:
        return _pooler_ips

    try:
        results = socket.getaddrinfo(SUPABASE_POOLER_HOST, 5432, socket.AF_INET)
        _pooler_ips = list(set([r[4][0] for r in results]))
        logger.info(f"Resolved pooler IPs: {_pooler_ips}")
    except Exception as e:
        logger.warning(f"Failed to resolve pooler IPs: {e}")
    return _pooler_ips


def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    """Patched getaddrinfo that redirects Supabase db hostname to pooler IPs."""
    project_ref = settings.supabase_project_ref
    if project_ref:
        db_hostname = f"db.{project_ref}.supabase.co"
        if host == db_hostname:
            pooler_ips = _resolve_pooler_ips()
            if pooler_ips:
                logger.debug(f"Redirecting {host} to pooler IP {pooler_ips[0]}")
                # Return the pooler IP as if it's the db hostname
                return [(socket.AF_INET, socket.SOCK_STREAM, 0, '', (pooler_ips[0], port))]

    # Fall back to original getaddrinfo
    return _original_getaddrinfo(host, port, family, type, proto, flags)


def _enable_dns_patch():
    """Enable the DNS patch for Supabase pooler connections."""
    global _pooler_ips
    socket.getaddrinfo = _patched_getaddrinfo
    # Pre-resolve pooler IPs
    _pooler_ips = _resolve_pooler_ips()
    logger.info("Enabled DNS patch for Supabase pooler SNI workaround")


def _test_connection(engine) -> bool:
    """Test database connection and log the result."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Database connection successful: {settings.database_url[:40]}...")
        return True
    except OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        logger.warning("Application will start but database operations will fail until connection is restored.")
        logger.warning(f"Current DATABASE_URL: {settings.database_url[:40]}...")
        return False
    except Exception as e:
        logger.error(f"Unexpected error testing database connection: {e}")
        return False


# Create engine with appropriate settings for the database type
engine_kwargs = {"pool_pre_ping": True}

# For PostgreSQL (including Supabase), add SSL and timeout settings
if settings.database_url.startswith("postgresql"):
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "connect_args": {"sslmode": "require", "connect_timeout": 10}
    })

    # Check if using Supabase - if so, enable DNS patch for SNI workaround
    parsed_url = urlparse(settings.database_url)
    hostname = parsed_url.hostname or ""
    project_ref = settings.supabase_project_ref

    # Enable DNS patch for Supabase connections when:
    # 1. Using pooler hostname directly, OR
    # 2. Using db hostname with a project_ref configured
    if "pooler.supabase.com" in hostname or ("supabase.co" in hostname and project_ref):
        if project_ref:
            logger.info(f"Detected Supabase connection for project: {project_ref}")
            logger.info(f"Enabling DNS patch to redirect db hostname to pooler IP for SNI support")
            _enable_dns_patch()

    engine = create_engine(settings.database_url, **engine_kwargs)
else:
    engine = create_engine(settings.database_url, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Test connection on startup (non-blocking - just logs the status)
db_connected = _test_connection(engine)


def get_db() -> Generator[Session, None, None]:
    """Get a database session. Raises error if connection is unavailable."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    """Check database connection status and return diagnostic information."""
    result = {
        "connected": False,
        "database_url": settings.database_url[:40] + "..." if len(settings.database_url) > 40 else settings.database_url,
        "database_type": "postgresql" if settings.database_url.startswith("postgresql") else "sqlite",
        "error": None
    }
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        result["connected"] = True
    except Exception as e:
        result["error"] = str(e)
    return result
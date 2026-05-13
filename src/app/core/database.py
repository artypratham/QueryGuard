# Async SQLAlchemy engine
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import get_settings
import logging


logger = logging.getLogger(__name__)

# Create an SQLAlchemy async engine
def _make_engine():
    """
    Creates an async engine pointed at Neon PostgreSQL.
    
    Neon's connection pooler uses PgBouncer in transaction mode, 
    which does not support prepared statements. 
    * Asyncpg's default statement cache errors with "prepared statement does not exist" after a pooled recoonect.
    Setting statement_cache_size=0 disables that cache entirely.
    
    We are using pool_pre_ping to catch stale connection from PgBouncer.
    """
    settings = get_settings()
    
    return create_async_engine(
    settings.database_url,
    echo=settings.debug,             #Set to True to log every SQL Statement
    pool_size= 5,           #Min 5 connections always open
    max_overflow= 10,       #Can create up to 10 extra if needed
    pool_recycle = 3600,  #Recycle connections every hour (CRITICAL for Neon because it closes idle after 5mins) 
    pool_pre_ping = True,   #Test Connection before using (cactches dropped connection)
    connect_args = {
        "ssl": "require",
        "server_Settings" : {"application_nane": "queryguard-api"},
        "statement_cache_size" : 0,
        # For extra safety with PgBouncer transaction mode:
        "prepared_statement_cache_size" : 0,
    }
)

SQLAlchemyEngine = _make_engine()

# 4. Session factory - Creates Session Instances . This is my gateway to Queries
async_session_factory : async_sessionmaker[AsyncSession] = async_sessionmaker(
    SQLAlchemyEngine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
# The above is used to create a factory function. 
# This creates a fresh session.Wherever I need a DB session I will do the following->
# async with async_session_factory() as session:
#       I will use this session for all queries
#       Do all the database work
#   await session.execute(...)
#   await session.commit()
#       Session Automatically closes when exiting the `with` block
# pass

# Each request gets its own session.



async def dispose_engine() -> None:
    # Called during shutdown
    await SQLAlchemyEngine.dispose()
    
    
# Async SQLAlchemy engine
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 1. Loading the environment variables  from .env
load_dotenv()

# 2. Getting the connection string 
# Using os.getenc allows you to provide a fallback or handle missing keys
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL: 
    raise ValueError("DATABASE_URL not found in environment variables")

# 3. Create the SQLAlchemy engine
SQLAlchemyEngine = create_async_engine(
    DATABASE_URL,
    echo=False,             #Set to True to log every SQL Statement
    pool_size= 5,           #Min 5 connections always open
    max_overflow= 10,       #Can create up to 10 extra if needed
    pool_recycling = 3600,  #Recycle connections every hour (CRITICAL for Neon because it closes idle after 5mins) 
    pool_pre_ping = True,   #Test Connection before using (cactches dropped connection)
)

# 4. Session factory - Creates Session Instances
async_session_factory = async_sessionmaker(
    SQLAlchemyEngine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# The above is used to create a factory function. Wherever I need a DB session I will do the following
# async with async_session_factory() as session:
#    I will use this sesion for all queries
#    This Automatically closes when exiting the `with` block
# pass
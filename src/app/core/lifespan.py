#Startup : sandbox cleanup + registry load

from contextlib import asynccontextmanager
from app.core.database import initialize_database, shutdown_database
from app.core.config import get_settings
import logging
from fastapi import FastAPI




@asynccontextmanager
async def lifespan(app: FastAPI):
    
    settings = get_settings()

    #Manage application Startup and shutdown
    #Startup  
    SQLAlchemyEngine, async_session_factory = await initialize_database(
        database_url = get_settings().database_url,
        environment = "production",
    )
    app.state.engine = SQLAlchemyEngine
    app.state.db_session = async_session_factory
    
    yield
    
    #Shutdown
    await shutdown_database()
    
app = FastAPI(lifespan = lifespan)
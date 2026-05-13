#Startup : sandbox cleanup + registry load]

#python imports
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

#imports from directory
from app.core.config import get_settings

# lifespan  module's job is to export the lifespan async generator,
# So FastAPI app will not be created here, but in main.py and lifespan is wired in.

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    

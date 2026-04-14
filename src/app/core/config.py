#Settings from .env
from functools import lru_cache
from pydantic_settings import BaseSettings

#BaseSettings allows values to be overriden by environment variables
#Helpful in production because it lets me stop some secrets from being in code
class Settings(BaseSettings):
    database_url:       str
    anthropic_api_key:  str = "" #BYOK model
    api_key:            str = "" #single harcoded pi key for stage 1
    sandbox_image:      str = "queryguard-sandbox:latest"
    sandbox_timeout:    int = 30
    csv_upload_dir:     str = "/home/deploy/queryguard-v2/uploads"
    environment:        str = "development"
    debug:              bool = False
    
    class Config:
        env_file = ".env"


#Least recently used cache already provided/implemented by python functools which saves the results of expensive function calls to avoid redundant computations
@lru_cache()
def get_settings() -> Settings:
    return Settings()



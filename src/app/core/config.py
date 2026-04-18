#Settings from .env
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

#BaseSettings allows values to be overriden by environment variables
#Helpful in production because it lets me stop some secrets from being in code
class Settings(BaseSettings):
        
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    database_url:       str
    anthropic_api_key:  str = "" #BYOK model
    api_key:            str = "" #single harcoded pi key for stage 1
    sandbox_image:      str = "queryguard-sandbox:latest"
    sandbox_timeout:    int = 30
    csv_upload_dir:     str = "/home/deploy/queryguard-v2/uploads"
    environment:        str = "development"
    debug:              bool = False
    cors_origins:        str = "" 
    
    
    # This below property helps to provide clean list of cors_origins without having to split on ","
    # everytime i need to use app.add_middleware()
    # now app.add_middleware(
    #    CORSMiddleware,
    #    allow_origins = settings.cors_origins_list
    #)
    @property #@property decorator treats this method like an attribute, not a function. so whenever we call it we dont haveto use parenthese-> settings.cors_origins_list #this is like an attribute
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.spilt(",") if o.strip()]
    #  o.strip() removes leading nad trailing whitespaces from each string, .split(",") splits hte list on ,if o.strip() excludes the empty strings,


#Least recently used cache already provided/implemented by python functools which saves the results of expensive function calls to avoid redundant computations
@lru_cache()
def get_settings() -> Settings:
    return Settings()



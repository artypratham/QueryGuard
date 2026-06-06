#Settings from .env
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from dataclasses import dataclass, field
import yaml

#BaseSettings allows values to be overriden by environment variables
#Helpful in production because it lets me stop some secrets from being in code
class Settings(BaseSettings):
        
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    database_url:           str
    database_url_direct:    str     = ""  # Optional; falls back to database_url in env.py
    anthropic_api_key:      str     = "" #BYOK model
    api_key:                str     = "" #single harcoded api key for stage 1
    sandbox_image:          str     = "queryguard-sandbox:latest"
    sandbox_timeout:        int     = 30
    csv_upload_dir:         str     = "/home/deploy/queryguard-v2/uploads"
    environment:            str     = "development"
    debug:                  bool    = False
    cors_origins:           str     = "" 
    
    # Sematic Search 
    # These configs control the behavior of MetricSearchEngine
    # Can be adjusted based on metric definitions and query patterns
    semantic_search_top_k : int = 5
    # if th enumber is higher the number of top results to return from semantic search will be higher and the reverse is also true
    
    
    
    #below is the minimum cosine similarity score to include a result in the search.
    #range: 0.0 to 1.0
    #0.3 : Very permissive (broad matches)
    #0.5 : Moderate (balanced)
    #0.7 : Strict (exact matches only)
    semantic_Search_threshold: float = 0.3 # we want to stick to fail open philosohy for stage 1 hence keeping this as very permissive
    
    
    #Batch size for embedding model. Larger = faster but more memory
    semantic_Searcj_batch_size :int = 2 
    
    #Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    
    
    # This below property helps to provide clean list of cors_origins without having to split on ","
    # everytime i need to use app.add_middleware()
    # now app.add_middleware(
    #    CORSMiddleware,
    #    allow_origins = settings.cors_origins_list
    #)
    @property #@property decorator treats this method like an attribute, not a function. so whenever we call it we dont haveto use parenthese-> settings.cors_origins_list #this is like an attribute
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
    #  o.strip() removes leading nad trailing whitespaces from each string, .split(",") splits hte list on ,if o.strip() excludes the empty strings,


#Least recently used cache already provided/implemented by python functools which saves the results of expensive function calls to avoid redundant computations
@lru_cache()
def get_settings() -> Settings:
    return Settings()


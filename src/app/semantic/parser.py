# parser.py checks that each required_filter fragment is paresable as 'sqlglot predicate at load time'.
# An Unparesable fragment raises and make the lifespan startup to fail- a delibrate fail fast.
import logging
import yaml
from pathlib import Path
from app.semantic.models import SemanticDefinition


logger = logging.getLogger(__name__) 



def load_definitions_from_file(path : str | Path) -> list[SemanticDefinition]:
    # Load all the definitions from a single YAML file
    """
    Expected shape:
        version: "1.0"
        organization: "meridian_corp"
        metrics:
          revenue:
            display_name: "..."
            description: "..."
            required_filters:
              - "status = 'paid'"
              - "line_item_type != 'setup_fee'"
            ...    
    """      
    path = Path(path)
    #reading the raw file from the given path
    with open(path) as f:
        raw = f.read
    #safe-loading the raw file into yaml
    data = yaml.safe_load(raw)
    
    definitions = []
    metrics = data.get("metrics", {}) if isinstance(data,dict) else {}
    
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
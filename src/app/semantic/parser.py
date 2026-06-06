# parser.py checks that each required_filter fragment is paresable as 'sqlglot predicate at load time'.
# An Unparesable fragment raises and make the lifespan startup to fail- a delibrate fail fast.
import logging
import yaml
from pathlib import Path
from app.semantic.models import SemanticDefinition
from app.governance.sql_analyzer import parse_required_filter

logger = logging.getLogger(__name__) 

def _validate_required_filters(metric_name: str, required_filters: list[str]) -> None:
    if not metric_name or not required_filters:
        raise ValueError(
            f"Metric name cannot be empty"
            f"required filters cannot be empty"
        )
    #we will fail loudly on un parseable fragments at load time.
    for fragment in required_filters:
        if not isinstance(fragment, str):
            raise ValueError(
                f"Metric  {metric_name!r}: required_filter must be a string, "
                f"got {type(fragment).__name__}: {fragment!r}"
            )
        try:
            parse_required_filter(fragment=fragment)
        except ValueError as e:
            raise ValueError(
                f"Metric {metric_name!r}: required_filter {fragment!r}"
                f"failed to parse as a SQL predicate: {e}"
            )
            

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
    
    for metric_name, body in metrics.items():
        if not isinstance(body, dict):
            continue
        filters = body.get("required_filters", []) or [] #The filters = body.get("required_filters", []) or [] looks redundant but isn't. body.get("required_filters", []) returns [] if the key is missing. But if the key is explicitly set to null in YAML (someone wrote required_filters: and stopped), .get() returns None, not []. The 'or []' collapses both None and [] to []. 
        _validate_required_filters(metric_name=metric_name, required_filters=filters)
        
        definitions.append(SemanticDefinition(
            metric_name         = metric_name,
            display_name        = body.get("display_name", metric_name),
            description         = body.get("description", ""),
            required_filters    = filters,
            time_dimension      = body.get("time_dimension", ""),
            grain               = body.get("grain",""),
            owner               = body.get("owner", ""),
            tags                = body.get("tags", []) or [],
            raw_yaml            = raw
        ))
        
    return definitions


def load_definitions_from_directory(directoy: str | Path) -> list[SemanticDefinition]:
    directoy = Path(directoy)
    if not directoy:
        raise ValueError (
            f"Semantic Definitions Directory {directoy} does not exist"
        )
    all_defs : list[SemanticDefinition] = []
    for pattern in (".yaml" , ".yml"):
        for path in sorted(directoy.glob(pattern=pattern)): #sorted(directory.glob(pattern)) does alphabetical iteration. Without sorted, the order is filesystem-dependent (sometimes inode order, sometimes mtime order, varies by OS).
            all_defs.extend(load_definitions_from_file(path=path))
            
    return all_defs

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
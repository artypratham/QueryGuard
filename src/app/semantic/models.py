from typing import Optional
from pydantic import BaseModel, Field

class SemanticDefinition(BaseModel):
    # A single business metric definition
    metric_name:        str = Field(..., description="snake_case identifier") #... is pydantic Ellipsis which means that this Field is requried
    display_name:       str 
    description:        str
    required_filters:   list[str] = Field(default_factory=list) #default_factory=list helps to create a fresh empty list for every instance of the class using the required filters, otherwise the same list object would have been shared by other instances of the class 
    time_dimension:     Optional[str]   = None
    grain:              Optional[str]   = None
    owner:              Optional[str]   = None
    tags:               list[str]       = Field(default_factory=list)
    raw_yaml:           Optional[str]   = None # we are adding this so the audit logs can record exactly what definition was applied to which query.
    #if the YAML changes, old audit entries still show the version that was actually in force at query time.
    
    
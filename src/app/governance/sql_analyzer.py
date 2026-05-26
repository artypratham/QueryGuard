# This is a stub required by the parser.py


import sqlglot
from sqlglot import exp

# we will parse a YAML sourced required_filter fragmet as sql WHERE predicate
# sql_glot.parse expects a full statement not a single bare predicate
# Trick : Wrap the fragment in SELECT 1 from t WHERE {fragment}, parse that, and return the predicate expression.
# This is the most reliable way to get a parse across all the predicate shapes we accept (binary comparisons, IS NULL, IN).
def parse_required_filter(fragment: str) -> exp.Expression:

        
    if not fragment or not fragment.strip():
        raise ValueError("required_filters fragment is empty")
    
    wrapped = f"SELECT 1 from t WHERE {fragment}" #sqlglot's parser is built to parse complete SQL statements.Calling parse_one with half ass sql statement throws error.
    #so  we wrap the predicate in a dummy SQL statement, this gets parsed and we pluch out the predicate node from the resulting AST.
    
    try:
        stmt = sqlglot.parse_one(wrapped , read = "duckdb") #This gets parsed and we pluck out the predicate node from the resulting AST.
        
    except sqlglot.errors.ParseError as e:
        raise ValueError(
            "Could not parse required_filter fragment {fragment}: {e}"
        ) from e
        
    where_clause = stmt.args.get("where") #.args.get("where") returns the Where wrapper node
    
    if where_clause is None:
        raise ValueError(
            "fragment {fragment} did not produce a WHERE clause when wrapped in a select"
        )
    
    return where_clause.this # .this attirbute on where_clause is the actual predicate expression.
        
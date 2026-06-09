import logging
from typing import Optional
from app.semantic.search import Metric_Search_Engine
from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

class SemanticRegistry:
    def __init__(
        self,
        definitions : list[dict],
        search_engine: Metric_Search_Engine,
        settings : Settings | None = None
        ):
        
        if settings is None:
            settings = get_settings()
        
        self._definitions = {d["metric name"]: d for d in definitions}
        self._engine = search_engine
        self._top_k = settings.semantic_search_top_k
        self._threshold = settings.semantic_Search_threshold
        
        async def lookup(Self, question: str) -> list[dict]:
            results = await self._engine.search(
                query=question,
                top_k=self._top_k,
                threshold=self._threshold,
            )
            
            matched = []
            for result in results:
                d = dict(result.definition)
                d["_similarity"] = result.similarity 
                matched.append(d)
            
            if matched:
                names_and_scores = ", ".join(
                    f"{d['metric_name']} ({d['_similarity']:.2f})" for d in matched
                )
            logger.info(f"Semantic lookup: {names_and_scores}")
            
            return matched
        
    def get_all_definitions(self) -> list[dict]:
        return list(self._definitions.values())
    
    def get_by_name(self, metric_name: str) -> Optional[str]:
         return self._definitions.get(metric_name)

        
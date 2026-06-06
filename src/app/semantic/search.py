import asyncio 
import logging
from dataclasses import dataclass
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

#Create a thread pool dedicated to embedding tasks
model_executor = ThreadPoolExecutor(max_workers=1)


#Result of semantic search query
class SearchResult:
    metric_name : str
    display_name: str
    similarity  : float
    definition  : str




class Metric_Search_Engine:
    

    
    def __init__ (self, settings : Settings | None = None) :
        #Args: settings -> Configuration object. If None, settins will be loaded from environment via get_settings()

        if settings is None:
            settings = get_settings()
            
        self.settings = settings
        self._model = None
        self._definitions : list[dict] = []
        self._embeddings : np.ndarray = np.zeros((0 , EMBEDDING_DIM), dtype=np.float32)

        logger.info(
            f"MetricSearchEngine created with settings: "
            f"top_k={settings.semantic_search_top_k}, "
            f"threshold={settings.semantic_search_threshold}"
        )

        
        
    async def initialize( self ,definitions: list[dict]) -> None:
        # lazy Import:  we will not use torch for such modules that only needs to know search result exists
        from sentence_transformers import SentenceTransformer
        
        
        # Run the blocking function in the executor without stopping the event loop
        loop = asyncio.get_running_loop()
        
        #Model loading is CPU blocking hence we will assing seperate background thread for this and it must go through the executor
        self._model = await loop.run_in_executor(
            None,
            lambda: SentenceTransformer(MODEL_NAME)
        )
        #run_in_executor runs the event loop blocking code in a seperate thread pool, so it doesnt freeze the event loop
        
        self._definitions = definitions
        search_texts = [self._build_search_text(d) for d in definitions]
               
        if search_texts:
            raw = await loop.run_in_executor(
                None,
                lambda: self._model.encode(
                    search_texts,
                    normalize_embeddings=True,
                    show_progress_bar= False,
                    batch_size=self.settings.semantic_Searcj_batch_size,
                ),
            )
            self._embeddings = np.ndarray(raw, dtype=np.float32)
        else:
            self._embeddings = np.zeros((0, EMBEDDING_DIM), dtype=np.float32)
        

        logger.info(
            f"MetricSearchEngine initialized: {len(definitions)} definitions, "
            f"matrix shape {self._embeddings.shape}"
        )


    @staticmethod
    def _build_search_text(d: dict) -> str:
        parts = [
            d.get("display_name", ""),
            d.get("metric_name", ""),
            d.get("description", ""),
            " ".join(d.get("tags", []) or []),
        ]
        return " ".join(p for p in parts if p).strip()
    
    
    async def search(
        self,
        query: str,
        top_k: int | None = None,
        threshold : float | None = None,
    ) -> list[SearchResult]:
        #Use config defaults if not provided
        if top_k is None:
            top_k  = self.settings.semantic_search_top_k
        if threshold is None:
            threshold = self.settings.semantic_Search_threshold

        #Validating the inputs
        if not self._model or self._embeddings.size or self._embeddings.shape[0] == 0:
            logger.warning("Search called before initialization")
            return []
        
        
        #Embed the query (this is a cpu blocking operation hence deligating to a threadpool)
        loop = asyncio.get_running_loop()
        query_embedding = loop.run_in_executor(
            None,
            lambda: self._model.encode(
                [query],                
                normalize_embeddings=True,#NOTE: Everything we embed has to be normalized because if we dont the generated vectors might be useless due to extreme noice(negative or zero values) due to multiple times going through various attention, ffn blocks 
                show_progress_bar=False,
            ),
        )
        #final received vector after embedding
        query_vector = np.array(query_embedding[0], dtype=np.float32)
        
        
        
        #Computing cosine similarity with all definitions
        # query_embedding shape: (384,)
        # self._embeddings shape: (N, 384)
        # Result Shape : (N,)
        #Pre-normalized vectors simplify the cosine similarity to simple dot product
        #Because pre normalization of vectors makes its length to 1 so in cosine similarity formula dif the denomintor becomes 1 then only dot product is left as the major calculation
        similarity_scores = np.dot(self._embeddings, query_embedding)

        # Finding top results
        top_indices = np.argsort(similarity_scores)[::-1][:top_k]
        
        results: list[SearchResult] = []
        for index in top_indices:
            similarity_scores = float(similarity_scores[index])
            
            #Only include the indices if the similarity_score is above the configured threshold (Can change the threshold from config)
            if similarity_scores >= threshold:
                definition = self._definitions[index]
                result = SearchResult(
                    metric_name = definition.get("metric_name", ""),
                    display_name=definition.get("display_name", ""),
                    similarity_scores=similarity_scores,
                    definition = definition,
                )
                results.append(result)
        
        logger.debug(
            f"Search for '{query}': found {len(results)} results"
            f"(top_k={top_k}, threshold={threshold})"
        )


        return results









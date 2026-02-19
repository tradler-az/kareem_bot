"""
Bosco Core - Vector Memory System
ChromaDB-based semantic memory for RAG and infinite context
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import hashlib

# Try to import chromadb, fallback to simple in-memory if not available
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("[VectorMemory] ChromaDB not available, using in-memory fallback")

# Try sentence transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class VectorMemory:
    """
    Vector-based semantic memory for Bosco Core
    Enables semantic search across conversations, codebase, and documents
    """
    
    def __init__(self, storage_dir: str = "data/vector_store", embedding_model: str = "all-MiniLM-L6-v2"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.embedding_model = embedding_model
        self.embedder = None
        self.client = None
        self.collection = None
        
        # In-memory fallback if chromadb not available
        self._in_memory_store: List[Dict] = []
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the vector store"""
        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer(self.embedding_model)
                print(f"[VectorMemory] Loaded embedding model: {self.embedding_model}")
            except Exception as e:
                print(f"[VectorMemory] Could not load embedding model: {e}")
                self.embedder = self._simple_embedder
        else:
            self.embedder = self._simple_embedder
        
        # Initialize ChromaDB
        if CHROMADB_AVAILABLE:
            try:
                self.client = chromadb.PersistentClient(
                    path=str(self.storage_dir),
                    settings=Settings(anonymized_telemetry=False)
                )
                # Try to get or create collection
                try:
                    self.collection = self.client.get_collection("bosco_memory")
                except:
                    self.collection = self.client.create_collection(
                        "bosco_memory",
                        metadata={"description": "Bosco Core semantic memory"}
                    )
                print("[VectorMemory] ChromaDB initialized successfully")
            except Exception as e:
                print(f"[VectorMemory] ChromaDB init error: {e}")
                self.client = None
        else:
            print("[VectorMemory] Using in-memory fallback")
    
    def _simple_embedder(self, texts: List[str]) -> List[List[float]]:
        """Simple hash-based embedding fallback"""
        embeddings = []
        for text in texts:
            # Create a simple deterministic embedding based on text hash
            hash_val = hash(text.encode()) % (2**32)
            # Create a sparse vector with some positions set
            vec = [0.0] * 384
            for i in range(min(len(text), 384)):
                vec[i] = (hash_val >> i) % 100 / 100.0
            embeddings.append(vec)
        return embeddings
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        embeddings = self.embedder([text])
        return embeddings[0].tolist() if hasattr(embeddings[0], 'tolist') else embeddings[0]
    
    def add(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a document to semantic memory
        
        Args:
            text: The text content to store
            metadata: Optional metadata dictionary
            doc_id: Optional custom document ID
            
        Returns:
            The document ID
        """
        if doc_id is None:
            doc_id = f"doc_{datetime.now().timestamp()}"
        
        meta = metadata or {}
        meta["text"] = text[:200]  # Store preview
        meta["timestamp"] = datetime.now().isoformat()
        
        if CHROMADB_AVAILABLE and self.collection is not None:
            try:
                embedding = self._get_embedding(text)
                self.collection.add(
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[meta],
                    ids=[doc_id]
                )
            except Exception as e:
                print(f"[VectorMemory] Add error: {e}")
                # Fallback to in-memory
                self._in_memory_store.append({
                    "id": doc_id,
                    "text": text,
                    "metadata": meta
                })
        else:
            # In-memory fallback
            self._in_memory_store.append({
                "id": doc_id,
                "text": text,
                "metadata": meta
            })
        
        return doc_id
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across stored documents
        
        Args:
            query: The search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of matching documents with scores
        """
        results = []
        
        if CHROMADB_AVAILABLE and self.collection is not None:
            try:
                query_embedding = self._get_embedding(query)
                
                where = filter_metadata if filter_metadata else None
                
                search_results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where,
                    include=["documents", "metadatas", "distances"]
                )
                
                if search_results["ids"] and search_results["ids"][0]:
                    for i, doc_id in enumerate(search_results["ids"][0]):
                        results.append({
                            "id": doc_id,
                            "text": search_results["documents"][0][i],
                            "metadata": search_results["metadatas"][0][i],
                            "distance": search_results["distances"][0][i],
                            "score": 1 - search_results["distances"][0][i]  # Convert distance to similarity
                        })
            except Exception as e:
                print(f"[VectorMemory] Search error: {e}")
        
        # If no results from ChromaDB or not available, use in-memory search
        if not results:
            results = self._in_memory_search(query, n_results)
        
        return results
    
    def _in_memory_search(self, query: str, n_results: int) -> List[Dict]:
        """Simple in-memory search fallback"""
        query_lower = query.lower()
        
        # Score by keyword matching
        scored = []
        query_words = set(query_lower.split())
        
        for doc in self._in_memory_store:
            text_lower = doc["text"].lower()
            
            # Calculate simple relevance score
            matches = sum(1 for word in query_words if word in text_lower)
            score = matches / max(len(query_words), 1)
            
            if score > 0:
                scored.append({
                    "id": doc["id"],
                    "text": doc["text"],
                    "metadata": doc.get("metadata", {}),
                    "score": score
                })
        
        # Sort by score and return top n
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:n_results]
    
    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        if CHROMADB_AVAILABLE and self.collection is not None:
            try:
                result = self.collection.get(ids=[doc_id])
                if result["ids"] and result["ids"][0]:
                    return {
                        "id": result["ids"][0],
                        "text": result["documents"][0],
                        "metadata": result["metadatas"][0]
                    }
            except:
                pass
        
        # Fallback search
        for doc in self._in_memory_store:
            if doc["id"] == doc_id:
                return doc
        
        return None
    
    def delete(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        if CHROMADB_AVAILABLE and self.collection is not None:
            try:
                self.collection.delete(ids=[doc_id])
                return True
            except:
                pass
        
        # In-memory delete
        initial_len = len(self._in_memory_store)
        self._in_memory_store = [d for d in self._in_memory_store if d["id"] != doc_id]
        return len(self._in_memory_store) < initial_len
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        total_docs = 0
        
        if CHROMADB_AVAILABLE and self.collection is not None:
            try:
                total_docs = self.collection.count()
            except:
                pass
        
        if total_docs == 0:
            total_docs = len(self._in_memory_store)
        
        return {
            "total_documents": total_docs,
            "storage_dir": str(self.storage_dir),
            "embedding_model": self.embedding_model,
            "chromadb_available": CHROMADB_AVAILABLE,
            "embeddings_available": SENTENCE_TRANSFORMERS_AVAILABLE
        }
    
    def clear(self):
        """Clear all stored data"""
        if CHROMADB_AVAILABLE and self.collection is not None:
            try:
                self.client.delete_collection("bosco_memory")
                self.collection = self.client.create_collection(
                    "bosco_memory",
                    metadata={"description": "Bosco Core semantic memory"}
                )
            except:
                pass
        
        self._in_memory_store.clear()
        print("[VectorMemory] Memory cleared")


class SemanticContext:
    """
    High-level semantic context manager
    Combines vector memory with conversation context
    """
    
    def __init__(self, vector_memory: Optional[VectorMemory] = None):
        self.vector_memory = vector_memory or VectorMemory()
        self.current_session_context: List[Dict] = []
    
    def add_interaction(self, user_message: str, bot_response: str, intent: str = ""):
        """Add a conversation interaction to memory"""
        # Add user message
        self.vector_memory.add(
            text=f"User: {user_message}",
            metadata={
                "type": "conversation",
                "role": "user",
                "intent": intent
            }
        )
        
        # Add bot response
        self.vector_memory.add(
            text=f"Bosco: {bot_response}",
            metadata={
                "type": "conversation",
                "role": "assistant",
                "intent": intent
            }
        )
        
        # Track in session
        self.current_session_context.append({
            "user": user_message,
            "bot": bot_response,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_knowledge(self, text: str, category: str = "general", source: str = "user"):
        """Add knowledge to the semantic memory"""
        self.vector_memory.add(
            text=text,
            metadata={
                "type": "knowledge",
                "category": category,
                "source": source
            }
        )
    
    def add_code(self, code: str, language: str = "python", description: str = ""):
        """Add code snippet to memory"""
        self.vector_memory.add(
            text=f"```{language}\n{code}\n```\n{description}",
            metadata={
                "type": "code",
                "language": language,
                "description": description
            }
        )
    
    def search_context(self, query: str, include_session: bool = True) -> Dict[str, Any]:
        """
        Search for relevant context
        
        Returns:
            Dictionary with semantic_results and session_context
        """
        # Search vector memory
        semantic_results = self.vector_memory.search(query, n_results=5)
        
        # Get recent session context
        session_context = self.current_session_context[-5:] if include_session else []
        
        return {
            "semantic_results": semantic_results,
            "session_context": session_context,
            "query": query
        }
    
    def get_relevant_context(self, query: str, max_tokens: int = 2000) -> str:
        """
        Get formatted relevant context for LLM prompt
        
        Args:
            query: The current user query
            max_tokens: Approximate max tokens (rough estimate)
            
        Returns:
            Formatted context string
        """
        context_data = self.search_context(query)
        
        context_parts = []
        
        # Add relevant past conversations
        for result in context_data["semantic_results"][:3]:
            if result.get("metadata", {}).get("type") == "conversation":
                context_parts.append(f"Past: {result['text'][:200]}")
        
        # Add session history
        for msg in context_data["session_context"][-3:]:
            context_parts.append(f"Session: User: {msg['user'][:100]}")
        
        return "\n".join(context_parts) if context_parts else ""


# Global instances
_vector_memory: Optional[VectorMemory] = None
_semantic_context: Optional[SemanticContext] = None


def get_vector_memory() -> VectorMemory:
    """Get the global vector memory instance"""
    global _vector_memory
    if _vector_memory is None:
        _vector_memory = VectorMemory()
    return _vector_memory


def get_semantic_context() -> SemanticContext:
    """Get the global semantic context instance"""
    global _semantic_context
    if _semantic_context is None:
        _semantic_context = SemanticContext(get_vector_memory())
    return _semantic_context


if __name__ == "__main__":
    # Test the vector memory
    print("=== Testing Vector Memory ===\n")
    
    # Create instance
    vm = VectorMemory()
    
    print(f"Stats: {vm.get_stats()}\n")
    
    # Add some test data
    print("Adding test documents...")
    
    vm.add(
        "Bosco's creator is named Tradler",
        metadata={"type": "fact", "category": "creator"}
    )
    
    vm.add(
        "Bosco can control the computer using pyautogui",
        metadata={"type": "fact", "category": "capability"}
    )
    
    vm.add(
        "The user prefers dark mode interface",
        metadata={"type": "preference", "category": "ui"}
    )
    
    vm.add(
        'def open_application(app_name):\n    import pyautogui\n    pyautogui.hotkey("super", "type", app_name)\n    return f"Opening {app_name}"',
        metadata={"type": "code", "language": "python"}
    )
    
    # Search tests
    print("\n--- Search Tests ---")
    
    queries = [
        "who created Bosco",
        "computer control",
        "user interface preferences",
        "python code function"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = vm.search(query, n_results=3)
        for r in results:
            print(f"  Score: {r.get('score', 0):.3f} | {r.get('text', '')[:60]}...")
    
    print(f"\nFinal Stats: {vm.get_stats()}")


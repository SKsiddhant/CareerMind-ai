import os
import json
import shutil
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from sentence_transformers import CrossEncoder
from dotenv import load_dotenv

load_dotenv()

class RAGPipeline:
    def __init__(self, persist_directory="./data/chroma_db", 
                 model_name="BAAI/bge-base-en-v1.5",
                 rerank_model="BAAI/bge-reranker-base"):
        self.persist_directory = persist_directory
        
        print(f"Loading Embedding Model: {model_name}...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        print(f"Loading Re-ranker Model: {rerank_model}...")
        self.reranker = CrossEncoder(rerank_model, device='cpu')
        
        self.vector_db = None
        self._init_db()

    def _init_db(self):
        # Always initialize with the persist directory
        self.vector_db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

    def reset_index(self):
        """Clear the existing index to avoid model mismatch errors"""
        print(f"Resetting index at {self.persist_directory}...")
        
        # In newer LangChain/Chroma, we might need to explicitly handle the client
        self.vector_db = None
        
        # Give Windows a moment to release file locks
        import time
        import gc
        gc.collect() # Force garbage collection to close file handles
        time.sleep(2)

        if os.path.exists(self.persist_directory):
            try:
                shutil.rmtree(self.persist_directory)
                print("Old index deleted successfully.")
            except Exception as e:
                print(f"Warning: Could not delete index directory automatically: {e}")
                print("Proceeding with manual cleanup if possible...")
        
        self._init_db()

    def add_jobs_to_index(self, jobs_json_path="data/jobs.json"):
        if not os.path.exists(jobs_json_path):
            print(f"No jobs file found at {jobs_json_path}")
            return

        with open(jobs_json_path, 'r') as f:
            jobs = json.load(f)

        documents = []
        ids = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700, 
            chunk_overlap=70,
            separators=["\n\n", "\n", ".", " ", ""]
        )

        for job in jobs:
            # Skip invalid/error scrapes
            desc = job.get('description', '')
            if "Page not found" in desc or job.get('title') == "N/A" or not desc:
                continue
            
            # Use company and skills in content for better searchability
            company = job.get('company', 'Unknown')
            title = job.get('title', 'N/A')
            skills = ", ".join(job.get('skills', []))
            content = f"Company: {company}\nTitle: {title}\nSkills: {skills}\nDescription: {desc}"
            
            metadata = {
                "url": job.get("url"), 
                "company": company,
                "title": title,
                "skills": skills,
                "location": job.get("location"),
                "hiring_manager": job.get("hiring_manager"),
                "scraped_at": job.get("scraped_at")
            }
            
            # Clean up None values in metadata for ChromaDB compatibility
            metadata = {k: v for k, v in metadata.items() if v is not None}
            
            # Create a unique ID for each chunk using the URL and a chunk index
            chunks = text_splitter.split_text(content)
            
            for i, chunk in enumerate(chunks):
                documents.append(Document(page_content=chunk, metadata=metadata))
                ids.append(f"{job['url']}#chunk{i}")

        if not documents:
            print("No new valid job documents to index.")
            return

        print(f"Syncing {len(documents)} chunks with ChromaDB (idempotent)...")
        # Upsert: adding with IDs will replace existing or add new
        self.vector_db.add_documents(documents=documents, ids=ids)
        print("Indexing complete.")

    def query_jobs(self, query, k=15, rerank_top_n=5, score_threshold=0.3):
        if not self.vector_db:
            return []
        
        print(f"1. Vector Search for: '{query}'")
        # Step 1: Broad Vector Search
        initial_results = self.vector_db.similarity_search(query, k=k)
        
        if not initial_results:
            return []

        # Step 2: Cross-Encoder Re-ranking
        print(f"2. Re-ranking top {len(initial_results)} results for 'utmost' relevance...")
        pairs = [[query, doc.page_content] for doc in initial_results]
        rerank_scores = self.reranker.predict(pairs)
        
        # Combine and sort by rerank score
        scored_results = []
        for i, doc in enumerate(initial_results):
            scored_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": float(rerank_scores[i])
            })
        
        # Sort by relevance score (descending)
        scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Filter by threshold and limit to top_n
        final_results = [r for r in scored_results if r['relevance_score'] > score_threshold][:rerank_top_n]
        
        return final_results

if __name__ == "__main__":
    pipeline = RAGPipeline()
    
    print("Checking for existing data and adding new jobs...")
    pipeline.add_jobs_to_index()
    
    test_query = "software engineer artificial intelligence"
    print(f"\nTesting Query: '{test_query}'")
    results = pipeline.query_jobs(test_query)
    
    if not results:
        print("No results found. Try running the scraper first to populate data/jobs.json.")
    else:
        for i, res in enumerate(results):
            print(f"\n--- Result {i+1} (Relevance Score: {res['relevance_score']:.4f}) ---")
            print(f"Company: {res['metadata'].get('company')}")
            print(f"Title: {res['metadata'].get('title')}")
            print(f"Content Snippet: {res['content'][:200]}...")
            print(f"URL: {res['metadata'].get('url')}")

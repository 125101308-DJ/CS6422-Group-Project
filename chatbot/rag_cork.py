"""
Cork Restaurant RAG System - Optimized for Mistral 7B
Complete setup with Mistral-specific configurations
"""

import os
from typing import List, Dict
import pandas as pd

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import LlamaCpp
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class CorkRestaurantRAG:
    """
    RAG system for Cork restaurants using Mistral 7B and FAISS
    """
    
    def __init__(
        self,
        model_path: str,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 400,
        chunk_overlap: int = 50,
        verbose: bool = True
    ):
        """
        Initialize the RAG pipeline with Mistral 7B
        
        Args:
            model_path: Path to Mistral GGUF model file
            embedding_model: HuggingFace embedding model
            chunk_size: Text chunk size
            chunk_overlap: Overlap between chunks
            verbose: Show detailed output
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vectorstore = None
        self.qa_chain = None
        self.verbose = verbose
        
        # Initialize embeddings
        if self.verbose:
            print("📦 Loading embedding model...")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},  # Change to 'cuda' for GPU
            encode_kwargs={'normalize_embeddings': True}
        )
        
        if self.verbose:
            print("✓ Embeddings loaded")
        
        # Initialize Mistral model with optimized settings
        if self.verbose:
            print("🤖 Loading Mistral 7B model...")
        
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        
        # Mistral-specific configuration
        self.llm = LlamaCpp(
            model_path=model_path,
            temperature=0.2,  # Lower for factual responses
            max_tokens=256,   # Shorter, more focused answers
            top_p=0.9,        # Slightly lower for consistency
            top_k=40,         # Mistral works well with this
            repeat_penalty=1.1,  # Reduce repetition
            callback_manager=callback_manager,
            verbose=False,
            n_ctx=4096,       # Mistral has 4k context (can use 8k for v0.2)
            n_batch=512,
            n_threads=4,      # Adjust based on your CPU cores
        )
        
        if self.verbose:
            print("✓ Mistral 7B loaded and ready")
    
    def load_restaurant_csv(self, csv_path: str) -> List[Document]:
        """Load Cork restaurant data from CSV"""
        if self.verbose:
            print(f"\n📂 Loading restaurant data from {csv_path}...")
        
        df = pd.read_csv(csv_path)
        
        if self.verbose:
            print(f"✓ Loaded {len(df)} restaurants")
        
        documents = []
        
        for idx, row in df.iterrows():
            content = self._format_restaurant(row)
            
            metadata = {
                'name': str(row.get('name', '')),
                'place_id': str(row.get('place_id', '')),
                'restaurant_type': str(row.get('restaurant_type', '')),
                'cuisine_type': str(row.get('cuisine_type', '')),
                'address': str(row.get('address', '')),
                'row_index': idx
            }
            
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)
        
        return documents
    
    def _format_restaurant(self, row: pd.Series) -> str:
        """Format restaurant data for optimal Mistral understanding"""
        parts = []
        
        name = row.get('name', 'Unknown')
        restaurant_type = row.get('restaurant_type', '')
        cuisine_type = row.get('cuisine_type', '')
        address = row.get('address', '')
        
        # Mistral prefers clear, structured format
        parts.append(f"Name: {name}")
        
        if restaurant_type:
            parts.append(f"Type: {restaurant_type}")
        
        if cuisine_type:
            parts.append(f"Cuisine: {cuisine_type}")
        
        if address:
            parts.append(f"Address: {address}")
            
            # Extract location info
            location_keywords = {
                'Centre': 'Cork City Centre',
                'Blackpool': 'Blackpool',
                'Ballincollig': 'Ballincollig',
                'Ballintemple': 'Ballintemple',
                'Douglas': 'Douglas',
                'Oliver Plunkett': 'Oliver Plunkett Street area',
                'Washington St': 'Washington Street area',
                'MacCurtain': 'MacCurtain Street area',
                'The Lough': 'The Lough area',
                'Victorian Quarter': 'Victorian Quarter'
            }
            
            for keyword, location in location_keywords.items():
                if keyword in address:
                    parts.append(f"Area: {location}")
                    break
        
        # Add searchable summary
        parts.append(f"Description: {name} is a {restaurant_type} in Cork serving {cuisine_type} cuisine")
        
        return "\n".join(parts)
    
    def create_vector_store(self, documents: List[Document]):
        """Create FAISS vector store from documents"""
        if self.verbose:
            print("\n🔄 Processing documents...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        splits = text_splitter.split_documents(documents)
        
        if self.verbose:
            print(f"✓ Created {len(splits)} chunks from {len(documents)} restaurants")
            print("🔄 Creating vector embeddings...")
        
        self.vectorstore = FAISS.from_documents(
            documents=splits,
            embedding=self.embeddings
        )
        
        if self.verbose:
            print("✓ Vector store created successfully")
    
    def save_vector_store(self, path: str = "cork_restaurants_faiss"):
        """Save vector store to disk"""
        if self.vectorstore is None:
            raise ValueError("Vector store not created yet")
        
        self.vectorstore.save_local(path)
        
        if self.verbose:
            print(f"💾 Vector store saved to {path}")
    
    def load_vector_store(self, path: str = "cork_restaurants_faiss"):
        """Load vector store from disk"""
        self.vectorstore = FAISS.load_local(
            path, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        if self.verbose:
            print(f"📁 Vector store loaded from {path}")
    
    def setup_qa_chain(self, k: int = 4):
        """
        Setup QA chain optimized for Mistral 7B
        
        Args:
            k: Number of documents to retrieve
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not created. Call create_vector_store() first")
        
        # Mistral-optimized prompt template
        # Mistral uses [INST] tags for instructions
        template = """<s>[INST] You are a helpful Cork restaurant assistant. Use the restaurant information below to answer questions about dining in Cork, Ireland.

Guidelines:
- Be concise and helpful
- Recommend specific restaurants from the information provided
- Include name, type, cuisine, and address when relevant
- If asked about location, focus on restaurants in that area
- If you don't have the information, say so

Restaurant Information:
{context}

Question: {question} [/INST]

Answer: """
        
        PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create retriever
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        if self.verbose:
            print(f"✓ QA chain ready (retrieving top {k} documents)")
    
    def query(self, question: str, return_sources: bool = False) -> Dict:
        """Query the RAG system"""
        if self.qa_chain is None:
            raise ValueError("QA chain not setup. Call setup_qa_chain() first")
        
        result = self.qa_chain({"query": question})
        
        response = {
            "answer": result["result"].strip(),
        }
        
        if return_sources:
            response["source_documents"] = result["source_documents"]
            response["source_names"] = [
                doc.metadata.get('name', 'Unknown') 
                for doc in result["source_documents"]
            ]
        
        return response
    
    def query_simple(self, question: str) -> str:
        """Simple query returning just the answer"""
        result = self.query(question, return_sources=False)
        return result["answer"]
    
    def search_by_cuisine(self, cuisine: str, limit: int = 5) -> List[Dict]:
        """Search restaurants by cuisine type"""
        if self.vectorstore is None:
            raise ValueError("Vector store not created yet")
        
        query = f"restaurants serving {cuisine} cuisine"
        docs = self.vectorstore.similarity_search(query, k=limit)
        
        results = []
        seen_names = set()
        
        for doc in docs:
            name = doc.metadata.get('name')
            if name and name not in seen_names:
                seen_names.add(name)
                results.append({
                    'name': name,
                    'type': doc.metadata.get('restaurant_type'),
                    'cuisine': doc.metadata.get('cuisine_type'),
                    'address': doc.metadata.get('address')
                })
        
        return results
    
    def search_by_location(self, location: str, limit: int = 5) -> List[Dict]:
        """Search restaurants by location"""
        if self.vectorstore is None:
            raise ValueError("Vector store not created yet")
        
        query = f"restaurants in {location} Cork"
        docs = self.vectorstore.similarity_search(query, k=limit)
        
        results = []
        seen_names = set()
        
        for doc in docs:
            name = doc.metadata.get('name')
            if name and name not in seen_names:
                seen_names.add(name)
                results.append({
                    'name': name,
                    'type': doc.metadata.get('restaurant_type'),
                    'cuisine': doc.metadata.get('cuisine_type'),
                    'address': doc.metadata.get('address')
                })
        
        return results
    
    def search_by_type(self, rest_type: str, limit: int = 5) -> List[Dict]:
        """Search by restaurant type (Pub, Café, etc.)"""
        if self.vectorstore is None:
            raise ValueError("Vector store not created yet")
        
        query = f"{rest_type} in Cork"
        docs = self.vectorstore.similarity_search(query, k=limit)
        
        results = []
        seen_names = set()
        
        for doc in docs:
            name = doc.metadata.get('name')
            if name and name not in seen_names:
                seen_names.add(name)
                results.append({
                    'name': name,
                    'type': doc.metadata.get('restaurant_type'),
                    'cuisine': doc.metadata.get('cuisine_type'),
                    'address': doc.metadata.get('address')
                })
        
        return results


def setup_mistral_rag(csv_path: str, force_rebuild: bool = False):
    """
    Quick setup function for Mistral RAG system
    
    Args:
        csv_path: Path to Cork restaurants CSV
        force_rebuild: Force rebuild of vector store
        
    Returns:
        Configured CorkRestaurantRAG instance
    """
    MODEL_PATH = "./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    VECTOR_STORE_PATH = "cork_restaurants_faiss_mistral"
    
    print("="*70)
    print("🍽️  Cork Restaurant RAG System - Mistral 7B")
    print("="*70)
    
    # Initialize RAG
    rag = CorkRestaurantRAG(model_path=MODEL_PATH)
    
    # Load or create vector store
    if not force_rebuild and os.path.exists(VECTOR_STORE_PATH):
        print("\n📁 Loading existing vector store...")
        rag.load_vector_store(VECTOR_STORE_PATH)
    else:
        print("\n🔨 Building vector store (first time setup)...")
        documents = rag.load_restaurant_csv(csv_path)
        rag.create_vector_store(documents)
        rag.save_vector_store(VECTOR_STORE_PATH)
    
    # Setup QA chain
    print("\n⚙️  Setting up QA chain...")
    rag.setup_qa_chain(k=4)
    
    print("\n" + "="*70)
    print("✅ System Ready!")
    print("="*70)
    
    return rag


# Main execution
if __name__ == "__main__":
    # Configuration
    CSV_FILE = "cork_restaurants.csv"
    
    # Setup system
    rag = setup_mistral_rag(CSV_FILE)
    
    # Example queries
    print("\n🔍 Testing with example queries...\n")
    
    test_queries = [
        "What Irish pubs are in Cork city centre?",
        "Where can I find good cafes?",
        "Show me restaurants on MacCurtain Street",
        "What gastropubs are available in Cork?",
        "Where can I get coffee in the city centre?",
    ]
    
    for i, question in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}: {question}")
        print('='*70)
        
        result = rag.query(question, return_sources=True)
        
        print(f"\n{result['answer']}")
        
        if result.get('source_names'):
            print(f"\n📍 Sources: {', '.join(set(result['source_names'][:3]))}")
        
        print()
    
    # Example: Search by cuisine
    print("\n" + "="*70)
    print("🍜 Searching Irish restaurants...")
    print("="*70)
    
    irish_restaurants = rag.search_by_cuisine("Irish", limit=5)
    for rest in irish_restaurants:
        print(f"\n• {rest['name']}")
        print(f"  Type: {rest['type']}")
        print(f"  Cuisine: {rest['cuisine']}")
        print(f"  Address: {rest['address']}")
    
    print("\n" + "="*70)
    print("✅ Demo Complete!")
    print("="*70)
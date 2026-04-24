import os

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import CharacterTextSplitter

load_dotenv()

if __name__ == "__main__":
    print("Ingesting...")
    loader = TextLoader("/Users/rpvp/POC/Python/langchain-course-forked/mediumblog1.txt")
    document = loader.load()

    print("Splitting...")
    # Use smaller chunk size to avoid oversized chunks
    text_splitter = CharacterTextSplitter(
        chunk_size=800,  # Smaller to stay under limit with overlap
        chunk_overlap=100,  # Some overlap for better context
        separator="\n\n"  # Split on paragraphs when possible
    )
    texts = text_splitter.split_documents(document)
    print(f"Created {len(texts)} chunks")

    # Check chunk sizes
    oversized_chunks = [i for i, text in enumerate(texts) if len(text.page_content) > 1000]
    if oversized_chunks:
        print(f"Warning: {len(oversized_chunks)} chunks are still over 1000 characters")
        for i in oversized_chunks[:3]:  # Show first 3
            print(f"  Chunk {i}: {len(texts[i].page_content)} characters")

    # Initialize embeddings - this creates 1536-dimensional vectors
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        model="text-embedding-ada-002"  # Explicit model (1536 dimensions)
    )

    print("Ingesting to Pinecone...")
    try:
        vectorstore = PineconeVectorStore.from_documents(
            texts,
            embeddings,
            index_name=os.environ["INDEX_NAME"]
        )
        print("✅ Ingestion completed successfully!")
        print(f"Ingested {len(texts)} text chunks to index: {os.environ['INDEX_NAME']}")

    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        print("\n🔧 If you see dimension mismatch error, run: python fix_pinecone_index.py")
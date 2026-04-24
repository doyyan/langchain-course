import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

def recreate_pinecone_index():
    """Delete and recreate Pinecone index with correct dimensions for OpenAI embeddings"""

    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index_name = os.environ["INDEX_NAME"]

    print(f"Working with index: {index_name}")

    # Check if index exists
    existing_indexes = [index.name for index in pc.list_indexes()]
    print(f"Existing indexes: {existing_indexes}")

    if index_name in existing_indexes:
        print(f"Deleting existing index: {index_name}")
        pc.delete_index(index_name)

        # Wait for deletion to complete
        print("Waiting for deletion to complete...")
        while index_name in [index.name for index in pc.list_indexes()]:
            time.sleep(1)
        print("Index deleted successfully!")

    # Create new index with 1536 dimensions for OpenAI embeddings
    print(f"Creating new index: {index_name} with 1536 dimensions")
    pc.create_index(
        name=index_name,
        dimension=1536,  # OpenAI text-embedding-ada-002 dimensions
        metric="cosine",
        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
    )

    # Wait for index to be ready
    print("Waiting for index to be ready...")
    while index_name not in [index.name for index in pc.list_indexes()]:
        time.sleep(1)

    print("Index created successfully!")
    print("You can now run your ingestion script.")

if __name__ == "__main__":
    recreate_pinecone_index()
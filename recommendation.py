from dotenv import load_dotenv
import os
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains.question_answering import load_qa_chain
from langchain_groq import ChatGroq

# Function to retrieve matching results from the vector store
def retrieve_query(query, k=2):
    matching_results = vectorestore.similarity_search(query, k=k)
    return matching_results

# Function to retrieve an answer for a given query
def retrieve_answer(query):
    ans_search = retrieve_query(query)
    print("Matching results:", ans_search)
    response = chain.run(input_documents=ans_search, question=query)
    return response

# Load environment variables
load_dotenv()

# Initialize Pinecone with API key
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Load embeddings and vector store
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

index_name = "gymrecommendation-huggingface"
vectorestore = PineconeVectorStore(embedding=embeddings, index_name=index_name)

# Configure the language model
llm = ChatGroq(
    model="llama-3.1-70b-versatile",   # Specify the model name
    temperature=1,                     # Set the desired temperature
    max_tokens=7999,                   # Define the maximum number of tokens
    timeout=10,                        # Set a timeout in seconds
    max_retries=2                      # Number of retries in case of errors
)

# Load the question-answering chain
chain = load_qa_chain(llm, chain_type="stuff")

# Accept user query from the command line
if __name__ == "__main__":
    print("Welcome to the fitness recommendation system!")
    user_query = input("Please enter your query: ")
    answer = retrieve_answer(user_query)
    print("\nYour personalized recommendation:")
    print(answer)

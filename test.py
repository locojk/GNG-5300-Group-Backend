import json
from utils.env_loader import load_platform_specific_env
import os
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone as PineconeVectorStore
from langchain.chains.question_answering import load_qa_chain
from langchain_groq import ChatGroq
from langchain.output_parsers import StructuredOutputParser, ResponseSchema


# Function to retrieve matching results from the vector store
def retrieve_query(query, k=2):
    matching_results = vectorestore.similarity_search(query, k=k)
    # Ensure returned objects are compatible with the QA chain
    return matching_results

# Function to retrieve an answer for a given query
def retrieve_answer(input_data):
    query = input_data.get("query")
    if not query:
        raise ValueError("Query is required in the input JSON.")
    
    # Retrieve matching documents
    matching_docs = retrieve_query(query)
    
    # # Define the JSON schema for the response
    # response_schemas = [
    #     ResponseSchema(name="Workout Name", description="Name of the workout"),
    #     ResponseSchema(name="Duration", description="Duration of the workout in minutes"),
    #     ResponseSchema(name="Difficulty", description="Difficulty level of the workout"),
    #     ResponseSchema(name="Exercises", description="List of exercises included in the workout"),
    #     ResponseSchema(name="Estimated Calories Burned", description="Estimated calories burned during the workout"),
    #     ResponseSchema(name="Equipment Needed", description="List of equipment needed for the workout"),
    #     ResponseSchema(name="Additional Tips", description="Any additional tips for the user")
    # ]
    
    response_schemas = [
        ResponseSchema(name="Workout Name", description="Name of the workout"),
        ResponseSchema(name="Duration", description="Duration of the workout in minutes"),
        ResponseSchema(name="Difficulty", description="Difficulty level of the workout"),
        ResponseSchema(name="Exercises", description="List of exercises included in the workout, with instructions for each exercise"),
        ResponseSchema(name="Estimated Calories Burned", description="Estimated calories burned during the workout"),
        ResponseSchema(name="Equipment Needed", description="List of equipment needed for the workout"),
        ResponseSchema(name="Additional Tips", description="Any additional tips for the user"),
        ResponseSchema(name="Total Calories Burned", description="Total calories burned for the entire workout plan")
    ]

    # Set up the StructuredOutputParser
    parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = parser.get_format_instructions()
    
    # Construct the prompt
    question = (
        f"Based on the following user information:\n"
        f"- Sex: {input_data.get('Sex', 'Not Specified')}\n"
        f"- Age: {input_data.get('Age', 'Not Specified')}\n"
        f"- Height: {input_data.get('Height', 'Not Specified')}\n"
        f"- Weight: {input_data.get('Weight', 'Not Specified')}\n"
        f"- Hypertension: {input_data.get('Hypertension', False)}\n"
        f"- Diabetes: {input_data.get('Diabetes', False)}\n"
        f"- BMI: {input_data.get('BMI', 'Not Specified')}\n"
        f"- Level: {input_data.get('Level', 'Beginner')}\n"
        f"- Fitness Goal: {input_data.get('Fitness Goal', 'General Fitness')}\n"
        f"- Fitness Type: {input_data.get('Fitness Type', 'Any')}\n\n"
        f"Provide a personalized workout recommendation strictly in JSON format. "
        f"Make sure the JSON follows this structure:\n\n"
        f"{format_instructions}"
    )
    
    # Get the response from the model
    response = chain.invoke({
        "input_documents": matching_docs,
        "question": question
    })
    
    # Parse the response into JSON
    parsed_output = parser.parse(response["output_text"])
    return parsed_output

# Load environment variables
load_platform_specific_env()

# Initialize Pinecone with API key
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Load embeddings and vector store
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

index_name = "gymrecommendation-huggingface"
vectorestore = PineconeVectorStore.from_existing_index(embedding=embeddings, index_name=index_name)

# Configure the language model
llm = ChatGroq(
    model="llama-3.1-70b-versatile",   # Specify the model name
    temperature=0.7,                   # Set the desired temperature
    max_tokens=1000,                   # Define the maximum number of tokens
    timeout=10,                        # Set a timeout in seconds
    max_retries=2                      # Number of retries in case of errors
)

# Create the RetrievalQA chain
chain = load_qa_chain(llm=llm, chain_type='stuff')

# Accept user input as JSON and output JSON with workout recommendation
if __name__ == "__main__":
    print("Welcome to the fitness recommendation system!")
    
    # Read JSON input from the user
    json_input = input("Please enter your query in JSON format: ")
    
    try:
        # Parse the input JSON
        input_data = json.loads(json_input)
        
        # Retrieve the workout recommendation
        recommendation = retrieve_answer(input_data)
        
        # Return the output as JSON
        output_data = {
            "recommendation": recommendation
        }
        print("\nOutput in JSON format:")
        print(json.dumps(output_data, indent=4))
    
    except json.JSONDecodeError:
        print("Invalid JSON format. Please enter a valid JSON input.")
    except Exception as e:
        print(f"Error: {e}")
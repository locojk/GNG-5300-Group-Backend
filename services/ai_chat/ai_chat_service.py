"""
@Time ： 2024-11-28
@Auth ： Adam Lyu
"""
import os
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone as PineconeVectorStore
from langchain.chains.question_answering import load_qa_chain
from langchain_groq import ChatGroq
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

from daos.workout.fitness_goal_dao import FitnessGoalDAO
from utils.logger import Logger
from daos.user.users_dao import UserDAO

from utils.env_loader import load_platform_specific_env

# Load environment variables
load_platform_specific_env()
logger = Logger(__name__)  # Initialize logger


class AIChatService:
    def __init__(self):
        try:
            logger.info("Initializing AIChatService...")

            # Initialize Pinecone
            self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            logger.info("Pinecone initialized successfully.")

            # Load embedding model
            embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
            logger.info(f"Embedding model '{embedding_model_name}' loaded successfully.")

            # Initialize vector store
            index_name = "gymrecommendation-huggingface"
            self.vector_store = PineconeVectorStore.from_existing_index(
                embedding=self.embeddings, index_name=index_name
            )
            logger.info(f"Vector store '{index_name}' initialized successfully.")

            # Configure language model
            self.llm = ChatGroq(
                model="llama-3.1-70b-versatile",
                temperature=0.7,
                max_tokens=1000,
                timeout=10,
                max_retries=2,
            )
            logger.info("Language model configured successfully.")

            # Create question-answering chain
            self.chain = load_qa_chain(llm=self.llm, chain_type='stuff')
            logger.info("Retrieval QA chain created successfully.")

            # Define response schemas for structured output
            self.response_schemas = [
                ResponseSchema(name="Workout Name", description="Name of the workout"),
                ResponseSchema(name="Duration", description="Duration of the workout in minutes"),
                ResponseSchema(name="Difficulty", description="Difficulty level of the workout"),
                ResponseSchema(
                    name="Exercises",
                    description="List of exercises included in the workout. Each exercise includes its name and specific instructions.",
                    schema={
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Name": {"type": "string", "description": "Name of the exercise"},
                                "Instructions": {"type": "string",
                                                 "description": "Step-by-step instructions for performing the exercise"}
                            },
                            "required": ["Name", "Instructions"]
                        }
                    }
                ),
                ResponseSchema(name="Estimated Calories Burned",
                               description="Estimated calories burned during the workout"),
                ResponseSchema(name="Equipment Needed", description="List of equipment needed for the workout"),
                ResponseSchema(name="Additional Tips", description="Any additional tips for the user"),
                ResponseSchema(name="Total Calories Burned",
                               description="Total calories burned for the entire workout plan")
            ]
            self.parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
            self.format_instructions = self.parser.get_format_instructions()
            logger.info("StructuredOutputParser initialized successfully.")

            # Initialize DAOs
            self.user_dao = UserDAO()
            self.fitness_goal_dao = FitnessGoalDAO()

        except Exception as e:
            logger.error(f"Error initializing AIChatService: {str(e)}")
            raise

    def retrieve_query(self, query, k=2):
        """Retrieve similar documents from the vector store."""
        try:
            logger.info(f"Retrieving query '{query}' with top {k} results...")
            results = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Query retrieved successfully. {len(results)} documents found.")
            return results
        except Exception as e:
            logger.error(f"Error retrieving query: {str(e)}")
            raise

    def generate_prompt(self, input_data):
        """Generate a prompt for the model."""
        try:
            logger.info("Generating prompt for input data...")
            user_info = [
                f"- Sex: {input_data.get('Sex', 'Not Specified')}",
                f"- Age: {input_data.get('Age', 'Not Specified')}",
                f"- Height: {input_data.get('Height', 'Not Specified')}",
                f"- Weight: {input_data.get('Weight', 'Not Specified')}",
                f"- Hypertension: {input_data.get('Hypertension', False)}",
                f"- Diabetes: {input_data.get('Diabetes', False)}",
                f"- BMI: {input_data.get('BMI', 'Not Specified')}",
                f"- Level: {input_data.get('Level', 'Beginner')}",
                f"- Fitness Goal: {input_data.get('Fitness Goal', 'General Fitness')}",
                f"- Fitness Type: {input_data.get('Fitness Type', 'Any')}",
            ]
            user_info_str = "\n".join(user_info)
            prompt = (
                f"Based on the following user information:\n{user_info_str}\n\n"
                f"Provide a personalized workout recommendation strictly in JSON format. "
                f"Ensure the JSON follows this structure:\n\n"
                f"{self.format_instructions}"
            )
            logger.info("Prompt generated successfully.")
            return prompt
        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}")
            raise

    def retrieve_answer(self, user_id, query):
        """Generate an answer based on user input."""
        try:
            logger.info(f"Retrieving answer for user_id {user_id} and query '{query}'...")

            # Retrieve user and fitness goal information
            user_info = self.user_dao.get_user_by_id(user_id)
            goal_info = self.fitness_goal_dao.get_goal_by_user_id(user_id)
            logger.debug(f"user_info -> {user_info}")
            logger.debug(f"goal_info -> {goal_info}")

            if not user_info:
                raise ValueError(f"User with ID {user_id} not found.")

            # Prepare input data
            input_data = {
                "query": query,
                "Sex": user_info.get("gender"),
                "Age": user_info.get("age"),
                "Height": user_info.get("height_cm"),
                "Weight": user_info.get("weight_kg"),
                "DaysPerWeek": user_info.get("days_per_week", "Beginner"),
                "Fitness_Goal": goal_info.get("goal", "General Fitness"),
                "WorkoutDuration": user_info.get("workout_duration", "Any"),
                "RestDay": user_info.get("rest_days", "Any"),
            }

            # Retrieve matching documents
            matching_docs = self.retrieve_query(query)

            # Generate prompt
            question = self.generate_prompt(input_data)

            # Get results from QA chain
            response = self.chain.invoke({
                "input_documents": matching_docs,
                "question": question,
            })

            # Parse response
            parsed_output = self.parser.parse(response["output_text"])
            logger.info("Answer retrieved and parsed successfully.")
            return parsed_output

        except ValueError as ve:
            logger.warning(f"Validation error: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving answer for user_id {user_id}: {str(e)}")
            raise


if __name__ == "__main__":
    import json

    # Initialize the service
    service = AIChatService()
    logger.info("AIChatService initialized for testing.")

    # Define a test user ID and query
    test_user_id = '6741f0e75b6291baa9b7a273'  # Replace with a valid test user ID
    test_query = "What is the best exercise for weight loss?"

    try:
        # Test retrieve_answer method
        logger.info(f"Testing retrieve_answer for user_id {test_user_id} with query '{test_query}'...")
        response = service.retrieve_answer(user_id=test_user_id, query=test_query)

        # Print test output
        print("\nTest User ID:", test_user_id)
        print("\nTest Query:", test_query)
        print("\nTest Output:")
        print(json.dumps(response, indent=4))
        logger.info("Test completed successfully.")

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")

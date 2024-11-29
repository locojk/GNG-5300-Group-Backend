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
from utils.env_loader import load_platform_specific_env
from utils.logger import Logger
from daos.user.users_dao import UserDAO

logger = Logger(__name__)  # 初始化日志记录器


class AIChatService:
    def __init__(self):
        try:
            logger.info("Initializing AIChatService...")

            # 加载环境变量
            load_platform_specific_env()
            logger.info("Environment variables loaded successfully.")

            # 初始化 Pinecone
            self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            logger.info("Pinecone initialized successfully.")

            # 加载嵌入模型
            embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
            logger.info(f"Embedding model '{embedding_model_name}' loaded successfully.")

            # 初始化向量存储
            index_name = "gymrecommendation-huggingface"
            self.vector_store = PineconeVectorStore.from_existing_index(
                embedding=self.embeddings, index_name=index_name
            )
            logger.info(f"Vector store '{index_name}' initialized successfully.")

            # 配置语言模型
            self.llm = ChatGroq(
                model="llama-3.1-70b-versatile",
                temperature=0.7,
                max_tokens=1000,
                timeout=10,
                max_retries=2,
            )
            logger.info("Language model configured successfully.")

            # 创建检索问答链
            self.chain = load_qa_chain(llm=self.llm, chain_type='stuff')
            logger.info("Retrieval QA chain created successfully.")

            # 初始化响应结构
            self.response_schemas = [
                ResponseSchema(name="Workout Name", description="Name of the workout"),
                ResponseSchema(name="Duration", description="Duration of the workout in minutes"),
                ResponseSchema(name="Difficulty", description="Difficulty level of the workout"),
                ResponseSchema(name="Exercises", description="List of exercises included in the workout"),
                ResponseSchema(name="Estimated Calories Burned",
                               description="Estimated calories burned during the workout"),
                ResponseSchema(name="Equipment Needed", description="List of equipment needed for the workout"),
                ResponseSchema(name="Additional Tips", description="Any additional tips for the user")
            ]
            self.parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
            self.format_instructions = self.parser.get_format_instructions()
            logger.info("StructuredOutputParser initialized successfully.")

            # 初始化 UserDAO
            self.user_dao = UserDAO()

        except Exception as e:
            logger.error(f"Error initializing AIChatService: {str(e)}")
            raise

    def retrieve_query(self, query, k=2):
        """从向量存储中检索相似的文档"""
        try:
            logger.info(f"Retrieving query '{query}' with top {k} results...")
            results = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Query retrieved successfully. {len(results)} documents found.")
            return results
        except Exception as e:
            logger.error(f"Error retrieving query: {str(e)}")
            raise

    def generate_prompt(self, input_data):
        """生成模型所需的提示"""
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
                f"Make sure the JSON follows this structure:\n\n"
                f"{self.format_instructions}"
            )
            logger.info("Prompt generated successfully.")
            return prompt
        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}")
            raise

    def retrieve_answer(self, user_id, query):
        """根据用户输入生成回答"""
        try:
            logger.info(f"Retrieving answer for user_id {user_id} and query '{query}'...")

            # 从用户信息表查询用户详情
            user_info = self.user_dao.get_user_info(user_id)
            if not user_info:
                raise ValueError(f"User with ID {user_id} not found.")

            # 整合用户信息和查询内容
            input_data = {
                "query": query,
                "Sex": user_info.get("sex"),
                "Age": user_info.get("age"),
                "Height": user_info.get("height"),
                "Weight": user_info.get("weight"),
                "Hypertension": user_info.get("hypertension"),
                "Diabetes": user_info.get("diabetes"),
                "BMI": user_info.get("bmi"),
                "Level": user_info.get("fitness_level", "Beginner"),
                "Fitness_Goal": user_info.get("fitness_goal", "General Fitness"),
                "Fitness_Type": user_info.get("fitness_type", "Any"),
            }

            # 检索匹配文档
            matching_docs = self.retrieve_query(query)

            # 生成提示
            question = self.generate_prompt(input_data)

            # 调用问答链生成结果
            response = self.chain.invoke({
                "input_documents": matching_docs,
                "question": question,
            })

            # 解析响应
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

    # 初始化服务
    service = AIChatService()
    logger.info("AIChatService initialized for testing.")

    # 定义测试用户 ID 和查询
    test_user_id = 123  # 替换为测试用户的 ID
    test_query = "What is the best exercise for weight loss?"

    try:
        # 调用服务生成回答
        logger.info(f"Testing retrieve_answer for user_id {test_user_id} with query '{test_query}'...")
        response = service.retrieve_answer(user_id=test_user_id, query=test_query)

        # 打印测试输出
        print("\nTest User ID:", test_user_id)
        print("\nTest Query:", test_query)
        print("\nTest Output:")
        print(json.dumps(response, indent=4))
        logger.info("Test completed successfully.")

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")

# if __name__ == "__main__":
#     import json
#
#     # 初始化服务
#     service = AIChatService()
#     logger.info("AIChatService initialized for testing.")
#
#     # 定义测试输入
#     test_input = {
#         "query": "What is the best exercise for weight loss?",
#         "Sex": "Female",
#         "Age": 30,
#         "Height": 165,
#         "Weight": 70,
#         "Hypertension": False,
#         "Diabetes": False,
#         "BMI": 25.7,
#         "Level": "Intermediate",
#         "Fitness Goal": "Weight Loss",
#         "Fitness Type": "Cardio"
#     }
#
#     try:
#         # 调用服务生成回答
#         logger.info("Testing retrieve_answer with sample input...")
#         response = service.retrieve_answer(test_input)
#
#         # 打印测试输出
#         print("\nTest Input:")
#         print(json.dumps(test_input, indent=4))
#         print("\nTest Output:")
#         print(json.dumps(response, indent=4))
#         logger.info("Test completed successfully.")
#
#     except Exception as e:
#         logger.error(f"Test failed with error: {str(e)}")

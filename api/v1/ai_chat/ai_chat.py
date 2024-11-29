"""
@Time ： 2024-11-23
@Auth ： Adam Lyu
"""
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Request
from utils.logger import Logger
from utils.decorators import handle_response
from services.ai_chat.ai_chat_service import AIChatService
from services.user.auth_service import AuthService

logger = Logger(__name__)
router = APIRouter()
service = AIChatService()
auth_service = AuthService()


# 请求体定义

class ChatQueryRequest(BaseModel):
    query: str = Field(..., description="用户的查询内容")


# 路由实现

@router.post("/ai_chat/query")
@handle_response
@auth_service.requires_auth
async def query_ai_chat(request: Request, body: ChatQueryRequest):
    """
    基于用户输入的查询内容，结合用户信息生成个性化的回复
    """
    user_id = request.state.user_id  # 从 request.state 获取经过认证的用户 ID
    logger.info(f"API: Generating AI chat response for user_id {user_id}")

    try:
        # 调用服务获取回答
        response = service.retrieve_answer(user_id=user_id, query=body.query)

        # 返回响应
        return {"status": "success", "data": response}
    except HTTPException as e:
        logger.warning(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error generating AI chat response for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/ai_chat/test")
@auth_service.requires_auth
async def test_ai_chat(request: Request):
    """
    测试接口，检查服务是否正常工作
    """
    user_id = request.state.user_id  # 从 request.state 获取经过认证的用户 ID
    logger.info(f"API: Testing AIChatService for user_id {user_id}")

    try:
        # 示例测试查询
        test_query = "What is the best exercise for weight loss?"

        # 调用服务获取测试回答
        response = service.retrieve_answer(user_id=user_id, query=test_query)
        logger.info("AIChatService test completed successfully.")

        # 返回测试结果
        return {"status": "success", "message": "Test passed", "data": response}
    except Exception as e:
        logger.error(f"Error during AIChatService test for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

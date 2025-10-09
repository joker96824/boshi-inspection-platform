"""
认证API接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.deps import get_db
from ...core.auth import get_current_user
from ...services.auth_service import AuthService
from ...schemas.user import UserLogin
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/login", response_model=dict)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    auth_service = AuthService(db)
    return await auth_service.login(
        username=user_credentials.username,
        password=user_credentials.password
    )


@router.post("/logout", response_model=dict)
async def logout(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """用户登出"""
    auth_service = AuthService(db)
    return await auth_service.logout(current_user["id"])


@router.post("/refresh", response_model=dict)
async def refresh_token(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """刷新令牌"""
    auth_service = AuthService(db)
    return await auth_service.refresh_token(current_user)


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """获取当前用户信息"""
    return ApiResponse.success(
        data={"user": current_user},
        message="获取用户信息成功"
    )
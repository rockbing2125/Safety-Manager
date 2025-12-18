"""
用户认证服务
"""
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
import jwt
from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.models import User, SessionLocal
from shared.config import settings
from shared.constants import UserRole


class AuthService:
    """用户认证服务"""

    def __init__(self):
        self.current_user: Optional[User] = None
        self.session_token: Optional[str] = None

    def login(self, username: str, password: str) -> tuple[bool, str, Optional[User]]:
        """用户登录"""
        try:
            db = SessionLocal()
            user = db.query(User).filter(User.username == username).first()

            if not user:
                logger.warning(f"登录失败: 用户 '{username}' 不存在")
                return False, "用户名或密码错误", None

            if not user.verify_password(password):
                logger.warning(f"登录失败: 密码错误")
                return False, "用户名或密码错误", None

            self.session_token = self._generate_token(user)
            self.current_user = user

            logger.info(f"用户 '{username}' 登录成功")
            db.close()
            return True, "登录成功", user

        except Exception as e:
            logger.error(f"登录失败: {e}")
            return False, f"登录失败: {str(e)}", None

    def logout(self):
        """用户登出"""
        if self.current_user:
            logger.info(f"用户 '{self.current_user.username}' 登出")
        self.current_user = None
        self.session_token = None

    def register(self, username: str, password: str, email: str, 
                role: UserRole = UserRole.VIEWER) -> tuple[bool, str, Optional[User]]:
        """用户注册"""
        try:
            db = SessionLocal()

            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                return False, "用户名已存在", None

            user = User(username=username, email=email, role=role)
            user.set_password(password)

            db.add(user)
            db.commit()
            db.refresh(user)

            logger.success(f"用户 '{username}' 注册成功")
            db.close()
            return True, "注册成功", user

        except Exception as e:
            logger.error(f"注册失败: {e}")
            return False, f"注册失败: {str(e)}", None

    def change_password(self, username_or_id, old_password: str,
                       new_password: str) -> tuple[bool, str]:
        """修改密码

        Args:
            username_or_id: 用户名或用户ID
            old_password: 旧密码
            new_password: 新密码
        """
        try:
            db = SessionLocal()

            # 根据参数类型查询用户
            if isinstance(username_or_id, int):
                user = db.query(User).filter(User.id == username_or_id).first()
            else:
                user = db.query(User).filter(User.username == username_or_id).first()

            if not user:
                return False, "用户不存在"

            if not user.verify_password(old_password):
                return False, "旧密码错误"

            user.set_password(new_password)
            db.commit()

            logger.info(f"用户 '{user.username}' 修改密码成功")
            db.close()
            return True, "密码修改成功"

        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            return False, f"修改密码失败: {str(e)}"

    def check_permission(self, permission: str) -> bool:
        """检查当前用户权限"""
        if not self.current_user:
            return False
        return self.current_user.has_permission(permission)

    def _generate_token(self, user: User) -> str:
        """生成JWT令牌"""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token

    def get_all_users(self) -> list[User]:
        """获取所有用户"""
        if not self.check_permission("manage_users"):
            return []

        try:
            db = SessionLocal()
            users = db.query(User).all()
            db.close()
            return users
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return []

    def update_user_role(self, user_id: int, new_role: UserRole) -> tuple[bool, str]:
        """更新用户角色"""
        if not self.check_permission("manage_users"):
            return False, "无权限修改用户角色"

        try:
            db = SessionLocal()
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return False, "用户不存在"

            user.role = new_role
            db.commit()

            logger.info(f"用户 '{user.username}' 角色已更新")
            db.close()
            return True, "角色更新成功"

        except Exception as e:
            return False, f"更新失败: {str(e)}"

    def delete_user(self, user_id: int) -> tuple[bool, str]:
        """删除用户"""
        if not self.check_permission("manage_users"):
            return False, "无权限删除用户"

        try:
            db = SessionLocal()
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return False, "用户不存在"

            if self.current_user and user.id == self.current_user.id:
                return False, "不能删除当前登录的用户"

            username = user.username
            db.delete(user)
            db.commit()

            logger.info(f"用户 '{username}' 已删除")
            db.close()
            return True, "用户删除成功"

        except Exception as e:
            return False, f"删除失败: {str(e)}"
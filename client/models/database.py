"""
数据库配置和初始化
"""
import sys
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from shared.config import settings


# 创建基类
Base = declarative_base()


# 根据配置选择数据库
def get_database_url() -> str:
    """获取数据库连接 URL"""
    if settings.OFFLINE_MODE:
        logger.info("使用 SQLite 数据库 (离线模式)")
        return settings.sqlite_url
    else:
        try:
            logger.info("尝试连接 PostgreSQL 数据库")
            return settings.postgres_url
        except Exception as e:
            logger.warning(f"PostgreSQL 连接失败,切换到 SQLite: {e}")
            return settings.sqlite_url


# 创建数据库引擎
database_url = get_database_url()
engine = create_engine(
    database_url,
    echo=False,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
)


# 为 SQLite 启用外键约束
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """设置 SQLite 参数"""
    if "sqlite" in database_url:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    try:
        # 导入所有模型
        from . import user, regulation, history

        logger.info("开始初始化数据库...")
        Base.metadata.create_all(bind=engine)
        logger.success("数据库初始化完成!")

        # 创建默认管理员账户
        from .user import User
        from shared.constants import UserRole

        db = SessionLocal()
        try:
            admin = db.query(User).filter(User.username == "admin").first()
            if not admin:
                admin = User(
                    username="admin",
                    email="admin@example.com",
                    role=UserRole.ADMIN
                )
                admin.set_password("admin123")
                db.add(admin)
                db.commit()
                logger.success("默认管理员账户创建成功 (admin/admin123)")
            else:
                logger.info("管理员账户已存在")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="数据库管理工具")
    parser.add_argument("--init", action="store_true", help="初始化数据库")
    args = parser.parse_args()

    if args.init:
        init_db()
    else:
        parser.print_help()
"""
搜索服务
"""
import sys
from pathlib import Path
from typing import List, Optional
from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.models import Regulation, SessionLocal


class SearchService:
    """搜索服务"""

    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

    def search(self, keyword: str, country: Optional[str] = None,
              category: Optional[str] = None) -> List[Regulation]:
        """搜索法规"""
        try:
            query = self.db.query(Regulation)

            if keyword:
                query = query.filter(
                    (Regulation.name.contains(keyword)) |
                    (Regulation.code.contains(keyword)) |
                    (Regulation.description.contains(keyword))
                )

            if country:
                query = query.filter(Regulation.country == country)

            if category:
                query = query.filter(Regulation.category == category)

            results = query.order_by(Regulation.created_at.desc()).all()
            logger.info(f"搜索 '{keyword}' 返回 {len(results)} 条结果")
            return results

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
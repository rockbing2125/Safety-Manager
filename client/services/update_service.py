"""
版本更新服务
"""
import sys
from pathlib import Path
import requests
from typing import Optional, Tuple, List
from packaging import version
from loguru import logger
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from shared.config import settings
from client.models import SessionLocal, UpdateNotification, NotificationType


class UpdateService:
    """版本更新服务"""

    def __init__(self):
        self.current_version = settings.APP_VERSION
        self.update_url = settings.UPDATE_CHECK_URL

    def check_for_updates(self) -> Tuple[bool, Optional[dict]]:
        """
        检查版本更新

        支持两种方式：
        1. 静态JSON文件：直接读取 version.json 文件内容
        2. API接口：调用后端API获取版本信息
        """
        try:
            logger.info(f"检查版本更新: {self.update_url}")

            # 使用英文User-Agent，避免编码问题
            response = requests.get(
                self.update_url,
                timeout=10,
                headers={'User-Agent': f'SafetyManager/{self.current_version}'}
            )

            if response.status_code != 200:
                logger.warning(f"检查更新失败: HTTP {response.status_code}")
                return False, None

            # 确保响应是UTF-8编码
            response.encoding = 'utf-8'

            # 解析JSON响应
            update_info = response.json()
            latest_version = update_info.get('version')

            if not latest_version:
                logger.warning("版本信息中未找到version字段")
                return False, None

            # 比较版本号
            if version.parse(latest_version) > version.parse(self.current_version):
                logger.info(f"发现新版本: {latest_version} (当前版本: {self.current_version})")
                return True, update_info
            else:
                logger.info(f"当前已是最新版本: {self.current_version}")
                return False, None

        except requests.exceptions.Timeout:
            logger.warning("检查更新超时，请检查网络连接")
            return False, None
        except requests.exceptions.ConnectionError:
            logger.warning("无法连接到更新服务器，请检查网络连接")
            return False, None
        except Exception as e:
            logger.error(f"检查更新失败: {e}")
            return False, None

    def get_update_info(self, update_data: dict) -> str:
        """格式化更新信息"""
        info = f"发现新版本: {update_data.get('version')}\n\n"

        if update_data.get('release_date'):
            info += f"发布日期: {update_data.get('release_date')}\n\n"

        if update_data.get('changelog'):
            info += "更新内容:\n"
            for change in update_data.get('changelog', []):
                info += f"• {change}\n"

        return info

    def download_update(self, download_url: str, save_path: str,
                       progress_callback=None) -> Tuple[bool, str]:
        """下载更新文件"""
        try:
            logger.info(f"开始下载更新: {download_url}")

            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded, total_size)

            logger.info(f"更新下载完成: {save_path}")
            return True, "下载成功"

        except Exception as e:
            logger.error(f"下载更新失败: {e}")
            return False, f"下载失败: {str(e)}"

    # ========== 更新通知管理 ==========

    def create_notification(self, notification_type: str, title: str,
                          message: str = None, version: str = None,
                          regulation_id: int = None) -> Tuple[bool, str]:
        """创建更新通知"""
        try:
            db = SessionLocal()
            try:
                notification = UpdateNotification(
                    type=notification_type,
                    title=title,
                    message=message,
                    version=version,
                    regulation_id=regulation_id,
                    is_read=False,
                    created_at=datetime.utcnow()
                )
                db.add(notification)
                db.commit()
                logger.info(f"创建更新通知成功: {title}")
                return True, "通知创建成功"
            finally:
                db.close()
        except Exception as e:
            logger.error(f"创建更新通知失败: {e}")
            return False, f"创建通知失败: {str(e)}"

    def get_unread_count(self) -> int:
        """获取未读通知数量"""
        try:
            db = SessionLocal()
            try:
                count = db.query(UpdateNotification).filter(
                    UpdateNotification.is_read == False
                ).count()
                return count
            finally:
                db.close()
        except Exception as e:
            logger.error(f"获取未读通知数量失败: {e}")
            return 0

    def get_all_notifications(self, limit: int = 50) -> List[UpdateNotification]:
        """获取所有通知"""
        try:
            db = SessionLocal()
            try:
                notifications = db.query(UpdateNotification).order_by(
                    UpdateNotification.created_at.desc()
                ).limit(limit).all()
                return notifications
            finally:
                db.close()
        except Exception as e:
            logger.error(f"获取通知列表失败: {e}")
            return []

    def mark_as_read(self, notification_id: int) -> Tuple[bool, str]:
        """标记通知为已读"""
        try:
            db = SessionLocal()
            try:
                notification = db.query(UpdateNotification).filter(
                    UpdateNotification.id == notification_id
                ).first()

                if not notification:
                    return False, "通知不存在"

                notification.is_read = True
                db.commit()
                logger.info(f"通知已标记为已读: {notification_id}")
                return True, "标记成功"
            finally:
                db.close()
        except Exception as e:
            logger.error(f"标记通知已读失败: {e}")
            return False, f"标记失败: {str(e)}"

    def mark_all_as_read(self) -> Tuple[bool, str]:
        """标记所有通知为已读"""
        try:
            db = SessionLocal()
            try:
                db.query(UpdateNotification).filter(
                    UpdateNotification.is_read == False
                ).update({"is_read": True})
                db.commit()
                logger.info("所有通知已标记为已读")
                return True, "标记成功"
            finally:
                db.close()
        except Exception as e:
            logger.error(f"标记所有通知已读失败: {e}")
            return False, f"标记失败: {str(e)}"

    def clear_all_notifications(self) -> Tuple[bool, str]:
        """清空所有通知"""
        try:
            db = SessionLocal()
            try:
                db.query(UpdateNotification).delete()
                db.commit()
                logger.info("所有通知已清空")
                return True, "清空成功"
            finally:
                db.close()
        except Exception as e:
            logger.error(f"清空通知失败: {e}")
            return False, f"清空失败: {str(e)}"
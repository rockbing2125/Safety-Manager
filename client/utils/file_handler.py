"""
文件处理工具类
"""
import sys
from pathlib import Path
import shutil
from typing import Tuple
from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


class FileHandler:
    """文件处理工具类"""

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        try:
            return Path(file_path).stat().st_size
        except Exception as e:
            logger.error(f"获取文件大小失败: {e}")
            return 0

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    @staticmethod
    def validate_file_extension(file_path: str, allowed_extensions: set) -> bool:
        """验证文件扩展名"""
        ext = Path(file_path).suffix.lower()
        return ext in allowed_extensions

    @staticmethod
    def validate_file_size(file_path: str, max_size: int) -> Tuple[bool, str]:
        """验证文件大小"""
        size = FileHandler.get_file_size(file_path)
        if size == 0:
            return False, "文件不存在或为空"

        if size > max_size:
            max_size_str = FileHandler.format_file_size(max_size)
            actual_size_str = FileHandler.format_file_size(size)
            return False, f"文件过大 ({actual_size_str})，最大允许 {max_size_str}"

        return True, ""

    @staticmethod
    def copy_file(source: str, destination: str) -> Tuple[bool, str]:
        """复制文件"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)

            if not source_path.exists():
                return False, "源文件不存在"

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)

            logger.info(f"文件复制成功: {source} -> {destination}")
            return True, "文件复制成功"

        except Exception as e:
            logger.error(f"文件复制失败: {e}")
            return False, f"文件复制失败: {str(e)}"

    @staticmethod
    def read_text_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """读取文本文件"""
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            return None
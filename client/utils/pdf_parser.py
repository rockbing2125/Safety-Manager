"""
PDF文档解析器
"""
import sys
from pathlib import Path
from typing import Optional
from loguru import logger

try:
    import PyPDF2
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logger.warning("PyPDF2或pdfplumber未安装，PDF解析功能不可用")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


class PDFParser:
    """PDF文档解析器"""

    @staticmethod
    def is_available() -> bool:
        """检查PDF解析功能是否可用"""
        return PDF_SUPPORT

    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        """获取PDF页数"""
        if not PDF_SUPPORT:
            return 0

        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return len(reader.pages)
        except Exception as e:
            logger.error(f"获取PDF页数失败: {e}")
            return 0

    @staticmethod
    def extract_text(pdf_path: str, page_num: Optional[int] = None) -> str:
        """提取PDF文本"""
        if not PDF_SUPPORT:
            return ""

        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)

                if page_num is not None:
                    if 0 <= page_num < len(reader.pages):
                        page = reader.pages[page_num]
                        return page.extract_text()
                    else:
                        return ""
                else:
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text

        except Exception as e:
            logger.error(f"提取PDF文本失败: {e}")
            return ""

    @staticmethod
    def extract_text_with_pdfplumber(pdf_path: str) -> str:
        """使用pdfplumber提取文本（更准确）"""
        if not PDF_SUPPORT:
            return ""

        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text

        except Exception as e:
            logger.error(f"提取PDF文本失败: {e}")
            return ""

    @staticmethod
    def get_metadata(pdf_path: str) -> dict:
        """获取PDF元数据"""
        if not PDF_SUPPORT:
            return {}

        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                metadata = reader.metadata

                if metadata:
                    return {
                        "title": metadata.get("/Title", ""),
                        "author": metadata.get("/Author", ""),
                        "subject": metadata.get("/Subject", ""),
                        "creator": metadata.get("/Creator", ""),
                    }
                return {}

        except Exception as e:
            logger.error(f"获取PDF元数据失败: {e}")
            return {}
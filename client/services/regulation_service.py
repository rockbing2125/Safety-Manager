"""
法规管理服务
"""
import sys
from pathlib import Path
from typing import Optional, List
import shutil
from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.models import Regulation, RegulationDocument, CodeFile, Tag, SessionLocal, ChangeHistory
from shared.config import settings, DOCUMENTS_DIR, CODES_DIR
from shared.constants import RegulationStatus, DocumentType, EntityType, ChangeType


class RegulationService:
    """法规管理服务"""

    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

    def create_regulation(self, code: str, name: str, country: Optional[str] = None,
                         category: Optional[str] = None, description: Optional[str] = None,
                         status: RegulationStatus = RegulationStatus.DRAFT,
                         version: Optional[str] = None, created_by: Optional[int] = None,
                         tags: Optional[List[str]] = None) -> tuple[bool, str, Optional[Regulation]]:
        """创建法规"""
        try:
            existing = self.db.query(Regulation).filter(Regulation.code == code).first()
            if existing:
                return False, f"法规编号 '{code}' 已存在", None

            regulation = Regulation(
                code=code, name=name, country=country, category=category,
                description=description, status=status, version=version, created_by=created_by
            )

            self.db.add(regulation)
            self.db.flush()

            if tags:
                self._add_tags_to_regulation(regulation, tags)

            self.db.commit()
            self.db.refresh(regulation)

            if created_by:
                ChangeHistory.create_change_record(
                    self.db, EntityType.REGULATION, regulation.id,
                    ChangeType.CREATE, regulation.to_dict(), f"创建法规: {name}", created_by
                )

            logger.success(f"法规 '{name}' 创建成功")
            return True, "法规创建成功", regulation

        except Exception as e:
            self.db.rollback()
            logger.error(f"创建法规失败: {e}")
            return False, f"创建失败: {str(e)}", None

    def update_regulation(self, regulation_id: int, **kwargs) -> tuple[bool, str, Optional[Regulation]]:
        """更新法规"""
        try:
            regulation = self.db.query(Regulation).filter(Regulation.id == regulation_id).first()
            if not regulation:
                return False, "法规不存在", None

            old_data = regulation.to_dict()

            for key, value in kwargs.items():
                if hasattr(regulation, key) and key != 'id':
                    setattr(regulation, key, value)

            if 'tags' in kwargs:
                self._update_regulation_tags(regulation, kwargs['tags'])

            self.db.commit()
            self.db.refresh(regulation)

            if 'updated_by' in kwargs:
                ChangeHistory.create_change_record(
                    self.db, EntityType.REGULATION, regulation.id,
                    ChangeType.UPDATE, {"old": old_data, "new": regulation.to_dict()},
                    f"更新法规: {regulation.name}", kwargs['updated_by']
                )

            return True, "法规更新成功", regulation

        except Exception as e:
            self.db.rollback()
            return False, f"更新失败: {str(e)}", None

    def delete_regulation(self, regulation_id: int, deleted_by: Optional[int] = None) -> tuple[bool, str]:
        """删除法规"""
        try:
            regulation = self.db.query(Regulation).filter(Regulation.id == regulation_id).first()
            if not regulation:
                return False, "法规不存在"

            if deleted_by:
                ChangeHistory.create_change_record(
                    self.db, EntityType.REGULATION, regulation.id,
                    ChangeType.DELETE, regulation.to_dict(),
                    f"删除法规: {regulation.name}", deleted_by
                )

            self._delete_regulation_files(regulation)

            regulation_name = regulation.name
            self.db.delete(regulation)
            self.db.commit()

            logger.info(f"法规 '{regulation_name}' 已删除")
            return True, "法规删除成功"

        except Exception as e:
            self.db.rollback()
            return False, f"删除失败: {str(e)}"

    def get_regulation(self, regulation_id: int) -> Optional[Regulation]:
        """获取法规"""
        return self.db.query(Regulation).filter(Regulation.id == regulation_id).first()

    def get_regulation_by_code(self, code: str) -> Optional[Regulation]:
        """通过编号获取法规"""
        return self.db.query(Regulation).filter(Regulation.code == code).first()

    def list_regulations(self, country: Optional[str] = None, category: Optional[str] = None,
                        status: Optional[RegulationStatus] = None,
                        tags: Optional[List[str]] = None,
                        keyword: Optional[str] = None) -> List[Regulation]:
        """列出法规"""
        query = self.db.query(Regulation)

        if country:
            query = query.filter(Regulation.country == country)
        if category:
            query = query.filter(Regulation.category == category)
        if status:
            query = query.filter(Regulation.status == status)
        if keyword:
            query = query.filter(
                (Regulation.name.contains(keyword)) |
                (Regulation.code.contains(keyword)) |
                (Regulation.description.contains(keyword))
            )
        if tags:
            query = query.join(Regulation.tags).filter(Tag.name.in_(tags))

        return query.order_by(Regulation.created_at.desc()).all()

    def add_document(self, regulation_id: int, file_path: str, doc_type: DocumentType,
                    upload_by: Optional[int] = None) -> tuple[bool, str, Optional[RegulationDocument]]:
        """添加法规文档"""
        try:
            regulation = self.get_regulation(regulation_id)
            if not regulation:
                return False, "法规不存在", None

            source_file = Path(file_path)
            if not source_file.exists():
                return False, "文件不存在", None

            target_dir = DOCUMENTS_DIR / str(regulation_id)
            target_dir.mkdir(parents=True, exist_ok=True)

            target_file = target_dir / source_file.name
            shutil.copy2(source_file, target_file)

            document = RegulationDocument(
                regulation_id=regulation_id,
                doc_type=doc_type,
                file_name=source_file.name,
                file_path=str(target_file),
                file_size=source_file.stat().st_size,
                upload_by=upload_by
            )

            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)

            # 记录历史
            if upload_by:
                ChangeHistory.create_change_record(
                    self.db, EntityType.REGULATION, regulation_id,
                    ChangeType.UPDATE, {"document_id": document.id, "file_name": source_file.name},
                    f"上传文档: {source_file.name}", upload_by
                )

            logger.success(f"文档 '{source_file.name}' 添加成功")
            return True, "文档添加成功", document

        except Exception as e:
            self.db.rollback()
            return False, f"添加失败: {str(e)}", None

    def add_code_file(self, regulation_id: int, file_path: str,
                     description: Optional[str] = None, usage_guide: Optional[str] = None,
                     version: Optional[str] = None,
                     created_by: Optional[int] = None) -> tuple[bool, str, Optional[CodeFile]]:
        """添加代码文件"""
        try:
            regulation = self.get_regulation(regulation_id)
            if not regulation:
                return False, "法规不存在", None

            source_file = Path(file_path)
            if not source_file.exists():
                return False, "文件不存在", None

            target_dir = CODES_DIR / str(regulation_id)
            target_dir.mkdir(parents=True, exist_ok=True)

            target_file = target_dir / source_file.name
            shutil.copy2(source_file, target_file)

            code_file = CodeFile(
                regulation_id=regulation_id,
                file_name=source_file.name,
                file_path=str(target_file),
                description=description,
                usage_guide=usage_guide,
                version=version,
                created_by=created_by
            )

            self.db.add(code_file)
            self.db.commit()
            self.db.refresh(code_file)

            # 记录历史
            if created_by:
                ChangeHistory.create_change_record(
                    self.db, EntityType.REGULATION, regulation_id,
                    ChangeType.UPDATE, {"code_file_id": code_file.id, "file_name": source_file.name},
                    f"上传代码文件: {source_file.name}", created_by
                )

            logger.success(f"代码文件 '{source_file.name}' 添加成功")
            return True, "代码文件添加成功", code_file

        except Exception as e:
            self.db.rollback()
            return False, f"添加失败: {str(e)}", None

    def _add_tags_to_regulation(self, regulation: Regulation, tag_names: List[str]):
        """为法规添加标签"""
        for tag_name in tag_names:
            tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                self.db.add(tag)
                self.db.flush()
            regulation.tags.append(tag)

    def _update_regulation_tags(self, regulation: Regulation, tag_names: List[str]):
        """更新法规标签"""
        regulation.tags.clear()
        self._add_tags_to_regulation(regulation, tag_names)

    def _delete_regulation_files(self, regulation: Regulation):
        """删除法规关联文件"""
        doc_dir = DOCUMENTS_DIR / str(regulation.id)
        if doc_dir.exists():
            shutil.rmtree(doc_dir)

        code_dir = CODES_DIR / str(regulation.id)
        if code_dir.exists():
            shutil.rmtree(code_dir)
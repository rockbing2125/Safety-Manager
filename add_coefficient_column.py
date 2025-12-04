"""
数据库迁移脚本：添加 coefficient（系数）列到 regulation_parameters 表
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shared.config import settings
from sqlalchemy import create_engine, text

def migrate():
    """执行迁移"""
    engine = create_engine(settings.sqlite_url)

    with engine.connect() as conn:
        # 检查列是否已存在
        result = conn.execute(text("PRAGMA table_info(regulation_parameters)"))
        columns = [row[1] for row in result]

        if 'coefficient' in columns:
            print("[OK] coefficient column already exists")
            return

        print("Adding coefficient column...")

        # 添加新列
        conn.execute(text(
            "ALTER TABLE regulation_parameters ADD COLUMN coefficient VARCHAR(50)"
        ))
        conn.commit()

        print("[OK] Successfully added coefficient column")

if __name__ == "__main__":
    try:
        migrate()
        print("\n[OK] Database migration completed!")
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()

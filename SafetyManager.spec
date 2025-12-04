# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

# 排除特定文件的函数
def should_include(file_path):
    """判断文件是否应该被包含在打包中"""
    exclude_files = {'.env', '.env.local', '.env.production'}
    exclude_patterns = {'__pycache__', '*.pyc', '*.pyo', '.git'}

    file_name = os.path.basename(file_path)
    if file_name in exclude_files:
        return False
    for pattern in exclude_patterns:
        if pattern.replace('*', '') in file_path:
            return False
    return True

# 创建空的数据目录结构（不包含数据库文件）
data_tree = []
for subdir in ['documents', 'codes', 'parameter_images', 'databases', 'logs']:
    data_dir = os.path.join('data', subdir)
    if os.path.exists(data_dir):
        # 对于 databases 目录，我们不包含任何文件，只创建目录结构
        if subdir == 'databases':
            continue  # 跳过，稍后单独添加数据库
        else:
            data_tree.append((data_dir, os.path.join('data', subdir)))

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 包含分发版配置文件
        ('.env.dist', '.'),
        # 不再使用 ('data', 'data')，改为单独指定每个子目录
        # 明确包含数据库文件（自带法规数据） - 这是唯一包含数据库的地方
        ('data/databases/regulations.db', 'data/databases'),
        ('client', 'client'),
        ('shared', 'shared'),
        # 包含 RDB 目录（Excel 数据源）
        ('RDB', 'RDB'),
    ] + data_tree,
    hiddenimports=[
        # PyQt6
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        # 数据库
        'sqlalchemy',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.orm',
        'sqlalchemy.sql',
        'sqlalchemy.pool',
        'sqlalchemy.dialects.sqlite',
        # 密码和认证
        'bcrypt',
        'jwt',
        'PyJWT',
        # 日志
        'loguru',
        'loguru._defaults',
        # 其他
        'requests',
        'packaging',
        'platformdirs',  # pkg_resources 依赖
        'pydantic',
        'pydantic_settings',
        'pydantic.deprecated.decorator',
        'pydantic_core',
        'pydantic_core._pydantic_core',
        # PDF 和文档处理
        'PyPDF2',
        'pdfplumber',
        'docx',
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.worksheet',
        # 代码高亮
        'pygments',
        'pygments.lexers',
        'pygments.formatters',
        'pygments.lexers.c_cpp',
        # 客户端模块
        'client',
        'client.main',
        'client.models',
        'client.models.database',
        'client.models.user',
        'client.models.regulation',
        'client.models.history',
        'client.models.parameter',
        'client.models.update_notification',
        'client.services',
        'client.services.auth_service',
        'client.services.regulation_service',
        'client.services.search_service',
        'client.services.update_service',
        'client.ui',
        'client.ui.main_window',
        'client.ui.login_dialog',
        'client.ui.regulation_dialog',
        'client.ui.regulation_detail_dialog',
        'client.ui.update_notifications_dialog',
        'client.ui.push_update_dialog',
        'client.ui.styles',
        'client.utils',
        'client.utils.file_handler',
        'client.utils.pdf_parser',
        'client.utils.docx_parser',
        'client.utils.data_exporter',
        # 共享模块
        'shared',
        'shared.config',
        'shared.constants',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SafetyManager',
    debug=True,  # 启用调试模式
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 启用控制台，显示错误信息
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SafetyManager',
)

并网法规管理系统
一个专为研发人员设计的并网法规管理桌面应用，支持法规查询、编辑、代码管理和团队协作。

功能特性
核心功能
📚 法规管理: 支持全球并网法规的增删改查
🔍 智能搜索: 全文搜索、多条件筛选、关键词高亮
📄 文档管理: 支持 PDF/Word 文档上传、预览和管理
💻 代码管理: C 代码上传、语法高亮、版本控制
📝 使用说明: 每个法规可添加详细的代码使用方法
📊 历史记录: 完整的变更历史追踪和版本对比
协作功能
👥 多用户支持: 团队协作，多人同时使用
🔐 权限管理: Admin、Editor、Viewer 三级权限
🔄 离线/在线: 支持离线使用和在线同步
🚀 版本升级: 联网时自动检测并升级版本
技术架构
技术栈
GUI: PyQt6
数据库: SQLite (本地) + PostgreSQL (服务器)
搜索: Whoosh 全文搜索引擎
文档处理: PyPDF2, python-docx
代码高亮: Pygments
版本控制: GitPython
系统架构
并网法规管理系统
├── 客户端 (Desktop App)
│   ├── PyQt6 GUI
│   ├── SQLite 本地数据库
│   └── 本地文件存储
├── 服务端 (可选)
│   ├── FastAPI REST API
│   ├── PostgreSQL 数据库
│   └── 文件服务器
└── 同步层
    ├── 版本控制
    └── 增量同步
安装说明
环境要求
Python 3.10+
Windows/macOS/Linux
安装步骤
克隆项目
git clone <repository-url>
cd grid-regulation-manager
创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
安装依赖
pip install -r requirements.txt
初始化数据库
python -m client.models.database --init
运行应用
python -m client.main
使用说明
首次登录
默认管理员账号: admin
默认密码: admin123
请在首次登录后立即修改密码
添加法规
点击「新增法规」按钮
填写法规信息（编号、名称、国家、分类等）
上传法规文档 (PDF/Word)
上传相关 C 代码
添加代码使用说明
保存
搜索法规
在搜索框输入关键词
支持法规名称、编号、内容搜索
可按国家、分类、标签筛选
查看历史
选择任意法规
点击「历史记录」查看所有变更
支持版本对比和回滚
项目结构
grid-regulation-manager/
├── client/                 # 客户端
│   ├── main.py            # 程序入口
│   ├── ui/                # UI 界面
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑
│   ├── utils/             # 工具类
│   └── resources/         # 资源文件
├── server/                # 服务端
│   ├── main.py
│   ├── api/               # API 接口
│   ├── models/            # 数据模型
│   └── database/          # 数据库
├── shared/                # 共享代码
├── tests/                 # 测试
├── docs/                  # 文档
├── data/                  # 数据目录
│   ├── documents/         # 法规文档
│   ├── codes/             # C 代码文件
│   └── databases/         # 本地数据库
└── requirements.txt       # 依赖列表
🚀 快速开始
3分钟快速体验
# 1. 安装依赖
pip install -r requirements.txt

# 2. 生成演示数据
python test_demo.py

# 3. 运行程序
python run.py

# 4. 登录系统 (admin / admin123)
详细安装文档: INSTALL.md

📖 文档
快速开始: QUICKSTART.md
安装指南: INSTALL.md
使用文档: docs/USAGE.md
🎯 功能演示
1. 法规管理
✅ 新增/编辑/删除法规
✅ 支持分类和标签
✅ 状态管理 (草稿/生效/归档)
2. 文档管理
✅ 上传 PDF/Word 文档
✅ 系统默认程序预览
✅ 文档与法规关联
3. 代码管理
✅ 上传 C 代码文件
✅ 语法高亮显示
✅ 编译和使用说明
4. 搜索功能
✅ 关键词全文搜索
✅ 多条件组合筛选
✅ 按国家/分类/标签过滤
5. 历史记录
✅ 完整变更历史
✅ 操作人追踪
✅ 时间线展示
📊 开发进度
[x] 项目架构设计
[x] 数据库模型
[x] 用户认证系统
[x] 主界面框架
[x] 法规管理功能
[x] 文档管理功能
[x] 代码管理功能
[x] 搜索筛选功能
[x] 历史记录功能
[ ] 全文搜索引擎 (Whoosh)
[ ] 服务器 API (FastAPI)
[ ] 离线/在线同步
[ ] 版本自动升级
[ ] 打包发布 (PyInstaller)
许可证
MIT License

联系方式
如有问题或建议，请联系开发团队。
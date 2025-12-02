# GitHub 版本更新功能说明

## 功能概述

项目现已支持通过 GitHub 托管 `version.json` 文件来实现自动版本更新推送，无需搭建服务器。

### 主要特性

✅ **免费托管** - 使用 GitHub 免费托管版本信息文件
✅ **全球访问** - 利用 GitHub CDN，全球用户都能快速访问
✅ **自动检测** - 程序自动检查更新（启动时 + 每5分钟）
✅ **版本控制** - 所有版本历史都可追踪
✅ **多种方案** - 支持 GitHub、Gitee、云存储等多种托管方式
✅ **简单易用** - 无需服务器维护，只需推送文件

---

## 文档导航

### 快速开始（推荐新手）
📖 **[GitHub版本更新快速开始.md](GitHub版本更新快速开始.md)**
- 5分钟快速配置
- 3步骤发布新版本
- 常见问题解答

### 完整指南（推荐进阶）
📖 **[GitHub版本更新配置指南.md](GitHub版本更新配置指南.md)**
- 详细的配置步骤
- 多种托管方案对比
- 安全建议和最佳实践
- 故障排查指南
- 命令速查表

### 配置参考
📄 **[.env.example](.env.example)**
- 环境变量配置示例
- 支持的所有托管方式

---

## 工作原理

```
┌─────────────────┐
│  开发者         │
│  修改版本信息   │
└────────┬────────┘
         │
         │ git push
         ▼
┌─────────────────┐
│  GitHub 仓库    │
│  version.json   │
└────────┬────────┘
         │
         │ GitHub CDN
         ▼
┌─────────────────┐
│  用户程序       │
│  自动检查更新   │
└─────────────────┘
```

### 流程说明

1. **开发者**：修改 `version.json` 文件，推送到 GitHub
2. **GitHub**：托管文件，通过 Raw 链接提供访问
3. **用户程序**：定期请求 Raw 链接，检查版本更新
4. **自动提醒**：发现新版本时显示更新通知

---

## 快速开始

### 第一步：创建 GitHub 仓库

```bash
# 1. 在 GitHub 创建新仓库（必须是 Public）
# 2. 在项目目录执行
git remote add origin https://github.com/你的用户名/Safety-Manager.git
git branch -M main
git push -u origin main
```

### 第二步：配置更新链接

创建 `.env` 文件：

```ini
UPDATE_CHECK_URL=https://raw.githubusercontent.com/你的用户名/Safety-Manager/main/version.json
```

### 第三步：测试

```bash
# 启动程序
python run.py

# 查看日志
type data\logs\app_main.log
```

应该看到：
```
检查版本更新: https://raw.githubusercontent.com/你的用户名/Safety-Manager/main/version.json
当前已是最新版本: 1.0.0
```

---

## 发布新版本

### 1. 更新 version.json

```json
{
  "version": "1.1.0",
  "release_date": "2025-12-03",
  "download_url": "https://github.com/你的用户名/Safety-Manager/releases/download/v1.1.0/SafetyManager_v1.1.0.zip",
  "changelog": [
    "✨ 新增 XXX 功能",
    "🐛 修复 XXX 问题",
    "⚡ 优化 XXX 性能"
  ],
  "required": false,
  "min_version": "1.0.0"
}
```

### 2. 推送到 GitHub

```bash
git add version.json
git commit -m "发布 v1.1.0 版本"
git push
```

### 3. 用户自动接收

- 用户程序自动检测更新（启动时 + 每5分钟）
- 显示更新通知和详细信息
- 提供下载链接

---

## 托管方案对比

| 方案 | 优点 | 缺点 | 推荐指数 |
|------|------|------|----------|
| **GitHub Releases** | 免费、稳定、与代码集成 | 国内访问较慢 | ⭐⭐⭐⭐⭐ |
| **Gitee** | 国内访问快、免费 | 容量限制 | ⭐⭐⭐⭐ |
| **阿里云 OSS** | 国内访问快、稳定 | 收费 | ⭐⭐⭐⭐ |
| **腾讯云 COS** | 国内访问快、稳定 | 收费 | ⭐⭐⭐⭐ |
| **自建服务器** | 完全控制 | 需要维护 | ⭐⭐⭐ |

---

## 支持的托管方式

### 1. GitHub Raw（推荐）

```ini
UPDATE_CHECK_URL=https://raw.githubusercontent.com/your-username/Safety-Manager/main/version.json
```

**优点**：免费、稳定、全球CDN
**缺点**：国内访问可能较慢

### 2. Gitee Raw（国内推荐）

```ini
UPDATE_CHECK_URL=https://gitee.com/your-username/Safety-Manager/raw/master/version.json
```

**优点**：国内访问快、免费
**缺点**：免费版有容量限制

### 3. 云存储服务

```ini
# 阿里云 OSS
UPDATE_CHECK_URL=https://your-bucket.oss-cn-beijing.aliyuncs.com/version.json

# 腾讯云 COS
UPDATE_CHECK_URL=https://your-bucket.cos.ap-beijing.myqcloud.com/version.json
```

**优点**：国内访问快、稳定
**缺点**：需要付费

---

## 版本信息文件格式

### version.json 字段说明

```json
{
  "version": "1.0.0",           // 必填：新版本号
  "release_date": "2025-12-02", // 必填：发布日期
  "download_url": "下载链接",    // 必填：安装包下载地址
  "changelog": [                 // 必填：更新日志（数组）
    "更新内容1",
    "更新内容2"
  ],
  "required": false,             // 可选：是否强制更新
  "min_version": "1.0.0"        // 可选：支持的最低版本
}
```

### 示例

```json
{
  "version": "1.1.0",
  "release_date": "2025-12-03",
  "download_url": "https://github.com/username/Safety-Manager/releases/download/v1.1.0/SafetyManager_v1.1.0.zip",
  "changelog": [
    "✨ 新增 GitHub 版本更新支持",
    "✨ 新增配置向导",
    "🐛 修复数据库连接问题",
    "⚡ 优化启动速度"
  ],
  "required": false,
  "min_version": "1.0.0"
}
```

---

## 自动更新检测机制

### 检测时机

1. **程序启动时** - 立即检查一次
2. **定时检查** - 每5分钟检查一次
3. **手动触发** - 点击"检查更新"按钮

### 提醒方式

1. **弹窗通知** - 首次检测到新版本时弹窗
2. **红点提示** - 工具栏按钮显示未读通知数
3. **通知列表** - 查看详细的更新信息

### 检测逻辑

```python
# 伪代码
if 远程版本 > 当前版本:
    显示更新通知
    提供下载链接
else:
    显示"当前已是最新版本"
```

---

## 常见问题

### Q1: 为什么必须使用 Public 仓库？

**A**: GitHub 的 Raw 链接只对公开仓库免费提供。私有仓库需要认证才能访问。

### Q2: 如何处理国内访问慢的问题？

**A**: 有三种方案：
1. 使用 Gitee 托管（推荐）
2. 使用国内云存储（阿里云、腾讯云）
3. 配置 GitHub 镜像加速

### Q3: 更新检测有延迟？

**A**: GitHub CDN 有缓存机制，推送后等待 1-2 分钟即可生效。

### Q4: 如何回滚版本？

**A**: 有两种方法：
1. 在 GitHub 恢复旧的 `version.json` 文件
2. 使用 Git 命令：`git checkout HEAD~1 version.json`

### Q5: 下载文件放在哪里？

**A**: 推荐使用 GitHub Releases：
- 免费托管
- 与代码版本集成
- 自动生成下载链接

---

## 项目文件说明

### 新增文件

- ✅ `GitHub版本更新说明.md` - 本文件，功能概述
- ✅ `GitHub版本更新快速开始.md` - 快速开始指南
- ✅ `GitHub版本更新配置指南.md` - 完整配置文档
- ✅ `.env.example` - 已更新配置示例

### 修改文件

- ✅ `shared/config.py` - 配置注释已更新
- ✅ `.gitignore` - 已存在，无需修改
- ✅ `version.json` - 版本信息模板

### Git 状态

- ✅ Git 仓库已初始化
- ✅ 初始提交已完成
- ⏳ 等待推送到 GitHub 远程仓库

---

## 下一步操作

### 开发者（管理员）

1. ✅ 已完成：初始化 Git 仓库
2. ⏳ 待完成：在 GitHub 创建远程仓库
3. ⏳ 待完成：推送代码到 GitHub
4. ⏳ 待完成：配置 `.env` 文件
5. ⏳ 待完成：测试更新功能

### 用户

1. 收到新版本程序
2. 解压并运行
3. 程序自动检查更新
4. 收到更新提醒时点击查看详情

---

## 技术支持

### 文档资源

- 📖 快速开始：`GitHub版本更新快速开始.md`
- 📖 完整指南：`GitHub版本更新配置指南.md`
- 📖 推送功能：`推送功能使用说明.md`
- 📖 多用户协作：`多用户使用说明.md`

### 日志文件

```bash
# 查看应用日志
type data\logs\app_main.log

# 查看最新日志
tail -f data\logs\app_main.log  # Linux/Mac
Get-Content data\logs\app_main.log -Tail 50 -Wait  # PowerShell
```

### 测试工具

```bash
# 测试推送功能
测试推送功能.bat

# 测试数据库连接
测试数据库连接.bat

# 配置共享数据库
配置共享数据库.bat
```

---

## 版本历史

### v1.0.0 (2025-12-02)
- ✨ 初始版本发布
- ✅ 支持离线单机运行
- ✅ 自动数据库初始化
- ✅ 内置版本更新推送（共享数据库方式）
- ✅ 开箱即用，无需配置

### v1.0.0 + GitHub 支持 (2025-12-02)
- ✨ 新增 GitHub 版本更新支持
- ✨ 新增完整配置文档
- ✨ 新增快速开始指南
- ✅ 支持多种托管方式
- ✅ Git 仓库初始化
- ✅ 配置示例更新

---

## 总结

通过 GitHub 托管 `version.json` 文件，你可以：

✅ **零成本** - 完全免费，无需服务器
✅ **零维护** - GitHub 负责稳定性和可用性
✅ **全球访问** - 利用 GitHub CDN，访问速度快
✅ **版本控制** - 所有历史版本可追溯
✅ **简单易用** - 只需推送文件即可发布新版本

开始使用吧！🚀

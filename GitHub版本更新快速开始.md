# GitHub 版本更新 - 快速开始

## 5分钟快速配置指南

### 第一步：创建 GitHub 仓库（2分钟）

1. 访问 [https://github.com/new](https://github.com/new)
2. 填写：
   - Repository name: `Safety-Manager`
   - Visibility: `Public`（必须公开）
3. 点击 "Create repository"

### 第二步：推送代码（1分钟）

在项目目录执行：

```bash
git remote add origin https://github.com/你的用户名/Safety-Manager.git
git branch -M main
git push -u origin main
```

**提示**：如果需要认证，使用 Personal Access Token 作为密码。

### 第三步：配置更新链接（1分钟）

在项目根目录创建 `.env` 文件：

```ini
UPDATE_CHECK_URL=https://raw.githubusercontent.com/你的用户名/Safety-Manager/main/version.json
```

**重要**：将 `你的用户名` 替换为你的 GitHub 用户名。

### 第四步：测试（1分钟）

启动程序：

```bash
python run.py
```

查看日志 `data/logs/app_main.log`，应该看到：
```
检查版本更新: https://raw.githubusercontent.com/...
当前已是最新版本: 1.0.0
```

---

## 发布新版本（3步骤）

### 1. 修改 version.json

```json
{
  "version": "1.1.0",
  "release_date": "2025-12-03",
  "download_url": "https://github.com/你的用户名/Safety-Manager/releases/download/v1.1.0/SafetyManager_v1.1.0.zip",
  "changelog": [
    "✨ 新增 XXX 功能",
    "🐛 修复 XXX 问题"
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

### 3. 用户自动收到更新

- 用户程序会自动检测（启动时 + 每5分钟）
- 显示更新通知

---

## 托管下载文件（GitHub Releases）

### 创建 Release

1. 在 GitHub 仓库页面点击 "Releases"
2. 点击 "Create a new release"
3. 填写：
   - Tag: `v1.1.0`
   - Title: `Safety Manager v1.1.0`
4. 上传打包的 zip 文件
5. 点击 "Publish release"

### 复制下载链接

Release 发布后，右键点击 zip 文件，复制链接地址，格式为：
```
https://github.com/你的用户名/Safety-Manager/releases/download/v1.1.0/SafetyManager_v1.1.0.zip
```

将此链接填入 `version.json` 的 `download_url` 字段。

---

## 常见问题

### Q: 推送时提示需要认证？

**A**: 需要创建 Personal Access Token：

1. 访问：[https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Generate new token (classic)
3. 勾选 `repo` 权限
4. 复制生成的 Token
5. 推送时使用 Token 作为密码

### Q: 程序提示无法连接到更新服务器？

**A**: 检查：

1. `.env` 中的 URL 是否正确
2. GitHub 链接是否使用 `raw.githubusercontent.com` 域名
3. 仓库是否设置为 Public
4. 网络连接是否正常

### Q: 更新检测有延迟？

**A**: GitHub CDN 有缓存，推送后等待 1-2 分钟再测试。

---

## 完整文档

详细说明请查看：`GitHub版本更新配置指南.md`

包含内容：
- 详细的配置步骤
- 多种托管方案
- 安全建议
- 故障排查
- 命令参考

---

## 快速命令参考

```bash
# 查看当前远程仓库
git remote -v

# 查看Git状态
git status

# 推送更新
git add version.json
git commit -m "发布新版本"
git push

# 测试更新链接
curl https://raw.githubusercontent.com/你的用户名/Safety-Manager/main/version.json

# 启动程序
python run.py

# 查看日志
type data\logs\app_main.log
```

---

## 需要帮助？

1. 查看完整文档：`GitHub版本更新配置指南.md`
2. 查看项目日志：`data/logs/app_main.log`
3. 运行测试脚本：`测试推送功能.bat`

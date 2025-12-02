# GitHub 版本更新配置指南

## 概述

本指南说明如何通过 GitHub 托管 `version.json` 文件，实现自动版本更新推送功能。

使用 GitHub 的优势：
- ✅ 免费托管静态文件
- ✅ 全球CDN加速访问
- ✅ 版本控制，可追踪历史
- ✅ 无需搭建服务器
- ✅ 高可用性和稳定性

---

## 第一步：创建 GitHub 仓库

### 1.1 登录 GitHub

访问 [https://github.com](https://github.com) 并登录你的账户（如果没有账户，需要先注册）

### 1.2 创建新仓库

1. 点击右上角的 "+" 按钮，选择 "New repository"
2. 填写仓库信息：
   - **Repository name**: `Safety-Manager`（或其他你喜欢的名称）
   - **Description**: `并网法规管理系统`
   - **Visibility**: 选择 `Public`（必须是公开仓库才能使用 Raw 链接）
   - **Initialize this repository with**: 不要勾选任何选项
3. 点击 "Create repository"

### 1.3 记录仓库地址

创建成功后，你会看到仓库的 URL，例如：
```
https://github.com/your-username/Safety-Manager
```

记录下你的：
- **GitHub 用户名**: `your-username`
- **仓库名**: `Safety-Manager`

---

## 第二步：推送代码到 GitHub

### 2.1 添加远程仓库

在项目根目录打开命令行，执行：

```bash
git remote add origin https://github.com/your-username/Safety-Manager.git
```

**注意**：将 `your-username` 和 `Safety-Manager` 替换为你的实际用户名和仓库名。

### 2.2 推送代码

```bash
git branch -M main
git push -u origin main
```

如果提示需要认证：
- **用户名**: 你的 GitHub 用户名
- **密码**: 使用 Personal Access Token（不是登录密码）

#### 如何创建 Personal Access Token

1. 访问 GitHub 设置：[https://github.com/settings/tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 设置：
   - **Note**: `Safety-Manager Push`
   - **Expiration**: 选择有效期（建议选择 "No expiration"）
   - **Select scopes**: 勾选 `repo`（完整仓库访问权限）
4. 点击 "Generate token"
5. **重要**：复制生成的 Token（只会显示一次）
6. 在推送时使用这个 Token 作为密码

### 2.3 验证推送成功

访问你的 GitHub 仓库页面，应该能看到所有文件已经上传。

---

## 第三步：获取 version.json 的 Raw 链接

### 3.1 访问 version.json 文件

在 GitHub 仓库页面，点击 `version.json` 文件

### 3.2 获取 Raw 链接

点击页面右上角的 "Raw" 按钮，浏览器地址栏会显示 Raw 链接，例如：

```
https://raw.githubusercontent.com/your-username/Safety-Manager/main/version.json
```

**链接格式说明：**
```
https://raw.githubusercontent.com/{用户名}/{仓库名}/{分支名}/version.json
```

**重要提示：**
- 必须使用 `raw.githubusercontent.com` 域名
- 不是 `github.com` 域名
- 分支名通常是 `main` 或 `master`

### 3.3 测试链接

在浏览器中打开这个 Raw 链接，应该能看到 JSON 内容：

```json
{
  "version": "1.0.0",
  "release_date": "2025-12-02",
  "download_url": "https://your-download-link.com/SafetyManager_v1.0.0.zip",
  "changelog": [
    "✨ 初始发布版本",
    "✅ 支持离线单机运行"
  ],
  "required": false,
  "min_version": "1.0.0"
}
```

---

## 第四步：配置程序使用 GitHub 链接

### 4.1 方式一：修改 .env 文件（推荐）

在项目根目录创建或编辑 `.env` 文件：

```ini
# GitHub 版本更新配置
UPDATE_CHECK_URL=https://raw.githubusercontent.com/your-username/Safety-Manager/main/version.json

# 其他配置
APP_VERSION=1.0.0
LOG_LEVEL=INFO
OFFLINE_MODE=True
```

**重要**：将 `your-username` 替换为你的 GitHub 用户名。

### 4.2 方式二：修改 shared/config.py（不推荐）

如果不想使用 `.env` 文件，可以直接修改配置文件：

编辑 `shared/config.py` 的第 119-122 行：

```python
UPDATE_CHECK_URL: str = Field(
    default="https://raw.githubusercontent.com/your-username/Safety-Manager/main/version.json",
    env="UPDATE_CHECK_URL"
)
```

**缺点**：每次更新代码都需要重新修改。

---

## 第五步：测试版本更新功能

### 5.1 启动程序测试

1. 启动程序：`python run.py` 或双击 `启动程序.bat`
2. 程序会在启动时自动检查更新
3. 查看日志文件 `data/logs/app_main.log`，应该看到：
   ```
   检查版本更新: https://raw.githubusercontent.com/...
   当前已是最新版本: 1.0.0
   ```

### 5.2 测试新版本推送

#### 步骤 1：修改 version.json

编辑项目中的 `version.json` 文件，修改版本号：

```json
{
  "version": "1.1.0",
  "release_date": "2025-12-03",
  "download_url": "https://example.com/SafetyManager_v1.1.0.zip",
  "changelog": [
    "✨ 新增 XXX 功能",
    "🐛 修复 XXX 问题",
    "⚡ 优化 XXX 性能"
  ],
  "required": false,
  "min_version": "1.0.0"
}
```

#### 步骤 2：提交并推送到 GitHub

```bash
git add version.json
git commit -m "发布 v1.1.0 版本"
git push
```

#### 步骤 3：验证更新

1. 等待 1-2 分钟（GitHub CDN 缓存刷新）
2. 重启程序
3. 程序应该检测到新版本并显示更新通知

---

## 第六步：发布新版本的完整流程

### 6.1 准备新版本

1. 完成代码开发和测试
2. 使用 `build.bat` 打包可执行文件
3. 将打包文件上传到下载服务器（下方有详细说明）

### 6.2 更新 version.json

```json
{
  "version": "1.2.0",
  "release_date": "2025-12-05",
  "download_url": "你的下载链接",
  "changelog": [
    "更新内容说明..."
  ],
  "required": false,
  "min_version": "1.0.0"
}
```

**字段说明：**
- `version`: 新版本号（必填）
- `release_date`: 发布日期（必填）
- `download_url`: 下载地址（必填）
- `changelog`: 更新日志（必填，数组格式）
- `required`: 是否强制更新（true/false）
- `min_version`: 支持的最低版本

### 6.3 推送到 GitHub

```bash
git add version.json
git commit -m "发布 v1.2.0 版本

更新内容：
- 新增 XXX 功能
- 修复 XXX 问题
"
git push
```

### 6.4 通知用户

- 用户程序会自动检测更新（启动时 + 每5分钟）
- 如果设置了共享数据库，管理员可以通过"推送更新"功能主动通知

---

## 下载文件托管方案

### 方案 1：GitHub Releases（推荐）

**优点**：免费、稳定、与代码仓库集成

**步骤：**

1. 在 GitHub 仓库页面点击 "Releases" → "Create a new release"
2. 填写发布信息：
   - **Tag version**: `v1.0.0`
   - **Release title**: `Safety Manager v1.0.0`
   - **Description**: 更新说明
3. 上传打包的 zip 文件（从 `dist/` 目录）
4. 点击 "Publish release"
5. 复制下载链接，更新到 `version.json` 的 `download_url`

**下载链接格式：**
```
https://github.com/your-username/Safety-Manager/releases/download/v1.0.0/SafetyManager_v1.0.0.zip
```

### 方案 2：云存储服务

#### 阿里云 OSS
```
https://your-bucket.oss-cn-beijing.aliyuncs.com/SafetyManager_v1.0.0.zip
```

#### 腾讯云 COS
```
https://your-bucket.cos.ap-beijing.myqcloud.com/SafetyManager_v1.0.0.zip
```

#### 百度云 BOS
```
https://your-bucket.bcebos.com/SafetyManager_v1.0.0.zip
```

### 方案 3：Gitee（国内替代方案）

如果你的用户在中国，GitHub 访问可能较慢，可以使用 Gitee：

1. 在 Gitee 创建仓库：[https://gitee.com](https://gitee.com)
2. 推送代码到 Gitee
3. 使用 Gitee 的 Raw 链接：
   ```
   https://gitee.com/your-username/Safety-Manager/raw/master/version.json
   ```

**优点**：国内访问速度快
**缺点**：免费版有容量限制

---

## 常见问题

### Q1: Raw 链接返回 404？

**可能原因：**
- 仓库是私有的（必须是公开仓库）
- 文件路径不正确
- 分支名错误（main vs master）

**解决方法：**
1. 确保仓库是公开的（Public）
2. 检查文件是否存在于仓库根目录
3. 确认分支名（`main` 或 `master`）

### Q2: 程序无法访问 GitHub？

**可能原因：**
- 网络问题
- 防火墙拦截
- GitHub 服务不可用

**解决方法：**
1. 测试网络连接：在浏览器中打开 Raw 链接
2. 检查防火墙设置
3. 考虑使用 Gitee 作为备选方案

### Q3: 更新检测延迟？

**原因**：GitHub CDN 缓存

**解决方法**：
- 推送后等待 1-2 分钟再测试
- 在 URL 后添加时间戳参数：`?t=timestamp`（需要修改代码）

### Q4: 下载速度慢？

**原因**：GitHub 在国内访问速度较慢

**解决方法**：
1. 使用 Gitee 托管
2. 使用国内云存储服务（阿里云 OSS、腾讯云 COS）
3. 使用 CDN 加速

### Q5: 如何回滚版本？

**步骤：**
1. 在 GitHub 仓库中找到之前的提交
2. 恢复旧的 `version.json` 文件
3. 提交并推送

或者使用 Git 命令：
```bash
git checkout HEAD~1 version.json
git commit -m "回滚版本到 v1.0.0"
git push
```

---

## 安全建议

### 1. 保护敏感信息

- 不要在 `version.json` 中包含敏感信息
- 不要提交包含密码的 `.env` 文件
- 使用 `.gitignore` 排除敏感文件

### 2. 验证更新文件

建议在 `version.json` 中添加文件哈希值：

```json
{
  "version": "1.0.0",
  "download_url": "...",
  "sha256": "文件的SHA256哈希值",
  ...
}
```

然后在程序中验证下载文件的完整性。

### 3. 使用 HTTPS

确保所有链接都使用 HTTPS：
- ✅ `https://raw.githubusercontent.com/...`
- ❌ `http://raw.githubusercontent.com/...`

---

## 附录：命令速查表

### Git 常用命令

```bash
# 查看状态
git status

# 添加文件
git add version.json

# 提交更改
git commit -m "更新说明"

# 推送到 GitHub
git push

# 查看远程仓库
git remote -v

# 查看提交历史
git log --oneline

# 拉取最新代码
git pull
```

### 测试更新功能

```bash
# 测试网络连接
curl https://raw.githubusercontent.com/your-username/Safety-Manager/main/version.json

# 或使用 PowerShell
Invoke-WebRequest https://raw.githubusercontent.com/your-username/Safety-Manager/main/version.json

# 启动程序测试
python run.py
```

---

## 技术支持

如遇到问题：

1. 查看日志文件：`data/logs/app_main.log`
2. 运行测试脚本：`测试推送功能.bat`
3. 检查配置：`python -c "from shared.config import settings; print(settings.UPDATE_CHECK_URL)"`

---

## 总结

通过 GitHub 托管 `version.json`，你可以：

✅ 免费实现版本更新推送
✅ 无需搭建和维护服务器
✅ 利用 GitHub 的全球 CDN
✅ 版本控制和历史追踪
✅ 高可用性和稳定性

完整流程：
1. 创建 GitHub 仓库 →
2. 推送代码 →
3. 配置 Raw 链接 →
4. 测试更新功能 →
5. 发布新版本

开始使用吧！

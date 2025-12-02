# GitHub 自动推送使用指南

## 功能简介

现在可以直接在软件中点击"GitHub 推送"按钮，自动将版本更新推送到 GitHub，无需手动操作 Git 命令！

### 主要特性

✅ **一键推送** - 在软件界面中完成所有操作
✅ **自动化** - 自动更新 version.json 和 shared/config.py
✅ **安全验证** - 需要 GitHub Token（高级密码）
✅ **实时反馈** - 显示推送进度和结果
✅ **权限控制** - 仅管理员可以使用

---

## 使用流程

### 第一步：获取 GitHub Token（首次配置）

#### 1.1 访问 GitHub 设置

打开浏览器，访问：
```
https://github.com/settings/tokens
```

#### 1.2 创建新的 Token

1. 点击 **"Generate new token"** → **"Generate new token (classic)"**

2. 填写信息：
   - **Note**（名称）: `Safety Manager Auto Push`
   - **Expiration**（有效期）:
     - 推荐选择 `No expiration`（永不过期）
     - 或选择一个长期有效期（如 1 年）
   - **Select scopes**（权限）:
     - ✅ 勾选 **`repo`**（完整的仓库访问权限）
     - 这是必须的，用于推送代码

3. 滚动到底部，点击 **"Generate token"**

#### 1.3 保存 Token

⚠️ **重要**：
- Token 只会显示**一次**！
- 立即复制并保存到安全的地方
- 格式类似：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### 1.4 配置到软件（可选）

**方式一：每次输入（推荐）**
- 每次使用时手动输入 Token
- 更安全，不会保存在本地

**方式二：配置文件（方便）**
- 编辑项目根目录的 `.env` 文件
- 添加一行：
  ```ini
  GITHUB_TOKEN=ghp_your_token_here
  ```
- 重启软件，会自动填充

---

### 第二步：准备发布文件

在推送版本更新前，需要先在 GitHub 创建 Release。

#### 2.1 打包软件

```bash
build.bat
```

等待打包完成。

#### 2.2 创建 GitHub Release

1. 访问 GitHub 仓库：
   ```
   https://github.com/rockbing2125/Safety-Manager/releases
   ```

2. 点击 **"Create a new release"**

3. 填写 Release 信息：
   - **Tag version**: `v1.1.0`（新版本号）
   - **Release title**: `Safety Manager v1.1.0`
   - **Description**: 更新说明

4. 上传分发包：
   - 从 `dist/` 目录压缩 `SafetyManager` 文件夹
   - 命名为：`SafetyManager_v1.1.0.zip`
   - 上传到 Release

5. 点击 **"Publish release"**

#### 2.3 获取下载链接

发布后，右键点击 zip 文件，选择"复制链接地址"：
```
https://github.com/rockbing2125/Safety-Manager/releases/download/v1.1.0/SafetyManager_v1.1.0.zip
```

保存这个链接，下一步会用到。

---

### 第三步：在软件中推送更新

#### 3.1 启动软件

1. 以管理员身份登录软件
2. 你会在工具栏看到"GitHub 推送"按钮

#### 3.2 点击 GitHub 推送

点击工具栏的"GitHub 推送"按钮，打开推送对话框。

#### 3.3 填写版本信息

**版本信息**：
- **当前版本**: 自动显示（例如 1.0.0）
- **新版本号**: 输入新版本号（例如 `1.1.0`）
- **下载链接**: 粘贴 Release 的下载链接
- **强制更新**: 勾选表示用户必须更新
- **同步更新 config.py**: 勾选会同时更新应用版本号

**更新日志**（每行一条）：
```
✨ 新增 Excel 导出功能
✨ 新增批量导入功能
🐛 修复搜索崩溃问题
⚡ 优化加载速度
```

**GitHub 配置**：
- **GitHub Token**: 输入你的 Personal Access Token
- 如果 `.env` 中已配置，会自动填充

#### 3.4 测试连接（可选）

点击"测试连接"按钮，验证：
- GitHub Token 是否正确
- 网络连接是否正常
- 是否有推送权限

#### 3.5 推送到 GitHub

1. 点击"推送到 GitHub"按钮
2. 确认对话框，选择"是"
3. 等待推送完成（显示进度条）
4. 成功后会提示"推送成功"

---

### 第四步：验证推送结果

#### 4.1 检查 GitHub 仓库

访问 GitHub 仓库，检查：
- ✅ 最新提交包含版本更新
- ✅ version.json 已更新
- ✅ 提交信息正确

#### 4.2 测试用户接收

1. 等待 1-2 分钟（GitHub CDN 刷新）
2. 重启旧版本的程序
3. 应该看到更新通知

---

## 完整示例

### 推送 v1.1.0 版本的完整流程

```
1. 开发新功能 → 代码完成

2. 打包程序
   $ build.bat

3. 创建 GitHub Release
   - Tag: v1.1.0
   - 上传: SafetyManager_v1.1.0.zip
   - 复制下载链接

4. 在软件中推送
   - 点击"GitHub 推送"
   - 新版本号: 1.1.0
   - 下载链接: (粘贴)
   - 更新日志: (填写)
   - GitHub Token: (输入)
   - 点击"推送"

5. 等待推送完成 ✅

6. 用户自动收到更新 🎉
```

时间：**约 5-10 分钟**（不含开发时间）

---

## 常见问题

### Q1: 推送失败：Authentication failed

**原因**: GitHub Token 不正确或已过期

**解决**:
1. 检查 Token 是否完整复制
2. 检查 Token 是否仍然有效
3. 重新生成新的 Token

### Q2: 推送失败：Permission denied

**原因**: Token 权限不足

**解决**:
1. 确认 Token 勾选了 `repo` 权限
2. 重新生成 Token 并勾选正确权限

### Q3: 推送失败：Not a git repository

**原因**: 当前目录不是 Git 仓库

**解决**:
1. 确认在正确的项目目录
2. 运行 `git status` 检查
3. 如果需要，重新 `git init`

### Q4: Token 安全性问题

**Q**: 如果保存 Token 到 .env 文件，安全吗？

**A**:
- `.env` 文件已在 `.gitignore` 中，不会提交到 Git
- 但本地存储仍有风险
- 推荐方式：每次手动输入 Token

**安全建议**:
1. 不要分享 Token 给他人
2. 定期更换 Token（每 3-6 个月）
3. 只给必要的权限（repo）
4. 如果泄露，立即撤销旧 Token

### Q5: 能否自动创建 Release？

**A**: 当前版本需要手动创建 Release

**原因**: Release 需要上传分发包，无法完全自动化

**未来改进**: 可以集成 GitHub API 自动创建 Release

### Q6: 推送后用户多久能收到？

**A**:
- GitHub CDN 刷新：1-2 分钟
- 用户程序检测：启动时或每 5 分钟
- **总时间**: 1-7 分钟

### Q7: 可以撤销推送吗？

**A**: Git 推送无法直接撤销，但可以：
1. 回滚版本号
2. 推送新的更正版本
3. 或手动修改 version.json

---

## 高级功能

### 强制更新

适用场景：发现严重 bug，必须让用户更新

操作：
1. 在推送对话框勾选"强制更新"
2. 推送后，用户必须更新才能继续使用

### 批量推送（未来）

计划功能：
- 同时推送到 GitHub 和 Gitee
- 同时推送多个版本（不同平台）
- 定时推送

---

## 与手动推送的对比

| 项目 | 手动推送 | 软件自动推送 |
|------|---------|-------------|
| **操作步骤** | 7 步 | 1 步 |
| **需要技能** | Git 命令 | 无 |
| **错误风险** | 较高 | 较低 |
| **时间** | 5-10 分钟 | 1-2 分钟 |
| **适用对象** | 开发者 | 管理员 |

---

## 最佳实践

### 发布前检查清单

- [ ] 代码已测试无误
- [ ] 版本号已决定（遵循语义化版本）
- [ ] build.bat 打包成功
- [ ] GitHub Release 已创建
- [ ] 分发包已上传
- [ ] 下载链接已复制
- [ ] 更新日志已准备
- [ ] GitHub Token 可用

### 发布流程建议

**开发阶段**:
1. 功能开发
2. 本地测试
3. 代码审查

**打包阶段**:
1. 运行 build.bat
2. 测试打包结果
3. 压缩分发包

**发布阶段**:
1. 创建 GitHub Release
2. 上传分发包
3. 软件中点击"GitHub 推送"

**验证阶段**:
1. 检查 GitHub 提交
2. 测试用户接收
3. 监控反馈

---

## 故障排查

### 检查 Git 环境

```bash
# 检查 Git 是否安装
git --version

# 检查是否在 Git 仓库中
git status

# 检查远程仓库配置
git remote -v
```

### 检查网络连接

```bash
# 测试 GitHub 连接
ping github.com

# 测试 Git 连接
git ls-remote --heads origin
```

### 查看错误日志

日志文件位置：`data/logs/app_main.log`

查看最近的错误：
```bash
# Windows
type data\logs\app_main.log | findstr /C:"ERROR"

# 或直接打开文件查看
```

---

## 技术原理

### 推送流程

```python
1. 检查 Git 环境
   ├─ Git 是否安装？
   ├─ 是否在 Git 仓库？
   └─ 远程仓库是否配置？

2. 更新本地文件
   ├─ 修改 version.json
   └─ 修改 shared/config.py（可选）

3. Git 操作
   ├─ git add version.json shared/config.py
   ├─ git commit -m "发布 vX.X.X"
   └─ git push

4. 完成
   └─ 用户自动接收更新
```

### Token 认证方式

软件使用 HTTPS + Token 方式推送：

```
https://{token}@github.com/{username}/{repo}.git
```

这种方式：
- ✅ 安全（Token 可随时撤销）
- ✅ 方便（无需配置 SSH）
- ✅ 兼容性好（防火墙友好）

---

## 相关文档

- **版本更新推送完整流程.md** - 手动推送流程
- **软件分发完整指南.md** - 软件分发指南
- **GitHub版本更新配置指南.md** - GitHub 配置详解

---

## 总结

使用 GitHub 自动推送功能，你可以：

✅ **节省时间** - 1 分钟完成推送，而不是 10 分钟
✅ **减少错误** - 自动化流程，避免手动失误
✅ **简化操作** - 不需要懂 Git 命令
✅ **实时反馈** - 知道推送进度和结果
✅ **安全可靠** - Token 认证，可随时撤销

**开始使用吧！** 🚀

只需要：
1. 获取 GitHub Token（首次）
2. 创建 Release
3. 在软件中点击"GitHub 推送"

就是这么简单！

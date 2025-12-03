# Git 数据同步使用说明

## 📋 功能概述

本系统支持多用户通过 Git 自动同步法规数据。当用户A更新法规后推送到GitHub，用户B启动程序时会自动收到更新提示。

---

## ✅ 验证推送是否成功

### 方法1：使用命令行验证

在项目目录运行：
```bash
git log --oneline -5
git ls-remote --heads origin
```

**说明：**
- 如果两个命令显示的最新提交哈希值相同，说明推送成功
- 例如：本地和远程都显示 `32cfcf4`，则推送成功

### 方法2：访问 GitHub 网页

访问你的仓库：https://github.com/rockbing2125/Safety-Manager

查看最新提交记录，应该能看到刚刚推送的提交。

### 方法3：使用诊断工具

运行 `check_git_env.py`：
```bash
python check_git_env.py
```

该工具会自动检查：
- Git 是否安装
- 是否在 Git 仓库中
- 远程仓库配置
- 本地和远程的差异

---

## 🔧 解决常见问题

### 问题1：其他电脑 Git 检查超时

**错误信息：**
```
ERROR | client.services.data_sync_service:check_git_available:53 |
检查 Git 失败: Command '['git', '--version']' timed out after 5 seconds
```

**原因：**
- 该电脑未安装 Git
- Git 未添加到系统 PATH

**解决方法：**

1. **检查 Git 是否安装：**
   ```bash
   git --version
   ```

2. **如果未安装，下载安装 Git：**
   - 访问：https://git-scm.com/downloads
   - 下载并安装 Git for Windows
   - 安装时选择"Add to PATH"

3. **验证安装：**
   ```bash
   git --version
   ```
   应该显示：`git version x.x.x`

4. **运行诊断工具：**
   ```bash
   python check_git_env.py
   ```

### 问题2：版本检查编码错误

**错误信息：**
```
ERROR | client.services.update_service:check_for_updates:69 |
检查更新失败: 'latin-1' codec can't encode characters
```

**原因：**
- HTTP headers 不支持中文字符

**解决方法：**
- 已在最新版本中修复
- 更新到最新代码即可

### 问题3：Git 不在 PATH 中

**症状：**
- 命令行找不到 git 命令
- 程序启动时 Git 检查失败

**解决方法：**

1. **找到 Git 安装路径：**
   - 通常在：`C:\Program Files\Git\cmd`

2. **添加到系统 PATH：**
   - 右键"此电脑" → 属性 → 高级系统设置
   - 环境变量 → 系统变量 → Path → 编辑
   - 新建 → 添加 Git 路径：`C:\Program Files\Git\cmd`
   - 确定保存

3. **重启命令行/程序**

### 问题4：没有配置远程仓库

**症状：**
- 无法推送/拉取
- 提示"未配置远程仓库"

**解决方法：**

```bash
# 检查远程仓库
git remote -v

# 如果没有，添加远程仓库
git remote add origin https://github.com/rockbing2125/Safety-Manager.git

# 验证
git remote -v
```

---

## 🚀 完整工作流程

### 场景：用户A更新数据，用户B同步

#### 用户A（更新方）：

1. 打开 SafetyManager.exe
2. 登录并更新法规参数
3. 点击菜单：工具栏 → **"GitHub 推送"**
4. 填写版本信息和更新日志
5. 输入 GitHub Token
6. 点击"推送到 GitHub"
7. 等待推送成功

#### 用户B（同步方）：

1. 打开 SafetyManager.exe
2. **自动检查**：程序启动时自动检查更新
3. **弹出对话框**：如果有更新，显示"发现数据更新"
4. 查看更新内容：
   - 提交历史
   - 变更文件列表
   - 谁做了什么修改
5. 点击"**立即同步**"
6. 程序自动拉取并应用更新
7. 数据自动重新加载

---

## 📊 诊断工具使用

### 运行诊断

```bash
cd D:\work_file\AI\Safety-Manager
python check_git_env.py
```

### 诊断结果示例

```
============================================================
Git 环境诊断
============================================================

1. 检查 Git 是否在 PATH 中...
   [成功] Git 已安装: git version 2.41.0.windows.1

2. 检查当前目录是否是 Git 仓库...
   [成功] 是 Git 仓库，.git 位于: .git

3. 检查远程仓库配置...
   [成功] 远程仓库配置:
      origin	https://github.com/rockbing2125/Safety-Manager.git (fetch)
      origin	https://github.com/rockbing2125/Safety-Manager.git (push)

4. 检查当前分支...
   [成功] 当前分支: main

5. 检查本地和远程的差异...
   正在获取远程更新...
   [成功] 本地是最新的

============================================================
诊断完成！
============================================================
```

### 诊断项说明

| 诊断项 | 说明 | 解决方法 |
|--------|------|----------|
| Git 是否在 PATH 中 | 检查 Git 命令是否可用 | 安装 Git 并添加到 PATH |
| 是否是 Git 仓库 | 检查当前目录是否有 .git | 确保在项目根目录运行 |
| 远程仓库配置 | 检查是否配置了 origin | 使用 `git remote add` 添加 |
| 当前分支 | 显示当前所在分支 | 通常应该在 main 分支 |
| 本地和远程差异 | 检查是否需要同步 | 如有差异，使用 git pull |

---

## 🎯 最佳实践

### 推送更新前：

1. ✅ 确保本地数据已保存
2. ✅ 检查 Git 状态：`git status`
3. ✅ 填写清晰的更新日志
4. ✅ 推送成功后验证：`git log`

### 同步更新前：

1. ✅ 保存当前正在编辑的数据
2. ✅ 查看更新内容，了解变更
3. ✅ 确认无冲突后再同步
4. ✅ 同步后检查数据是否正确

### 日常维护：

1. 📅 定期检查更新
2. 📝 及时同步他人的修改
3. 🔄 保持良好的协作习惯
4. 💾 重要数据做好备份

---

## 🆘 需要帮助？

### 遇到问题时：

1. **运行诊断工具**：`python check_git_env.py`
2. **查看日志**：检查 `logs/` 目录下的日志文件
3. **检查 Git 状态**：`git status`
4. **查看远程状态**：`git remote -v`

### 联系支持：

- 查看 GitHub Issues
- 联系系统管理员
- 查看项目文档

---

## 📌 注意事项

1. **Git 必须安装**：数据同步功能需要 Git 支持
2. **网络连接**：需要能够访问 GitHub
3. **权限管理**：确保有仓库的读写权限
4. **数据冲突**：同时修改同一条数据时需要手动处理
5. **定期备份**：重要数据建议定期备份

---

**最后更新：** 2025-12-03
**版本：** v1.1.4

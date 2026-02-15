# 如何在 GitHub 上发布

本指南说明如何在 GitHub 上创建 v1.0.0 版本发布。

---

## 📋 前置条件

- [x] 所有代码已提交到 main/master 分支
- [x] pyproject.toml 已创建（版本 1.0.0）
- [x] CHANGELOG.md 已创建
- [x] RELEASE.md 已创建
- [x] README.md 已完善

---

## 🚀 步骤 1：创建 Git 标签

在本地项目目录执行：

```bash
# 创建标签 v1.0.0
git tag -a v1.0.0 -m "Release v1.0.0"

# 推送标签到 GitHub
git push origin v1.0.0
```

或者使用 Lightweight 标签：

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## 🌐 步骤 2：在 GitHub 上创建 Release

### 方法 A：通过 GitHub 网页界面（推荐）

1. 访问项目仓库：https://github.com/RSLN-creator/Comic-Crawler
2. 点击右侧的 **"Releases"** 链接
3. 点击 **"Draft a new release"** 按钮
4. 填写发布信息：

   - **Choose a tag**: 选择 `v1.0.0`
   - **Release title**: `v1.0.0`
   - **Describe this release**: 复制 `RELEASE.md` 的内容

5. **Attach binaries**（可选）：
   - 如果有打包好的 .exe 文件，可以拖拽上传

6. 点击 **"Publish release"** 完成！

---

### 方法 B：通过 GitHub CLI

如果你安装了 GitHub CLI：

```bash
gh release create v1.0.0 \
  --title "v1.0.0" \
  --notes-file RELEASE.md
```

---

## 📦 步骤 3：验证发布

发布完成后检查：

- [x] 访问 https://github.com/RSLN-creator/Comic-Crawler/releases
- [x] 确认 v1.0.0 发布存在
- [x] 确认源码压缩包已自动生成（.zip 和 .tar.gz）
- [x] 确认发布说明内容正确

---

## 📝 发布检查清单

在发布前确认：

- [ ] 所有代码已提交
- [ ] 已通过测试
- [ ] CHANGELOG.md 已更新
- [ ] 版本号已更新（pyproject.toml）
- [ ] README.md 是最新的
- [ ] 已创建 Git 标签
- [ ] 已推送到 GitHub

---

## 🎉 发布完成！

恭喜！v1.0.0 已成功发布到 GitHub。

用户现在可以：
- 从 Releases 页面下载源码
- 按照 README 说明运行项目
- 提交 Issue 反馈问题

---

## 🔮 未来发布

下次发布时：

1. 更新版本号（pyproject.toml）
2. 更新 CHANGELOG.md
3. 创建新的 Git tag
4. 在 GitHub 创建新的 Release

遵循语义化版本规范：
- **主版本号 (Major)**：不兼容的 API 修改
- **次版本号 (Minor)**：向下兼容的功能性新增
- **修订号 (Patch)**：向下兼容的问题修正

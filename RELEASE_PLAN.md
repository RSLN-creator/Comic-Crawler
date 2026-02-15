# Comic-Crawler 发布计划

## 📋 项目当前状态分析

### ✅ 已有功能
- Web UI (FastAPI + 静态前端)
- 漫画下载功能 (JMComic)
- CBZ 打包 (Kavita 兼容)
- 设置持久化
- 服务启停管理 (start.bat, end.bat)
- 完整的 README.md

### ❌ 缺少的发布要素
- 项目元数据 (pyproject.toml, setup.cfg)
- 版本号管理
- PyInstaller 打包配置
- Docker 支持
- CI/CD 配置
- CHANGELOG.md
- 便携式版本

---

## 🚀 发布可能性

### 1. PyPI 包发布
**目标**: 将 jmcomic 库发布到 PyPI

**需要做**:
- 创建 pyproject.toml
- 配置包元数据
- 添加版本号
- 测试 pip install

---

### 2. 独立可执行文件 (.exe)
**目标**: 使用 PyInstaller 打包成单个 exe 文件

**需要做**:
- 创建 PyInstaller spec 文件
- 配置打包选项
- 测试打包后的功能
- 解决依赖问题

---

### 3. Docker 镜像发布
**目标**: 提供 Docker 镜像，一键运行

**需要做**:
- 创建 Dockerfile
- 配置 docker-compose.yml
- 测试容器运行
- 推送到 Docker Hub

---

### 4. GitHub Release
**目标**: 在 GitHub 上发布完整版本

**需要做**:
- 整理发布文件
- 创建发布说明
- 上传打包好的文件
- 管理版本标签

---

### 5. 便携式版本 (Portable)
**目标**: 无需安装，解压即用

**需要做**:
- 嵌入 Python 运行时
- 创建便携式启动脚本
- 配置相对路径
- 测试在不同电脑上运行

---

## 📝 实施计划

### 第一阶段：基础准备 (P0)

- [x] 分析项目结构
- [ ] 创建 pyproject.toml
- [ ] 创建 setup.cfg
- [ ] 确定版本号 (v1.0.0)
- [ ] 创建 CHANGELOG.md

### 第二阶段：打包配置 (P0)

- [ ] 创建 PyInstaller spec 文件
- [ ] 配置打包选项
- [ ] 测试打包
- [ ] 修复打包问题

### 第三阶段：容器化 (P1)

- [ ] 创建 Dockerfile
- [ ] 创建 docker-compose.yml
- [ ] 测试容器运行
- [ ] 优化镜像大小

### 第四阶段：CI/CD (P1)

- [ ] 创建 GitHub Actions 配置
- [ ] 配置自动测试
- [ ] 配置自动打包
- [ ] 配置自动发布

### 第五阶段：便携式版本 (P1)

- [ ] 研究 Python 嵌入方案
- [ ] 创建便携式启动脚本
- [ ] 测试便携性
- [ ] 优化体积

### 第六阶段：发布 (P0)

- [ ] 最终测试
- [ ] 创建发布标签
- [ ] 上传 GitHub Release
- [ ] 发布 PyPI 包 (可选)
- [ ] 发布 Docker 镜像 (可选)
- [ ] 更新 README

---

## 📦 推荐的发布顺序

### 方案 A：最小可行发布 (快速)
1. GitHub Release (源码 + 启动脚本)
2. PyInstaller .exe 打包
3. 更新文档

### 方案 B：完整发布 (全面)
1. 所有基础准备
2. PyPI 发布
3. .exe 打包
4. Docker 镜像
5. GitHub Release
6. CI/CD 自动化

### 方案 C：便携优先 (用户友好)
1. 便携式版本
2. .exe 打包
3. GitHub Release
4. 文档

---

## ⚠️ 注意事项

### 技术风险
- PyInstaller 可能遇到依赖问题
- Docker 镜像可能较大
- 便携式版本体积可能过大

### 法律风险
- 项目仅供学习使用
- 不要存储漫画内容
- 遵守当地法律法规

### 用户体验
- 确保启动简单
- 提供清晰的错误提示
- 保持向后兼容

---

## 🎯 成功标准

### 对于 .exe 版本
- [ ] 双击即可运行
- [ ] 无需安装 Python
- [ ] 所有功能正常
- [ ] 体积 &lt; 100MB (理想)

### 对于 Docker 版本
- [ ] docker-compose up 一键启动
- [ ] 数据持久化
- [ ] 镜像大小 &lt; 500MB

### 对于 GitHub Release
- [ ] 包含所有必要文件
- [ ] 有清晰的发布说明
- [ ] 有版本标签

---

## 📚 参考资源

- PyInstaller 文档: https://pyinstaller.org/
- Python 打包指南: https://packaging.python.org/
- Docker 最佳实践: https://docs.docker.com/develop/dev-best-practices/
- GitHub Actions: https://docs.github.com/en/actions

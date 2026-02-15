# Changelog

所有重要的项目变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
本项目遵循 [语义化版本 (Semantic Versioning)](https://semver.org/lang/zh-CN/)。

---

## [1.0.0] - 2026-02-15

### ✨ 新增
- 完整的 Web UI 界面（Kavita 风格）
- FastAPI 后端 API
- 漫画下载功能（支持 JM 前缀 ID）
- CBZ 打包功能（Kavita 兼容）
- 设置持久化功能
- 实时日志显示
- 终端输出实时显示
- 目录浏览功能（支持多盘符）
- 一键停止服务功能（end.bat + Web UI 按钮）
- start.bat 启动脚本（隐藏窗口模式）
- end.bat 停止服务脚本
- 完整的 README.md 文档
- pyproject.toml 项目配置
- CHANGELOG.md 变更日志

### 📝 文档
- 完善的 README.md，包含快速开始、首次运行指南、API 文档等
- 常见问题解答（FAQ）
- 服务管理说明

### 🐛 修复
- 修复了设置保存后不生效的问题
- 修复了端口冲突处理
- 修复了服务停止功能

### 🔧 配置
- 后端默认端口：8765
- 前端默认端口：3000
- 依赖已完整列出在 requirements.txt

---

## [1.0.1] - 2026-02-15

### 🐛 修复
- 修复 api_server.py 中 terminal_outputs 重复定义的严重Bug
- 修复 start.bat 中 Python 命令检测问题（支持 py 和 python 命令自动检测）
- 修复跨平台启动脚本的兼容性问题
- 解决 API 连接不稳定的问题（"已连接-未连接"的波动问题）

### 🔧 改进
- start.bat 现在会自动检测可用的 Python 命令（py 或 python）
- 简化了启动流程，确保完整安装后端依赖
- 使用 sys.executable 确保跨平台 Python 解释器兼容性
- 移除了开发文档（HOW_TO_RELEASE.md、RELEASE_PLAN.md、RELEASE.md）

---

## [未发布]

### 计划中
- PyInstaller .exe 打包
- Docker 镜像支持
- GitHub Actions CI/CD
- 便携式版本

---

[1.0.1]: https://github.com/RSLN-creator/Comic-Crawler/releases/tag/v1.0.1
[1.0.0]: https://github.com/RSLN-creator/Comic-Crawler/releases/tag/v1.0.0

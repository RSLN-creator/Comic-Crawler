# Comic-Crawler

基于 Kavita UI 风格的现代化漫画下载器应用，采用 "静态前端 + Python FastAPI 后端" 的现代轻量架构。

## 功能特性

- **下载管理**: 批量下载漫画专辑，支持 JM 前缀 ID
- **Kavita 打包**: 一键转换为 CBZ 格式，方便导入 Kavita、Komga 等漫画阅读器
- **设置管理**: 持久化保存用户配置
- **深色主题**: Kavita UI 设计风格 - 参考 Kavita 开源项目的界面设计
- **实时日志**: 下载和打包进度实时显示
- **终端实时显示**: 实时显示底层 Python 终端输出，方便调试和查看详细信息
- **目录浏览**: 支持多盘符浏览，方便选择文件路径
- **返回上级目录**: 目录浏览中支持返回上级目录，包括返回"此电脑"界面
- **一键停止服务**: 提供 end.bat 脚本和 Web UI 按钮，方便停止服务

## 技术栈

### 前端
- Tailwind CSS (CDN) - 现代 CSS 框架
- Vanilla JavaScript - 原生 JavaScript
- Kavita UI 设计风格 - 参考 Kavita 开源项目的界面设计

### 后端
- Python FastAPI - 高性能异步 API 框架
- Uvicorn 服务器 - ASGI 服务器
- JMComic 库 - 核心下载功能

## 系统要求

- **Python 3.8+** (必须)
- 稳定的网络连接
- 足够的磁盘空间用于存储漫画
- 支持现代浏览器（Chrome、Firefox、Edge 等）

## 目录结构

```
Comic-Crawler/
├── src/                              # 主源码
│   ├── jmcomic/                      # JMComic 核心库
│   └── web_app/                      # Web 应用
│       ├── backend/                   # FastAPI 后端
│       └── frontend/                  # 静态前端
├── data/                             # 数据目录（自动创建）
│   ├── downloads/                    # 漫画下载目录
│   └── cbz_output/                   # CBZ 打包输出目录
├── scripts/                          # 脚本文件
│   └── start.py                      # 跨平台启动脚本
├── README.md                         # 项目说明文档
├── CHANGELOG.md                      # 版本变更日志
├── RELEASE.md                        # 发布说明
├── HOW_TO_RELEASE.md                 # 发布指南
├── RELEASE_PLAN.md                   # 发布计划
├── pyproject.toml                    # 项目配置
├── requirements.txt                  # Python 依赖文件
├── start.bat                         # Windows 启动脚本
├── end.bat                           # Windows 停止服务脚本
└── .gitignore                        # Git 忽略文件
```

## 快速启动

### Windows

```bash
# 双击运行启动脚本
start.bat
```

### Linux/Mac

```bash
# 运行启动脚本
python scripts/start.py
```

## 首次运行指南

### 第一步：安装 Python

如果还没有安装 Python，请按以下步骤操作：

1. **下载 Python**
   - 访问 [Python 官网](https://www.python.org/downloads/)
   - 下载 Python 3.8 或更高版本

2. **安装 Python (Windows)**
   - 运行下载的安装程序
   - **重要**: 勾选 "Add Python to PATH" 选项
   - 点击 "Install Now" 完成安装

3. **验证安装**
   ```bash
   python --version
   ```
   如果显示版本号，说明安装成功。

### 第二步：克隆项目

```bash
git clone https://github.com/RSLN-creator/Comic-Crawler.git
cd Comic-Crawler
```

### 第三步：安装依赖

```bash
# 安装项目依赖
python -m pip install -r requirements.txt
```

### 第四步：启动应用

- Windows: 双击运行 `start.bat`
- Linux/Mac: 运行 `python scripts/start.py`

## 手动启动

### 第一步：安装依赖

```bash
# 安装后端依赖
pip install -r src/web_app/backend/requirements.txt
```

### 第二步：启动后端 API 服务

```bash
cd src/web_app/backend
python -m uvicorn api_server:app --host 0.0.0.0 --port 8765 --reload
```

### 第三步：启动前端服务

```bash
cd src/web_app/frontend
python -m http.server 3000
```

### 第四步：访问应用

打开浏览器访问：http://localhost:3000

## 配置说明

### 环境变量

| 变量 | 描述 | 默认值 |
|------|------|------|
| `BACKEND_PORT` | 后端 API 服务端口 | 8765 |
| `FRONTEND_PORT` | 前端 Web 服务端口 | 3000 |

### 默认路径

| 路径 | 描述 | 默认值 |
|------|------|------|
| 下载目录 | 漫画文件保存路径 | `data/downloads` |
| 打包输出 | CBZ 文件输出路径 | `data/cbz_output` |

## API 接口

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API 状态检查 |
| `/api/settings` | GET | 获取当前设置 |
| `/api/settings` | POST | 更新设置 |
| `/api/download` | POST | 启动下载任务 |
| `/api/download/{task_id}` | GET | 查询下载状态 |
| `/api/pack` | POST | 启动打包任务 |
| `/api/pack/{task_id}` | GET | 查询打包状态 |
| `/api/browse` | GET | 浏览目录结构 |
| `/api/terminal/{task_id}` | GET | 获取任务终端输出 |
| `/api/shutdown` | POST | 停止服务 |

## 服务管理

### 启动服务

- **Windows**: 双击运行 `start.bat`
- **Linux/Mac**: 运行 `python scripts/start.py`

### 停止服务

- **Windows**: 
  - 方法1: 在 Web UI 设置页面点击红色"停止服务"按钮
  - 方法2: 双击运行 `end.bat`
  - 方法3: 直接关闭后端和前端对应的命令行窗口
- **Linux/Mac**: 在终端按 `Ctrl+C` 停止服务

### 重启服务

- **Windows**: 
  1. 先运行 `end.bat` 停止旧服务
  2. 重新双击运行 `start.bat`
- **Linux/Mac**: 
  1. 按 `Ctrl+C` 停止旧服务
  2. 重新运行 `python scripts/start.py`

### 手动重启后端

```bash
# 进入后端目录
cd src/web_app/backend
# 停止旧服务（Ctrl+C），然后重新启动
python -m uvicorn api_server:app --host 0.0.0.0 --port 8765 --reload
```

### 手动重启前端

```bash
# 进入前端目录
cd src/web_app/frontend
# 停止旧服务（Ctrl+C），然后重新启动
python -m http.server 3000
```

## 使用示例


### 配置设置

   - 在 "设置" 页面配置默认下载路径和其他参数
   - 点击 "保存设置" 按钮持久化配置

### 开始下载

   - 在 "下载管理" 页面输入专辑 ID（支持多行输入）
   - 点击 "开始下载" 按钮启动下载任务
   - 查看实时下载进度和日志

### 打包为 CBZ

   - 在 "Kavita 打包" 页面选择下载目录
   - 选择输出目录
   - 点击 "开始打包" 按钮生成 CBZ 文件

### 导入到 Kavita

   - 将生成的 CBZ 文件复制到 Kavita 的漫画库目录
   - 在 Kavita 中扫描库以识别新漫画


### 下载漫画

1. 在 "下载管理" 页面输入专辑 ID，例如：
   ```
   JM1224005
   123456
   ```

2. 选择下载路径和其他设置
3. 点击 "开始下载" 按钮

### 打包为 CBZ

1. 在 "Kavita 打包" 页面选择包含漫画的目录
2. 选择输出目录
3. 点击 "开始打包" 按钮
4. 等待打包完成后，在输出目录中找到生成的 CBZ 文件

## 命令行使用 (暂未完善)

除了 Web 界面，Comic-Crawler 还支持命令行模式使用：

### 基础命令

```bash
# 进入项目目录
cd Comic-Crawler

# 下载专辑（支持多个ID）
python -m jmcomic 12345 67890

# 下载章节（使用 p 前缀）
python -m jmcomic p12345 p67890

# 混合下载专辑和章节
python -m jmcomic 12345 67890 p12345
```

### 使用配置文件

```bash
# 使用自定义配置文件
python -m jmcomic 12345 --option="path/to/option.yml"
```

### 启动 GUI 界面

```bash
# 启动图形界面（如果已安装 tkinter）
python -m jmcomic --gui
```

### 命令行参数

- `id_list`: 要下载的专辑/章节ID列表（空格分隔）
  - 专辑ID：直接输入数字（如 `12345`）
  - 章节ID：添加 `p` 前缀（如 `p12345`）
- `--option`: 指定配置文件路径
- `--gui`: 启动图形界面

## 常见问题

### Q: 端口被占用怎么办？

如果启动时提示端口被占用（3000 或 8765），可以按以下方法处理：

**Windows:**

```bash
# 查看哪个程序占用了端口（以3000为例，8765同理）
netstat -ano | findstr :3000

# 查看占用端口的进程名
tasklist | findstr <进程ID>

# 结束占用端口的进程（如果不需要该程序）
taskkill /F /PID <进程ID>
```

**或者更换端口：**

1. 编辑 `start.bat`，修改端口设置
2. 编辑 `scripts/start.py`，修改对应端口
3. 重新运行启动脚本

### Q: 下载失败怎么办？

A: 检查网络连接，确保专辑 ID 正确，查看日志中的错误信息。

### Q: 打包后在 Kavita 中显示乱序怎么办？

A: CBZ 文件已经按照章节顺序命名，Kavita 会自动按文件名排序显示。

### Q: 如何添加新的下载任务？

A: 在下载管理页面清空现有 ID，输入新的 ID 列表，然后点击 "开始下载"。

### Q: 如何正确停止服务？

A: 推荐使用以下方法之一：
1. 在 Web UI 的设置页面点击红色"停止服务"按钮
2. 双击运行 `end.bat` 脚本（Windows）

## 许可证

本项目仅供学习交流使用，请勿用于非法用途。

## 免责声明

- 本项目仅提供下载工具，不存储任何漫画内容
- 下载内容的版权归原作者所有
- 请遵守当地法律法规，合理使用本工具

## 贡献

欢迎提交 Issue 和 Pull Request，共同改进项目！

## 联系方式

- 项目地址: https://github.com/RSLN-creator/Comic-Crawler
- 问题反馈: https://github.com/RSLN-creator/Comic-Crawler/issues

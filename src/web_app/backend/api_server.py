"""
Comic-Crawler Web API 服务
提供 RESTful API 接口供前端调用
"""
import os
import sys
import json
import asyncio
import threading
import io
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn


class OutputCapture:
    """捕获标准输出和标准错误的捕获器
    """
    def __init__(self):
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        self.lines: List[str] = []
        self.current_task_id: Optional[str] = None
    
    def write_stdout(self, text):
        line = text.rstrip('\n')
        if line:
            self.lines.append(line)
            if self.current_task_id and self.current_task_id in terminal_outputs:
                terminal_outputs[self.current_task_id].append(line)
        self.old_stdout.write(text)
        self.old_stdout.flush()
    
    def write_stderr(self, text):
        line = text.rstrip('\n')
        if line:
            self.lines.append(line)
            if self.current_task_id and self.current_task_id in terminal_outputs:
                terminal_outputs[self.current_task_id].append(line)
        self.old_stderr.write(text)
        self.old_stderr.flush()
    
    def start(self, task_id: Optional[str] = None):
        self.lines = []
        self.current_task_id = task_id
        sys.stdout = type('', (), {'write': self.write_stdout})()
        sys.stderr = type('', (), {'write': self.write_stderr})()
    
    def stop(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.current_task_id = None
    
    def get_output(self):
        return '\n'.join(self.lines)
    
    def clear(self):
        self.lines = []


output_capture = OutputCapture()
terminal_outputs: Dict[str, List[str]] = {}

# 添加源码路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from jmcomic import JmModuleConfig, JmOption
from jmcomic.api import (
    download_album,
    download_photo,
    pack_album_to_kavita,
    pack_albums_to_kavita,
    create_option_by_file
)

app = FastAPI(
    title="Comic-Crawler Web API",
    description="Comic-Crawler 下载器 Web API 服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

download_tasks: Dict[str, Dict] = {}
pack_tasks: Dict[str, Dict] = {}


class DownloadRequest(BaseModel):
    album_ids: List[str]
    download_path: str = str(Path.home() / "Downloads" / "Comic-Crawler")
    thread_count: int = 5
    image_format: str = ".jpg"
    client_type: str = "html"


class PackRequest(BaseModel):
    source_dir: str
    output_dir: str
    overwrite: bool = True
    compress_level: int = 1


class SettingsModel(BaseModel):
    download_path: str = str(Path.home() / "Downloads" / "Comic-Crawler")
    thread_count: int = 5
    image_format: str = ".jpg"
    client_type: str = "html"
    kavita_output_dir: str = ""


SETTINGS_FILE = Path(__file__).parent / "settings.json"


def load_settings() -> SettingsModel:
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return SettingsModel(**json.load(f))
    return SettingsModel()


def save_settings(settings: SettingsModel):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings.model_dump(), f, ensure_ascii=False, indent=2)


@app.get("/")
async def root():
    return {"message": "Comic-Crawler Web API", "version": "1.0.0"}


@app.get("/api/settings")
async def get_settings():
    settings = load_settings()
    return settings.model_dump()


@app.post("/api/settings")
async def update_settings(settings: SettingsModel):
    save_settings(settings)
    return {"success": True, "message": "设置已保存"}


@app.post("/api/download")
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    if not request.album_ids or len(request.album_ids) == 0:
        raise HTTPException(status_code=400, detail="专辑ID列表不能为空")
    
    task_id = f"download_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    download_tasks[task_id] = {
        "status": "pending",
        "album_ids": request.album_ids,
        "completed": [],
        "failed": [],
        "logs": []
    }
    terminal_outputs[task_id] = []
    
    download_path = request.download_path
    album_ids = list(request.album_ids)
    
    def run_download():
        download_tasks[task_id]["status"] = "running"
        output_capture.start(task_id)
        
        try:
            option = JmModuleConfig.option_class().default()
            option.dir_rule.base_dir = download_path
            
            for album_id in album_ids:
                try:
                    album_id = album_id.strip()
                    if album_id.upper().startswith("JM"):
                        album_id = album_id[2:]
                    
                    if not album_id.isdigit():
                        download_tasks[task_id]["logs"].append({
                            "level": "warning",
                            "message": f"跳过无效ID: {album_id}"
                        })
                        continue
                    
                    download_tasks[task_id]["logs"].append({
                        "level": "info",
                        "message": f"开始下载: {album_id}"
                    })
                    
                    album, downloader = download_album(album_id, option=option)
                    
                    download_tasks[task_id]["completed"].append({
                        "id": album_id,
                        "name": album.name,
                        "path": str(downloader.option.dir_rule.base_dir)
                    })
                    download_tasks[task_id]["logs"].append({
                        "level": "success",
                        "message": f"下载完成: {album.name}"
                    })
                    
                except Exception as e:
                    import traceback
                    error_detail = f"{str(e)}"
                    download_tasks[task_id]["failed"].append({
                        "id": album_id,
                        "error": error_detail
                    })
                    download_tasks[task_id]["logs"].append({
                        "level": "error",
                        "message": f"下载失败 {album_id}: {error_detail}"
                    })
            
            download_tasks[task_id]["status"] = "completed"
            
        except Exception as e:
            import traceback
            download_tasks[task_id]["status"] = "error"
            download_tasks[task_id]["logs"].append({
                "level": "error",
                "message": f"{str(e)}\n{traceback.format_exc()}"
            })
        finally:
            terminal_outputs[task_id] = output_capture.lines.copy()
            output_capture.stop()
    
    thread = threading.Thread(target=run_download, daemon=True)
    thread.start()
    
    return {"task_id": task_id, "message": "下载任务已启动"}


@app.get("/api/download/{task_id}")
async def get_download_status(task_id: str):
    if task_id not in download_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    return download_tasks[task_id]


@app.post("/api/pack")
async def start_pack(request: PackRequest, background_tasks: BackgroundTasks):
    if not request.source_dir or not request.source_dir.strip():
        raise HTTPException(status_code=400, detail="源目录不能为空")
    if not request.output_dir or not request.output_dir.strip():
        raise HTTPException(status_code=400, detail="输出目录不能为空")
    
    source_path = Path(request.source_dir)
    if not source_path.exists():
        raise HTTPException(status_code=400, detail=f"源目录不存在: {request.source_dir}")
    if not source_path.is_dir():
        raise HTTPException(status_code=400, detail=f"源路径不是目录: {request.source_dir}")
    
    task_id = f"pack_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    pack_tasks[task_id] = {
        "status": "pending",
        "source_dir": request.source_dir,
        "output_dir": request.output_dir,
        "stats": {"success": 0, "failed": 0, "total": 0},
        "files": [],
        "logs": []
    }
    terminal_outputs[task_id] = []
    
    def run_pack():
        pack_tasks[task_id]["status"] = "running"
        output_capture.start(task_id)
        
        try:
            source_path = Path(request.source_dir)
            output_path = Path(request.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            album_dirs = [d for d in source_path.iterdir() if d.is_dir()]
            pack_tasks[task_id]["stats"]["total"] = len(album_dirs)
            
            for album_dir in album_dirs:
                try:
                    pack_tasks[task_id]["logs"].append({
                        "level": "info",
                        "message": f"正在打包: {album_dir.name}"
                    })
                    
                    cbz_paths = pack_album_to_kavita(
                        str(album_dir),
                        str(output_path),
                        overwrite=request.overwrite,
                        compress_level=request.compress_level
                    )
                    
                    if cbz_paths:
                        for cbz_path in cbz_paths:
                            pack_tasks[task_id]["files"].append(str(cbz_path))
                        pack_tasks[task_id]["stats"]["success"] += 1
                        pack_tasks[task_id]["logs"].append({
                            "level": "success",
                            "message": f"打包完成: {len(cbz_paths)}个文件"
                        })
                    else:
                        pack_tasks[task_id]["stats"]["failed"] += 1
                        
                except Exception as e:
                    pack_tasks[task_id]["stats"]["failed"] += 1
                    pack_tasks[task_id]["logs"].append({
                        "level": "error",
                        "message": f"打包失败 {album_dir.name}: {str(e)}"
                    })
            
            pack_tasks[task_id]["status"] = "completed"
            
        except Exception as e:
            pack_tasks[task_id]["status"] = "error"
            pack_tasks[task_id]["logs"].append({
                "level": "error",
                "message": str(e)
            })
        finally:
            terminal_outputs[task_id] = output_capture.lines.copy()
            output_capture.stop()
    
    thread = threading.Thread(target=run_pack)
    thread.start()
    
    return {"task_id": task_id, "message": "打包任务已启动"}


@app.get("/api/pack/{task_id}")
async def get_pack_status(task_id: str):
    if task_id not in pack_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    return pack_tasks[task_id]


@app.get("/api/browse")
async def browse_directory(path: str = ""):
    import platform
    
    try:
        if not path:
            if platform.system() == "Windows":
                drives = []
                for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    drive_path = f"{letter}:\\"
                    if os.path.exists(drive_path):
                        drives.append({
                            "name": f"本地磁盘 ({letter}:)",
                            "path": drive_path,
                            "is_dir": True
                        })
                return {
                    "current": "此电脑",
                    "parent": None,
                    "items": drives,
                    "is_root": True
                }
            else:
                path = "/"
        
        target = Path(path)
        if not target.exists():
            raise HTTPException(status_code=404, detail="目录不存在")
        
        if target.is_file():
            target = target.parent
        
        items = []
        for item in sorted(target.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if item.name.startswith('.'):
                continue
            try:
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "is_dir": item.is_dir()
                })
            except PermissionError:
                continue
        
        # 检查是否为盘符根目录 (如 C:\)
        is_drive_root = False
        if platform.system() == "Windows":
            drive_letter = target.drive
            if drive_letter and str(target) == drive_letter + '\\':
                is_drive_root = True
        
        parent_path = None if is_drive_root else (str(target.parent) if target.parent != target else None)
        
        return {
            "current": str(target),
            "parent": parent_path,
            "items": items,
            "is_root": False
        }
        
    except PermissionError:
        raise HTTPException(status_code=403, detail="没有权限访问此目录")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/terminal/{task_id}")
async def get_terminal_output(task_id: str):
    """获取任务的终端输出
    """
    if task_id not in terminal_outputs:
        return {"output": []}
    return {"output": terminal_outputs[task_id]}


@app.post("/api/shutdown")
async def shutdown():
    """停止服务
    """
    import os
    import subprocess
    
    try:
        project_root = Path(__file__).parent.parent.parent.parent
        end_bat = project_root / "end.bat"
        
        if end_bat.exists():
            subprocess.Popen([str(end_bat)], shell=True)
        
        return {"success": True, "message": "Stopping services..."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def run_server(host: str = "127.0.0.1", port: int = 8765):
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_server()

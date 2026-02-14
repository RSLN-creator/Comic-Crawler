"""
JMComic 现代化图形界面 (Flet 版本)

基于 Flet 框架，提供类似 Kavita 的现代化体验。
支持批量下载专辑、Kavita CBZ 打包、配置管理等功能。

Author: Claude
Version: 2.7.0
"""

import os
import sys
import threading
import time
from pathlib import Path
from typing import Optional, List

import flet as ft

# 添加 src 到路径
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir / 'src'))

from jmcomic import JmModuleConfig, JmOption
from jmcomic.api import download_album, pack_albums_to_kavita


# ===================== 主题配色 (Kavita 风格) =====================
THEME = {
    # Kavita 风格深色主题
    'primary': '#6366f1',        # Indigo 500 - 主色调
    'primary_dark': '#4f46e5',   # Indigo 600 - 主色调深色
    'secondary': '#10b981',      # Emerald 500 - 次色调
    'bg_dark': '#0f172a',        # Slate 900 - 背景色
    'bg_card': '#1e293b',        # Slate 800 - 卡片背景
    'bg_hover': '#334155',       # Slate 700 - 悬停背景
    'text_primary': '#f1f5f9',   # Slate 100 - 主文本
    'text_secondary': '#94a3b8', # Slate 400 - 次文本
    'border': '#334155',         # Slate 700 - 边框色
    'success': '#22c55e',        # Green 500 - 成功色
    'danger': '#ef4444',         # Red 500 - 危险色
    'warning': '#f59e0b',       # Amber 500 - 警告色
    'info': '#3b82f6',           # Blue 500 - 信息色
}


class FletGUI:
    """
    JMComic Flet 图形界面主类

    提供现代化的用户界面，支持：
    - 批量下载专辑
    - Kavita CBZ 打包
    - 配置管理
    - 实时日志显示
    """

    def __init__(self) -> None:
        """初始化 GUI 组件"""
        self.page: Optional[ft.Page] = None
        self.download_thread: Optional[threading.Thread] = None
        self.download_queue: List[str] = []
        self.download_results: dict = {}
        self.is_downloading: bool = False
        self.nav_index: int = 0

        # 初始化 UI 组件
        self._init_components()

    def _init_components(self) -> None:
        """初始化所有 UI 组件"""
        # ===================== 输入组件 =====================

        # 专辑ID输入框
        self.album_ids_text = ft.TextField(
            label="专辑ID",
            hint_text="输入专辑ID，每行一个",
            multiline=True,
            min_lines=6,
            border_color=THEME['border'],
            focused_border_color=THEME['primary'],
            text_style=ft.TextStyle(color=THEME['text_primary']),
            hint_style=ft.TextStyle(color=THEME['text_secondary']),
            label_style=ft.TextStyle(color=THEME['text_secondary']),
        )

        # 并发线程数滑块
        self.thread_count = ft.Slider(
            min=1,
            max=20,
            divisions=19,
            value=5,
            label="{value}",
            active_color=THEME['primary'],
        )

        # 源目录输入框
        self.source_dir = ft.TextField(
            label="源目录",
            hint_text="选择包含专辑子目录的源目录",
            border_color=THEME['border'],
            focused_border_color=THEME['primary'],
            text_style=ft.TextStyle(color=THEME['text_primary']),
            hint_style=ft.TextStyle(color=THEME['text_secondary']),
            label_style=ft.TextStyle(color=THEME['text_secondary']),
        )

        # 输出目录输入框
        self.output_dir = ft.TextField(
            label="输出目录",
            hint_text="CBZ文件输出目录",
            border_color=THEME['border'],
            focused_border_color=THEME['primary'],
            text_style=ft.TextStyle(color=THEME['text_primary']),
            hint_style=ft.TextStyle(color=THEME['text_secondary']),
            label_style=ft.TextStyle(color=THEME['text_secondary']),
        )

        # 覆盖复选框
        self.overwrite = ft.Checkbox(
            label="覆盖已存在的CBZ文件",
            value=True,
            fill_color=THEME['primary'],
            check_color=ft.Colors.WHITE,
            label_style=ft.TextStyle(color=THEME['text_primary']),
        )

        # 下载路径输入框
        self.download_path = ft.TextField(
            label="下载路径",
            value=str(Path.home() / 'Downloads' / 'JMComic'),
            border_color=THEME['border'],
            focused_border_color=THEME['primary'],
            text_style=ft.TextStyle(color=THEME['text_primary']),
            hint_style=ft.TextStyle(color=THEME['text_secondary']),
            label_style=ft.TextStyle(color=THEME['text_secondary']),
        )

        # 图片格式下拉框
        self.image_format = ft.Dropdown(
            label="图片格式",
            options=[
                ft.DropdownOption(".jpg"),
                ft.DropdownOption(".png"),
                ft.DropdownOption(".webp"),
            ],
            value=".jpg",
            border_color=THEME['border'],
            focused_border_color=THEME['primary'],
            text_style=ft.TextStyle(color=THEME['text_primary']),
            label_style=ft.TextStyle(color=THEME['text_secondary']),
        )

        # 客户端类型下拉框
        # 注意: 实际的 client_key 是 "html" (网页端) 和 "api" (移动端)
        self.client_type = ft.Dropdown(
            label="客户端类型",
            options=[
                ft.DropdownOption("html", "网页端"),
                ft.DropdownOption("api", "移动端"),
            ],
            value="html",
            border_color=THEME['border'],
            focused_border_color=THEME['primary'],
            text_style=ft.TextStyle(color=THEME['text_primary']),
            label_style=ft.TextStyle(color=THEME['text_secondary']),
        )

        # ===================== 日志组件 =====================

        # 日志列表
        self.log_list = ft.ListView(
            expand=True,
            spacing=8,
            padding=15,
        )

    # ===================== 界面构建方法 =====================

    def build(self, page: ft.Page) -> None:
        """
        构建主界面

        Args:
            page: Flet 页面对象
        """
        self.page = page

        # 页面基础设置
        page.title = "JMComic 下载器 v2.7.0"
        page.window_width = 1400
        page.window_height = 900
        page.window_min_width = 1200
        page.window_min_height = 800
        page.theme = ft.Theme(color_scheme_seed=THEME['primary'])
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = THEME['bg_dark']
        page.padding = 0

        # 构建主容器
        main_content = ft.Row(
            [
                self._build_sidebar(),
                ft.VerticalDivider(width=1, color=THEME['border']),
                ft.Column(
                    [
                        self._build_header(),
                        ft.Divider(height=1, color=THEME['border']),
                        ft.Container(
                            content=self._build_content_area(),
                            expand=True,
                        ),
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        )

        page.add(main_content)

        # 加载已保存的设置
        self._load_settings()

    def _build_sidebar(self) -> ft.Container:
        """
        构建侧边栏导航

        Returns:
            侧边栏容器
        """
        nav_items = [
            self._nav_item("下载", 0, ft.icons.Icons.DOWNLOAD),
            self._nav_item("Kavita", 1, ft.icons.Icons.ARTICLE),
            self._nav_item("设置", 2, ft.icons.Icons.SETTINGS),
            self._nav_item("关于", 3, ft.icons.Icons.INFO),
        ]

        return ft.Container(
            content=ft.Column(
                [
                    # Logo 区域
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.Icons.BOOK, size=40, color=THEME['primary']),
                                ft.Text(
                                    "JMComic",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=THEME['text_primary'],
                                ),
                                ft.Text(
                                    "v2.7.0",
                                    size=12,
                                    color=THEME['text_secondary'],
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        padding=25,
                    ),
                    ft.Divider(height=1, color=THEME['border']),
                    # 导航项
                    ft.Column(
                        nav_items,
                        spacing=8,
                    ),
                    ft.Container(expand=True),
                    # 底部信息
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.Icons.CODE, size=18, color=THEME['text_secondary']),
                                ft.Text(
                                    "开源项目",
                                    size=11,
                                    color=THEME['text_secondary'],
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        padding=25,
                    ),
                ],
            ),
            width=260,
            bgcolor=THEME['bg_card'],
        )

    def _nav_item(self, text: str, index: int, icon) -> ft.Container:
        """
        构建导航项

        Args:
            text: 导航文本
            index: 导航索引
            icon: 图标

        Returns:
            导航项容器
        """
        def on_click(e):
            """导航项点击事件"""
            self.nav_index = index
            self._update_content_area()

        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=22, color=THEME['text_primary']),
                    ft.Text(
                        text,
                        size=14,
                        color=THEME['text_primary'],
                    ),
                ],
                spacing=12,
            ),
            padding=ft.padding.symmetric(horizontal=22, vertical=14),
            border_radius=10,
            margin=ft.margin.symmetric(horizontal=12),
            on_click=on_click,
        )

    def _build_header(self) -> ft.Container:
        """
        构建顶部标题栏

        Returns:
            标题栏容器
        """
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        self._get_page_title(),
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=THEME['text_primary'],
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        ft.icons.Icons.REFRESH,
                        icon_color=THEME['text_secondary'],
                        tooltip="刷新",
                    ),
                ],
            ),
            padding=22,
        )

    def _get_page_title(self) -> str:
        """
        获取当前页面标题

        Returns:
            页面标题
        """
        titles = ["下载管理", "Kavita 打包", "设置", "关于"]
        return titles[self.nav_index] if self.nav_index < len(titles) else "未知"

    def _build_content_area(self) -> ft.Control:
        """
        构建内容区域

        Returns:
            内容区域控件
        """
        if self.nav_index == 0:
            return self._build_download_page()
        elif self.nav_index == 1:
            return self._build_kavita_page()
        elif self.nav_index == 2:
            return self._build_settings_page()
        else:
            return self._build_about_page()

    def _update_content_area(self) -> None:
        """更新内容区域"""
        self.page.clean()
        self.build(self.page)
        self.page.update()

    def _build_download_page(self) -> ft.Column:
        """
        构建下载页面

        Returns:
            下载页面列容器
        """
        return ft.Column(
            [
                ft.Row(
                    [
                        # 左侧控制面板
                        ft.Container(
                            content=ft.Column(
                                [
                                    # 专辑ID输入卡片
                                    self._build_card(
                                        "专辑ID",
                                        ft.Column(
                                            [
                                                self.album_ids_text,
                                                ft.Row(
                                                    [
                                                        ft.ElevatedButton(
                                                            "粘贴",
                                                            icon=ft.icons.Icons.CONTENT_PASTE,
                                                            bgcolor=THEME['bg_hover'],
                                                            color=THEME['text_primary'],
                                                            on_click=self._paste_album_ids,
                                                        ),
                                                        ft.ElevatedButton(
                                                            "清空",
                                                            icon=ft.icons.Icons.DELETE,
                                                            bgcolor=THEME['bg_hover'],
                                                            color=THEME['text_primary'],
                                                            on_click=self._clear_album_ids,
                                                        ),
                                                    ],
                                                    spacing=12,
                                                ),
                                            ],
                                            spacing=12,
                                        ),
                                    ),
                                    # 下载选项卡片
                                    self._build_card(
                                        "下载选项",
                                        ft.Column(
                                            [
                                                ft.Text("并发线程数:", color=THEME['text_primary']),
                                                self.thread_count,
                                            ],
                                            spacing=12,
                                        ),
                                    ),
                                    # 操作按钮区域
                                    ft.Column(
                                        [
                                            ft.ElevatedButton(
                                                "开始下载",
                                                icon=ft.icons.Icons.DOWNLOAD,
                                                bgcolor=THEME['primary'],
                                                color=ft.Colors.WHITE,
                                                style=ft.ButtonStyle(
                                                    shape=ft.RoundedRectangleBorder(radius=10),
                                                    padding=12,
                                                ),
                                                on_click=self._start_download,
                                                height=50,
                                            ),
                                            ft.ElevatedButton(
                                                "停止下载",
                                                icon=ft.icons.Icons.STOP,
                                                bgcolor=THEME['danger'],
                                                color=ft.Colors.WHITE,
                                                style=ft.ButtonStyle(
                                                    shape=ft.RoundedRectangleBorder(radius=10),
                                                    padding=12,
                                                ),
                                                on_click=self._stop_download,
                                                height=50,
                                            ),
                                        ],
                                        spacing=12,
                                    ),
                                ],
                                spacing=18,
                            ),
                            width=420,
                            padding=22,
                        ),
                        # 右侧日志区域
                        ft.Container(
                            content=self._build_log_card("下载日志"),
                            expand=True,
                            padding=22,
                        ),
                    ],
                    expand=True,
                ),
            ],
        )

    def _build_kavita_page(self) -> ft.Column:
        """
        构建 Kavita 打包页面

        Returns:
            Kavita 页面列容器
        """
        return ft.Column(
            [
                ft.Row(
                    [
                        # 左侧控制面板
                        ft.Container(
                            content=ft.Column(
                                [
                                    # 功能说明卡片
                                    self._build_card(
                                        "功能说明",
                                        ft.Text(
                                            "实现一键转化为CBZ格式，方便阅读",
                                            color=THEME['text_secondary'],
                                            size=14,
                                        ),
                                    ),
                                    # 源目录卡片
                                    self._build_card(
                                        "源目录",
                                        ft.Column(
                                            [
                                                self.source_dir,
                                                ft.ElevatedButton(
                                                    "浏览",
                                                    icon=ft.icons.Icons.FOLDER_OPEN,
                                                    bgcolor=THEME['primary'],
                                                    color=ft.Colors.WHITE,
                                                    style=ft.ButtonStyle(
                                                        shape=ft.RoundedRectangleBorder(radius=8),
                                                        padding=12,
                                                    ),
                                                    on_click=self._select_source_dir,
                                                    height=45,
                                                ),
                                            ],
                                            spacing=12,
                                        ),
                                    ),
                                    # 输出目录卡片
                                    self._build_card(
                                        "输出目录",
                                        ft.Column(
                                            [
                                                self.output_dir,
                                                ft.ElevatedButton(
                                                    "浏览",
                                                    icon=ft.icons.Icons.FOLDER_OPEN,
                                                    bgcolor=THEME['primary'],
                                                    color=ft.Colors.WHITE,
                                                    style=ft.ButtonStyle(
                                                        shape=ft.RoundedRectangleBorder(radius=8),
                                                        padding=12,
                                                    ),
                                                    on_click=self._select_output_dir,
                                                    height=45,
                                                ),
                                            ],
                                            spacing=12,
                                        ),
                                    ),
                                    # 选项卡片
                                    self._build_card(
                                        "选项",
                                        self.overwrite,
                                    ),
                                    # 按钮区域
                                    ft.Column(
                                        [
                                            # 打包按钮
                                            ft.ElevatedButton(
                                                "开始打包",
                                                icon=ft.icons.Icons.INVENTORY_2,
                                                bgcolor=THEME['secondary'],
                                                color=ft.Colors.WHITE,
                                                style=ft.ButtonStyle(
                                                    shape=ft.RoundedRectangleBorder(radius=10),
                                                    padding=12,
                                                ),
                                                on_click=self._start_kavita_pack,
                                                height=50,
                                            ),
                                            # 保存设置按钮
                                            ft.ElevatedButton(
                                                "保存设置",
                                                icon=ft.icons.Icons.SAVE,
                                                bgcolor=THEME['primary'],
                                                color=ft.Colors.WHITE,
                                                style=ft.ButtonStyle(
                                                    shape=ft.RoundedRectangleBorder(radius=10),
                                                    padding=12,
                                                ),
                                                on_click=self._save_settings,
                                                height=50,
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                ],
                                spacing=18,
                            ),
                            width=420,
                            padding=22,
                        ),
                        # 右侧日志区域
                        ft.Container(
                            content=self._build_log_card("打包日志"),
                            expand=True,
                            padding=22,
                        ),
                    ],
                    expand=True,
                ),
            ],
        )

    def _build_settings_page(self) -> ft.Column:
        """
        构建设置页面

        Returns:
            设置页面列容器
        """
        return ft.Column(
            [
                self._build_card(
                    "下载设置",
                    ft.Column(
                        [
                            # 下载路径 + 浏览按钮
                            ft.Column(
                                [
                                    self.download_path,
                                    ft.ElevatedButton(
                                        "浏览",
                                        icon=ft.icons.Icons.FOLDER_OPEN,
                                        bgcolor=THEME['primary'],
                                        color=ft.Colors.WHITE,
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            padding=12,
                                        ),
                                        on_click=self._select_download_dir,
                                        height=45,
                                    ),
                                ],
                                spacing=12,
                            ),
                            ft.Container(height=12),
                            self.image_format,
                            ft.Container(height=12),
                            self.client_type,
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "保存设置",
                                icon=ft.icons.Icons.SAVE,
                                bgcolor=THEME['primary'],
                                color=ft.Colors.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    padding=12,
                                ),
                                on_click=self._save_settings,
                                height=50,
                            ),
                        ],
                        spacing=8,
                    ),
                ),
            ],
        )

    def _build_about_page(self) -> ft.Column:
        """
        构建关于页面

        Returns:
            关于页面列容器
        """
        return ft.Column(
            [
                self._build_card(
                    "关于",
                    ft.Column(
                        [
                            ft.Container(
                                content=ft.Icon(
                                    ft.icons.Icons.BOOK,
                                    size=72,
                                    color=THEME['primary'],
                                ),
                                padding=25,
                            ),
                            ft.Text(
                                "JMComic 下载器",
                                size=26,
                                weight=ft.FontWeight.BOLD,
                                color=THEME['text_primary'],
                            ),
                            ft.Text(
                                "版本: 2.7.0",
                                size=16,
                                color=THEME['text_secondary'],
                            ),
                            ft.Divider(height=25, color=THEME['border']),
                            ft.Text(
                                "功能特性",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=THEME['text_primary'],
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "• 批量下载 JM 漫画\n"
                                    "• 自动 CBZ 打包\n"
                                    "• 多线程高速下载\n"
                                    "• 完整元数据保留\n"
                                    "• 现代化图形界面",
                                    color=THEME['text_secondary'],
                                    height=140,
                                ),
                                padding=ft.padding.symmetric(horizontal=20),
                            ),
                            ft.Divider(height=25, color=THEME['border']),
                            ft.Text(
                                "项目地址",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=THEME['text_primary'],
                            ),
                            ft.Text(
                                "github.com/hect0x7/JMComic-Crawler-Python",
                                color=THEME['text_secondary'],
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                ),
            ],
        )

    def _build_card(self, title: str, content) -> ft.Container:
        """
        构建通用卡片组件

        Args:
            title: 卡片标题
            content: 卡片内容

        Returns:
            卡片容器
        """
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        title,
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=THEME['text_primary'],
                    ),
                    ft.Divider(height=1, color=THEME['border']),
                    content,
                ],
                spacing=12,
            ),
            bgcolor=THEME['bg_card'],
            border_radius=14,
            padding=18,
        )

    def _build_log_card(self, title: str) -> ft.Container:
        """
        构建日志卡片（带复制按钮）

        Args:
            title: 卡片标题

        Returns:
            日志卡片容器
        """
        return ft.Container(
            content=ft.Column(
                [
                    # 标题栏
                    ft.Row(
                        [
                            ft.Text(
                                title,
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=THEME['text_primary'],
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                ft.icons.Icons.CONTENT_COPY,
                                icon_color=THEME['text_secondary'],
                                tooltip="复制所有日志",
                                on_click=self._copy_all_logs,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=1, color=THEME['border']),
                    # 日志内容
                    ft.Container(
                        content=self.log_list,
                        bgcolor=THEME['bg_dark'],
                        border_radius=10,
                        padding=12,
                    ),
                ],
                spacing=12,
            ),
            bgcolor=THEME['bg_card'],
            border_radius=14,
            padding=18,
        )

    # ===================== 事件处理方法 =====================

    def _copy_all_logs(self, e) -> None:
        """
        复制所有日志到剪贴板

        Args:
            e: Flet 事件对象
        """
        try:
            # 收集所有日志消息
            log_messages = []
            for log_item in self.log_list.controls:
                # 获取日志文本（Row中第二个元素是Text）
                if isinstance(log_item.content, ft.Row):
                    for control in log_item.content.controls:
                        if isinstance(control, ft.Text):
                            log_messages.append(control.value)
                            break

            all_logs = '\n'.join(log_messages)

            # 使用 tkinter 复制到剪贴板
            from tkinter import Tk
            root = Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(all_logs)
            root.update()
            root.destroy()

            self._log("所有日志已复制到剪贴板", "success")
        except Exception as ex:
            self._log(f"复制日志失败: {ex}", "error")

    def _paste_album_ids(self, e) -> None:
        """
        粘贴专辑ID

        Args:
            e: Flet 事件对象
        """
        try:
            from tkinter import Tk
            root = Tk()
            root.withdraw()
            text = root.clipboard_get()
            root.destroy()
            current = self.album_ids_text.value or ""
            self.album_ids_text.value = current + text
            self.page.update()
        except Exception:
            # 剪贴板访问失败，静默处理
            pass

    def _clear_album_ids(self, e) -> None:
        """
        清空专辑ID

        Args:
            e: Flet 事件对象
        """
        self.album_ids_text.value = ""
        self.page.update()

    def _select_source_dir(self, e) -> None:
        """
        选择源目录

        Args:
            e: Flet 事件对象
        """
        self._select_directory(self.source_dir, "选择源目录")

    def _select_output_dir(self, e) -> None:
        """
        选择输出目录

        Args:
            e: Flet 事件对象
        """
        self._select_directory(self.output_dir, "选择输出目录")

    def _select_download_dir(self, e) -> None:
        """
        选择下载路径

        Args:
            e: Flet 事件对象
        """
        self._select_directory(self.download_path, "选择下载路径")

    def _select_directory(self, field, title: str) -> None:
        """
        选择目录的通用方法

        Args:
            field: 目标输入框控件
            title: 对话框标题
        """
        try:
            from tkinter import Tk, filedialog
            root = Tk()
            root.withdraw()
            path = filedialog.askdirectory(title=title)
            root.destroy()
            if path:
                field.value = path
                self.page.update()
        except Exception:
            # 目录选择失败，静默处理
            pass

    def _load_settings(self) -> None:
        """
        从配置文件加载设置到UI组件
        """
        try:
            config_path = Path(__file__).parent.parent.parent / 'assets' / 'option' / 'gui_option.yml'

            if not config_path.exists():
                return

            # 尝试使用 yaml 加载
            try:
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            except ImportError:
                # 如果 yaml 不可用，使用 create_option_by_file
                from jmcomic import create_option_by_file
                option = create_option_by_file(str(config_path))
                config = {
                    'dir_rule': {'base_dir': option.dir_rule.base_dir},
                    'download': {
                        'image': {'suffix': option.download.image.suffix},
                        'threading': {
                            'image': option.download.threading.image,
                            'photo': option.download.threading.photo,
                        }
                    },
                    'client': {'impl': option.client.impl},
                }

            # 更新下载路径
            if 'dir_rule' in config and 'base_dir' in config['dir_rule']:
                self.download_path.value = config['dir_rule']['base_dir']

            # 更新图片格式
            if 'download' in config and 'image' in config['download'] and 'suffix' in config['download']['image']:
                suffix = config['download']['image']['suffix']
                if suffix in ['.jpg', '.png', '.webp']:
                    self.image_format.value = suffix

            # 更新客户端类型
            if 'client' in config and 'impl' in config['client']:
                impl = config['client']['impl']
                if impl in ['html', 'api']:
                    self.client_type.value = impl

            # 更新线程数
            if 'download' in config and 'threading' in config['download']:
                threading_config = config['download']['threading']
                if 'image' in threading_config:
                    try:
                        self.thread_count.value = float(threading_config['image'])
                    except (ValueError, TypeError):
                        pass

            # 更新页面（如果页面已初始化）
            if self.page:
                self.page.update()

            # 加载GUI特定设置
            self._load_gui_settings()
        except Exception as ex:
            # 加载失败时静默处理，使用默认值
            pass

    def _load_gui_settings(self) -> None:
        """
        加载GUI特定设置
        """
        try:
            gui_settings_path = Path(__file__).parent.parent.parent / 'assets' / 'option' / 'gui_settings.yml'

            if not gui_settings_path.exists():
                return

            import yaml
            with open(gui_settings_path, 'r', encoding='utf-8') as f:
                gui_settings = yaml.safe_load(f)

            # 加载Kavita打包设置
            if 'kavita' in gui_settings:
                kavita = gui_settings['kavita']
                if 'source_dir' in kavita:
                    self.source_dir.value = kavita['source_dir']
                if 'output_dir' in kavita:
                    self.output_dir.value = kavita['output_dir']
                if 'overwrite' in kavita:
                    self.overwrite.value = bool(kavita['overwrite'])

            # 更新页面（如果页面已初始化）
            if self.page:
                self.page.update()
        except Exception:
            # 加载失败时静默处理
            pass

    def _save_settings(self, e) -> None:
        """
        保存设置到配置文件

        Args:
            e: Flet 事件对象
        """
        try:
            option = JmModuleConfig.option_class().default()

            # 设置基础目录
            download_path = self.download_path.value
            os.makedirs(download_path, exist_ok=True)
            option.dir_rule.base_dir = download_path

            # 设置图片格式
            option.download.image.suffix = self.image_format.value

            # 设置客户端类型
            option.client.impl = self.client_type.value

            # 设置线程数
            option.download.threading.photo = int(self.thread_count.value)
            option.download.threading.image = int(self.thread_count.value)

            # 保存到文件
            config_path = Path(__file__).parent.parent.parent / 'assets' / 'option' / 'gui_option.yml'
            os.makedirs(config_path.parent, exist_ok=True)
            option.to_file(str(config_path))

            # 保存GUI特定设置
            try:
                import yaml
                gui_settings = {
                    'kavita': {
                        'source_dir': self.source_dir.value or '',
                        'output_dir': self.output_dir.value or '',
                        'overwrite': self.overwrite.value,
                    }
                }
                gui_settings_path = Path(__file__).parent.parent.parent / 'assets' / 'option' / 'gui_settings.yml'
                with open(gui_settings_path, 'w', encoding='utf-8') as f:
                    yaml.dump(gui_settings, f, allow_unicode=True, default_flow_style=False)
            except Exception as gui_ex:
                # GUI设置保存失败不影响主流程
                pass

            self._log("设置已保存", "success")
        except Exception as ex:
            self._log(f"保存设置失败: {ex}", "error")

    def _start_download(self, e) -> None:
        """
        开始下载专辑

        Args:
            e: Flet 事件对象
        """
        # 检查是否已有下载任务
        if self.is_downloading:
            self._log("已有下载任务正在进行中", "warning")
            return

        # 获取并验证专辑ID
        album_ids_text = self.album_ids_text.value or ""
        if not album_ids_text:
            self._log("请输入专辑ID", "warning")
            return

        # 解析专辑ID列表 (支持 JM123 和 123 两种格式)
        album_ids = []
        for line in album_ids_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.upper().startswith('JM'):
                line = line[2:]
            if line.isdigit():
                album_ids.append(line)
            else:
                self._log(f"跳过无效ID: {line}", "warning")
        
        if not album_ids:
            self._log("没有有效的专辑ID", "warning")
            return

        # 开始下载
        self.is_downloading = True
        self._log(f"开始下载 {len(album_ids)} 个专辑...", "info")

        def download_task():
            """下载任务线程函数"""
            try:
                option = self._load_or_create_option()
                total = len(album_ids)

                # 逐个下载专辑
                for idx, album_id in enumerate(album_ids, 1):
                    if not self.is_downloading:
                        break

                    self._log(f"开始下载专辑: {album_id}", "info")
                    self._update_progress(idx, total, f"下载中: {album_id}")

                    try:
                        album, downloader = download_album(album_id, option)
                        self.download_results[album_id] = {'success': True, 'album': album}
                        self._log(f"专辑 {album_id} 下载完成", "success")

                    except Exception as ex:
                        self.download_results[album_id] = {'success': False, 'error': str(ex)}
                        self._log(f"专辑 {album_id} 下载失败: {ex}", "error")

                # 下载完成
                success_count = sum(1 for r in self.download_results.values() if r.get('success'))
                self._log(f"下载完成！成功: {success_count}/{total}", "success")
                self._update_progress(total, total, "完成")

            except Exception as ex:
                self._log(f"下载线程错误: {ex}", "error")
            finally:
                self.is_downloading = False

        # 启动下载线程
        self.download_thread = threading.Thread(target=download_task)
        self.download_thread.daemon = True
        self.download_thread.start()

    def _stop_download(self, e) -> None:
        """
        停止下载任务

        Args:
            e: Flet 事件对象
        """
        if self.is_downloading:
            self.is_downloading = False
            self._log("正在停止下载...", "warning")

    def _start_kavita_pack(self, e) -> None:
        """
        开始 Kavita CBZ 打包

        Args:
            e: Flet 事件对象
        """
        # 检查是否已有任务
        if self.is_downloading:
            self._log("已有任务正在进行中", "warning")
            return

        # 获取并验证目录
        source_dir = self.source_dir.value
        output_dir = self.output_dir.value

        if not source_dir or not output_dir:
            self._log("请选择源目录和输出目录", "warning")
            return

        if not Path(source_dir).exists():
            self._log("源目录不存在", "error")
            return

        # 开始打包
        self.is_downloading = True
        self._log("开始打包Kavita CBZ文件...", "info")
        self._update_progress(0, 1, "准备中...")

        def pack_task():
            """打包任务线程函数"""
            try:
                stats = pack_albums_to_kavita(source_dir, output_dir, self.overwrite.value)
                self._log(
                    f"打包完成！成功: {stats['success']}, "
                    f"失败: {stats['failed']}, 总计: {stats['total']}",
                    "success"
                )
                self._update_progress(1, 1, "完成")

            except Exception as ex:
                self._log(f"打包线程错误: {ex}", "error")
            finally:
                self.is_downloading = False

        # 启动打包线程
        self.download_thread = threading.Thread(target=pack_task)
        self.download_thread.daemon = True
        self.download_thread.start()

    def _load_or_create_option(self):
        """
        加载或创建配置对象

        Returns:
            配置对象
        """
        config_path = Path(__file__).parent.parent.parent / 'assets' / 'option' / 'gui_option.yml'

        # 如果配置文件存在则加载
        if config_path.exists():
            from jmcomic import create_option_by_file
            option = create_option_by_file(str(config_path))
        else:
            # 否则创建默认配置
            option = JmModuleConfig.option_class().default()
            download_path = self.download_path.value
            os.makedirs(download_path, exist_ok=True)
            option.dir_rule.base_dir = download_path
            option.download.image.suffix = self.image_format.value
            option.client.impl = self.client_type.value
            option.download.threading.photo = int(self.thread_count.value)
            option.download.threading.image = int(self.thread_count.value)

        # 始终使用 GUI 中选择的客户端类型（覆盖配置文件中的值）
        option.client.impl = self.client_type.value
        option.download.threading.photo = int(self.thread_count.value)
        option.download.threading.image = int(self.thread_count.value)

        return option

    def _log(self, message: str, level: str = "info") -> None:
        """
        添加日志到日志列表

        Args:
            message: 日志消息
            level: 日志级别 (info/success/warning/error)
        """
        # 日志级别对应的颜色和图标
        colors = {
            'info': THEME['info'],
            'success': THEME['success'],
            'warning': THEME['warning'],
            'error': THEME['danger'],
        }

        icons = {
            'info': ft.icons.Icons.INFO,
            'success': ft.icons.Icons.CHECK_CIRCLE,
            'warning': ft.icons.Icons.WARNING,
            'error': ft.icons.Icons.ERROR,
        }

        # 生成时间戳
        timestamp = time.strftime('%H:%M:%S')

        # 创建日志项
        log_item = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        icons.get(level, ft.icons.Icons.INFO),
                        size=18,
                        color=colors.get(level, THEME['info'])
                    ),
                    ft.Text(
                        f"[{timestamp}] {message}",
                        size=13,
                        color=THEME['text_primary'],
                    ),
                ],
                spacing=10,
            ),
            bgcolor=THEME['bg_card'],
            border_radius=6,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
        )

        # 添加到日志列表
        self.log_list.controls.append(log_item)
        self.page.update()

    def _update_progress(self, current: int, total: int, text: str = "") -> None:
        """
        更新进度条和状态（已禁用，保留方法签名以保持兼容性）

        Args:
            current: 当前进度
            total: 总进度
            text: 状态文本
        """
        # 进度条已从界面中移除，此方法保留为空操作
        pass


def main():
    """
    主函数 - 启动 Flet 应用

    使用 Flet 的应用入口点，创建并显示 GUI 界面。
    """
    app = FletGUI()

    ft.app(
        target=app.build,
        assets_dir="assets",
    )


if __name__ == '__main__':
    main()

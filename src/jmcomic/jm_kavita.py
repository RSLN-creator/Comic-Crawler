"""
JMComic Kavita 打包模块
将下载的漫画打包为CBZ格式，并生成ComicInfo.xml元数据
"""

import os
import re
import json
import zipfile
from pathlib import Path
from typing import List, Dict, Optional, Union
from xml.etree.ElementTree import Element, SubElement
from xml.dom import minidom

from common import *
from .jm_config import JmModuleConfig, jm_log


class KavitaConfig:
    """Kavita打包配置"""

    def __init__(self, overwrite: bool = True, compress_level: int = 1):
        """
        :param overwrite: 是否覆盖已存在的CBZ文件
        :param compress_level: 压缩级别 (0-9)，1为最快，9为最小体积
        """
        self.overwrite = overwrite
        self.compress_level = compress_level


def prettify_xml(elem: Element) -> bytes:
    """格式化XML输出"""
    from xml.etree.ElementTree import tostring
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    xml_lines = []
    for line in reparsed.toprettyxml(indent="  ").split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('<?xml'):
            xml_lines.append(line)
    return '\n'.join(xml_lines).encode('utf-8')


def load_metadata_json(album_dir: Path) -> Dict:
    """
    读取metadata.json文件（全量加载，不丢失任何字段）

    :param album_dir: 专辑目录路径
    :return: 元数据字典
    """
    metadata_path = album_dir / 'metadata.json'

    default_metadata = {
        'album_id': '',
        'name': album_dir.name,
        'description': '',
        'authors': [],
        'actors': [],
        'tags': [],
        'works': [],
        'page_count': 0,
        'pub_date': '',
        'update_date': '',
        'likes': '',
        'views': '',
        'comment_count': 0,
    }

    if not metadata_path.exists():
        jm_log('kavita', f'未找到metadata.json，使用默认值: {album_dir}')
        return default_metadata

    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            loaded_metadata = json.load(f)
        if not isinstance(loaded_metadata, dict):
            raise ValueError("非字典格式")

        # 全量合并，不过滤任何字段
        default_metadata.update(loaded_metadata)
        # 确保列表字段类型正确
        for key in ['authors', 'actors', 'tags', 'works']:
            if not isinstance(default_metadata[key], list):
                default_metadata[key] = [str(default_metadata[key]).strip()] if str(default_metadata[key]).strip() else []

        jm_log('kavita', f'成功读取元数据: {metadata_path}')
        return default_metadata
    except Exception as e:
        jm_log('kavita', f'读取metadata失败 ({str(e)[:50]})，使用默认值')
        return default_metadata


def generate_comicinfo_xml(metadata: Dict, album_detail: Optional['JmAlbumDetail'] = None) -> bytes:
    """
    全量写入元数据到ComicInfo.xml（无字段过滤，确保所有信息都写入）

    :param metadata: 元数据字典
    :param album_detail: 可选的专辑详情对象
    :return: XML字节内容
    """
    root = Element("ComicInfo")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")

    title = str(metadata.get('name', 'Unknown')).strip() or 'Unknown'
    album_id = str(metadata.get('album_id', '')).strip()

    chapter_number = metadata.get('chapter_number', 1)
    total_chapters = metadata.get('total_chapters', 1)

    SubElement(root, "Series").text = title
    SubElement(root, "Title").text = f"{title} - Ch.{chapter_number}"
    SubElement(root, "Manga").text = "YesAndRightToLeft"
    SubElement(root, "Number").text = str(chapter_number)
    SubElement(root, "Volume").text = "1"
    if total_chapters > 1:
        SubElement(root, "Count").text = str(total_chapters)

    page_count = str(metadata.get('page_count', '')).strip()
    if page_count and page_count.isdigit():
        SubElement(root, "PageCount").text = page_count

    # 作者信息
    authors = [str(a).strip() for a in metadata.get('authors', []) if str(a).strip()]
    if authors:
        authors_str = ", ".join(authors)
        SubElement(root, "Writer").text = authors_str
        SubElement(root, "Artist").text = authors_str

    # 人物角色
    actors = [str(a).strip() for a in metadata.get('actors', []) if str(a).strip()]
    if actors:
        actors_str = ", ".join(actors)
        SubElement(root, "Characters").text = actors_str

    # 标签/分类
    tags = [str(t).strip() for t in metadata.get('tags', []) if str(t).strip()]
    if tags:
        tags_str = ", ".join(tags)
        SubElement(root, "Genre").text = tags_str

    # 作品系列
    works = [str(w).strip() for w in metadata.get('works', []) if str(w).strip()]
    if works:
        works_str = ", ".join(works)
        SubElement(root, "SeriesGroup").text = works_str

    # 描述信息
    description = str(metadata.get('description', '')).strip()
    if description:
        SubElement(root, "Summary").text = description

    # 出版日期
    pub_date = str(metadata.get('pub_date', '')).strip()
    if len(pub_date) >= 4:
        year_str = pub_date[:4]
        if year_str.isdigit():
            SubElement(root, "Year").text = year_str
    if len(pub_date) >= 7:
        month_str = pub_date[5:7]
        if month_str.isdigit() and 1 <= int(month_str) <= 12:
            SubElement(root, "Month").text = month_str

    # 固定信息
    SubElement(root, "LanguageISO").text = "zh"
    SubElement(root, "Format").text = "CBZ"
    SubElement(root, "FileType").text = "WebP"
    SubElement(root, "Publisher").text = "JMComic"
    SubElement(root, "Imprint").text = "禁漫天堂"

    # 统计与ID信息
    comments_parts = []
    if album_id:
        comments_parts.append(f"JMComic Album ID: {album_id}")
    likes = str(metadata.get('likes', '')).strip()
    if likes:
        comments_parts.append(f"Likes: {likes}")
    views = str(metadata.get('views', '')).strip()
    if views:
        comments_parts.append(f"Views: {views}")
    comment_count = str(metadata.get('comment_count', '')).strip()
    if comment_count and comment_count.isdigit():
        comments_parts.append(f"Comments: {comment_count}")

    if comments_parts:
        SubElement(root, "Comments").text = " ".join(comments_parts)

    return prettify_xml(root)


def clean_series_name(raw_name: str) -> str:
    """
    清理系列名（移除非法字符）

    :param raw_name: 原始名称
    :return: 清理后的名称
    """
    if not raw_name:
        return f"Unknown_{hash(os.urandom(4)) & 0xffffffff:x}"
    clean = re.sub(r'[<>:"|?*]', '_', raw_name)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean[:50]


def natural_sort_key(filename: str) -> List:
    """
    自然排序键（确保图片顺序正确）

    :param filename: 文件名
    :return: 排序键列表
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]


def extract_chapter_number(folder_name: str) -> tuple:
    """
    从文件夹名提取章节号用于排序

    :param folder_name: 文件夹名
    :return: (章节号, 原始名称) 用于排序
    """
    match = re.search(r'第?(\d+)[话章集]', folder_name)
    if match:
        return (int(match.group(1)), folder_name.lower())
    all_digits = re.findall(r'(\d+)', folder_name)
    if all_digits:
        return (int(all_digits[-1]), folder_name.lower())
    return (999999, folder_name.lower())


def find_all_images(folder: Path) -> List[Path]:
    """
    查找目录下所有图片文件，按章节和页码正确排序

    :param folder: 目录路径
    :return: 图片文件路径列表
    """
    img_extensions = {'.webp', '.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    images = []
    for item in folder.rglob('*'):
        if item.is_file() and item.suffix.lower() in img_extensions:
            images.append(item)
    images.sort(key=lambda x: (
        extract_chapter_number(x.parent.name),
        natural_sort_key(x.name)
    ))
    return images


class KavitaPacker:
    """Kavita CBZ打包器"""

    def __init__(self, config: Optional[KavitaConfig] = None):
        """
        :param config: 打包配置
        """
        self.config = config or KavitaConfig()

    def _find_chapter_dirs(self, album_dir: Path, metadata: Dict = None) -> List[tuple]:
        """
        查找章节目录（包含图片的子目录）
        优先使用元数据中的章节索引信息进行排序

        :param album_dir: 专辑目录
        :param metadata: 元数据字典（可选）
        :return: [(章节号, 章节目录路径)] 列表
        """
        img_extensions = {'.webp', '.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        chapters = []
        dir_list = []

        for item in album_dir.iterdir():
            if item.is_dir():
                has_images = any(
                    f.suffix.lower() in img_extensions
                    for f in item.iterdir()
                    if f.is_file()
                )
                if has_images:
                    dir_list.append(item)

        if metadata and 'episodes' in metadata and len(metadata['episodes']) == len(dir_list):
            jm_log('kavita', f'[META] 使用元数据章节信息排序')
            episodes = metadata['episodes']
            for item in dir_list:
                matched = False
                for ep in episodes:
                    ep_name = ep.get('name', '')
                    ep_index = ep.get('index', 0)
                    ep_sort = ep.get('sort', ep_index)
                    ep_indextitle = ep.get('indextitle', '')
                    
                    if ep_name and ep_name in item.name:
                        chapters.append((ep_sort, item))
                        matched = True
                        break
                    if ep_indextitle and ep_indextitle in item.name:
                        chapters.append((ep_sort, item))
                        matched = True
                        break
                
                if not matched:
                    chapter_num = self._extract_chapter_number(item.name)
                    chapters.append((chapter_num, item))
        else:
            for item in dir_list:
                chapter_num = self._extract_chapter_number(item.name)
                chapters.append((chapter_num, item))

        chapters.sort(key=lambda x: x[0])
        return chapters

    def _extract_chapter_number(self, folder_name: str) -> float:
        """
        从文件夹名提取章节号

        :param folder_name: 文件夹名
        :return: 章节号（支持小数如 12.1, 12.2）
        """
        match = re.search(r'第?(\d+(?:\.\d+)?)[话章集]', folder_name)
        if match:
            return float(match.group(1))
        
        match = re.search(r'\b[pP]\s+(\d+(?:[\.\-]\d+)?)', folder_name)
        if match:
            num_str = match.group(1).replace('-', '.')
            return float(num_str)
        
        match = re.search(r'\s+(\d+(?:[\.\-]\d+)?)\s*$', folder_name)
        if match:
            num_str = match.group(1).replace('-', '.')
            return float(num_str)
        
        match = re.search(r'~(\d+)年', folder_name)
        if match:
            return 1.0
        
        all_digits = re.findall(r'(\d+)', folder_name)
        if all_digits:
            last_num = float(all_digits[-1])
            if last_num > 100:
                return 1.0
            return last_num
        
        return 1.0

    def pack_album(self,
                   album_dir: Union[str, Path],
                   output_dir: Union[str, Path],
                   album_detail: Optional['JmAlbumDetail'] = None) -> List[Path]:
        """
        打包单个专辑为CBZ
        - 多章节专辑：每个章节单独打包，Kavita识别为一卷多章
        - 单章节专辑：直接打包

        :param album_dir: 专辑源目录
        :param output_dir: 输出目录
        :param album_detail: 可选的专辑详情对象
        :return: 生成的CBZ文件路径列表
        """
        album_dir = Path(album_dir)
        output_dir = Path(output_dir)
        result_paths = []

        if not album_dir.exists():
            jm_log('kavita', f'专辑目录不存在: {album_dir}')
            return result_paths

        metadata = load_metadata_json(album_dir)
        if album_detail is not None:
            metadata.update({
                'album_id': album_detail.album_id,
                'name': album_detail.name,
                'description': album_detail.description,
                'authors': album_detail.authors,
                'actors': album_detail.actors,
                'tags': album_detail.tags,
                'works': album_detail.works,
                'page_count': album_detail.page_count,
                'pub_date': album_detail.pub_date,
                'update_date': album_detail.update_date,
                'likes': album_detail.likes,
                'views': album_detail.views,
                'comment_count': album_detail.comment_count,
                'episode_count': len(album_detail.episode_list) if hasattr(album_detail, 'episode_list') else 1,
            })

        series_name = clean_series_name(metadata['name'])
        series_output_dir = output_dir / series_name
        series_output_dir.mkdir(parents=True, exist_ok=True)

        chapter_dirs = self._find_chapter_dirs(album_dir, metadata)

        if len(chapter_dirs) > 1:
            jm_log('kavita', f'[INFO] 检测到多章节专辑，共 {len(chapter_dirs)} 章')
            total_chapters = len(chapter_dirs)
            for idx, (chapter_num, chapter_dir) in enumerate(chapter_dirs):
                chapter_metadata = metadata.copy()
                chapter_metadata['chapter_number'] = idx + 1
                chapter_metadata['total_chapters'] = total_chapters

                cbz_path = self._pack_chapter(
                    chapter_dir, series_output_dir, series_name,
                    idx + 1, total_chapters, chapter_metadata, album_detail
                )
                if cbz_path:
                    result_paths.append(cbz_path)
        else:
            jm_log('kavita', f'[INFO] 单章节专辑，直接打包')
            all_images = find_all_images(album_dir)
            if not all_images:
                jm_log('kavita', f'[ERROR] 未找到任何图片，跳过: {album_dir}')
                return result_paths

            metadata['chapter_number'] = 1
            metadata['total_chapters'] = 1

            cbz_name = re.sub(r'[<>:"|?*]', '_', f"{series_name}_c001.cbz")
            cbz_path = series_output_dir / cbz_name

            if cbz_path.exists() and not self.config.overwrite:
                jm_log('kavita', f'CBZ已存在，跳过: {cbz_path}')
                return [cbz_path]

            try:
                xml_bytes = generate_comicinfo_xml(metadata, album_detail)
                with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED,
                                   compresslevel=self.config.compress_level) as zf:
                    zf.writestr("ComicInfo.xml", xml_bytes)
                    for img_idx, img in enumerate(all_images):
                        new_img_name = f"{img_idx + 1:03d}{img.suffix.lower()}"
                        zf.write(img, arcname=new_img_name)

                jm_log('kavita', f'[SUCCESS] 成功生成: {cbz_path.name}')
                result_paths.append(cbz_path)
            except Exception as e:
                jm_log('kavita', f'[ERROR] 打包失败: {str(e)[:100]}')
                if cbz_path.exists():
                    cbz_path.unlink(missing_ok=True)

        return result_paths

    def _pack_chapter(self,
                      chapter_dir: Path,
                      output_dir: Path,
                      series_name: str,
                      chapter_num: int,
                      total_chapters: int,
                      metadata: Dict,
                      album_detail: Optional['JmAlbumDetail'] = None) -> Optional[Path]:
        """
        打包单个章节

        :param chapter_dir: 章节目录
        :param output_dir: 输出目录
        :param series_name: 系列名
        :param chapter_num: 章节号
        :param total_chapters: 总章节数
        :param metadata: 元数据
        :param album_detail: 专辑详情
        :return: CBZ文件路径
        """
        img_extensions = {'.webp', '.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        images = []
        for item in chapter_dir.iterdir():
            if item.is_file() and item.suffix.lower() in img_extensions:
                images.append(item)
        images.sort(key=lambda x: natural_sort_key(x.name))

        if not images:
            jm_log('kavita', f'[WARN] 章节无图片: {chapter_dir}')
            return None

        cbz_name = re.sub(r'[<>:"|?*]', '_', f"{series_name}_c{chapter_num:03d}.cbz")
        cbz_path = output_dir / cbz_name

        if cbz_path.exists() and not self.config.overwrite:
            jm_log('kavita', f'CBZ已存在，跳过: {cbz_path}')
            return cbz_path

        try:
            xml_bytes = generate_comicinfo_xml(metadata, album_detail)
            with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED,
                               compresslevel=self.config.compress_level) as zf:
                zf.writestr("ComicInfo.xml", xml_bytes)
                for img_idx, img in enumerate(images):
                    new_img_name = f"{img_idx + 1:03d}{img.suffix.lower()}"
                    zf.write(img, arcname=new_img_name)

            jm_log('kavita', f'[SUCCESS] 章节{chapter_num}/{total_chapters}: {cbz_path.name} ({len(images)}张)')
            return cbz_path
        except Exception as e:
            jm_log('kavita', f'[ERROR] 章节打包失败: {str(e)[:100]}')
            if cbz_path.exists():
                cbz_path.unlink(missing_ok=True)
            return None

    def pack_from_album_detail(self,
                               album_detail: 'JmAlbumDetail',
                               source_dir: Union[str, Path],
                               output_dir: Union[str, Path]) -> List[Path]:
        """
        使用专辑详情对象打包

        :param album_detail: 专辑详情对象
        :param source_dir: 源下载目录
        :param output_dir: 输出目录
        :return: 生成的CBZ文件路径
        """
        source_dir = Path(source_dir)

        # 方法1：尝试通过metadata.json查找专辑目录
        album_dir = self.find_album_dir_by_metadata(source_dir, album_detail.album_id)
        if album_dir is not None:
            jm_log('kavita', f'通过metadata.json找到专辑目录: {album_dir}')
            return self.pack_album(album_dir, output_dir, album_detail)

        # 方法2：尝试专辑ID目录
        album_dir = source_dir / str(album_detail.album_id)
        if album_dir.exists():
            jm_log('kavita', f'使用专辑ID目录: {album_dir}')
            return self.pack_album(album_dir, output_dir, album_detail)

        # 方法3：尝试专辑名称目录（使用与DirRule相同的规范化逻辑）
        from .jm_option import fix_windir_name
        from .jm_toolkit import JmcomicText
        # 注意：这里无法获取normalize_zh配置，假设为None
        album_name = fix_windir_name(JmcomicText.to_zh(album_detail.name, None)).strip()
        album_dir = source_dir / album_name
        if album_dir.exists():
            jm_log('kavita', f'使用专辑名称目录: {album_dir}')
            return self.pack_album(album_dir, output_dir, album_detail)

        # 方法4：如果只有一个子目录，使用它
        subdirs = [item for item in source_dir.iterdir() if item.is_dir()]
        if len(subdirs) == 1:
            album_dir = subdirs[0]
            jm_log('kavita', f'使用唯一子目录: {album_dir}')
            return self.pack_album(album_dir, output_dir, album_detail)

        # 方法5：查找包含图片的子目录
        for item in source_dir.iterdir():
            if item.is_dir():
                # 检查是否包含图片文件
                images = find_all_images(item)
                if images:
                    album_dir = item
                    jm_log('kavita', f'使用包含图片的子目录: {album_dir}')
                    return self.pack_album(album_dir, output_dir, album_detail)

        jm_log('kavita', f'[ERROR] 无法找到专辑目录: {source_dir}')
        return []

    def find_album_dir_by_metadata(self, source_dir: Path, album_id: str) -> Optional[Path]:
        """
        通过metadata.json查找专辑目录
        """
        import json
        for item in source_dir.iterdir():
            if item.is_dir():
                metadata_path = item / 'metadata.json'
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        if metadata.get('album_id') == album_id:
                            return item
                    except:
                        continue
        return None


def pack_album_to_kavita(album_dir: Union[str, Path],
                        output_dir: Union[str, Path],
                        overwrite: bool = True,
                        compress_level: int = 1) -> List[Path]:
    """
    便捷函数：打包单个专辑为Kavita CBZ格式
    多章节专辑会分别打包为多个CBZ文件

    :param album_dir: 专辑源目录
    :param output_dir: 输出目录
    :param overwrite: 是否覆盖已存在的CBZ
    :param compress_level: 压缩级别
    :return: 生成的CBZ文件路径列表
    """
    config = KavitaConfig(overwrite=overwrite, compress_level=compress_level)
    packer = KavitaPacker(config)
    return packer.pack_album(album_dir, output_dir)


def pack_albums_to_kavita(source_dir: Union[str, Path],
                          output_dir: Union[str, Path],
                          overwrite: bool = True,
                          compress_level: int = 1) -> Dict[str, int]:
    """
    批量打包专辑为Kavita CBZ格式

    :param source_dir: 源目录（包含多个专辑子目录）
    :param output_dir: 输出目录
    :param overwrite: 是否覆盖已存在的CBZ
    :param compress_level: 压缩级别
    :return: 统计信息字典 {'success': 成功数, 'failed': 失败数, 'total': 总数}
    """
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)

    config = KavitaConfig(overwrite=overwrite, compress_level=compress_level)
    packer = KavitaPacker(config)

    album_dirs = sorted([d for d in source_dir.iterdir() if d.is_dir()], key=lambda x: x.name)

    stats = {'success': 0, 'failed': 0, 'total': len(album_dirs)}

    for album_dir in album_dirs:
        results = packer.pack_album(album_dir, output_dir)
        if results:
            stats['success'] += 1
        else:
            stats['failed'] += 1

    return stats

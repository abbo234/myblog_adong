from pathlib import Path
from datetime import datetime
import re
import shutil

# =========================
# 你需要修改的配置
# =========================

# 你的原始 Markdown 教程目录
SOURCE_DIR = Path(r"E:\Python爬虫流程控制_V2")

# 导入到 Hugo 的目标目录
DEST_DIR = Path(r"D:\HugoBlog\myblog\content\posts\python-crawler-workflow")

# 默认分类
BASE_CATEGORY = "爬虫与数据处理"

# 默认标签
DEFAULT_TAGS = ["Python", "爬虫", "数据处理"]

# 是否复制图片资源
COPY_IMAGE_ASSETS = True

# 允许复制的图片格式
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

# 第一次测试建议只处理 5 篇文章
# 测试没问题后，把 5 改成 None
TEST_LIMIT = 5


# =========================
# 工具函数
# =========================

def read_text_safely(path: Path) -> str:
    """尽量兼容 UTF-8 和常见中文编码。"""
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"无法读取文件编码：{path}")


def has_front_matter(text: str) -> bool:
    """判断文件顶部是否已有 Hugo Front Matter。"""
    s = text.lstrip("\ufeff\r\n\t ")

    if s.startswith("+++\n") or s.startswith("+++\r\n"):
        return "\n+++" in s[3:] or "\r\n+++" in s[3:]

    if s.startswith("---\n") or s.startswith("---\r\n"):
        return "\n---" in s[3:] or "\r\n---" in s[3:]

    return False


def toml_escape(value: str) -> str:
    """转义 TOML 字符串。"""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def toml_array(items):
    """生成 TOML 数组，并去重。"""
    result = []
    for item in items:
        item = str(item).strip()
        if item and item not in result:
            result.append(item)

    return "[" + ", ".join(f'"{toml_escape(x)}"' for x in result) + "]"


def clean_label(name: str) -> str:
    """
    清理文件夹名：
    例如 01_需求澄清与任务入口 -> 需求澄清与任务入口
    """
    name = name.strip()
    name = re.sub(r"^\d+[_\-\s]*", "", name)
    return name.strip()


def extract_title_from_markdown(text: str, file_path: Path) -> str:
    """
    优先使用 Markdown 一级标题作为 title。
    如果没有一级标题，就用文件名。
    """
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()

    title = file_path.stem
    title = re.sub(r"^\d+[_\-\s]*", "", title)
    title = title.replace("_", " ").replace("-", " ").strip()
    return title or file_path.stem


def extract_weight_from_filename(file_path: Path):
    """
    从文件名前缀提取排序权重。
    例如 030_客户原始需求如何转成爬虫任务.md -> weight = 30
    """
    match = re.match(r"^(\d+)", file_path.stem)
    if match:
        return int(match.group(1))
    return None


def build_front_matter(text: str, src_file: Path, rel_path: Path) -> str:
    title = extract_title_from_markdown(text, src_file)

    # 用文件修改时间作为发布时间
    date_value = datetime.fromtimestamp(src_file.stat().st_mtime).astimezone().isoformat(timespec="seconds")

    # 根据父级文件夹生成分类和标签
    folder_labels = [clean_label(part) for part in rel_path.parent.parts if clean_label(part)]

    categories = [BASE_CATEGORY]
    if folder_labels:
        categories.append(folder_labels[0])

    tags = DEFAULT_TAGS + folder_labels

    weight = extract_weight_from_filename(src_file)

    lines = [
        "+++",
        f'title = "{toml_escape(title)}"',
        f"date = {date_value}",
        "draft = false",
        f"tags = {toml_array(tags)}",
        f"categories = {toml_array(categories)}",
    ]

    if weight is not None:
        lines.append(f"weight = {weight}")

    lines.append("+++")

    return "\n".join(lines) + "\n\n"


# =========================
# 主流程
# =========================

def main():
    if not SOURCE_DIR.exists():
        raise SystemExit(f"原始目录不存在：{SOURCE_DIR}")

    DEST_DIR.mkdir(parents=True, exist_ok=True)

    md_files = sorted(SOURCE_DIR.rglob("*.md"))

    if TEST_LIMIT is not None:
        md_files = md_files[:TEST_LIMIT]

    added_front_matter_count = 0
    already_has_front_matter_count = 0
    copied_md_count = 0
    copied_asset_count = 0

    for src_file in md_files:
        rel_path = src_file.relative_to(SOURCE_DIR)
        dest_file = DEST_DIR / rel_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        text = read_text_safely(src_file)

        if has_front_matter(text):
            output_text = text
            already_has_front_matter_count += 1
        else:
            front_matter = build_front_matter(text, src_file, rel_path)
            output_text = front_matter + text.lstrip("\ufeff")
            added_front_matter_count += 1

        dest_file.write_text(output_text, encoding="utf-8")
        copied_md_count += 1

    # 只有正式全量导入时，才复制图片资源
    if COPY_IMAGE_ASSETS and TEST_LIMIT is None:
        for src_file in SOURCE_DIR.rglob("*"):
            if src_file.is_file() and src_file.suffix.lower() in IMAGE_EXTS:
                rel_path = src_file.relative_to(SOURCE_DIR)
                dest_file = DEST_DIR / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)
                copied_asset_count += 1

    print("导入完成")
    print(f"Markdown 文件数量：{copied_md_count}")
    print(f"新增 Front Matter：{added_front_matter_count}")
    print(f"已有 Front Matter，未重复添加：{already_has_front_matter_count}")
    print(f"复制图片资源数量：{copied_asset_count}")
    print(f"目标目录：{DEST_DIR}")


if __name__ == "__main__":
    main()
from pathlib import Path
from datetime import datetime
import re
import shutil
import sys


# ============================================================
# 0. 输出编码处理：减少 VS Code / Code Runner 中文乱码
# ============================================================

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


# ============================================================
# 1. 基础配置：主要修改这里
# ============================================================

# 原始 Obsidian Markdown 教程目录
SOURCE_DIR = Path(r"E:\Obsidian\Pro_01\02_Learning\Python爬虫流程控制_V2\阶段04网页数据来源判断")

# Hugo 文章导入目标目录
DEST_DIR = Path(r"D:\HugoBlog\myblog\content\posts\python-crawler-workflow")

# 默认分类
BASE_CATEGORY = "爬虫与数据处理"

# 默认标签
DEFAULT_TAGS = ["Python", "爬虫", "数据处理"]

# 是否复制图片资源
COPY_IMAGE_ASSETS = True

# 允许复制的图片格式
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

# 当前是修复模式，建议直接全量处理
# 如果你想先测试，可以改成 20
TEST_LIMIT = None

# 如果目标文件已经存在，是否覆盖
# 这次需要覆盖，因为之前导入的副本有 Front Matter 解析问题
OVERWRITE_EXISTING = True

# 是否统一重新生成 Hugo Front Matter
# 建议保持 True
FORCE_REGENERATE_HUGO_FRONT_MATTER = True

# 是否剥离原文顶部已有的 Obsidian/YAML/TOML Front Matter
# 建议保持 True，否则博客正文可能会显示原来的 metadata
STRIP_EXISTING_SOURCE_FRONT_MATTER = True

# 是否清空目标目录后重新导入
# 默认 False，更安全
# 如果你确认目标目录只存放这批导入文章，可以改成 True
CLEAN_DEST_BEFORE_IMPORT = False


# ============================================================
# 2. 忽略规则
# ============================================================

IGNORE_HIDDEN_DIRS = True
IGNORE_HIDDEN_FILES = True

IGNORE_DIR_NAMES = {
    ".obsidian",
    ".git",
    ".trash",
    ".vscode",
    ".idea",
    "__pycache__",
    "node_modules",
}

IGNORE_FILE_NAMES = {
    ".DS_Store",
    "Thumbs.db",
}

IGNORE_FILE_PREFIXES = (
    "~$",
)

# 常见 Front Matter 字段，用于判断 --- 块到底是不是元数据
COMMON_FRONT_MATTER_KEYS = {
    "title",
    "date",
    "draft",
    "tags",
    "categories",
    "category",
    "description",
    "summary",
    "slug",
    "url",
    "aliases",
    "weight",
    "author",
    "authors",
    "lastmod",
    "created",
    "updated",
    "publishdate",
    "expirydate",
    "layout",
    "type",
}


# ============================================================
# 3. 路径与文件工具
# ============================================================

def is_relative_to(child: Path, parent: Path) -> bool:
    """兼容性判断：child 是否位于 parent 下面。"""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def is_ignored_path(rel_path: Path) -> bool:
    """
    判断某个相对路径是否应该被忽略。
    rel_path 必须是相对于 SOURCE_DIR 的路径。
    """

    parts = rel_path.parts

    # 忽略隐藏目录，例如 .obsidian、.git
    if IGNORE_HIDDEN_DIRS:
        for part in parts[:-1]:
            if part.startswith("."):
                return True

    # 忽略指定目录
    for part in parts[:-1]:
        if part in IGNORE_DIR_NAMES:
            return True

    # 忽略隐藏文件
    if IGNORE_HIDDEN_FILES and rel_path.name.startswith("."):
        return True

    # 忽略指定文件
    if rel_path.name in IGNORE_FILE_NAMES:
        return True

    # 忽略临时文件
    if rel_path.name.startswith(IGNORE_FILE_PREFIXES):
        return True

    return False


def read_text_safely(path: Path) -> str:
    """
    尽量兼容 UTF-8 和常见中文编码。
    Obsidian 默认通常是 UTF-8。
    """

    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue

    raise RuntimeError(f"无法读取文件编码：{path}")


def toml_escape(value: str) -> str:
    """转义 TOML 字符串。"""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def toml_array(items) -> str:
    """生成 TOML 数组，并去重。"""

    result = []

    for item in items:
        item = str(item).strip()
        if item and item not in result:
            result.append(item)

    return "[" + ", ".join(f'"{toml_escape(x)}"' for x in result) + "]"


def clean_label(name: str) -> str:
    """
    清理文件夹名，用于生成 tags/categories。

    示例：
    01_需求澄清与任务入口 -> 需求澄清与任务入口
    030_客户原始需求 -> 客户原始需求
    """

    name = name.strip()
    name = re.sub(r"^\d+[_\-\s]*", "", name)
    return name.strip()


# ============================================================
# 4. Front Matter 处理
# ============================================================

def get_top_delimited_block(text: str):
    """
    获取文件顶部的 --- 或 +++ 包裹块。

    返回：
    {
        "delimiter": "---" or "+++",
        "block": 中间内容,
        "body": 去掉该块后的正文
    }

    如果文件顶部没有这种块，返回 None。

    注意：
    这里只是提取，不代表这个块一定是合法 Front Matter。
    """

    text = text.lstrip("\ufeff")

    lines = text.splitlines(keepends=True)

    if not lines:
        return None

    first_line = lines[0].strip()

    if first_line not in {"---", "+++"}:
        return None

    delimiter = first_line

    # 只在前 120 行内找结束符，避免误判超长正文
    max_scan_lines = min(len(lines), 120)

    for i in range(1, max_scan_lines):
        if lines[i].strip() == delimiter:
            block = "".join(lines[1:i])
            body = "".join(lines[i + 1:])
            return {
                "delimiter": delimiter,
                "block": block,
                "body": body,
            }

    return None


def is_plausible_front_matter_block(block: str, delimiter: str) -> bool:
    """
    判断顶部 --- / +++ 块是否像真正的 Front Matter。

    核心目的：
    - 合法 Obsidian/YAML/TOML 元数据：剥离
    - 普通 Markdown 分割线和正文：不要误删
    """

    if not block.strip():
        return False

    # 如果出现 Markdown 标题，大概率不是纯元数据
    if re.search(r"^\s*#{1,6}\s+", block, flags=re.MULTILINE):
        return False

    # TOML Front Matter：常见形式是 key = value
    if delimiter == "+++":
        toml_key_lines = re.findall(
            r"^\s*([A-Za-z_][A-Za-z0-9_\-]*)\s*=",
            block,
            flags=re.MULTILINE,
        )
        if not toml_key_lines:
            return False

        lower_keys = {k.lower() for k in toml_key_lines}
        if lower_keys & COMMON_FRONT_MATTER_KEYS:
            return True

        return len(toml_key_lines) >= 2

    # YAML Front Matter：常见形式是 key: value
    if delimiter == "---":
        yaml_key_lines = re.findall(
            r"^\s*([A-Za-z_][A-Za-z0-9_\-]*)\s*:",
            block,
            flags=re.MULTILINE,
        )

        if not yaml_key_lines:
            return False

        lower_keys = {k.lower() for k in yaml_key_lines}

        # 有常见元数据字段，认为是 Front Matter
        if lower_keys & COMMON_FRONT_MATTER_KEYS:
            return True

        # 至少两个英文 key，也比较像元数据
        if len(yaml_key_lines) >= 2:
            return True

    return False


def extract_simple_meta_from_block(block: str, delimiter: str) -> dict:
    """
    从已有 Front Matter 中提取少量字段。
    目前主要提取 title，避免已有标题丢失。
    不做复杂 YAML/TOML 完整解析，降低依赖。
    """

    meta = {}

    if delimiter == "---":
        title_match = re.search(
            r'^\s*title\s*:\s*(.+?)\s*$',
            block,
            flags=re.MULTILINE | re.IGNORECASE,
        )
    else:
        title_match = re.search(
            r'^\s*title\s*=\s*(.+?)\s*$',
            block,
            flags=re.MULTILINE | re.IGNORECASE,
        )

    if title_match:
        raw_title = title_match.group(1).strip()
        raw_title = raw_title.strip('"').strip("'").strip()
        if raw_title:
            meta["title"] = raw_title

    return meta


def normalize_source_markdown(text: str):
    """
    处理原始 Markdown：

    1. 如果顶部是可信的 Obsidian/YAML/TOML Front Matter：
       - 提取 title 等少量信息
       - 从正文中剥离这个块
    2. 如果顶部只是普通 --- 分割线：
       - 不剥离，保留正文
    """

    text = text.lstrip("\ufeff")

    if not STRIP_EXISTING_SOURCE_FRONT_MATTER:
        return text, {}, False

    top_block = get_top_delimited_block(text)

    if not top_block:
        return text, {}, False

    delimiter = top_block["delimiter"]
    block = top_block["block"]
    body = top_block["body"]

    if not is_plausible_front_matter_block(block, delimiter):
        return text, {}, False

    meta = extract_simple_meta_from_block(block, delimiter)

    return body.lstrip("\r\n"), meta, True


# ============================================================
# 5. 标题、排序、分类生成
# ============================================================

def extract_title_from_markdown(body_text: str, file_path: Path, source_meta: dict) -> str:
    """
    标题优先级：

    1. 原有 Front Matter 里的 title
    2. 正文里的一级标题
    3. 文件名
    """

    meta_title = source_meta.get("title")

    if meta_title:
        return meta_title.strip()

    for line in body_text.splitlines():
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

    示例：
    030_客户原始需求如何转成爬虫任务.md -> weight = 30
    """

    match = re.match(r"^(\d+)", file_path.stem)

    if match:
        return int(match.group(1))

    return None


def build_hugo_front_matter(body_text: str, src_file: Path, rel_path: Path, source_meta: dict) -> str:
    """
    生成 Hugo TOML Front Matter。
    """

    title = extract_title_from_markdown(body_text, src_file, source_meta)

    # 用原文件最后修改时间作为发布时间
    # 生成 TOML 可识别的 datetime
    date_value = (
        datetime
        .fromtimestamp(src_file.stat().st_mtime)
        .astimezone()
        .isoformat(timespec="seconds")
    )

    # 根据父级文件夹生成标签
    folder_labels = [
        clean_label(part)
        for part in rel_path.parent.parts
        if clean_label(part)
    ]

    # categories 不宜过多，保持博客分类干净
    categories = [BASE_CATEGORY]

    if folder_labels:
        categories.append(folder_labels[0])

    # tags 可以更细，用于保留原来的目录信息
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


# ============================================================
# 6. 文件收集与资源复制
# ============================================================

def collect_markdown_files():
    """
    收集需要导入的 Markdown 文件，并过滤掉 .obsidian 等目录。
    """

    all_md_files = sorted(SOURCE_DIR.rglob("*.md"))

    valid_md_files = []

    for path in all_md_files:
        rel_path = path.relative_to(SOURCE_DIR)

        if is_ignored_path(rel_path):
            continue

        valid_md_files.append(path)

    ignored_count = len(all_md_files) - len(valid_md_files)

    if TEST_LIMIT is not None:
        valid_md_files = valid_md_files[:TEST_LIMIT]

    return valid_md_files, ignored_count, len(all_md_files)


def copy_image_assets():
    """
    复制图片资源。

    注意：
    这里只复制图片文件，不自动修复 Obsidian 的 ![[图片.png]] 语法。
    """

    copied_asset_count = 0
    ignored_asset_count = 0

    if not COPY_IMAGE_ASSETS:
        return copied_asset_count, ignored_asset_count

    for src_file in SOURCE_DIR.rglob("*"):
        if not src_file.is_file():
            continue

        rel_path = src_file.relative_to(SOURCE_DIR)

        if is_ignored_path(rel_path):
            ignored_asset_count += 1
            continue

        if src_file.suffix.lower() not in IMAGE_EXTS:
            continue

        dest_file = DEST_DIR / rel_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        if dest_file.exists() and not OVERWRITE_EXISTING:
            continue

        shutil.copy2(src_file, dest_file)
        copied_asset_count += 1

    return copied_asset_count, ignored_asset_count


# ============================================================
# 7. 安全检查
# ============================================================

def safety_check():
    """
    防止明显危险的路径配置。
    """

    if not SOURCE_DIR.exists():
        raise SystemExit(f"原始目录不存在：{SOURCE_DIR}")

    if SOURCE_DIR.resolve() == DEST_DIR.resolve():
        raise SystemExit("危险：SOURCE_DIR 和 DEST_DIR 不能是同一个目录。")

    if is_relative_to(DEST_DIR, SOURCE_DIR):
        raise SystemExit("危险：DEST_DIR 不能放在 SOURCE_DIR 里面，否则可能重复导入。")

    if is_relative_to(SOURCE_DIR, DEST_DIR):
        raise SystemExit("危险：SOURCE_DIR 不能放在 DEST_DIR 里面。")


def clean_destination_dir():
    """
    可选：清空目标目录。
    默认不启用，避免误删。
    """

    if not CLEAN_DEST_BEFORE_IMPORT:
        return

    if DEST_DIR.exists():
        shutil.rmtree(DEST_DIR)

    DEST_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 8. 主流程
# ============================================================

def main():
    print("=" * 70)
    print("Obsidian Markdown -> Hugo posts 导入脚本")
    print("=" * 70)
    print(f"原始目录：{SOURCE_DIR}")
    print(f"目标目录：{DEST_DIR}")
    print(f"测试限制：{TEST_LIMIT}")
    print(f"覆盖已有文件：{OVERWRITE_EXISTING}")
    print(f"统一生成 Hugo Front Matter：{FORCE_REGENERATE_HUGO_FRONT_MATTER}")
    print(f"剥离原文 Front Matter：{STRIP_EXISTING_SOURCE_FRONT_MATTER}")
    print("=" * 70)

    safety_check()
    clean_destination_dir()

    DEST_DIR.mkdir(parents=True, exist_ok=True)

    md_files, ignored_md_count, all_md_count = collect_markdown_files()

    copied_md_count = 0
    skipped_existing_count = 0
    stripped_source_fm_count = 0
    generated_hugo_fm_count = 0
    error_count = 0
    error_records = []

    for src_file in md_files:
        rel_path = src_file.relative_to(SOURCE_DIR)
        dest_file = DEST_DIR / rel_path

        try:
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            if dest_file.exists() and not OVERWRITE_EXISTING:
                skipped_existing_count += 1
                continue

            raw_text = read_text_safely(src_file)

            body_text, source_meta, stripped = normalize_source_markdown(raw_text)

            if stripped:
                stripped_source_fm_count += 1

            # 关键策略：
            # 不信任原始 Obsidian 文档的 --- 块。
            # 导入到 Hugo 的副本，一律使用自己生成的 TOML Front Matter。
            if FORCE_REGENERATE_HUGO_FRONT_MATTER:
                hugo_front_matter = build_hugo_front_matter(
                    body_text=body_text,
                    src_file=src_file,
                    rel_path=rel_path,
                    source_meta=source_meta,
                )
                output_text = hugo_front_matter + body_text.lstrip("\ufeff")
                generated_hugo_fm_count += 1
            else:
                output_text = raw_text.lstrip("\ufeff")

            dest_file.write_text(output_text, encoding="utf-8", newline="\n")
            copied_md_count += 1

        except Exception as e:
            error_count += 1
            error_records.append((str(src_file), str(e)))

    copied_asset_count = 0
    ignored_asset_count = 0

    # 全量模式才复制图片资源
    if TEST_LIMIT is None:
        copied_asset_count, ignored_asset_count = copy_image_assets()

    print("=" * 70)
    print("导入完成")
    print("=" * 70)
    print(f"原始 Markdown 总数：{all_md_count}")
    print(f"已忽略 Markdown 数量：{ignored_md_count}")
    print(f"本次实际处理 Markdown 数量：{len(md_files)}")
    print(f"复制 Markdown 数量：{copied_md_count}")
    print(f"跳过已存在文件数量：{skipped_existing_count}")
    print(f"剥离原文 Front Matter 数量：{stripped_source_fm_count}")
    print(f"生成 Hugo Front Matter 数量：{generated_hugo_fm_count}")
    print(f"复制图片资源数量：{copied_asset_count}")
    print(f"已忽略资源文件数量：{ignored_asset_count}")
    print(f"错误数量：{error_count}")
    print(f"原始目录：{SOURCE_DIR}")
    print(f"目标目录：{DEST_DIR}")
    print("=" * 70)

    if error_records:
        print("以下文件处理失败：")
        for file_path, error_msg in error_records[:20]:
            print(f"- {file_path}")
            print(f"  错误：{error_msg}")

        if len(error_records) > 20:
            print(f"还有 {len(error_records) - 20} 个错误未显示。")

    if TEST_LIMIT is not None:
        print("当前是测试模式。确认本地预览正常后，把 TEST_LIMIT 改成 None 再全量导入。")

    print("下一步建议：运行 hugo 检查构建是否通过。")


if __name__ == "__main__":
    main()
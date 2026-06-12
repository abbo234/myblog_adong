from pathlib import Path
from datetime import datetime
import re
import shutil
import sys


# ============================================================
# 0. 输出编码处理：减少 PowerShell / VS Code 中文乱码
# ============================================================

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


# ============================================================
# 1. 基础配置：主要改这里
# ============================================================

# 你的 Obsidian 笔记根目录
# 改成你真实的“随记”所在目录
SOURCE_DIR = Path(r"E:\Obsidian\Pro_03\article")

# 导入到 Hugo 的目标目录
# 建议随记统一放到 content/posts/notes
DEST_DIR = Path(r"D:\HugoBlog\myblog\content\posts\notes")

# 只导入这些相对路径
# 可以写文件，也可以写文件夹
#
# 示例 1：只导入一个文件
# INCLUDE_RELATIVE_PATHS = [
#     "随记/今天的想法.md",
# ]
#
# 示例 2：导入一个文件夹
# INCLUDE_RELATIVE_PATHS = [
#     "随记",
# ]
#
# 示例 3：导入多个文件或文件夹
# INCLUDE_RELATIVE_PATHS = [
#     "随记",
#     "临时笔记/AI感想.md",
# ]
#
# 如果留空 []，就会导入 SOURCE_DIR 下所有 .md，不推荐
INCLUDE_RELATIVE_PATHS = [
    ".",
]

# 博客分类
BASE_CATEGORY = "随记"

# 默认标签
DEFAULT_TAGS = ["随记"]

# 是否根据文件夹自动生成标签
AUTO_TAGS_FROM_FOLDERS = True

# 是否复制图片资源
COPY_IMAGE_ASSETS = True

# 允许复制的图片格式
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

# 测试模式：先只处理前 5 篇
# 确认没问题后改成 None
TEST_LIMIT = 5

# 如果目标文件已经存在，是否覆盖
OVERWRITE_EXISTING = True

# 是否统一重新生成 Hugo Front Matter
FORCE_REGENERATE_HUGO_FRONT_MATTER = True

# 是否剥离原文顶部已有的 Obsidian/YAML/TOML Front Matter
STRIP_EXISTING_SOURCE_FRONT_MATTER = True

# 是否清空目标目录后重新导入
# 默认 False，避免误删
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
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def normalize_rel_path(path_text: str) -> Path:
    """
    统一处理 Windows / Obsidian 路径写法。
    """
    return Path(path_text.replace("/", "\\"))


def is_ignored_path(rel_path: Path) -> bool:
    parts = rel_path.parts

    if IGNORE_HIDDEN_DIRS:
        for part in parts[:-1]:
            if part.startswith("."):
                return True

    for part in parts[:-1]:
        if part in IGNORE_DIR_NAMES:
            return True

    if IGNORE_HIDDEN_FILES and rel_path.name.startswith("."):
        return True

    if rel_path.name in IGNORE_FILE_NAMES:
        return True

    if rel_path.name.startswith(IGNORE_FILE_PREFIXES):
        return True

    return False


def read_text_safely(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue

    raise RuntimeError(f"无法读取文件编码：{path}")


def toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def toml_array(items) -> str:
    result = []

    for item in items:
        item = str(item).strip()
        if item and item not in result:
            result.append(item)

    return "[" + ", ".join(f'"{toml_escape(x)}"' for x in result) + "]"


def clean_label(name: str) -> str:
    name = name.strip()
    name = re.sub(r"^\d+[_\-\s]*", "", name)
    return name.strip()


def make_safe_slug_from_filename(file_path: Path) -> str:
    """
    生成一个简单 slug。
    中文标题也可以发布，但 URL 不好看。
    这里不强制英文 slug，避免乱改。
    """
    stem = file_path.stem.strip()
    stem = re.sub(r"^\d+[_\-\s]*", "", stem)
    stem = stem.replace(" ", "-")
    return stem


# ============================================================
# 4. Front Matter 处理
# ============================================================

def get_top_delimited_block(text: str):
    text = text.lstrip("\ufeff")
    lines = text.splitlines(keepends=True)

    if not lines:
        return None

    first_line = lines[0].strip()

    if first_line not in {"---", "+++"}:
        return None

    delimiter = first_line
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
    if not block.strip():
        return False

    # 如果块里有 Markdown 标题，大概率不是元数据
    if re.search(r"^\s*#{1,6}\s+", block, flags=re.MULTILINE):
        return False

    if delimiter == "+++":
        keys = re.findall(
            r"^\s*([A-Za-z_][A-Za-z0-9_\-]*)\s*=",
            block,
            flags=re.MULTILINE,
        )
    else:
        keys = re.findall(
            r"^\s*([A-Za-z_][A-Za-z0-9_\-]*)\s*:",
            block,
            flags=re.MULTILINE,
        )

    if not keys:
        return False

    lower_keys = {k.lower() for k in keys}

    if lower_keys & COMMON_FRONT_MATTER_KEYS:
        return True

    return len(keys) >= 2


def extract_simple_meta_from_block(block: str, delimiter: str) -> dict:
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
# 5. 标题、标签、Front Matter 生成
# ============================================================

def extract_title_from_markdown(body_text: str, file_path: Path, source_meta: dict) -> str:
    if source_meta.get("title"):
        return source_meta["title"].strip()

    for line in body_text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()

    title = file_path.stem
    title = re.sub(r"^\d+[_\-\s]*", "", title)
    title = title.replace("_", " ").replace("-", " ").strip()

    return title or file_path.stem


def build_tags(rel_path: Path):
    tags = list(DEFAULT_TAGS)

    if AUTO_TAGS_FROM_FOLDERS:
        for part in rel_path.parent.parts:
            label = clean_label(part)
            if label:
                tags.append(label)

    return tags


def build_hugo_front_matter(body_text: str, src_file: Path, rel_path: Path, source_meta: dict) -> str:
    title = extract_title_from_markdown(body_text, src_file, source_meta)

    date_value = (
        datetime
        .fromtimestamp(src_file.stat().st_mtime)
        .astimezone()
        .isoformat(timespec="seconds")
    )

    tags = build_tags(rel_path)

    lines = [
        "+++",
        f'title = "{toml_escape(title)}"',
        f"date = {date_value}",
        "draft = false",
        f"tags = {toml_array(tags)}",
        f'categories = {toml_array([BASE_CATEGORY])}',
        "+++",
    ]

    return "\n".join(lines) + "\n\n"


# ============================================================
# 6. 文件收集
# ============================================================

def collect_markdown_files_from_include_paths():
    """
    根据 INCLUDE_RELATIVE_PATHS 收集 Markdown 文件。
    """

    if not INCLUDE_RELATIVE_PATHS:
        print("警告：INCLUDE_RELATIVE_PATHS 为空，将扫描 SOURCE_DIR 下所有 Markdown。")
        candidates = sorted(SOURCE_DIR.rglob("*.md"))
    else:
        candidates = []

        for item in INCLUDE_RELATIVE_PATHS:
            rel_item = normalize_rel_path(item)
            full_path = SOURCE_DIR / rel_item

            if not full_path.exists():
                print(f"警告：指定路径不存在，已跳过：{full_path}")
                continue

            if full_path.is_file():
                if full_path.suffix.lower() == ".md":
                    candidates.append(full_path)
                else:
                    print(f"警告：不是 Markdown 文件，已跳过：{full_path}")

            elif full_path.is_dir():
                candidates.extend(sorted(full_path.rglob("*.md")))

    valid_files = []
    ignored_count = 0

    for path in candidates:
        rel_path = path.relative_to(SOURCE_DIR)

        if is_ignored_path(rel_path):
            ignored_count += 1
            continue

        valid_files.append(path)

    # 去重并排序
    valid_files = sorted(set(valid_files))

    if TEST_LIMIT is not None:
        valid_files = valid_files[:TEST_LIMIT]

    return valid_files, ignored_count, len(candidates)


def get_included_root_dirs():
    """
    用于复制图片时缩小扫描范围。
    """
    roots = []

    if not INCLUDE_RELATIVE_PATHS:
        return [SOURCE_DIR]

    for item in INCLUDE_RELATIVE_PATHS:
        rel_item = normalize_rel_path(item)
        full_path = SOURCE_DIR / rel_item

        if full_path.exists():
            if full_path.is_file():
                roots.append(full_path.parent)
            else:
                roots.append(full_path)

    return roots


def copy_image_assets():
    copied_asset_count = 0
    ignored_asset_count = 0

    if not COPY_IMAGE_ASSETS:
        return copied_asset_count, ignored_asset_count

    roots = get_included_root_dirs()

    for root in roots:
        for src_file in root.rglob("*"):
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
    if not SOURCE_DIR.exists():
        raise SystemExit(f"原始目录不存在：{SOURCE_DIR}")

    if SOURCE_DIR.resolve() == DEST_DIR.resolve():
        raise SystemExit("危险：SOURCE_DIR 和 DEST_DIR 不能是同一个目录。")

    if is_relative_to(DEST_DIR, SOURCE_DIR):
        raise SystemExit("危险：DEST_DIR 不能放在 SOURCE_DIR 里面，否则可能重复导入。")

    if is_relative_to(SOURCE_DIR, DEST_DIR):
        raise SystemExit("危险：SOURCE_DIR 不能放在 DEST_DIR 里面。")


def clean_destination_dir():
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
    print("随记 Markdown -> Hugo posts 导入脚本")
    print("=" * 70)
    print(f"原始目录：{SOURCE_DIR}")
    print(f"目标目录：{DEST_DIR}")
    print(f"只导入这些路径：{INCLUDE_RELATIVE_PATHS}")
    print(f"测试限制：{TEST_LIMIT}")
    print(f"覆盖已有文件：{OVERWRITE_EXISTING}")
    print(f"分类：{BASE_CATEGORY}")
    print("=" * 70)

    safety_check()
    clean_destination_dir()

    DEST_DIR.mkdir(parents=True, exist_ok=True)

    md_files, ignored_md_count, candidate_count = collect_markdown_files_from_include_paths()

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
    print(f"候选 Markdown 数量：{candidate_count}")
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
        print("当前是测试模式，只处理部分文章。")
        print("确认本地预览正常后，把 TEST_LIMIT 改成 None 再全量导入。")

    print("下一步：运行 hugo 检查构建。")


if __name__ == "__main__":
    main()
import os
import sys

# 处理未安装 Pillow 的情况，避免直接崩溃
try:
    from PIL import Image
except ImportError:
    print("缺少 Pillow 库，请先安装：pip install Pillow")
    sys.exit(1)

# ========== 配置区域（相对当前 .py 文件） ==========
# 单文件模式：将 SINGLE_INPUT_FILE 设置为相对脚本的路径（例如 "images/source.png"）
# 批量模式：将 SINGLE_INPUT_FILE 设为 None，脚本会遍历 INPUT_DIR
SINGLE_INPUT_FILE = None

# 批量输入目录（相对脚本），仅在 SINGLE_INPUT_FILE 为 None 时生效
INPUT_DIR = "images"

# 输出目录（相对脚本）
OUTPUT_DIR = "icons"

# ICO 中嵌入的尺寸
ICON_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128)]
# ================================================


def script_dir() -> str:
    """返回当前脚本所在的绝对目录路径。"""
    return os.path.dirname(os.path.abspath(__file__))


def resolve_from_script(*parts) -> str:
    """将给定相对路径片段，严格基于脚本目录拼接为绝对路径。"""
    return os.path.abspath(os.path.join(script_dir(), *parts))


def ensure_dir(path: str) -> None:
    """若目录不存在则创建。"""
    os.makedirs(path, exist_ok=True)


def get_unique_filename(path: str) -> str:
    """避免重名冲突：若存在，则追加 (2), (3)..."""
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    counter = 2
    candidate = f"{base}({counter}){ext}"
    while os.path.exists(candidate):
        counter += 1
        candidate = f"{base}({counter}){ext}"
    return candidate


def save_as_ico(input_abs: str, output_abs: str, sizes: list[tuple[int, int]]) -> None:
    """将任意支持格式图片保存为 .ico，必要时取首帧并转 RGBA。"""
    try:
        img = Image.open(input_abs)

        # 若为动图（如 GIF），取首帧
        try:
            img.seek(0)
        except Exception:
            pass

        # 统一转为 RGBA（ICO 对透明度处理更稳定）
        img = img.convert("RGBA")

        # 创建输出目录
        ensure_dir(os.path.dirname(output_abs))

        # 写入 ICO（多尺寸）
        img.save(output_abs, format="ICO", sizes=sizes)
        print(f"[OK] {os.path.relpath(input_abs, script_dir())} -> {os.path.relpath(output_abs, script_dir())}")
    except Exception as e:
        print(f"[ERR] {os.path.relpath(input_abs, script_dir())}: {e}")


def convert_single(relative_input_path: str, relative_output_path: str, sizes: list[tuple[int, int]]) -> None:
    input_abs = resolve_from_script(relative_input_path)
    output_abs = resolve_from_script(relative_output_path)

    if not os.path.isfile(input_abs):
        print(f"[MISS] 找不到输入文件：{relative_input_path}")
        return

    # 统一输出为 .ico
    base_name = os.path.splitext(os.path.basename(input_abs))[0]
    output_abs = os.path.join(os.path.dirname(output_abs), base_name + ".ico")
    output_abs = get_unique_filename(output_abs)

    save_as_ico(input_abs, output_abs, sizes)


def convert_batch(relative_input_dir: str, relative_output_dir: str, sizes: list[tuple[int, int]]) -> None:
    input_dir_abs = resolve_from_script(relative_input_dir)
    output_dir_abs = resolve_from_script(relative_output_dir)

    if not os.path.isdir(input_dir_abs):
        print(f"[MISS] 找不到输入目录：{relative_input_dir}")
        return

    supported_exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp"}
    total, ok, err = 0, 0, 0

    for name in os.listdir(input_dir_abs):
        src_abs = os.path.join(input_dir_abs, name)

        # 跳过子目录，仅处理文件；跳过隐藏文件（以 . 开头）
        if not os.path.isfile(src_abs) or name.startswith("."):
            continue

        ext = os.path.splitext(name)[1].lower()
        if ext not in supported_exts:
            continue

        total += 1
        base = os.path.splitext(name)[0]
        dst_abs = os.path.join(output_dir_abs, base + ".ico")
        dst_abs = get_unique_filename(dst_abs)

        try:
            save_as_ico(src_abs, dst_abs, sizes)
            ok += 1
        except Exception:
            err += 1

    print(f"\n[SUMMARY] 总计: {total}, 成功: {ok}, 失败: {err}")
    print(f"[OUTPUT] {os.path.relpath(output_dir_abs, script_dir())}")


def main():
    # 输出目录准备
    ensure_dir(resolve_from_script(OUTPUT_DIR))

    if SINGLE_INPUT_FILE:
        # 单文件模式：输入是相对脚本路径；输出目录用 OUTPUT_DIR
        relative_input = SINGLE_INPUT_FILE
        relative_output_dir = OUTPUT_DIR
        convert_single(relative_input, relative_output_dir, ICON_SIZES)
    else:
        # 批量模式：遍历 INPUT_DIR，将所有支持格式转为 .ico 到 OUTPUT_DIR
        convert_batch(INPUT_DIR, OUTPUT_DIR, ICON_SIZES)


if __name__ == "__main__":
    main()

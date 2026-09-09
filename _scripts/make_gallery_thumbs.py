# -*- coding: utf-8 -*-
"""
make_gallery_thumbs.py — 首页 Gallery 照片缩略图生成脚本
=================================================================
用途
----
把 assets/images/photos/ 下的原始大图（3~9MB 相机/手机原图）批量缩小为
网页展示用小图，输出到 assets/images/gallery/（同名文件, 约 70~220KB/张）。

目录结构约定
------------
  assets/images/photos/  原图库(不直接上线, 供 Lightbox 点击放大查看)
  assets/images/gallery/ 列表小图(首页画廊加载这些; 点击缩略图后 Lightbox 加载 photos/ 原图)
  _showcase/*.md         画廊条目: image 字段指向 /assets/images/gallery/<同名>.jpg

为什么需要小图：
  首页画廊会逐张加载图片, 3~9MB 原图会让页面卡顿、浪费流量;
  画廊卡片最大显示宽度仅 ~300px, 900px 宽的小图肉眼无差别。
  高清原图通过点击缩略图的 Lightbox 浮层按需加载。

用法（在仓库根目录执行）
----------------------
  python _scripts/make_gallery_thumbs.py               # 默认 900px 宽, JPEG q82
  python _scripts/make_gallery_thumbs.py --width 1200  # 自定义宽度
  python _scripts/make_gallery_thumbs.py --force       # 忽略已有文件, 全部重新生成

幂等性
------
第二次运行会跳过已生成且不旧于源图的文件（输出 SKIP），可放心重复执行。
新照片流程: 原图放入 photos/ → 运行本脚本 → 在 _showcase/ 建/改 md 条目(image 指 gallery/)。

依赖: Pillow (pip install Pillow)
"""
import argparse
import os
import sys

from PIL import Image, ImageOps

# 仓库根目录 = 本脚本的上一级目录（脚本位于 <root>/_scripts/ 下）
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 原图目录：原始大图（不直接上线）
PHOTOS_DIR = os.path.join(ROOT, "assets", "images", "photos")
# 列表小图输出目录：Gallery 条目 image 字段指向这里（/assets/images/gallery/xxx.jpg）
GALLERY_DIR = os.path.join(ROOT, "assets", "images", "gallery")

# 支持的输入格式
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def make_thumbnail(src_path, dst_path, width, quality, force=False):
    """将 src_path 缩小为 dst_path。返回状态字符串，供打印。"""
    # 幂等检查：目标已存在、且不比源图旧 → 跳过（--force 可强制重做）
    if not force and os.path.exists(dst_path):
        if os.path.getmtime(dst_path) >= os.path.getmtime(src_path):
            return "SKIP (已存在)"
    im = Image.open(src_path)
    # 按 EXIF 方向信息自动摆正（手机竖拍照片常见，否则会横躺）
    im = ImageOps.exif_transpose(im)
    im = im.convert("RGB")
    # 只缩小、不放大：小图保持原始尺寸，避免无谓放大模糊
    if im.width > width:
        new_h = round(im.height * width / im.width)
        im = im.resize((width, new_h), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    # quality: JPEG 压缩质量(0-100)，82 在体积与画质间较平衡; optimize 进一步减体积
    im.save(dst_path, "JPEG", quality=quality, optimize=True)
    return "OK"


def main():
    ap = argparse.ArgumentParser(description="首页 Gallery 照片缩略图生成器")
    ap.add_argument("--width", type=int, default=900, help="小图最大宽度(px), 默认 900")
    ap.add_argument("--quality", type=int, default=82, help="JPEG 质量 1-100, 默认 82")
    ap.add_argument("--force", action="store_true", help="强制重新生成, 忽略已有小图")
    ap.add_argument("--photos", default=PHOTOS_DIR, help="原图目录, 默认 assets/images/photos")
    ap.add_argument("--output", default=GALLERY_DIR, help="输出目录, 默认 assets/images/gallery")
    args = ap.parse_args()

    if not os.path.isdir(args.photos):
        print(f"[错误] 原图目录不存在: {args.photos}")
        sys.exit(1)
    # 收集待处理照片（按文件名排序，输出顺序稳定）
    files = sorted(
        f for f in os.listdir(args.photos)
        if f.lower().endswith(IMAGE_EXTS) and not f.startswith(".")
    )
    if not files:
        print(f"[提示] {args.photos} 下没有图片文件")
        return

    print(f"[原图] {args.photos}")
    print(f"[输出] {args.output}  (宽度≤{args.width}px, JPEG q{args.quality})")
    print("-" * 60)
    total_before = total_after = 0
    for name in files:
        src = os.path.join(args.photos, name)
        # 保持原名与扩展名大小写（GitHub Pages/Linux 文件系统大小写敏感, .JPG 不能变成 .jpg）
        # 非 JPEG 格式(png/webp/bmp)才统一转存为 .jpg
        ext = os.path.splitext(name)[1]
        if ext.lower() in (".jpg", ".jpeg"):
            dst = os.path.join(args.output, name)
        else:
            dst = os.path.join(args.output, os.path.splitext(name)[0] + ".jpg")
        status = make_thumbnail(src, dst, args.width, args.quality, args.force)
        kb_before = os.path.getsize(src) // 1024
        kb_after = os.path.getsize(dst) // 1024 if os.path.exists(dst) else 0
        total_before += kb_before
        total_after += kb_after
        print(f"[{status:^6}] {name:<32} {kb_before:>6}KB -> {kb_after:>6}KB")
    print("-" * 60)
    print(f"[合计] {len(files)} 张: {total_before}KB -> {total_after}KB (节省 ~{(1 - total_after / max(total_before, 1)) * 100:.0f}%)")
    print("[完成] 新照片放入 photos/ 后重跑本脚本即可增量生成 gallery/ 小图。")


if __name__ == "__main__":
    main()


# -*- coding: utf-8 -*-
"""
make_gallery_thumbs.py — 首页 Gallery 照片缩略图生成脚本
=================================================================
用途
----
把 assets/images/photos/ 下的原始大图（3~9MB 相机/手机原图）批量缩小为
网页展示用缩略图，输出到 assets/images/gallery/thumbs/（约 70~200KB/张）。

为什么需要缩图：
  首页 _showcase/ 画廊会逐张加载图片，3~9MB 原图会让页面卡顿、浪费流量；
  画廊卡片最大显示宽度仅 ~300px，900px 宽的缩略图肉眼无差别。

用法（在仓库根目录执行）
----------------------
  python _scripts/make_gallery_thumbs.py               # 默认 900px 宽, JPEG q82
  python _scripts/make_gallery_thumbs.py --width 1200  # 自定义宽度
  python _scripts/make_gallery_thumbs.py --force       # 忽略已有文件, 全部重新生成
  python _scripts/make_gallery_thumbs.py --photos "其他目录"   # 自定义照片源目录

幂等性
------
第二次运行会跳过已生成且不旧于源图的缩略图（输出 SKIP），可放心重复执行。

依赖: Pillow (pip install Pillow)
"""
import argparse
import os
import sys

from PIL import Image, ImageOps

# 仓库根目录 = 本脚本的上一级目录（脚本位于 <root>/_scripts/ 下）
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 照片源目录：放置原始大图
PHOTOS_DIR = os.path.join(ROOT, "assets", "images", "photos")
# 缩略图输出目录：Gallery 条目 image 字段应指向这里（如 /assets/images/gallery/thumbs/xxx.jpg）
THUMBS_DIR = os.path.join(ROOT, "assets", "images", "gallery", "thumbs")

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
    ap.add_argument("--width", type=int, default=900, help="缩略图最大宽度(px), 默认 900")
    ap.add_argument("--quality", type=int, default=82, help="JPEG 质量 1-100, 默认 82")
    ap.add_argument("--force", action="store_true", help="强制重新生成, 忽略已有缩略图")
    ap.add_argument("--photos", default=PHOTOS_DIR, help="照片源目录, 默认 assets/images/photos")
    args = ap.parse_args()

    if not os.path.isdir(args.photos):
        print(f"[错误] 照片目录不存在: {args.photos}")
        sys.exit(1)
    # 收集待处理照片（按文件名排序，输出顺序稳定）
    files = sorted(
        f for f in os.listdir(args.photos)
        if f.lower().endswith(IMAGE_EXTS) and not f.startswith(".")
    )
    if not files:
        print(f"[提示] {args.photos} 下没有图片文件")
        return

    print(f"[源目录] {args.photos}")
    print(f"[输出]   {THUMBS_DIR}  (宽度≤{args.width}px, JPEG q{args.quality})")
    print("-" * 60)
    total_before = total_after = 0
    for name in files:
        src = os.path.join(args.photos, name)
        # 输出统一用 .jpg（PIL 会把 png/webp 等也转成 JPEG）
        dst = os.path.join(THUMBS_DIR, os.path.splitext(name)[0] + ".jpg")
        status = make_thumbnail(src, dst, args.width, args.quality, args.force)
        kb_before = os.path.getsize(src) // 1024
        kb_after = os.path.getsize(dst) // 1024 if os.path.exists(dst) else 0
        total_before += kb_before
        total_after += kb_after
        print(f"[{status:^6}] {name:<32} {kb_before:>6}KB -> {kb_after:>6}KB")
    print("-" * 60)
    print(f"[合计] {len(files)} 张: {total_before}KB -> {total_after}KB (节省 ~{(1 - total_after / max(total_before, 1)) * 100:.0f}%)")
    print("[完成] 新照片放入源目录后重跑本脚本即可增量生成缩略图。")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
annotate.py — Screenshot annotations for helpdesk articles.

Subcommands:
    number      Numbered marker (1, 2, 3...) over a point
    arrow       Arrow from one point to another
    box         Outlined rectangle highlighting a region
    crop        Crop a region with surrounding padding (zoom-in)
    blur        Gaussian blur over a region (mask sensitive data)
    composite   Side-by-side composition (before/after)
    thumbnail   Downscale + re-encode for cheap agent consumption

Each subcommand takes --in and --out. Chain operations by piping the
output of one into the input of the next:
    --in raw/x.png --out assets/x.webp
    --in assets/x.webp --out assets/x.webp  (overwrites)

Output format is inferred from the --out suffix:
    .webp  → WebP (default for annotated assets and thumbs)
    .png   → PNG lossless (use only for raw captures)
    .jpg   → JPEG (fallback when WebP is unavailable downstream)

Examples:
    python annotate.py number --in a.png --out b.webp --xy 200,300 --n 1
    python annotate.py arrow --in a.png --out b.webp --from 100,100 --to 200,200
    python annotate.py box --in a.png --out b.webp --bbox 100,100,500,400
    python annotate.py crop --in a.png --out b.webp --bbox 100,100,500,400 --padding 30
    python annotate.py blur --in a.png --out b.webp --bbox 100,100,500,400
    python annotate.py composite --in a.png,b.png --out z.webp --labels "Before,After"
    python annotate.py thumbnail --in raw/x.png --out thumbs/x.webp --max-width 1024 --quality 75
"""

import argparse
import math
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    sys.stderr.write(
        "Pillow is not installed. Run: pip install Pillow\n"
    )
    sys.exit(1)


# Consistent palette across all documentation
ACCENT_RED = (229, 57, 53)         # #E53935 — primary highlight
WHITE = (255, 255, 255)
TEXT_DARK = (33, 33, 33)
SHADOW = (0, 0, 0, 64)             # 25% alpha
BG_NEUTRAL = (245, 245, 245)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Try a reasonable sans-serif; fall back to the default if none found."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _parse_xy(s: str) -> Tuple[int, int]:
    parts = [int(p.strip()) for p in s.split(",")]
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f"Expected X,Y, got: {s}")
    return tuple(parts)


def _parse_bbox(s: str) -> Tuple[int, int, int, int]:
    parts = [int(p.strip()) for p in s.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(
            f"Expected X1,Y1,X2,Y2, got: {s}"
        )
    return tuple(parts)


def _parse_paths(s: str) -> List[Path]:
    return [Path(p.strip()) for p in s.split(",")]


def _open_rgba(path: Path) -> Image.Image:
    img = Image.open(path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img


def _save(img: Image.Image, path: Path, quality: int = 90) -> None:
    """Save img to disk, picking the format from the path suffix.

    - .webp → WebP at the requested quality (alpha preserved). Default for
      annotated assets (article output) and thumbs (agent consumption).
    - .png  → PNG lossless. Use only for raw captures or when WebP is not an
      option downstream.
    - .jpg / .jpeg → JPEG (alpha is flattened to RGB).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".webp":
        img.save(path, format="WEBP", quality=quality, method=6)
    elif suffix in (".jpg", ".jpeg"):
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.save(path, format="JPEG", quality=quality, optimize=True)
    else:
        img.save(path, format="PNG", optimize=True)


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

def op_number(
    img: Image.Image,
    xy: Tuple[int, int],
    n: int,
    radius: int = 22,
) -> Image.Image:
    """Numbered red circle with white border and drop shadow."""
    x, y = xy
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Shadow
    shadow_offset = 3
    draw.ellipse(
        [
            x - radius - 2 + shadow_offset,
            y - radius - 2 + shadow_offset,
            x + radius + 2 + shadow_offset,
            y + radius + 2 + shadow_offset,
        ],
        fill=SHADOW,
    )
    # Outer white border
    draw.ellipse(
        [x - radius - 4, y - radius - 4, x + radius + 4, y + radius + 4],
        fill=WHITE,
    )
    # Red circle
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        fill=ACCENT_RED,
    )

    # Centred number
    text = str(n)
    font = _load_font(max(18, radius - 2))
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    # Small vertical adjustment (PIL's textbbox is slightly off upward)
    tx = x - tw / 2 - bbox[0]
    ty = y - th / 2 - bbox[1]
    draw.text((tx, ty), text, fill=WHITE, font=font)

    return Image.alpha_composite(img, overlay)


def op_arrow(
    img: Image.Image,
    from_xy: Tuple[int, int],
    to_xy: Tuple[int, int],
    color: Tuple[int, int, int] = ACCENT_RED,
    width: int = 5,
    head_length: int = 22,
) -> Image.Image:
    """Straight arrow with a triangular head."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    x1, y1 = from_xy
    x2, y2 = to_xy

    angle = math.atan2(y2 - y1, x2 - x1)
    head_angle = math.radians(28)  # spread of the arrowhead

    # Shorten the shaft so it doesn't poke through the head
    line_end_x = x2 - (head_length - 4) * math.cos(angle)
    line_end_y = y2 - (head_length - 4) * math.sin(angle)

    # Line shadow
    draw.line(
        [(x1 + 2, y1 + 2), (line_end_x + 2, line_end_y + 2)],
        fill=SHADOW,
        width=width + 1,
    )
    # Line
    draw.line(
        [(x1, y1), (line_end_x, line_end_y)],
        fill=color + (255,),
        width=width,
    )

    # Arrowhead — triangle
    px1 = x2 - head_length * math.cos(angle - head_angle)
    py1 = y2 - head_length * math.sin(angle - head_angle)
    px2 = x2 - head_length * math.cos(angle + head_angle)
    py2 = y2 - head_length * math.sin(angle + head_angle)

    # Head shadow
    draw.polygon(
        [(x2 + 2, y2 + 2), (px1 + 2, py1 + 2), (px2 + 2, py2 + 2)],
        fill=SHADOW,
    )
    # Head
    draw.polygon(
        [(x2, y2), (px1, py1), (px2, py2)],
        fill=color + (255,),
    )

    return Image.alpha_composite(img, overlay)


def op_box(
    img: Image.Image,
    bbox: Tuple[int, int, int, int],
    color: Tuple[int, int, int] = ACCENT_RED,
    width: int = 4,
    corner_radius: int = 6,
) -> Image.Image:
    """Rounded rectangle highlighting a region."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    x1, y1, x2, y2 = bbox

    # Soft shadow
    draw.rounded_rectangle(
        [x1 + 2, y1 + 2, x2 + 2, y2 + 2],
        radius=corner_radius,
        outline=SHADOW,
        width=width + 1,
    )
    # Main rectangle
    draw.rounded_rectangle(
        [x1, y1, x2, y2],
        radius=corner_radius,
        outline=color + (255,),
        width=width,
    )

    return Image.alpha_composite(img, overlay)


def op_crop(
    img: Image.Image,
    bbox: Tuple[int, int, int, int],
    padding: int = 20,
) -> Image.Image:
    """Crop a region with padding on every side."""
    w, h = img.size
    x1, y1, x2, y2 = bbox
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(w, x2 + padding)
    y2 = min(h, y2 + padding)
    return img.crop((x1, y1, x2, y2))


def op_blur(
    img: Image.Image,
    bbox: Tuple[int, int, int, int],
    radius: int = 14,
) -> Image.Image:
    """Apply gaussian blur to a region (mask sensitive data)."""
    img = img.copy()
    region = img.crop(bbox)
    blurred = region.filter(ImageFilter.GaussianBlur(radius=radius))
    img.paste(blurred, (bbox[0], bbox[1]))
    return img


def op_composite(
    imgs: List[Image.Image],
    labels: Optional[List[str]] = None,
    gap: int = 24,
    label_height: int = 44,
    bg: Tuple[int, int, int] = BG_NEUTRAL,
) -> Image.Image:
    """Side-by-side composition with optional top labels."""
    if not imgs:
        raise ValueError("At least one image is required.")

    # Normalise to the same height
    target_h = max(im.size[1] for im in imgs)
    resized = []
    for im in imgs:
        w, h = im.size
        if h != target_h:
            new_w = int(w * target_h / h)
            im = im.resize((new_w, target_h), Image.LANCZOS)
        resized.append(im)

    total_w = sum(im.size[0] for im in resized) + gap * (len(resized) - 1)
    has_labels = labels is not None and len(labels) == len(resized)
    top_offset = label_height if has_labels else 0

    canvas = Image.new("RGBA", (total_w, target_h + top_offset), bg + (255,))

    x = 0
    for i, im in enumerate(resized):
        canvas.paste(im, (x, top_offset), im if im.mode == "RGBA" else None)
        if has_labels:
            draw = ImageDraw.Draw(canvas)
            font = _load_font(20)
            label = labels[i]
            bbox = draw.textbbox((0, 0), label, font=font)
            tw = bbox[2] - bbox[0]
            draw.text(
                (x + im.size[0] / 2 - tw / 2, 12),
                label,
                fill=TEXT_DARK,
                font=font,
            )
        x += im.size[0] + gap

    return canvas


def op_thumbnail(
    img: Image.Image,
    max_width: int = 1024,
) -> Image.Image:
    """Downscale to a maximum width, preserving aspect ratio.

    Used to produce small WebP renderings of raw captures for the agent to
    analyse. Cheaper to send to the model than a 2560×1600 PNG. If the image
    is already narrower than max_width, returns it unchanged.
    """
    w, h = img.size
    if w <= max_width:
        return img
    new_h = int(round(h * max_width / w))
    return img.resize((max_width, new_h), Image.LANCZOS)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Screenshot annotations for helpdesk articles."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # number
    p = sub.add_parser("number", help="Numbered marker")
    p.add_argument("--in", dest="inp", required=True, type=Path)
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument("--xy", required=True, type=_parse_xy, help="X,Y")
    p.add_argument("--n", required=True, type=int)
    p.add_argument("--radius", type=int, default=22)

    # arrow
    p = sub.add_parser("arrow", help="Arrow from A to B")
    p.add_argument("--in", dest="inp", required=True, type=Path)
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument("--from", dest="from_xy", required=True, type=_parse_xy)
    p.add_argument("--to", dest="to_xy", required=True, type=_parse_xy)
    p.add_argument("--width", type=int, default=5)

    # box
    p = sub.add_parser("box", help="Outlined rectangle")
    p.add_argument("--in", dest="inp", required=True, type=Path)
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument("--bbox", required=True, type=_parse_bbox, help="X1,Y1,X2,Y2")
    p.add_argument("--width", type=int, default=4)

    # crop
    p = sub.add_parser("crop", help="Crop with padding")
    p.add_argument("--in", dest="inp", required=True, type=Path)
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument("--bbox", required=True, type=_parse_bbox)
    p.add_argument("--padding", type=int, default=20)

    # blur
    p = sub.add_parser("blur", help="Gaussian blur over a region")
    p.add_argument("--in", dest="inp", required=True, type=Path)
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument("--bbox", required=True, type=_parse_bbox)
    p.add_argument("--radius", type=int, default=14)

    # composite
    p = sub.add_parser("composite", help="Side-by-side composition")
    p.add_argument(
        "--in", dest="inp", required=True, type=_parse_paths,
        help="Comma-separated paths"
    )
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument(
        "--labels", type=str, default=None,
        help="Comma-separated labels (same count as inputs)"
    )
    p.add_argument("--gap", type=int, default=24)
    p.add_argument(
        "--quality", type=int, default=90,
        help="Quality for lossy output formats (WebP/JPEG); default 90"
    )

    # thumbnail
    p = sub.add_parser(
        "thumbnail",
        help="Downscale + re-encode for cheap agent consumption",
    )
    p.add_argument("--in", dest="inp", required=True, type=Path)
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument(
        "--max-width", dest="max_width", type=int, default=1024,
        help="Maximum output width in px; default 1024"
    )
    p.add_argument(
        "--quality", type=int, default=75,
        help="Quality for lossy output formats (WebP/JPEG); default 75"
    )

    args = parser.parse_args()

    # composite uses `inp` as a list; the others use a single Path
    if args.cmd == "composite":
        imgs = [_open_rgba(p) for p in args.inp]
        labels = [s.strip() for s in args.labels.split(",")] if args.labels else None
        if labels and len(labels) != len(imgs):
            sys.stderr.write(
                f"Label count ({len(labels)}) does not match image count ({len(imgs)}).\n"
            )
            return 2
        result = op_composite(imgs, labels=labels, gap=args.gap)
        _save(result, args.out, quality=args.quality)
        print(f"ok {args.out}")
        return 0

    img = _open_rgba(args.inp)
    quality = 90  # default for annotated assets

    if args.cmd == "number":
        result = op_number(img, args.xy, args.n, radius=args.radius)
    elif args.cmd == "arrow":
        result = op_arrow(img, args.from_xy, args.to_xy, width=args.width)
    elif args.cmd == "box":
        result = op_box(img, args.bbox, width=args.width)
    elif args.cmd == "crop":
        result = op_crop(img, args.bbox, padding=args.padding)
    elif args.cmd == "blur":
        result = op_blur(img, args.bbox, radius=args.radius)
    elif args.cmd == "thumbnail":
        result = op_thumbnail(img, max_width=args.max_width)
        quality = args.quality
    else:
        sys.stderr.write(f"Unknown command: {args.cmd}\n")
        return 2

    _save(result, args.out, quality=quality)
    print(f"ok {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

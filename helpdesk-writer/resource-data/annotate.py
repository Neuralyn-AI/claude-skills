#!/usr/bin/env python3
"""
annotate.py — Anotação de screenshots para a central de ajuda do Tryon.

Subcomandos:
    number      Bolinha numerada (1, 2, 3...) sobre um ponto
    arrow       Seta de um ponto a outro
    box         Retângulo destacando uma área
    crop        Recorte com padding (zoom-in)
    blur        Desfoque em região (mascarar dados sensíveis)
    composite   Composição lado-a-lado (antes/depois)

Cada subcomando aceita --in e --out. Você pode encadear:
    --in raw/x.png --out assets/x.png
    --in assets/x.png --out assets/x.png  (sobrescreve)

Uso:
    python annotate.py number --in a.png --out b.png --xy 200,300 --n 1
    python annotate.py arrow --in a.png --out b.png --from 100,100 --to 200,200
    python annotate.py box --in a.png --out b.png --bbox 100,100,500,400
    python annotate.py crop --in a.png --out b.png --bbox 100,100,500,400 --padding 30
    python annotate.py blur --in a.png --out b.png --bbox 100,100,500,400
    python annotate.py composite --in a.png,b.png --out z.png --labels "Antes,Depois"
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
        "Pillow não está instalado. Rode: pip install Pillow\n"
    )
    sys.exit(1)


# Paleta consistente em toda a documentação
ACCENT_RED = (229, 57, 53)        # #E53935 — destaque principal
WHITE = (255, 255, 255)
TEXT_DARK = (33, 33, 33)
SHADOW = (0, 0, 0, 64)             # 25% alpha
BG_NEUTRAL = (245, 245, 245)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Tenta uma sans-serif razoável; cai pro default se nada disponível."""
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
        raise argparse.ArgumentTypeError(f"Esperado X,Y, recebi: {s}")
    return tuple(parts)


def _parse_bbox(s: str) -> Tuple[int, int, int, int]:
    parts = [int(p.strip()) for p in s.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(
            f"Esperado X1,Y1,X2,Y2, recebi: {s}"
        )
    return tuple(parts)


def _parse_paths(s: str) -> List[Path]:
    return [Path(p.strip()) for p in s.split(",")]


def _open_rgba(path: Path) -> Image.Image:
    img = Image.open(path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img


def _save(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # PNG preserva qualidade — sempre PNG pra documentação
    img.save(path, format="PNG", optimize=True)


# ---------------------------------------------------------------------------
# Operações
# ---------------------------------------------------------------------------

def op_number(
    img: Image.Image,
    xy: Tuple[int, int],
    n: int,
    radius: int = 22,
) -> Image.Image:
    """Bolinha numerada vermelha com borda branca e sombra."""
    x, y = xy
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Sombra
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
    # Borda branca externa
    draw.ellipse(
        [x - radius - 4, y - radius - 4, x + radius + 4, y + radius + 4],
        fill=WHITE,
    )
    # Círculo vermelho
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        fill=ACCENT_RED,
    )

    # Texto centralizado
    text = str(n)
    font = _load_font(max(18, radius - 2))
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    # Pequeno ajuste vertical (textbbox em PIL é levemente off pra cima)
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
    """Seta reta com cabeça triangular."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    x1, y1 = from_xy
    x2, y2 = to_xy

    angle = math.atan2(y2 - y1, x2 - x1)
    head_angle = math.radians(28)  # abertura

    # Encurta a linha pra não furar a cabeça
    line_end_x = x2 - (head_length - 4) * math.cos(angle)
    line_end_y = y2 - (head_length - 4) * math.sin(angle)

    # Sombra da linha
    draw.line(
        [(x1 + 2, y1 + 2), (line_end_x + 2, line_end_y + 2)],
        fill=SHADOW,
        width=width + 1,
    )
    # Linha
    draw.line(
        [(x1, y1), (line_end_x, line_end_y)],
        fill=color + (255,),
        width=width,
    )

    # Cabeça da seta — triângulo
    px1 = x2 - head_length * math.cos(angle - head_angle)
    py1 = y2 - head_length * math.sin(angle - head_angle)
    px2 = x2 - head_length * math.cos(angle + head_angle)
    py2 = y2 - head_length * math.sin(angle + head_angle)

    # Sombra da cabeça
    draw.polygon(
        [(x2 + 2, y2 + 2), (px1 + 2, py1 + 2), (px2 + 2, py2 + 2)],
        fill=SHADOW,
    )
    # Cabeça
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
    """Retângulo destacando uma região, com cantos arredondados."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    x1, y1, x2, y2 = bbox

    # Sombra suave
    draw.rounded_rectangle(
        [x1 + 2, y1 + 2, x2 + 2, y2 + 2],
        radius=corner_radius,
        outline=SHADOW,
        width=width + 1,
    )
    # Retângulo principal
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
    """Recorta uma região com padding em volta."""
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
    """Aplica gaussian blur em uma região (mascarar dados)."""
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
    """Composição lado-a-lado com labels opcionais no topo."""
    if not imgs:
        raise ValueError("Pelo menos uma imagem é necessária.")

    # Normaliza alturas pra mesma altura
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Anotações em screenshots para o Tryon Helpdesk."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # number
    p = sub.add_parser("number", help="Bolinha numerada")
    p.add_argument("--in", dest="inp", required=True, type=Path)
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument("--xy", required=True, type=_parse_xy, help="X,Y")
    p.add_argument("--n", required=True, type=int)
    p.add_argument("--radius", type=int, default=22)

    # arrow
    p = sub.add_parser("arrow", help="Seta de A pra B")
    p.add_argument("--in", dest="inp", required=True, type=Path)
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument("--from", dest="from_xy", required=True, type=_parse_xy)
    p.add_argument("--to", dest="to_xy", required=True, type=_parse_xy)
    p.add_argument("--width", type=int, default=5)

    # box
    p = sub.add_parser("box", help="Retângulo de destaque")
    p.add_argument("--in", dest="inp", required=True, type=Path)
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument("--bbox", required=True, type=_parse_bbox, help="X1,Y1,X2,Y2")
    p.add_argument("--width", type=int, default=4)

    # crop
    p = sub.add_parser("crop", help="Recorte com padding")
    p.add_argument("--in", dest="inp", required=True, type=Path)
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument("--bbox", required=True, type=_parse_bbox)
    p.add_argument("--padding", type=int, default=20)

    # blur
    p = sub.add_parser("blur", help="Desfoque em região (mascarar)")
    p.add_argument("--in", dest="inp", required=True, type=Path)
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument("--bbox", required=True, type=_parse_bbox)
    p.add_argument("--radius", type=int, default=14)

    # composite
    p = sub.add_parser("composite", help="Composição lado-a-lado")
    p.add_argument(
        "--in", dest="inp", required=True, type=_parse_paths,
        help="Caminhos separados por vírgula"
    )
    p.add_argument("--out", dest="out", required=True, type=Path)
    p.add_argument(
        "--labels", type=str, default=None,
        help="Labels separados por vírgula (mesma quantidade que imagens)"
    )
    p.add_argument("--gap", type=int, default=24)

    args = parser.parse_args()

    # composite tem inp como lista, os outros tem inp como Path
    if args.cmd == "composite":
        imgs = [_open_rgba(p) for p in args.inp]
        labels = [s.strip() for s in args.labels.split(",")] if args.labels else None
        if labels and len(labels) != len(imgs):
            sys.stderr.write(
                f"Quantidade de labels ({len(labels)}) não bate com imagens ({len(imgs)}).\n"
            )
            return 2
        result = op_composite(imgs, labels=labels, gap=args.gap)
        _save(result, args.out)
        print(f"✓ {args.out}")
        return 0

    img = _open_rgba(args.inp)

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
    else:
        sys.stderr.write(f"Comando desconhecido: {args.cmd}\n")
        return 2

    _save(result, args.out)
    print(f"✓ {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

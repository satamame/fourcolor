"""docs/10 用の図を生成する（四角版・サンプル01）。

  - square_sample01_labels.svg … 格子グラフを横ラベル h / 縦ラベル v の
    2パターンで（マスの色は国の色、中の数字がラベル値、太線が国境）
  - square_sample01_table.svg  … 横ラベルをヘッダ・縦ラベルを行インデックスに
    した2軸表（セルは対応マスと同じ色、数字は仮色値）

実行: python samples/square_figures.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fourcolor.axistable import COLORLESS, EMPTY, SEP
from fourcolor.mapcheck import build_edges
from fourcolor.render import STYLE, _line, _text, build_palette
from fourcolor.square import SquareGrid
from fourcolor.squaretable import build_square_table, square_axis_labels

import square_sample01


def square_panel(grid, country_of, labels, pal, org, side, title):
    out = []
    ox, oy = org
    w, h = grid.cols * side, grid.rows * side
    out.append(_text(ox + w / 2, oy - 14, title, size=16,
                     color=STYLE["text"], bold=True))
    for (r, c) in grid.nodes():
        x, y = ox + c * side, oy + r * side
        cty = country_of[(r, c)]
        fill = STYLE["colorless"] if cty is None else pal[cty]
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{side}" '
                   f'height="{side}" fill="{fill}" stroke="{STYLE["grid"]}" '
                   f'stroke-width="1"/>')
        if (r, c) in labels:
            out.append(_text(x + side / 2, y + side / 2 + 5,
                             str(labels[(r, c)]), size=15,
                             color=STYLE["text"], bold=True))
    # 国境（隣り合う別の国の境）を太線で
    for (r, c) in grid.nodes():
        x, y = ox + c * side, oy + r * side
        if c + 1 < grid.cols and country_of[(r, c)] != country_of[(r, c + 1)]:
            out.append(_line((x + side, y), (x + side, y + side),
                             stroke=STYLE["boundary"], stroke_width=3))
        if r + 1 < grid.rows and country_of[(r, c)] != country_of[(r + 1, c)]:
            out.append(_line((x, y + side), (x + side, y + side),
                             stroke=STYLE["boundary"], stroke_width=3))
    out.append(f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{w}" height="{h}" '
               f'fill="none" stroke="{STYLE["boundary"]}" stroke-width="3"/>')
    return out


def labels_svg(grid, country_of, edges, side=56):
    h, v = square_axis_labels(grid, edges)
    pal = build_palette({c for c in country_of.values() if c is not None})
    w = grid.cols * side
    margin, gap = 24, 52
    width = margin * 2 + w * 2 + gap
    height = 50 + grid.rows * side + 24
    out = [f'<svg viewBox="0 0 {width:.0f} {height:.0f}" '
           f'xmlns="http://www.w3.org/2000/svg">']
    out += square_panel(grid, country_of, h, pal, (margin, 50), side,
                        "横ラベル h（行スキャン）")
    out += square_panel(grid, country_of, v, pal, (margin + w + gap, 50), side,
                        "縦ラベル v（列スキャン）")
    out.append("</svg>")
    return "\n".join(out)


def table_svg(grid, country_of, edges, cell=28):
    table, h, v = build_square_table(grid, edges, country_of)
    cells = table.cells
    pal = build_palette({c for c in country_of.values() if c is not None})
    id_color = {table.cid[c]: pal[c] for c in table.cid}
    used_h, used_v = set(h.values()), set(v.values())
    n_rows, n_cols = table.n_rows, table.n_cols
    pad_l, pad_t = 34, 40
    width = pad_l + n_cols * cell + 8
    height = pad_t + n_rows * cell + 8
    out = [f'<svg viewBox="0 0 {width:.0f} {height:.0f}" '
           f'xmlns="http://www.w3.org/2000/svg">']
    out.append(_text(pad_l + n_cols * cell / 2, 16, "横ラベル h →", size=14,
                     color=STYLE["text"], bold=True))
    cy = pad_t + n_rows * cell / 2
    out.append(f'<text x="14" y="{cy:.1f}" font-size="14" text-anchor="middle" '
               f'fill="{STYLE["text"]}" font-weight="bold" '
               f'font-family="sans-serif" transform="rotate(-90 14 {cy:.1f})">'
               f'縦ラベル v ↓</text>')
    for j in range(n_cols):
        if (j + 1) in used_h:
            out.append(_text(pad_l + j * cell + cell / 2, pad_t - 8,
                             str(j + 1), size=13, color=STYLE["text"]))
    for i in range(n_rows):
        if (i + 1) in used_v:
            out.append(_text(pad_l - 9, pad_t + i * cell + cell / 2 + 5,
                             str(i + 1), size=13, color=STYLE["text"]))
    for i, row in enumerate(cells):
        for j, val in enumerate(row):
            if val == SEP:
                continue
            x, y = pad_l + j * cell, pad_t + i * cell
            if val == EMPTY:
                out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell-2}" '
                           f'height="{cell-2}" fill="#fbfbfb" stroke="#e2e2e2" '
                           f'stroke-width="1"/>')
            elif val == COLORLESS:
                out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell-2}" '
                           f'height="{cell-2}" fill="{STYLE["colorless"]}" '
                           f'stroke="{STYLE["node_stroke"]}" stroke-width="1.2" '
                           f'stroke-dasharray="3 2"/>')
            else:
                out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell-2}" '
                           f'height="{cell-2}" fill="{id_color[val]}" '
                           f'stroke="{STYLE["node_stroke"]}" stroke-width="1.2"/>')
                out.append(_text(x + (cell - 2) / 2, y + (cell - 2) / 2 + 5,
                                 str(val), size=13, color=STYLE["text"],
                                 bold=True))
    out.append("</svg>")
    return "\n".join(out)


def main():
    grid, country_of, edges = square_sample01.build_sample()
    here = Path(__file__).resolve().parent
    (here / "square_sample01_labels.svg").write_text(
        labels_svg(grid, country_of, edges), encoding="utf-8")
    (here / "square_sample01_table.svg").write_text(
        table_svg(grid, country_of, edges), encoding="utf-8")
    print("生成: samples/square_sample01_labels.svg")
    print("生成: samples/square_sample01_table.svg")


if __name__ == "__main__":
    main()

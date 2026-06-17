"""docs/09 用の図を生成する。

サンプル01 について:
  - axistable_sample01_labels.svg … ハニカムグラフを横ラベル h / 縦ラベル v の
    2パターンで（ノードの色は国の色、中の数字がラベル値）
  - axistable_sample01_table.svg  … 横ラベルをヘッダ・縦ラベルを行インデックスに
    した2軸表（セルは対応ノードと同じ色、数字は仮色値）

実行: python samples/axistable_figures.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fourcolor.axistable import (COLORLESS, EMPTY, SEP, axis_labels,
                                 build_axis_table, country_seed)
from fourcolor.render import STYLE, _line, _poly, _text, build_palette

import sample01_k4
import sample03_point

SQRT3 = 3 ** 0.5


def honeycomb_panel(grid, country_of, edges, labels, pal, org, side, title):
    """ハニカムグラフ1枚分の SVG 要素を返す（ノードの数字 = labels[node]）。"""
    out = []
    tri_w = grid.size * side
    out.append(_text(org[0] + tri_w / 2, org[1] - 22, title, size=16,
                     color=STYLE["text"], bold=True))
    same = [e for e, a in edges.items() if a["same_value"] is True]
    diff = [e for e, a in edges.items() if a["same_value"] is False]
    for u, v in same:
        out.append(_line(grid.node_center(u, side, org),
                         grid.node_center(v, side, org),
                         stroke=STYLE["same"], stroke_width=1.5,
                         stroke_dasharray="5 4"))
    for u, v in diff:
        out.append(_line(grid.node_center(u, side, org),
                         grid.node_center(v, side, org),
                         stroke=STYLE["boundary"], stroke_width=2.5))
    for node in grid.nodes():
        cx, cy = grid.node_center(node, side, org)
        if country_of[node] is None:  # 無色ノード: 白丸（破線）+ ラベル
            out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="13" '
                       f'fill="{STYLE["colorless"]}" stroke="{STYLE["node_stroke"]}" '
                       f'stroke-width="1.2" stroke-dasharray="3 2"/>')
        else:
            out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="13" '
                       f'fill="{pal[country_of[node]]}" '
                       f'stroke="{STYLE["node_stroke"]}" stroke-width="1.2"/>')
        out.append(_text(cx, cy + 5, str(labels[node]), size=14,
                         color=STYLE["text"], bold=True))
    return out


def labels_svg(grid, country_of, edges, side=64):
    h, v = axis_labels(grid, edges)
    pal = build_palette({c for c in country_of.values() if c is not None})
    tri_w = grid.size * side
    tri_h = grid.size * side * SQRT3 / 2
    margin, gap = 24, 40
    panel_w = tri_w + 30
    width = margin * 2 + panel_w * 2 + gap
    height = 40 + tri_h + 30
    out = [f'<svg viewBox="0 0 {width:.0f} {height:.0f}" '
           f'xmlns="http://www.w3.org/2000/svg">']
    o0 = (margin + 15, 50)
    o1 = (margin + 15 + panel_w + gap, 50)
    out += honeycomb_panel(grid, country_of, edges, h, pal, o0, side,
                           "横ラベル h（行スキャン）")
    out += honeycomb_panel(grid, country_of, edges, v, pal, o1, side,
                           "縦ラベル v（列スキャン）")
    out.append("</svg>")
    return "\n".join(out)


def table_svg(grid, country_of, edges, cell=28):
    table, h, v, cid = build_axis_table(grid, edges, country_of)
    pal = build_palette({c for c in country_of.values() if c is not None})
    id_color = {cid[c]: pal[c] for c in cid}
    used_h = set(h.values())
    used_v = set(v.values())
    n_rows, n_cols = len(table), len(table[0])
    pad_l, pad_t = 34, 40
    width = pad_l + n_cols * cell + 8
    height = pad_t + n_rows * cell + 8
    out = [f'<svg viewBox="0 0 {width:.0f} {height:.0f}" '
           f'xmlns="http://www.w3.org/2000/svg">']
    out.append(_text(pad_l + n_cols * cell / 2, 16, "横ラベル h →", size=14,
                     color=STYLE["text"], bold=True))
    out.append(f'<text x="14" y="{pad_t + n_rows * cell / 2:.1f}" '
               f'font-size="14" text-anchor="middle" fill="{STYLE["text"]}" '
               f'font-weight="bold" font-family="sans-serif" '
               f'transform="rotate(-90 14 {pad_t + n_rows * cell / 2:.1f})">'
               f'縦ラベル v ↓</text>')
    # 列ヘッダ（使われている h の値だけ）
    for j in range(n_cols):
        if (j + 1) in used_h:
            out.append(_text(pad_l + j * cell + cell / 2, pad_t - 8,
                             str(j + 1), size=13, color=STYLE["text"]))
    # 行ヘッダ（使われている v の値だけ）
    for i in range(n_rows):
        if (i + 1) in used_v:
            out.append(_text(pad_l - 9, pad_t + i * cell + cell / 2 + 5,
                             str(i + 1), size=13, color=STYLE["text"]))
    # セル本体
    for i, row in enumerate(table):
        for j, val in enumerate(row):
            if val == SEP:
                continue
            x = pad_l + j * cell
            y = pad_t + i * cell
            if val == EMPTY:
                out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell-2}" '
                           f'height="{cell-2}" fill="#fbfbfb" stroke="#e2e2e2" '
                           f'stroke-width="1"/>')
            elif val == COLORLESS:  # 無色ノード: 白塗り＋実線枠（ノードはある）
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
    here = Path(__file__).resolve().parent
    for mod, tag, side in [(sample01_k4, "sample01", 64),
                           (sample03_point, "sample03", 52)]:
        grid, country_of, edges = mod.build_sample()
        (here / f"axistable_{tag}_labels.svg").write_text(
            labels_svg(grid, country_of, edges, side=side), encoding="utf-8")
        (here / f"axistable_{tag}_table.svg").write_text(
            table_svg(grid, country_of, edges), encoding="utf-8")
        print(f"生成: samples/axistable_{tag}_labels.svg")
        print(f"生成: samples/axistable_{tag}_table.svg")


if __name__ == "__main__":
    main()

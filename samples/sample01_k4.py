"""サンプル01: 簡単な地図とそのハニカムグラフ表現。

地図: 中央の国 D を、3つの国 A, B, C が取り囲む。
      4つの国は互いにすべて隣接する (クラスタグラフは K4) ので、4色が必要な最小の例。

表現: 1辺4の三角形盤 (ノード16個) 上で、各国を連結なノード集合に割り当てる。
      - 各ノードの隣接数は最大3 (ハニカムグラフの性質)
      - エッジ属性 same_value: True=同じ国の内部 / False=国境

実行: python samples/sample01_k4.py
      → 検証結果を表示し、samples/sample01_k4.svg (地図/三角形分割/ハニカムグラフの3面図) を出力
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fourcolor import is_valid_coloring, solve
from fourcolor.honeycomb import HoneycombTriangle
from fourcolor.mapcheck import build_edges, representation_stats
from fourcolor.render import render_svg

SIZE = 4

# 各ノード (r, p) → 国
COUNTRY_OF = {
    # B: 左上の国 (7ノード)
    (1, 1): "B", (2, 1): "B", (2, 2): "B", (3, 1): "B", (3, 2): "B",
    (4, 1): "B", (4, 2): "B",
    # C: 右の国 (5ノード)
    (2, 3): "C", (3, 4): "C", (3, 5): "C", (4, 6): "C", (4, 7): "C",
    # D: 中央の国 (1ノード)
    (3, 3): "D",
    # A: 下の国 (3ノード)
    (4, 3): "A", (4, 4): "A", (4, 5): "A",
}

# 期待する国同士の隣接関係 (K4: すべての組が隣接)
EXPECTED_BORDERS = {
    frozenset(pair)
    for pair in [("A", "B"), ("A", "C"), ("A", "D"),
                 ("B", "C"), ("B", "D"), ("C", "D")]
}


def build_sample():
    """(grid, country_of, edges) を返す。edges が「塗られていない地図」の入力形式。"""
    grid = HoneycombTriangle(SIZE)
    return grid, COUNTRY_OF, build_edges(grid, COUNTRY_OF)


def check_sample(grid, country_of, edges):
    """サンプルが表現として正しいことを機械的に検証し、統計を返す。"""
    stats = representation_stats(grid, country_of, edges)

    # 国同士の隣接関係が意図どおり (K4)
    assert set(stats["borders"]) == EXPECTED_BORDERS, \
        f"国境関係が想定と違う: {stats['borders']}"

    # 4色で塗れて、3色では塗れない
    colors = solve(edges, num_colors=4)
    assert colors is not None and is_valid_coloring(edges, colors), "4彩色に失敗"
    assert solve(edges, num_colors=3) is None, "3色で塗れてしまった (K4 のはず)"

    nodes = grid.nodes()
    return {
        "ノード数": stats["nodes"],
        "エッジ数": stats["edges"],
        "内部エッジ (same_value=True)": stats["same_edges"],
        "国境エッジ (same_value=False)": stats["diff_edges"],
        "国の数": len(stats["countries"]),
        "最大隣接数": stats["max_degree"],
        "4彩色の例": {c: colors[next(n for n in nodes if country_of[n] == c)]
                      for c in stats["countries"]},
    }


def main():
    grid, country_of, edges = build_sample()
    stats = check_sample(grid, country_of, edges)
    print("サンプル01 (K4: 4色が必要な最小の地図) — 検証 OK")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    out_path = Path(__file__).with_suffix(".svg")
    out_path.write_text(render_svg(grid, country_of, edges), encoding="utf-8")
    print(f"SVG を出力: {out_path}")


if __name__ == "__main__":
    main()

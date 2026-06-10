"""サンプル02: 少し大きい地図 (7カ国) とそのハニカムグラフ表現。

地図: 1辺6の三角形盤 (ノード36個) に7つの国 A〜G を配置する。
      サンプル01 に無かった特徴を含む:
      - 国境が複数のエッジからなる (例: B と D は2本のエッジで接する)
      - すべての国が互いに隣接するわけではない (例: B と C は接しない)
      - 3つの国に挟まれた小さな国 E
      - この地図は実は3色で塗れる (4色は「最悪の場合」の保証であって、
        どの地図にも4色が必要なわけではない)

配置 (行ごと、左から):
            A
          A A A
        B A A A C
      B B D D D C C
    B B B D E D C C C
  F F F F F E G G G G G

実行: python samples/sample02_seven.py
      → 検証結果を表示し、samples/sample02_seven.svg を出力
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fourcolor import is_valid_coloring, solve
from fourcolor.honeycomb import HoneycombTriangle
from fourcolor.mapcheck import build_edges, representation_stats
from fourcolor.render import render_svg

SIZE = 6

COUNTRY_OF = {
    # A: 頂上の国 (7ノード)
    (1, 1): "A", (2, 1): "A", (2, 2): "A", (2, 3): "A",
    (3, 2): "A", (3, 3): "A", (3, 4): "A",
    # B: 左の国 (6ノード)
    (3, 1): "B", (4, 1): "B", (4, 2): "B", (5, 1): "B", (5, 2): "B", (5, 3): "B",
    # C: 右の国 (6ノード)
    (3, 5): "C", (4, 6): "C", (4, 7): "C", (5, 7): "C", (5, 8): "C", (5, 9): "C",
    # D: 中央の国 (5ノード)
    (4, 3): "D", (4, 4): "D", (4, 5): "D", (5, 4): "D", (5, 6): "D",
    # E: D, F, G に挟まれた小さな国 (2ノード)
    (5, 5): "E", (6, 6): "E",
    # F: 左下の国 (5ノード)
    (6, 1): "F", (6, 2): "F", (6, 3): "F", (6, 4): "F", (6, 5): "F",
    # G: 右下の国 (5ノード)
    (6, 7): "G", (6, 8): "G", (6, 9): "G", (6, 10): "G", (6, 11): "G",
}

# 期待する国同士の隣接関係 (10組。K7 の21組には遠く及ばない = 隣接はまばら)
EXPECTED_BORDERS = {
    frozenset(pair)
    for pair in [("A", "B"), ("A", "C"), ("A", "D"),
                 ("B", "D"), ("B", "F"),
                 ("C", "D"), ("C", "G"),
                 ("D", "E"), ("E", "F"), ("E", "G")]
}


def build_sample():
    grid = HoneycombTriangle(SIZE)
    return grid, COUNTRY_OF, build_edges(grid, COUNTRY_OF)


def check_sample(grid, country_of, edges):
    stats = representation_stats(grid, country_of, edges)

    assert set(stats["borders"]) == EXPECTED_BORDERS, \
        f"国境関係が想定と違う: {sorted(map(sorted, stats['borders']))}"

    # 複数エッジからなる国境があること (サンプル01 との対比ポイント)
    multi = {tuple(sorted(k)): n for k, n in stats["borders"].items() if n >= 2}
    assert multi, "複数エッジの国境が1つも無い"

    # 4色はもちろん、この地図は3色でも塗れる (2色では不可: A-B-D の三角形がある)
    colors4 = solve(edges, num_colors=4)
    assert colors4 is not None and is_valid_coloring(edges, colors4), "4彩色に失敗"
    colors3 = solve(edges, num_colors=3)
    assert colors3 is not None and is_valid_coloring(edges, colors3), "3彩色に失敗"
    assert solve(edges, num_colors=2) is None, "2色で塗れてしまった"

    nodes = grid.nodes()
    return {
        "ノード数": stats["nodes"],
        "エッジ数": stats["edges"],
        "内部エッジ (same_value=True)": stats["same_edges"],
        "国境エッジ (same_value=False)": stats["diff_edges"],
        "国の数": len(stats["countries"]),
        "最大隣接数": stats["max_degree"],
        "複数エッジの国境": multi,
        "3彩色の例": {c: colors3[next(n for n in nodes if country_of[n] == c)]
                      for c in stats["countries"]},
    }


def main():
    grid, country_of, edges = build_sample()
    stats = check_sample(grid, country_of, edges)
    print("サンプル02 (7カ国・3色で足りる地図) — 検証 OK")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    out_path = Path(__file__).with_suffix(".svg")
    out_path.write_text(render_svg(grid, country_of, edges, side=70),
                        encoding="utf-8")
    print(f"SVG を出力: {out_path}")


if __name__ == "__main__":
    main()

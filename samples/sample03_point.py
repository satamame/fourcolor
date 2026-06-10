"""サンプル03: 7カ国が1点に集まる地図と「無色ノード」。

地図のある1点に7つの国 A〜G が集まっている。
点で触れているだけの国同士は隣接する扱いに「ならない」(同じ色でもよい)。
ただし点の周りで隣どうしに並ぶ国 (A-B, B-C, ..., G-A) は、
その点から伸びる国境線で接しているので、普通に隣接する。

三角形盤の格子点には最大6個の三角形しか集まれないため、
6カ国までの点は普通の格子点で表現できるが、7カ国以上は表現できない。
そこで点を小さな三角形1個に「膨らませ」、それを無色ノードとする:
  - 無色ノードはどの国にも属さず、色も塗らない (country_of の値は None)
  - 無色ノードに接するエッジは same_value=None (制約なし)
  - 無色ノード1個の周りには、辺で接する3セル + 角だけで接する9セルの
    計12セルが環状に並ぶので、最大12カ国まで集まれる
    (さらに多くの国は、無色ノードを2個以上つなげて表現する)

実行: python samples/sample03_point.py
      → 検証結果を表示し、samples/sample03_point.svg を出力
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fourcolor import is_valid_coloring, solve
from fourcolor.honeycomb import HoneycombTriangle
from fourcolor.mapcheck import build_edges, representation_stats
from fourcolor.render import render_svg

SIZE = 6

# 無色ノード X の位置。X の周りを A→B→C→D→E→F→G の順に7カ国が囲む。
POINT = (4, 4)

COUNTRY_OF = {
    # A: 上の国 (X に辺で接し、X の上に広がる)
    (1, 1): "A", (2, 1): "A", (2, 2): "A", (2, 3): "A", (3, 3): "A", (3, 4): "A",
    # B: 右上の国
    (3, 5): "B", (4, 6): "B", (4, 7): "B", (5, 8): "B", (5, 9): "B",
    # C: 右下の国
    (4, 5): "C", (5, 6): "C", (5, 7): "C",
    (6, 8): "C", (6, 9): "C", (6, 10): "C", (6, 11): "C",
    # D: 下の国
    (5, 4): "D", (5, 5): "D", (6, 5): "D", (6, 6): "D", (6, 7): "D",
    # E: 左の国
    (4, 1): "E", (4, 2): "E", (4, 3): "E",
    (5, 1): "E", (5, 2): "E", (5, 3): "E",
    (6, 1): "E", (6, 2): "E", (6, 3): "E", (6, 4): "E",
    # F, G: X の左上の角に点で接するだけの小さな国
    (3, 1): "F",
    (3, 2): "G",
    # X: 無色ノード (7カ国が集まる点を膨らませたもの)
    POINT: None,
}

# 期待する国境: 点の周りで隣どうしの7組だけ (7頂点の輪 C7)。
# 隣どうしでない組 (A-C, A-D, B-E など14組) は点で触れるだけなので国境を持たない。
EXPECTED_BORDERS = {
    frozenset(pair)
    for pair in [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"),
                 ("E", "F"), ("F", "G"), ("G", "A")]
}


def build_sample():
    grid = HoneycombTriangle(SIZE)
    return grid, COUNTRY_OF, build_edges(grid, COUNTRY_OF)


def check_sample(grid, country_of, edges):
    stats = representation_stats(grid, country_of, edges)

    # 国境は「点の周りで隣どうし」の7組だけ
    assert set(stats["borders"]) == EXPECTED_BORDERS, \
        f"国境関係が想定と違う: {sorted(map(sorted, stats['borders']))}"

    # 無色ノードはちょうど1個で、そこに7カ国全部が集まっている
    assert stats["colorless_nodes"] == 1
    [mp] = stats["meeting_points"]
    assert mp["blob"] == [POINT]
    assert mp["countries"] == ["A", "B", "C", "D", "E", "F", "G"], \
        f"点に集まる国が想定と違う: {mp['countries']}"

    # 国の隣接グラフは7頂点の輪 (奇数長サイクル) なので、3色必要・3色で十分
    colors3 = solve(edges, num_colors=3)
    assert colors3 is not None and is_valid_coloring(edges, colors3), "3彩色に失敗"
    assert solve(edges, num_colors=2) is None, "2色で塗れてしまった"
    # 無色ノードには色が付かない
    assert POINT not in colors3

    nodes = grid.nodes()
    return {
        "ノード数": stats["nodes"],
        "エッジ数": stats["edges"],
        "内部エッジ (True) / 国境エッジ (False) / 制約なし (None)":
            (stats["same_edges"], stats["diff_edges"], stats["none_edges"]),
        "国の数": len(stats["countries"]),
        "無色ノード数": stats["colorless_nodes"],
        "点に集まる国": mp["countries"],
        "最大隣接数": stats["max_degree"],
        "3彩色の例": {c: colors3[next(n for n in nodes if country_of[n] == c)]
                      for c in stats["countries"]},
    }


def main():
    grid, country_of, edges = build_sample()
    stats = check_sample(grid, country_of, edges)
    print("サンプル03 (7カ国が1点に集まる地図と無色ノード) — 検証 OK")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    out_path = Path(__file__).with_suffix(".svg")
    out_path.write_text(render_svg(grid, country_of, edges, side=70),
                        encoding="utf-8")
    print(f"SVG を出力: {out_path}")


if __name__ == "__main__":
    main()

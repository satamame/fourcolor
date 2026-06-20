"""四角版・地図データのテンプレート（手順書 docs/11 の作例）。

格子のサイズと各マスの国を決めるだけ。座標 (r, c) は r=行(上から0)、
c=列(左から0)。国は連結（同じ国のマスは辺でつながっている）にすること。
5カ国以上が1点に集まる所だけ、そのマスを None（無色ノード）にする。

実行（図の生成）: python samples/square_figures.py square_mymap
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fourcolor.mapcheck import build_edges
from fourcolor.square import SquareGrid

ROWS, COLS = 3, 4

# (r, c) -> 国名（文字列）。無色ノードは None。
COUNTRY_OF = {
    (0, 0): "A", (0, 1): "A", (0, 2): "B", (0, 3): "B",
    (1, 0): "A", (1, 1): "C", (1, 2): "C", (1, 3): "B",
    (2, 0): "D", (2, 1): "D", (2, 2): "C", (2, 3): "B",
}


def build_sample():
    """(grid, country_of, edges) を返す（square_figures がこれを呼ぶ）。"""
    grid = SquareGrid(ROWS, COLS)
    return grid, COUNTRY_OF, build_edges(grid, COUNTRY_OF)

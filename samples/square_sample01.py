"""四角版プロトタイプのサンプル01: 3×3 格子上の K4（4色が必要な最小の例）。

地図:
    A B B
    A D C
    A C C
  4つの国 A, B, C, D が互いにすべて隣接する（K4）。4色必要・3色不可。

このスクリプトは、四角版でも 2軸ラベル表の議論が成り立つことを確認する:
  (1) 等式（同じ横/縦ラベル）の推移閉包 = 国の分割
  (2) 差1（横/縦ラベル）の異色ペア = 国境（baseline と一致）
  (3) 各ブロックは最大1セル（四角版の構造的な単純化）

実行: python samples/square_sample01.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fourcolor.baseline import solve
from fourcolor.mapcheck import build_edges
from fourcolor.square import SquareGrid
from fourcolor.squaretable import build_square_table, table_equivalence
from fourcolor.verify import is_valid_coloring

COUNTRY_OF = {
    (0, 0): "A", (0, 1): "B", (0, 2): "B",
    (1, 0): "A", (1, 1): "D", (1, 2): "C",
    (2, 0): "A", (2, 1): "C", (2, 2): "C",
}


def build_sample():
    grid = SquareGrid(3, 3)
    return grid, COUNTRY_OF, build_edges(grid, COUNTRY_OF)


def main():
    grid, country_of, edges = build_sample()

    # K4 の確認（4色で塗れて3色では塗れない）
    c4 = solve(edges, 4)
    assert c4 is not None and is_valid_coloring(edges, c4), "4彩色に失敗"
    assert solve(edges, 3) is None, "3色で塗れてしまった（K4 のはず）"

    table, h, v = build_square_table(grid, edges, country_of)
    eq_ok, border_ok, max_block = table_equivalence(grid, edges, country_of)

    print("四角版サンプル01 (3×3 K4)")
    print(f"  国 → 仮色値: {table.cid}")
    print(f"  表 ({table.n_rows}行 × {table.n_cols}列):")
    print(table)
    print(f"  (1) 等式の推移閉包 = 国の分割: {eq_ok}")
    print(f"  (2) 差1 の異色ペア = 国境(K4): {border_ok}")
    print(f"  (3) ブロック内の最大セル数: {max_block}  (四角は最大1のはず)")
    print(f"  初期の塗り分けが正しい: {table.is_valid_coloring()}  "
          f"色数: {table.n_colors()}")
    assert eq_ok and border_ok and max_block == 1


if __name__ == "__main__":
    main()

"""四角版サンプル02: 5カ国が1点に集まる例（無色ノード）。

四角格子では、1つの格子点に集まれる国は4つまで（格子点に4マス）。
5カ国以上が1点に集まる場合は、その点を小さな正方形1個に膨らませて
「無色ノード」にする（どの国にも属さず、接するエッジは same_value=None）。

地図 (X = 無色ノード):
    A A B
    A X C
    E E D
  X の周りを A→B→C→D→E が時計回りに囲む。隣どうしの5組だけが隣接（輪 C5）
  なので 3色必要・3色で十分。点で接するだけの非隣接（A-C, B-D など）は国境を持たない。

実行: python samples/square_sample02_point.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fourcolor.baseline import solve
from fourcolor.mapcheck import build_edges
from fourcolor.rowlabel import colorless_nodes
from fourcolor.square import SquareGrid
from fourcolor.squaretable import build_square_table, table_equivalence
from fourcolor.verify import is_valid_coloring

POINT = (1, 1)

COUNTRY_OF = {
    (0, 0): "A", (0, 1): "A", (0, 2): "B",
    (1, 0): "A", POINT: None, (1, 2): "C",
    (2, 0): "E", (2, 1): "E", (2, 2): "D",
}

# X の周りの隣どうし5組だけ（輪 C5）
EXPECTED_BORDERS = {frozenset(p) for p in
                    [("A", "B"), ("B", "C"), ("C", "D"),
                     ("D", "E"), ("E", "A")]}


def build_sample():
    grid = SquareGrid(3, 3)
    return grid, COUNTRY_OF, build_edges(grid, COUNTRY_OF)


def main():
    grid, country_of, edges = build_sample()

    # 無色ノードがちょうど1個 X
    colorless = colorless_nodes(grid, edges)
    assert colorless == {POINT}, f"無色ノードが想定と違う: {colorless}"

    # C5（奇数の輪）なので 3色必要・2色不可
    c3 = solve(edges, 3)
    assert c3 is not None and is_valid_coloring(edges, c3), "3彩色に失敗"
    assert solve(edges, 2) is None, "2色で塗れてしまった（C5 のはず）"
    assert POINT not in c3, "無色ノードに色が付いている"

    table, h, v = build_square_table(grid, edges, country_of)
    eq_ok, border_ok, max_block = table_equivalence(grid, edges, country_of)

    # 期待した国境（C5）と一致
    border_pairs = set()
    for axis in (h, v):
        by = {}
        for n in (m for m in h if m not in colorless):
            by.setdefault(axis[n], []).append(n)
        for val in by:
            if val + 1 in by:
                for u in by[val]:
                    for w in by[val + 1]:
                        if country_of[u] != country_of[w]:
                            border_pairs.add(
                                frozenset((country_of[u], country_of[w])))

    print("四角版サンプル02 (5カ国が1点・無色ノード)")
    print(f"  国 → 仮色値: {table.cid}")
    print(f"  無色ノード: {sorted(colorless)}")
    print(f"  表 ({table.n_rows}行 × {table.n_cols}列、o=無色):")
    print(table)
    print(f"  (1) 等式の推移閉包 = 国の分割: {eq_ok}")
    print(f"  (2) 差1 の異色ペア = baseline の国境: {border_ok}")
    print(f"      その国境 = C5 と一致: {border_pairs == EXPECTED_BORDERS}")
    print(f"  (3) ブロック内の最大セル数: {max_block}")
    assert eq_ok and border_ok and max_block == 1
    assert border_pairs == EXPECTED_BORDERS


if __name__ == "__main__":
    main()

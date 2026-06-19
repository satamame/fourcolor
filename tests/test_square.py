"""四角版プロトタイプ (fourcolor/square.py, squaretable.py) のテスト。

2軸ラベル表が baseline と同値になること（等式の推移閉包=国、差1=国境）と、
四角では各ブロックが最大1セルになることを、複数の格子地図で確認する。
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))

from fourcolor.baseline import solve
from fourcolor.mapcheck import build_edges
from fourcolor.square import SquareGrid
from fourcolor.squaretable import table_equivalence
from fourcolor.verify import is_valid_coloring

import square_sample01
import square_sample02_point

# K4 でない別の地図（縦帯3色: A|B|C, 隣り合うものだけ隣接 = パス）
STRIPES = {(r, c): "ABC"[c] for r in range(3) for c in range(3)}

# 4×4 のいくつかの国（連結）
BLOCKS = {
    (0, 0): "P", (0, 1): "P", (0, 2): "Q", (0, 3): "Q",
    (1, 0): "P", (1, 1): "R", (1, 2): "R", (1, 3): "Q",
    (2, 0): "S", (2, 1): "R", (2, 2): "T", (2, 3): "T",
    (3, 0): "S", (3, 1): "S", (3, 2): "T", (3, 3): "U",
}


class SquareTableTest(unittest.TestCase):

    def _check(self, grid, country_of):
        edges = build_edges(grid, country_of)
        eq_ok, border_ok, max_block = table_equivalence(grid, edges, country_of)
        self.assertTrue(eq_ok, "等式の推移閉包が国の分割と一致しない")
        self.assertTrue(border_ok, "差1の異色ペアが baseline の国境と一致しない")
        self.assertEqual(max_block, 1, "四角ではブロックは最大1セルのはず")

    def test_sample01_k4(self):
        grid, country_of, edges = square_sample01.build_sample()
        self.assertIsNotNone(solve(edges, 4))
        self.assertIsNone(solve(edges, 3))         # K4: 3色不可
        self._check(grid, country_of)

    def test_stripes(self):
        self._check(SquareGrid(3, 3), STRIPES)

    def test_blocks(self):
        self._check(SquareGrid(4, 4), BLOCKS)

    def test_sample02_colorless(self):
        grid, country_of, edges = square_sample02_point.build_sample()
        self.assertIsNotNone(solve(edges, 3))
        self.assertIsNone(solve(edges, 2))         # C5: 2色不可
        self._check(grid, country_of)

    def test_samples_main_run(self):
        square_sample01.main()       # 内部の assert が通ること
        square_sample02_point.main()


if __name__ == "__main__":
    unittest.main()

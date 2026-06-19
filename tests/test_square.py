"""四角版プロトタイプ (fourcolor/square.py, squaretable.py) のテスト。

2軸ラベル表が baseline と同値になること（等式の推移閉包=国、差1=国境）と、
四角では各ブロックが最大1セルになることを、複数の格子地図で確認する。
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

from fourcolor.baseline import solve
from fourcolor.mapcheck import build_edges
from fourcolor.square import SquareGrid
from fourcolor.axistable import AxisTable
from fourcolor.squaretable import (build_square_table, is_grid_realizable,
                                   table_equivalence)
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

    def test_weak_conditions_insufficient_k5(self):
        """四角版でも弱い条件だけでは4色不能の表（K5）が作れる (exp6)。"""
        from exp6_square_soundness import (build_square_k5, constraint_graph,
                                           square_weak_ok)
        from fourcolor.baseline import color_clusters
        t = build_square_k5()
        self.assertTrue(square_weak_ok(t))         # 弱い条件は満たす
        adj = constraint_graph(t)
        self.assertEqual(len(adj), 5)              # K5
        self.assertTrue(all(len(s) == 4 for s in adj.values()))
        self.assertIsNone(color_clusters(adj, 4))  # 4色で塗れない

    def test_grid_derived_is_reconstructible(self):
        """格子由来の表は、色を使わず再構成でき平面地図と判定される (exp7)。"""
        for build in (square_sample01.build_sample,
                      square_sample02_point.build_sample):
            grid, country_of, edges = build()
            table, _, _ = build_square_table(grid, edges, country_of)
            ok, reason = is_grid_realizable(table)
            self.assertTrue(ok, reason)

    def test_k5_not_reconstructible(self):
        """弱い条件のみの K5 表は再構成できない（辺連結性で詰まる）(exp7)。"""
        from exp6_square_soundness import build_square_k5
        ok, reason = is_grid_realizable(build_square_k5())
        self.assertFalse(ok)
        self.assertIn("辺連結", reason)

    def test_user_5conditions_insufficient(self):
        """ユーザー提示の5条件をすべて満たすのに格子に再構成できない反例 (exp8)。

        K5 は条件5（全ブロック1セル）を破るので反例ではないが、全ブロックを
        埋めても 5条件だけでは不十分（国が辺連結にならない例がある）。
        """
        from exp8_user_conditions import check_user_conditions
        S, E = -2, -1
        cells = [
            [1, E, S, E, E],
            [E, E, S, 2, E],
            [S, S, S, S, S],
            [1, E, S, E, 1],
            [E, E, S, E, E],
            [S, S, S, S, S],
            [1, E, S, E, E],
            [E, E, S, 2, E],
        ]
        t = AxisTable(cells)
        self.assertEqual(check_user_conditions(t), [])   # 5条件すべて満たす
        ok, reason = is_grid_realizable(t)
        self.assertFalse(ok)                             # でも再構成できない
        self.assertIn("辺連結", reason)


if __name__ == "__main__":
    unittest.main()

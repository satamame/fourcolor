"""基盤コードのユニットテスト。実行: python -m unittest discover -s tests -v"""

import unittest

from fourcolor import (
    DSU,
    TriBoard,
    Contradiction,
    is_valid_coloring,
    random_cluster_map,
    solve,
    violations,
)


class TestDSU(unittest.TestCase):
    def test_union_find(self):
        dsu = DSU()
        dsu.union("a", "b")
        dsu.union("b", "c")
        self.assertTrue(dsu.same("a", "c"))
        self.assertFalse(dsu.same("a", "d"))


class TestTriBoard(unittest.TestCase):
    def test_cell_count(self):
        # マスの総数は m(m+1)/2
        for m in (1, 3, 8):
            self.assertEqual(len(TriBoard(m).cells()), m * (m + 1) // 2)

    def test_neighbor_counts(self):
        board = TriBoard(4)
        # 角は2、辺上は4、内部は6 (セル隣接グラフは三角格子)
        self.assertEqual(len(board.neighbors((0, 0))), 2)   # 頂点
        self.assertEqual(len(board.neighbors((3, 0))), 2)   # 左下の角
        self.assertEqual(len(board.neighbors((3, 3))), 2)   # 右下の角
        self.assertEqual(len(board.neighbors((2, 0))), 4)   # 左辺上
        self.assertEqual(len(board.neighbors((2, 1))), 6)   # 内部

    def test_neighbors_symmetric(self):
        board = TriBoard(5)
        for cell in board.cells():
            for nb in board.neighbors(cell):
                self.assertIn(cell, board.neighbors(nb))


class TestVerify(unittest.TestCase):
    def test_violations(self):
        edges = {
            (1, 2): {"same_value": True},
            (2, 3): {"same_value": False},
        }
        self.assertTrue(is_valid_coloring(edges, {1: 0, 2: 0, 3: 1}))
        self.assertEqual(
            violations(edges, {1: 0, 2: 1, 3: 1}),
            [("same_violated", 1, 2), ("diff_violated", 2, 3)],
        )
        self.assertEqual(violations(edges, {1: 0, 2: 0}), [("uncolored", 2, 3)])


def k4_cluster_edges():
    """クラスタ A={a1,a2}, B, C, D が互いにすべて隣接する地図 (4色が必要)。"""
    return {
        ("a1", "a2"): {"same_value": True},
        ("a1", "b"): {"same_value": False},
        ("a1", "c"): {"same_value": False},
        ("a2", "d"): {"same_value": False},
        ("b", "c"): {"same_value": False},
        ("b", "d"): {"same_value": False},
        ("c", "d"): {"same_value": False},
    }


class TestBaseline(unittest.TestCase):
    def test_contradiction_detected(self):
        edges = {
            (1, 2): {"same_value": True},
            (2, 3): {"same_value": True},
            (1, 3): {"same_value": False},
        }
        with self.assertRaises(Contradiction):
            solve(edges)

    def test_k4_needs_four_colors(self):
        edges = k4_cluster_edges()
        colors = solve(edges, num_colors=4)
        self.assertIsNotNone(colors)
        self.assertTrue(is_valid_coloring(edges, colors))
        # 同一クラスタは同色、4クラスタで4色すべて使う
        self.assertEqual(colors["a1"], colors["a2"])
        self.assertEqual(len({colors["a1"], colors["b"], colors["c"], colors["d"]}), 4)
        # 3色では塗れない
        self.assertIsNone(solve(edges, num_colors=3))

    def test_random_maps_are_four_colorable(self):
        # クラスタ縮約グラフは平面グラフなので、四色定理により必ず4彩色できるはず
        for seed in range(10):
            board, edges = random_cluster_map(m=8, p_merge=0.5, seed=seed)
            colors = solve(edges, num_colors=4)
            self.assertIsNotNone(colors, f"seed={seed} で4彩色に失敗")
            self.assertTrue(is_valid_coloring(edges, colors), f"seed={seed} で制約違反")


if __name__ == "__main__":
    unittest.main()

"""honeycomb モジュールとサンプル01のテスト。"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))

from fourcolor import is_valid_coloring, solve
from fourcolor.honeycomb import HoneycombTriangle
from fourcolor.mapcheck import build_edges, representation_stats
import sample01_k4
import sample02_seven
import sample03_point


class TestHoneycombTriangle(unittest.TestCase):
    def test_node_count(self):
        # 1辺 size の三角形分割で小三角形は size**2 個
        for size in (1, 2, 4, 7):
            self.assertEqual(len(HoneycombTriangle(size).nodes()), size * size)

    def test_max_degree_is_three(self):
        # ハニカムグラフの核心: どのノードも隣接数は最大3
        grid = HoneycombTriangle(6)
        degrees = [len(grid.neighbors(n)) for n in grid.nodes()]
        self.assertLessEqual(max(degrees), 3)
        # 下向き三角形 (内部) はちょうど3
        self.assertEqual(len(grid.neighbors((3, 2))), 3)
        # 大三角形の角は1
        self.assertEqual(len(grid.neighbors((1, 1))), 1)

    def test_neighbors_symmetric(self):
        grid = HoneycombTriangle(5)
        for node in grid.nodes():
            for nb in grid.neighbors(node):
                self.assertIn(node, grid.neighbors(nb))

    def test_shared_edge(self):
        grid = HoneycombTriangle(4)
        for u, v in grid.adjacent_pairs():
            p1, p2 = grid.shared_edge(u, v)
            self.assertNotEqual(p1, p2)
        with self.assertRaises(ValueError):
            grid.shared_edge((1, 1), (4, 7))  # 隣接していない


class TestSample01(unittest.TestCase):
    def test_sample_is_consistent(self):
        grid, country_of, edges = sample01_k4.build_sample()
        stats = sample01_k4.check_sample(grid, country_of, edges)
        self.assertEqual(stats["ノード数"], 16)
        self.assertEqual(stats["国の数"], 4)
        self.assertEqual(stats["最大隣接数"], 3)
        # 国境エッジは6本 (K4 の辺数と一致: 各国境がちょうど1本のエッジ)
        self.assertEqual(stats["国境エッジ (same_value=False)"], 6)

    def test_svg_renders(self):
        grid, country_of, edges = sample01_k4.build_sample()
        svg = sample01_k4.render_svg(grid, country_of, edges)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("ハニカムグラフ", svg)
        # 座標ラベルが入っている
        self.assertIn("(4,7)", svg)


class TestSample02(unittest.TestCase):
    def test_sample_is_consistent(self):
        grid, country_of, edges = sample02_seven.build_sample()
        stats = sample02_seven.check_sample(grid, country_of, edges)
        self.assertEqual(stats["ノード数"], 36)
        self.assertEqual(stats["エッジ数"], 45)
        self.assertEqual(stats["国の数"], 7)
        self.assertEqual(stats["最大隣接数"], 3)
        # B-D は2本のエッジで接する (国境エッジ数は1本とは限らない)
        self.assertEqual(stats["複数エッジの国境"][("B", "D")], 2)

    def test_svg_renders(self):
        grid, country_of, edges = sample02_seven.build_sample()
        svg = sample02_seven.render_svg(grid, country_of, edges, side=70)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("(6,11)", svg)


class TestSample03(unittest.TestCase):
    def test_sample_is_consistent(self):
        grid, country_of, edges = sample03_point.build_sample()
        stats = sample03_point.check_sample(grid, country_of, edges)
        self.assertEqual(stats["ノード数"], 36)
        self.assertEqual(stats["国の数"], 7)
        self.assertEqual(stats["無色ノード数"], 1)
        self.assertEqual(stats["点に集まる国"],
                         ["A", "B", "C", "D", "E", "F", "G"])

    def test_svg_renders(self):
        grid, country_of, edges = sample03_point.build_sample()
        svg = sample03_point.render_svg(grid, country_of, edges, side=70)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("無色ノード", svg)


class TestColorlessCapacity(unittest.TestCase):
    """無色ノード1個の周りには最大12カ国が集まれることの機械検証。

    無色ノード X=(4,4) を囲む環状の12セル (辺で接する3 + 角だけで接する9) に
    12個の異なる国を1セルずつ置き、さらに盤の残りを2カ国 H, I で埋める。
    環の隣どうしは国境で接するが、隣どうしでない組は点で触れるだけで
    国境を持たない、という点の性質が12カ国でも保たれることを確かめる。
    """

    # X=(4,4) の周囲を時計回りに一周する12セル
    RING = [(3, 3), (3, 4), (3, 5), (4, 6), (4, 5), (5, 6),
            (5, 5), (5, 4), (4, 3), (4, 2), (3, 1), (3, 2)]

    def test_twelve_countries_at_one_point(self):
        grid = HoneycombTriangle(6)
        ring_names = [f"N{i:02d}" for i in range(12)]
        country_of = {cell: name for cell, name in zip(self.RING, ring_names)}
        country_of[(4, 4)] = None
        for cell in [(1, 1), (2, 1), (2, 2), (2, 3)]:
            country_of[cell] = "I"  # 上の残り
        for cell in grid.nodes():
            country_of.setdefault(cell, "H")  # 下の残り

        edges = build_edges(grid, country_of)
        stats = representation_stats(grid, country_of, edges)

        # 無色ノード1個に12カ国が集まっている
        [mp] = stats["meeting_points"]
        self.assertEqual(mp["countries"], ring_names)

        # 環の国同士の国境は「隣どうし」の12組だけ
        consecutive = {frozenset((ring_names[i], ring_names[(i + 1) % 12]))
                       for i in range(12)}
        ring_borders = {b for b in stats["borders"]
                        if b <= set(ring_names)}
        self.assertEqual(ring_borders, consecutive)

        # もちろん4色で塗れる
        colors = solve(edges, num_colors=4)
        self.assertIsNotNone(colors)
        self.assertTrue(is_valid_coloring(edges, colors))


if __name__ == "__main__":
    unittest.main()

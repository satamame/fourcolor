"""実験2A の道具 (fourcolor/tait.py) のテスト。"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))

from fourcolor import is_valid_coloring
from fourcolor.honeycomb import HoneycombTriangle
from fourcolor.mapcheck import build_edges
from fourcolor.tait import (aligned_coloring, alignment_score, analyze_map,
                            class_table, edge_direction, enumerate_colorings)
import sample01_k4


def unclustered_edges(size):
    grid = HoneycombTriangle(size)
    country_of = {n: f"N{n[0]:02d}_{n[1]:02d}" for n in grid.nodes()}
    return grid, build_edges(grid, country_of)


class TestEdgeDirection(unittest.TestCase):
    def test_direction_counts(self):
        # 1辺4の盤: 行間 (方向0) は▽の数=6本、行内は左▲/左▽が6本ずつ
        grid = HoneycombTriangle(4)
        counts = {0: 0, 1: 0, 2: 0}
        for u, v in grid.adjacent_pairs():
            counts[edge_direction(u, v)] += 1
        self.assertEqual(counts, {0: 6, 1: 6, 2: 6})


class TestAlignedColoring(unittest.TestCase):
    def test_proper_and_perfectly_aligned(self):
        # 国なしの盤では、方向と完全整合した4彩色が構成できる
        for size in (3, 4, 6):
            grid, edges = unclustered_edges(size)
            colors = aligned_coloring(grid)
            self.assertTrue(is_valid_coloring(edges, colors), f"size={size}")
            borders = [(edge_direction(u, v), u, v)
                       for (u, v), a in edges.items()
                       if a["same_value"] is False]
            table = class_table(borders, colors)
            self.assertEqual(alignment_score(table), 1.0, f"size={size}")
            # 方向ごとに XOR クラスは1種類だけ
            for d in (0, 1, 2):
                used = [x for x, n in table[d].items() if n > 0]
                self.assertEqual(len(used), 1, f"size={size} dir={d}")


class TestEnumerate(unittest.TestCase):
    def test_k4_has_unique_canonical_coloring(self):
        # K4 の彩色は色の入れ替えを除いて1通り
        adj = {c: {d for d in "ABCD" if d != c} for c in "ABCD"}
        colorings, truncated = enumerate_colorings(adj)
        self.assertEqual(len(colorings), 1)
        self.assertFalse(truncated)

    def test_cap(self):
        # 制約なしの5点 (彩色は多数) を cap=3 で打ち切れる
        adj = {i: set() for i in range(5)}
        colorings, truncated = enumerate_colorings(adj, cap=3)
        self.assertEqual(len(colorings), 3)
        self.assertTrue(truncated)


class TestAnalyzeSample01(unittest.TestCase):
    def test_sample01_best_score(self):
        # K4 では3つの XOR クラスが3組の完全マッチング {AB,CD} {AC,BD} {AD,BC}
        # に固定されるため、整合スコアは彩色によらず 3/6 = 0.5
        _, _, edges = sample01_k4.build_sample()
        result = analyze_map(edges)
        self.assertEqual(result["n_countries"], 4)
        self.assertEqual(result["n_borders"], 6)
        self.assertEqual(result["n_colorings"], 1)
        self.assertAlmostEqual(result["best_score"], 0.5)
        self.assertAlmostEqual(result["worst_score"], 0.5)


if __name__ == "__main__":
    unittest.main()

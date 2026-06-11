"""行ラベリング (fourcolor/rowlabel.py) のテスト。

最重要のテストは「行ラベリング + 行間併合の結果が baseline の縮約と一致する」
(docs/05 §6 の答え合わせ)。3つのサンプルすべてで機械検証する。
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))

from fourcolor.baseline import build_cluster_graph
from fourcolor.honeycomb import HoneycombTriangle
from fourcolor.mapcheck import build_edges
from fourcolor.rowlabel import (colorless_nodes, label_clusters, row_labels)
import sample01_k4
import sample02_seven
import sample03_point

SAMPLES = [sample01_k4, sample02_seven, sample03_point]


def baseline_view(edges, labeled_nodes):
    """baseline の縮約結果を (国の分割, 隣接) の形に直す (比較用)。"""
    dsu, adj = build_cluster_graph(edges)
    countries = {}
    for n in labeled_nodes:
        countries.setdefault(dsu.find(n), set()).add(n)
    nodes_of = {rep: frozenset(ns) for rep, ns in countries.items()}
    adjacency = {frozenset((nodes_of[a], nodes_of[b]))
                 for a, nbs in adj.items() for b in nbs if a in nodes_of}
    return set(nodes_of.values()), adjacency


class TestRowLabels(unittest.TestCase):
    def test_sample01_row3(self):
        # docs/05 §2 の表: 行3 は B B D C C → c = 1 1 2 3 3
        grid, _, edges = sample01_k4.build_sample()
        labels = row_labels(grid, edges)
        self.assertEqual([labels[(3, p)] for p in range(1, 6)],
                         [(3, 1), (3, 1), (3, 2), (3, 3), (3, 3)])

    def test_sample03_row4_with_colorless(self):
        # docs/05 §2 の表: 行4 は E E E X C B B → c = 1 1 1 — 3 4 4
        grid, _, edges = sample03_point.build_sample()
        labels = row_labels(grid, edges)
        self.assertEqual([labels.get((4, p)) for p in range(1, 8)],
                         [(4, 1), (4, 1), (4, 1), None, (4, 3), (4, 4), (4, 4)])

    def test_colorless_detection(self):
        grid, country_of, edges = sample03_point.build_sample()
        expected = {n for n, c in country_of.items() if c is None}
        self.assertEqual(colorless_nodes(grid, edges), expected)

    def test_row_starting_with_colorless(self):
        # 行頭が無色ノードでも、最初の非無色ノードに (r, 1) が付く
        grid = HoneycombTriangle(2)
        country_of = {(1, 1): "A", (2, 1): None, (2, 2): "A", (2, 3): "B"}
        edges = build_edges(grid, country_of)
        labels = row_labels(grid, edges)
        self.assertEqual(labels[(2, 2)], (2, 1))
        self.assertEqual(labels[(2, 3)], (2, 2))
        self.assertNotIn((2, 1), labels)

    def test_label_lexicographic_order_is_scan_order(self):
        # 同じ行内では c は単調非減少 (走査順として使える)
        for sample in SAMPLES:
            grid, _, edges = sample.build_sample()
            labels = row_labels(grid, edges)
            for r in range(1, grid.size + 1):
                cs = [labels[(r, p)][1] for p in range(1, 2 * r)
                      if (r, p) in labels]
                self.assertEqual(cs, sorted(cs))


class TestMergeMatchesBaseline(unittest.TestCase):
    def test_all_samples_match_baseline(self):
        # 行ラベリング + 行間併合 = baseline の縮約 (国の分割も隣接も一致)
        for sample in SAMPLES:
            grid, _, edges = sample.build_sample()
            labels, countries, adjacency = label_clusters(grid, edges)
            row_partition = set(countries.values())
            row_adjacency = {
                frozenset((countries[a], countries[b]))
                for pair in adjacency for a, b in [tuple(pair)]
            }
            base_partition, base_adjacency = baseline_view(edges, set(labels))
            self.assertEqual(row_partition, base_partition, sample.__name__)
            self.assertEqual(row_adjacency, base_adjacency, sample.__name__)

    def test_sample01_country_count(self):
        grid, _, edges = sample01_k4.build_sample()
        _, countries, adjacency = label_clusters(grid, edges)
        self.assertEqual(len(countries), 4)   # A, B, C, D
        self.assertEqual(len(adjacency), 6)   # K4 の辺数

    def test_sample03_country_count(self):
        grid, _, edges = sample03_point.build_sample()
        _, countries, adjacency = label_clusters(grid, edges)
        self.assertEqual(len(countries), 7)   # A〜G (無色ノードは含まれない)
        self.assertEqual(len(adjacency), 7)   # 7頂点の輪 C7


if __name__ == "__main__":
    unittest.main()

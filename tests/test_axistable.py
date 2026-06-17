"""2軸ラベル表 (fourcolor/axistable.py) のテスト。

表現B（無色ノードにも列・行を与える）での docs/09 の主張1〜3 と、
無色ノードを含めても規則的な三角階段が保たれることを3サンプルで機械検証する。
"""

import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))

from fourcolor.axistable import (COLORLESS, EMPTY, SEP, axis_labels,
                                 build_axis_table, country_seed)
from fourcolor.rowlabel import colorless_nodes
import sample01_k4
import sample02_seven
import sample03_point

SAMPLES = [sample01_k4, sample02_seven, sample03_point]


def runs(values):
    """連続した整数のかたまり（区切りで分けられたブロックの範囲）を返す。"""
    vals = sorted(set(values))
    blocks, cur = [], [vals[0]]
    for x in vals[1:]:
        if x == cur[-1] + 1:
            cur.append(x)
        else:
            blocks.append(cur)
            cur = [x]
    blocks.append(cur)
    return blocks


class AxisTableTest(unittest.TestCase):

    def test_encoding_four_values(self):
        """セルは -2/-1/0/>=1 のみ。値>=0 ⇔ そのマスにノードがある。"""
        for mod in SAMPLES:
            grid, country_of, edges = mod.build_sample()
            table, h, v, cid = build_axis_table(grid, edges, country_of)
            seen = {x for row in table for x in row}
            self.assertTrue(seen <= ({SEP, EMPTY, COLORLESS} | set(cid.values())),
                            f"{mod.__name__}: 想定外のセル値 {seen}")
            self.assertEqual(len(set(cid.values())), len(cid))  # 国ごとに一意
            # 値>=0 のセル数 = ノード数（無色含む）
            n_nodes = len(grid.nodes())
            n_cells_ge0 = sum(1 for row in table for x in row if x >= 0)
            # 同じ (h,v) に2ノードが乗る場合があるので「セル数 <= ノード数」
            self.assertLessEqual(n_cells_ge0, n_nodes)
            self.assertGreater(n_cells_ge0, 0)

    def test_colorless_cells_are_zero(self):
        """無色ノードのセルはちょうど COLORLESS(0)。"""
        for mod in SAMPLES:
            grid, country_of, edges = mod.build_sample()
            colorless = colorless_nodes(grid, edges)
            table, h, v, _ = build_axis_table(grid, edges, country_of)
            for n in colorless:
                self.assertEqual(table[v[n] - 1][h[n] - 1], COLORLESS)
            n_zero = sum(1 for row in table for x in row if x == COLORLESS)
            self.assertEqual(n_zero, len({(h[n], v[n]) for n in colorless}))

    def test_separator_marks_label_gaps(self):
        """区切りセルは、横/縦ラベルが未使用の位置にちょうど一致する。"""
        for mod in SAMPLES:
            grid, country_of, edges = mod.build_sample()
            h, v = axis_labels(grid, edges)
            used_h, used_v = set(h.values()), set(v.values())
            table, _, _, _ = build_axis_table(grid, edges, country_of)
            for i, row in enumerate(table):
                for j, x in enumerate(row):
                    is_sep = (j + 1) not in used_h or (i + 1) not in used_v
                    self.assertEqual(x == SEP, is_sep)

    def test_claim1_at_most_one_cell_per_row_and_col_in_block(self):
        """主張1: ブロック内のセル（有色+無色）は1行に最大1・1列に最大1。"""
        for mod in SAMPLES:
            grid, country_of, edges = mod.build_sample()
            h, v = axis_labels(grid, edges)
            nodes = list(h)
            for hb in runs(h.values()):
                for vb in runs(v.values()):
                    hset, vset = set(hb), set(vb)
                    cells = {(h[n], v[n]) for n in nodes
                             if h[n] in hset and v[n] in vset}
                    self.assertLessEqual(len(cells), 2)
                    per_row = Counter(vv for _, vv in cells)
                    per_col = Counter(hh for hh, _ in cells)
                    if cells:
                        self.assertLessEqual(max(per_row.values()), 1)
                        self.assertLessEqual(max(per_col.values()), 1)

    def test_claim23_same_line_same_country(self):
        """主張2/3: 同じ行・同じ列の有色セルは同じ国。"""
        for mod in SAMPLES:
            grid, country_of, edges = mod.build_sample()
            colorless = colorless_nodes(grid, edges)
            h, v = axis_labels(grid, edges)
            colored = [n for n in h if n not in colorless]
            for axis in (h, v):
                by_label = {}
                for n in colored:
                    by_label.setdefault(axis[n], set()).add(country_of[n])
                for countries in by_label.values():
                    self.assertEqual(len(countries), 1)

    def test_triangular_staircase_with_colorless(self):
        """表現Bでは無色ノードがあっても規則的な三角階段が保たれる。

        列ブロック数 = 行ブロック数 = n、ブロック(i,j) 非空 ⇔ j<=i、
        対角ブロック(i,i) はちょうど1セル。
        """
        for mod in SAMPLES:
            grid, country_of, edges = mod.build_sample()
            h, v = axis_labels(grid, edges)
            nodes = list(h)
            hb, vb = runs(h.values()), runs(v.values())
            self.assertEqual(len(hb), grid.size)
            self.assertEqual(len(vb), grid.size)
            cells = {}
            for n in nodes:
                ci = next(i for i, b in enumerate(hb) if h[n] in b)
                rj = next(j for j, b in enumerate(vb) if v[n] in b)
                cells.setdefault((ci, rj), set()).add((h[n], v[n]))
            for i in range(grid.size):
                for j in range(grid.size):
                    self.assertEqual((i, j) in cells, j <= i)
                self.assertEqual(len(cells[(i, i)]), 1)


if __name__ == "__main__":
    unittest.main()

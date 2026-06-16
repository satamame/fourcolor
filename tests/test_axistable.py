"""2軸ラベル表 (fourcolor/axistable.py) のテスト。

docs/09 の主張1〜3 を3サンプルで機械検証する:
  主張1 … 区切り(-1)で囲まれた各ブロック内では、ノードのセルは
          1行に最大1個・1列に最大1個（セル単位）。
  主張2 … 同じ行（縦ラベルが同じ）のノードセルは同じ国（→同色になりうる）。
  主張3 … 同じ列（横ラベルが同じ）のノードセルは同じ国。
"""

import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))

from fourcolor.axistable import (EMPTY, SEP, axis_labels, build_axis_table,
                                 country_seed)
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

    def test_encoding_three_values(self):
        """セルは -1（区切り）/ 0（空き）/ 1以上（仮色値）の3種類だけ。"""
        for mod in SAMPLES:
            grid, country_of, edges = mod.build_sample()
            table, _, _, cid = build_axis_table(grid, edges, country_of)
            seen = {x for row in table for x in row}
            self.assertTrue(seen <= ({SEP, EMPTY} | set(cid.values())),
                            f"{mod.__name__}: 想定外のセル値 {seen}")
            # 仮色値は国ごとに一意（国数 = 仮色値の種類数）
            self.assertEqual(len(set(cid.values())), len(cid))

    def test_separator_marks_label_gaps(self):
        """区切りセルは、横/縦ラベルが飛んだ（未使用の）位置に一致する。"""
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
        for mod in SAMPLES:
            grid, country_of, edges = mod.build_sample()
            h, v = axis_labels(grid, edges)
            nodes = list(h)
            for hb in runs(h.values()):
                for vb in runs(v.values()):
                    hset, vset = set(hb), set(vb)
                    cells = {(h[n], v[n]) for n in nodes
                             if h[n] in hset and v[n] in vset}
                    self.assertLessEqual(len(cells), 2)  # 1ブロックは最大2セル
                    per_row = Counter(vv for _, vv in cells)
                    per_col = Counter(hh for hh, _ in cells)
                    if cells:
                        self.assertLessEqual(max(per_row.values()), 1)
                        self.assertLessEqual(max(per_col.values()), 1)

    def test_claim2_same_row_same_country(self):
        for mod in SAMPLES:
            grid, country_of, edges = mod.build_sample()
            h, v = axis_labels(grid, edges)
            nodes = list(h)
            for val in set(v.values()):
                countries = {country_of[n] for n in nodes if v[n] == val}
                self.assertEqual(len(countries), 1)

    def test_claim3_same_col_same_country(self):
        for mod in SAMPLES:
            grid, country_of, edges = mod.build_sample()
            h, v = axis_labels(grid, edges)
            nodes = list(h)
            for val in set(h.values()):
                countries = {country_of[n] for n in nodes if h[n] == val}
                self.assertEqual(len(countries), 1)


if __name__ == "__main__":
    unittest.main()

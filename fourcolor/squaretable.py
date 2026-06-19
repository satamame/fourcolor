"""格子グラフ → 2軸ラベル表（四角版プロトタイプ）。

三角版 (axistable.py) との違いは「スキャンの順序」だけ:
  - 横ラベル: 各行を左→右に普通にスキャン
  - 縦ラベル: 各列を上→下に普通にスキャン（三角のジグザグが不要）

採番規則・セルの値の意味・AxisTable は三角版と完全に共有する。
四角では「列ブロック = 格子の行」「行ブロック = 格子の列」で、その交点は
マス1個なので、各ブロックは最大1セル（三角の ▲▽ ペア=最大2セルより単純）。
"""

from .axistable import (COLORLESS, EMPTY, SEP, AxisTable, cumulative_labels,
                        country_seed)
from .baseline import build_cluster_graph
from .dsu import DSU
from .rowlabel import colorless_nodes


def square_row_groups(grid):
    """横スキャン: 各行のノード列（左→右）。"""
    return [[(r, c) for c in range(grid.cols)] for r in range(grid.rows)]


def square_column_groups(grid):
    """縦スキャン: 各列のノード列（上→下）。ジグザグ不要。"""
    return [[(r, c) for r in range(grid.rows)] for c in range(grid.cols)]


def square_axis_labels(grid, edges):
    h = cumulative_labels(square_row_groups(grid), edges)
    v = cumulative_labels(square_column_groups(grid), edges)
    return h, v


def build_square_table(grid, edges, country_of):
    """格子グラフから2軸ラベル表 (AxisTable) を作る。

    返り値: (table, h, v)  table.cid に {国: 仮色値} が入る。
    """
    h, v = square_axis_labels(grid, edges)
    colorless = colorless_nodes(grid, edges)
    colored = [n for n in h if n not in colorless]
    cid = country_seed(colored, country_of)
    node_cell = {}
    for n in h:
        node_cell[(h[n], v[n])] = (COLORLESS if n in colorless
                                   else cid[country_of[n]])
    used_h = set(h.values())
    used_v = set(v.values())
    max_h, max_v = max(used_h), max(used_v)
    cells = []
    for vv in range(1, max_v + 1):
        row = []
        for hh in range(1, max_h + 1):
            if hh not in used_h or vv not in used_v:
                row.append(SEP)
            else:
                row.append(node_cell.get((hh, vv), EMPTY))
        cells.append(row)
    table = AxisTable(cells)
    table.cid = cid
    return table, h, v


def table_equivalence(grid, edges, country_of):
    """2軸表が baseline の縮約と同値かを確認する（オラクル比較）。

    返り値 (eq_ok, border_ok, max_block_cells):
      eq_ok        … 等式（同じ横/縦ラベル）の推移閉包 = 国の分割
      border_ok    … 差1（横/縦ラベル）の異色ペア = baseline の国境
      max_block_cells … 区切りで囲まれた1ブロック内の最大セル数（四角は1のはず）
    """
    h, v = square_axis_labels(grid, edges)
    nodes = list(h)

    # 等式の推移閉包
    dsu = DSU()
    for n in nodes:
        dsu.find(n)
    by_h, by_v = {}, {}
    for n in nodes:
        by_h.setdefault(h[n], []).append(n)
        by_v.setdefault(v[n], []).append(n)
    for group in list(by_h.values()) + list(by_v.values()):
        for a in group[1:]:
            dsu.union(group[0], a)
    clusters = {}
    for n in nodes:
        clusters.setdefault(dsu.find(n), set()).add(n)

    # baseline の国分割
    bdsu, badj = build_cluster_graph(edges)
    bclusters = {}
    for n in nodes:
        bclusters.setdefault(bdsu.find(n), set()).add(n)
    eq_ok = ({frozenset(s) for s in clusters.values()}
             == {frozenset(s) for s in bclusters.values()})

    # 差1 の異色ペア（国名で）
    pairs = set()
    for axis in (h, v):
        by = {}
        for n in nodes:
            by.setdefault(axis[n], []).append(n)
        for val in by:
            if val + 1 in by:
                for u in by[val]:
                    for w in by[val + 1]:
                        if country_of[u] != country_of[w]:
                            pairs.add(frozenset((country_of[u], country_of[w])))
    baseline_borders = {frozenset((country_of[a], country_of[b]))
                        for a, nbs in badj.items() for b in nbs}
    border_ok = pairs == baseline_borders

    # ブロック内の最大セル数
    def runs(values):
        vals = sorted(set(values))
        out, cur = [], [vals[0]]
        for x in vals[1:]:
            if x == cur[-1] + 1:
                cur.append(x)
            else:
                out.append(cur)
                cur = [x]
        out.append(cur)
        return out

    hb, vb = runs(h.values()), runs(v.values())
    max_block = 0
    for cb in map(set, hb):
        for rb in map(set, vb):
            cnt = sum(1 for n in nodes if h[n] in cb and v[n] in rb)
            max_block = max(max_block, cnt)

    return eq_ok, border_ok, max_block

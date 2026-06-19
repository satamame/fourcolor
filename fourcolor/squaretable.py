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
    colorless = colorless_nodes(grid, edges)
    colored = [n for n in h if n not in colorless]  # 無色ノードは国でない

    # 等式の推移閉包（有色ノードのみ）
    dsu = DSU()
    for n in colored:
        dsu.find(n)
    by_h, by_v = {}, {}
    for n in colored:
        by_h.setdefault(h[n], []).append(n)
        by_v.setdefault(v[n], []).append(n)
    for group in list(by_h.values()) + list(by_v.values()):
        for a in group[1:]:
            dsu.union(group[0], a)
    clusters = {}
    for n in colored:
        clusters.setdefault(dsu.find(n), set()).add(n)

    # baseline の国分割（有色ノードのみ）
    bdsu, badj = build_cluster_graph(edges)
    bclusters = {}
    for n in colored:
        bclusters.setdefault(bdsu.find(n), set()).add(n)
    eq_ok = ({frozenset(s) for s in clusters.values()}
             == {frozenset(s) for s in bclusters.values()})

    # 差1 の異色ペア（有色ノードのみ。国名で）
    pairs = set()
    for axis in (h, v):
        by = {}
        for n in colored:
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

    # ブロック内の最大セル数（無色マスも1セルとして数える）
    nodes = list(h)

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


# ---- 健全性: 表 → 格子グラフ → 平面地図 の再構成（色を使わない判定）----

def _index_runs(indices):
    out = []
    for x in indices:
        if out and x == out[-1][-1] + 1:
            out[-1].append(x)
        else:
            out.append([x])
    return out


def reconstruct(table):
    """2軸表から格子（マスの集まり）を再構成する。

    返り値 (square, reason):
      square … {(grid_row, grid_col): (i, j)}  元のセル位置（有色/無色）
      reason … 再構成できない場合の理由（このとき square は None）
    対応: 列ブロック=格子の行、行ブロック=格子の列、各ブロック1マス。
    セルの「値」は仮色値であって国ではないので、ここでは位置だけを返す
    （「国」= 等式の同値類は is_grid_realizable 側で構成する）。
    """
    cells = table.cells
    nrow, ncol = table.n_rows, table.n_cols
    sep_rows = {i for i in range(nrow) if all(x == SEP for x in cells[i])}
    sep_cols = {j for j in range(ncol)
                if all(cells[i][j] == SEP for i in range(nrow))}
    col_blocks = _index_runs([j for j in range(ncol) if j not in sep_cols])
    row_blocks = _index_runs([i for i in range(nrow) if i not in sep_rows])
    square = {}
    for a, cb in enumerate(col_blocks):
        for b, rb in enumerate(row_blocks):
            occ = [(i, j) for i in rb for j in cb if cells[i][j] >= 0]
            if len(occ) > 1:
                return None, f"ブロック(行{a},列{b})にマスが{len(occ)}個（>1）"
            if occ:
                square[(a, b)] = occ[0]
    return square, None


def _country_classes(table):
    """「国」= 等式の同値類を構成する（仮色値ではなく構造から）。

    有色セル（値>=1）を、同じ横ラベル(列)・同じ縦ラベル(行)で併合した
    Union-Find を返す。無色セル(0)は国でないので含めない。
    """
    cells = table.cells
    nrow, ncol = table.n_rows, table.n_cols
    colored = [(i, j) for i in range(nrow) for j in range(ncol)
               if cells[i][j] >= 1]
    dsu = DSU()
    for p in colored:
        dsu.find(p)
    by_row, by_col = {}, {}
    for (i, j) in colored:
        by_row.setdefault(i, []).append((i, j))
        by_col.setdefault(j, []).append((i, j))
    for grp in list(by_row.values()) + list(by_col.values()):
        for p in grp[1:]:
            dsu.union(grp[0], p)
    return dsu


def is_grid_realizable(table):
    """表が格子由来（=平面地図）として再構成できるかを、色を使わず判定する。

    「国」は仮色値ではなく**等式の同値類**（同じ横/縦ラベルでつながる有色セル）。
    格子由来なら満たすべき構造:
      1. 各ブロックは最大1マス（reconstruct が成功する）。
      2. 各列・各行のノード有セルは単色（条件1,2 が成立している）。
      3. 各国（同値類）が格子上で辺連結（ポリオミノ）。
      4. 再構成した格子の国境が、表の差1の隣接とちょうど一致する。
    すべて満たせば「格子由来 ⟹ 平面地図」が言え、四色定理から4色可が従う。

    返り値 (ok, reason)。
    """
    from collections import deque

    cells = table.cells
    nrow, ncol = table.n_rows, table.n_cols

    # 2. 各列・各行のノード有セルは単色（条件1,2 の確認）
    for j in range(ncol):
        if len({cells[i][j] for i in range(nrow) if cells[i][j] >= 0}) > 1:
            return False, f"列 {j} が単色でない（条件1違反）"
    for i in range(nrow):
        if len({x for x in cells[i] if x >= 0}) > 1:
            return False, f"行 {i} が単色でない（条件2違反）"

    # 「国」= 等式の同値類
    dsu = _country_classes(table)

    # 1. 再構成（(a,b) -> 元のセル位置 (i,j)）
    square, reason = reconstruct(table)
    if square is None:
        return False, reason
    present = set(square)
    # 各マスの「国」（同値類の代表）。無色マスは None。
    sq_class = {ab: (dsu.find((i, j)) if cells[i][j] >= 1 else None)
                for ab, (i, j) in square.items()}

    def grid_neighbors(p):
        a, b = p
        for q in ((a - 1, b), (a + 1, b), (a, b - 1), (a, b + 1)):
            if q in present:
                yield q

    # 3. 各国（同値類）が辺連結
    by_class = {}
    for ab, cls in sq_class.items():
        if cls is not None:
            by_class.setdefault(cls, []).append(ab)
    for cls, abs_ in by_class.items():
        seen, dq = {abs_[0]}, deque([abs_[0]])
        while dq:
            cur = dq.popleft()
            for q in grid_neighbors(cur):
                if sq_class[q] == cls and q not in seen:
                    seen.add(q)
                    dq.append(q)
        if len(seen) != len(abs_):
            return False, f"ある国（同値類）が辺連結でない（{len(abs_)}マスが分裂）"

    # 4. 国境の一致（再構成の隣接 == 表の差1）。国は同値類で識別する。
    rec_borders = set()
    for (a, b), cls in sq_class.items():
        if cls is None:
            continue
        for q in ((a + 1, b), (a, b + 1)):
            if q in sq_class and sq_class[q] is not None and sq_class[q] != cls:
                rec_borders.add(frozenset((cls, sq_class[q])))
    col_class, row_class = {}, {}
    for j in range(ncol):
        cs = {dsu.find((i, j)) for i in range(nrow) if cells[i][j] >= 1}
        if cs:
            col_class[j] = next(iter(cs))
    for i in range(nrow):
        cs = {dsu.find((i, j)) for j in range(ncol) if cells[i][j] >= 1}
        if cs:
            row_class[i] = next(iter(cs))
    table_borders = set()
    for j in range(ncol - 1):
        if j in col_class and j + 1 in col_class and \
                col_class[j] != col_class[j + 1]:
            table_borders.add(frozenset((col_class[j], col_class[j + 1])))
    for i in range(nrow - 1):
        if i in row_class and i + 1 in row_class and \
                row_class[i] != row_class[i + 1]:
            table_borders.add(frozenset((row_class[i], row_class[i + 1])))
    if rec_borders != table_borders:
        return False, "国境が表の差1と一致しない"

    return True, None

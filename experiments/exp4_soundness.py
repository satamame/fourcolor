"""実験4: 主張1〜3だけでは不十分（健全性の反例）(docs/09)。

「区切りで囲まれたブロック内では1行/1列に最大1個（主張1）」「同じ行/列は同色
（主張2/3）」という弱い条件だけを満たすのに、4色で塗れない（5色必要な）
2軸ラベル表を狙い撃ちで構築する。これが作れれば、主張1〜3だけでは
「表の塗り分け = 平面地図の塗り分け」にならない（不健全）ことが確定する。

構築（K5 を作る）:
  - 5つの国を行 0..4 に割り当てる（各国はその行に広がる＝同じ行で併合）。
  - 連続する行 (i, i+1) は隣接 → 不等式で辺ができる（K5 の連続4辺）。
  - 非連続ペア (i, j) は「2列だけのガジェットブロック」で作る:
    左列の行 i に国 i、右列の行 j に国 j を置く。隣り合う列なので辺 i-j。
    ガジェット同士は区切り列で隔てる。
  - 連続4辺 + 非連続6辺 = 10辺 = K5。

実行: python experiments/exp4_soundness.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fourcolor.axistable import COLORLESS, EMPTY, SEP, AxisTable
from fourcolor.baseline import color_clusters
from fourcolor.dsu import DSU


def build_k5_table():
    """K5 を表す主張1〜3充足の表（AxisTable）を作る。"""
    rows = 5
    non_consec = [(0, 2), (0, 3), (0, 4), (1, 3), (1, 4), (2, 4)]  # 6ガジェット
    # 各ガジェットは 2列、間に区切り列を1本。列数 = 6*2 + 5 = 17
    cells = [[EMPTY] * (len(non_consec) * 3 - 1) for _ in range(rows)]
    for g, (i, j) in enumerate(non_consec):
        left = g * 3
        right = g * 3 + 1
        if g > 0:                       # ガジェット間の区切り列
            for r in range(rows):
                cells[r][left - 1] = SEP
        cells[i][left] = i + 1          # 国 i の仮色値 = i+1 (>=1)
        cells[j][right] = j + 1         # 国 j
    return AxisTable(cells)


def claims_1_to_3_hold(t):
    """主張1〜3（弱い条件）が成り立つかを返す（三角階段は問わない）。"""
    def runs(idxs):
        out = []
        for x in idxs:
            if out and x == out[-1][-1] + 1:
                out[-1].append(x)
            else:
                out.append([x])
        return out

    sep_rows = {i for i in range(t.n_rows) if all(x == SEP for x in t.cells[i])}
    sep_cols = {j for j in range(t.n_cols)
                if all(t.cells[i][j] == SEP for i in range(t.n_rows))}
    col_blocks = runs([j for j in range(t.n_cols) if j not in sep_cols])
    row_blocks = runs([i for i in range(t.n_rows) if i not in sep_rows])
    # 主張1: 各ブロック内、1行/1列に最大1ノード
    for cb in col_blocks:
        for rb in row_blocks:
            per_row = {}
            per_col = {}
            for i in rb:
                for j in cb:
                    if t.cells[i][j] >= 0:
                        per_row[i] = per_row.get(i, 0) + 1
                        per_col[j] = per_col.get(j, 0) + 1
            if (per_row and max(per_row.values()) > 1) or \
               (per_col and max(per_col.values()) > 1):
                return False
    # 主張2/3: 同じ行/列の有色セルは1色
    for i in range(t.n_rows):
        if len({x for x in t.cells[i] if x >= 1}) > 1:
            return False
    for j in range(t.n_cols):
        if len({t.cells[i][j] for i in range(t.n_rows) if t.cells[i][j] >= 1}) > 1:
            return False
    return True


def constraint_graph(t):
    """表の等式（同行同列で併合）＋不等式（隣の行/列）から制約グラフを作る。

    返り値: adj = {代表セル: 隣接代表セルの集合}
    """
    dsu = DSU()
    colored = t.colored_positions()
    for pos in colored:
        dsu.find(pos)
    # 等式: 同じ行・同じ列の有色セルを併合
    by_row, by_col = {}, {}
    for (i, j) in colored:
        by_row.setdefault(i, []).append((i, j))
        by_col.setdefault(j, []).append((i, j))
    for group in list(by_row.values()) + list(by_col.values()):
        for a in group[1:]:
            dsu.union(group[0], a)
    # 不等式: 隣り合う列・行の有色セルの代表元に辺
    adj = {dsu.find(p): set() for p in colored}
    for j in range(t.n_cols - 1):
        a = [p for p in by_col.get(j, [])]
        b = [p for p in by_col.get(j + 1, [])]
        for u in a:
            for w in b:
                ru, rw = dsu.find(u), dsu.find(w)
                if ru != rw:
                    adj[ru].add(rw)
                    adj[rw].add(ru)
    for i in range(t.n_rows - 1):
        a = [p for p in by_row.get(i, [])]
        b = [p for p in by_row.get(i + 1, [])]
        for u in a:
            for w in b:
                ru, rw = dsu.find(u), dsu.find(w)
                if ru != rw:
                    adj[ru].add(rw)
                    adj[rw].add(ru)
    return adj


def main():
    t = build_k5_table()
    print("構築した表（行=国、ガジェットで非連続ペアの辺を作る）:")
    print(t)
    print()

    print(f"主張1〜3 を満たす: {claims_1_to_3_hold(t)}")
    print(f"三角階段（is_well_formed）: {t.is_well_formed()}  ← 弱い条件なので不成立でよい")

    adj = constraint_graph(t)
    n_v = len(adj)
    n_e = sum(len(s) for s in adj.values()) // 2
    print(f"制約グラフ: 頂点 {n_v}、辺 {n_e}  (K5 は 5頂点・10辺)")
    is_k5 = n_v == 5 and n_e == 10 and all(len(s) == 4 for s in adj.values())
    print(f"K5 か: {is_k5}")

    four = color_clusters(adj, num_colors=4)
    five = color_clusters(adj, num_colors=5)
    print(f"4色で塗れる: {four is not None}")
    print(f"5色で塗れる: {five is not None}")
    print()
    if claims_1_to_3_hold(t) and four is None:
        print("==> 主張1〜3 を満たすのに4色で塗れない表が存在する。")
        print("    つまり主張1〜3 だけでは『表の塗り分け = 平面地図の塗り分け』に")
        print("    ならない（不健全）。三角階段（主張4）が本質的に効いている。")


if __name__ == "__main__":
    main()

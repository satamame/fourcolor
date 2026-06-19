"""実験8: ユーザー提示の5条件で十分か（四角版、docs/10）。

5条件:
  1. ノード有セル（有色/無色）で横ラベルが同じなら同じ色
  2. 同じく縦ラベルが同じなら同じ色
  3. 横ラベルの差が1の2つのノード有セルは同じ色にならない
  4. 縦ラベルの差が1の2つのノード有セルは同じ色にならない
  5. 各ブロックに1個のノード有セルが存在する（=全ブロックがちょうど1セル）

まず exp6 の K5 がこの5条件（特に5）を満たさないことを確認し、次に
「2×2ブロックを全マス1セルで埋めた表」を小サイズで全列挙して、5条件を満たすのに
格子に再構成できない（=反例）ものがあるかを探す。

実行: python experiments/exp8_user_conditions.py
"""

import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fourcolor.axistable import EMPTY, SEP, AxisTable
from fourcolor.dsu import DSU
from fourcolor.squaretable import is_grid_realizable

from exp6_square_soundness import build_square_k5


def check_user_conditions(table):
    """5条件のうち満たさないものの番号リストを返す（空なら全部満たす）。"""
    cells = table.cells
    nrow, ncol = table.n_rows, table.n_cols
    fail = []
    # 1,2: 同じ列/行は単色（ノード有セル = 値>=0）
    for j in range(ncol):
        vals = {cells[i][j] for i in range(nrow) if cells[i][j] >= 0}
        if len(vals) > 1:
            fail.append(1)
            break
    for i in range(nrow):
        vals = {x for x in cells[i] if x >= 0}
        if len(vals) > 1:
            fail.append(2)
            break
    # 3,4: 隣の列/行は別色
    def colvals(j):
        return {cells[i][j] for i in range(nrow) if cells[i][j] >= 0}

    def rowvals(i):
        return {x for x in cells[i] if x >= 0}
    if any(colvals(j) & colvals(j + 1) for j in range(ncol - 1)):
        fail.append(3)
    if any(rowvals(i) & rowvals(i + 1) for i in range(nrow - 1)):
        fail.append(4)
    # 5: 各ブロックにちょうど1セル
    sep_rows = {i for i in range(nrow) if all(x == SEP for x in cells[i])}
    sep_cols = {j for j in range(ncol)
                if all(cells[i][j] == SEP for i in range(nrow))}

    def runs(idxs):
        out = []
        for x in idxs:
            if out and x == out[-1][-1] + 1:
                out[-1].append(x)
            else:
                out.append([x])
        return out
    cbs = runs([j for j in range(ncol) if j not in sep_cols])
    rbs = runs([i for i in range(nrow) if i not in sep_rows])
    for cb in map(set, cbs):
        for rb in map(set, rbs):
            cnt = sum(1 for i in rb for j in cb if cells[i][j] >= 0)
            if cnt != 1:
                fail.append(5)
                break
        else:
            continue
        break
    return sorted(set(fail))


def build_full_block_table(A, B, choices):
    """A列ブロック×B行ブロック、各ブロック2×2に1セルを置いた表。

    choices[(a,b)] in 0..3 がブロック内の位置。色は等式クラス（同じ行/列で併合）で
    付けるので条件1,2は自動成立。条件3,4が破れる配置は coloring_violations で弾く。
    """
    nrow, ncol = 3 * B - 1, 3 * A - 1
    cells = [[EMPTY] * ncol for _ in range(nrow)]
    for b in range(B - 1):
        for k in range(ncol):
            cells[3 * b + 2][k] = SEP
    for a in range(A - 1):
        for k in range(nrow):
            cells[k][3 * a + 2] = SEP
    placed = []
    for a in range(A):
        for b in range(B):
            ch = choices[a * B + b]
            i = 3 * b + (ch // 2)
            j = 3 * a + (ch % 2)
            cells[i][j] = 1
            placed.append((i, j))
    # 等式クラスで色付け
    dsu = DSU()
    for p in placed:
        dsu.find(p)
    rowmap, colmap = {}, {}
    for (i, j) in placed:
        rowmap.setdefault(i, []).append((i, j))
        colmap.setdefault(j, []).append((i, j))
    for grp in list(rowmap.values()) + list(colmap.values()):
        for p in grp[1:]:
            dsu.union(grp[0], p)
    color = {}
    for (i, j) in placed:
        r = dsu.find((i, j))
        color.setdefault(r, len(color) + 1)
        cells[i][j] = color[r]
    return AxisTable(cells)


def search(A, B):
    n_blocks = A * B
    total = valid = counter = 0
    example = None
    for choices in product(range(4), repeat=n_blocks):
        total += 1
        t = build_full_block_table(A, B, choices)
        if t.coloring_violations():     # 条件3,4 が破れている配置
            continue
        if check_user_conditions(t):    # 念のため5条件を確認
            continue
        valid += 1
        ok, reason = is_grid_realizable(t)
        if not ok:
            counter += 1
            if example is None:
                example = (choices, t, reason)
    print(f"A={A},B={B}: 全{total}  5条件OK {valid}  再構成不可(反例) {counter}",
          flush=True)
    return example


def main():
    k5 = build_square_k5()
    print("exp6 の K5 が満たさない条件:", check_user_conditions(k5),
          "（5 が入っていれば条件5違反＝5条件の反例ではない）")
    print()
    for A, B in [(2, 2), (2, 3), (3, 2), (3, 3)]:
        ex = search(A, B)
        if ex:
            choices, t, reason = ex
            print(f"  反例 (A={A},B={B}): {reason}")
            print(t)
            break


if __name__ == "__main__":
    main()

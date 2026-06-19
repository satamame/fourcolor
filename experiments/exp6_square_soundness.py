"""実験6: 四角版でも弱い条件だけでは不十分（健全性の反例）(docs/10)。

四角版テーブルの「分かりやすい必要条件」:
  - 各ブロック（区切りで囲まれた領域）は最大1セル（四角の特徴）
  - 区切りは十字をなす / 同じ行・列は同色
これだけを満たすのに4色で塗れない（K5）表を狙い撃ちで作る。

構築（三角版 exp4 と同じ発想に、行区切りを足す）:
  - 5つの国を5本の「データ行」に割り当てる（行で併合）。データ行の間には
    区切り行を入れて隣接させない（→ 行どうしの辺は作らない）。
  - K5 の10辺それぞれを「2列だけのガジェット」で作る（区切り列で隔てる）:
    左列のデータ行 i に国 i、右列のデータ行 j に国 j。隣り合う列なので辺 i-j。
  - 各ブロックは (ガジェットの2列)×(1データ行) で最大1セル。

実行: python experiments/exp6_square_soundness.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fourcolor.axistable import EMPTY, SEP, AxisTable
from fourcolor.baseline import color_clusters
from exp4_soundness import constraint_graph


def build_square_k5():
    """四角版テーブルとして K5 を表す表（各ブロック最大1セル）を作る。"""
    n = 5
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)]  # 10辺
    n_rows = 2 * n - 1            # データ行 0,2,4,6,8 / 区切り行 1,3,5,7
    n_cols = 3 * len(edges) - 1   # ガジェットごとに2列＋区切り1列
    cells = [[EMPTY] * n_cols for _ in range(n_rows)]
    for r in range(1, n_rows, 2):           # 区切り行
        cells[r] = [SEP] * n_cols
    for g, (i, j) in enumerate(edges):
        left, right = 3 * g, 3 * g + 1
        if g > 0:                            # ガジェット間の区切り列
            for r in range(n_rows):
                cells[r][left - 1] = SEP
        cells[2 * i][left] = i + 1           # 国 i（データ行 2i）
        cells[2 * j][right] = j + 1          # 国 j（データ行 2j）
    return AxisTable(cells)


def square_weak_ok(t):
    """四角版の弱い条件（各ブロック≤1セル・区切りは十字）を満たすか。"""
    for row in t.cells:                      # 値の範囲
        for x in row:
            if x < 1 and x not in (SEP, EMPTY, 0):
                return False
    sep_rows = {i for i in range(t.n_rows) if all(x == SEP for x in t.cells[i])}
    sep_cols = {j for j in range(t.n_cols)
                if all(t.cells[i][j] == SEP for i in range(t.n_rows))}
    for i in range(t.n_rows):                # 区切りは十字
        for j in range(t.n_cols):
            if (t.cells[i][j] == SEP) != (i in sep_rows or j in sep_cols):
                return False

    def runs(idxs):
        out = []
        for x in idxs:
            if out and x == out[-1][-1] + 1:
                out[-1].append(x)
            else:
                out.append([x])
        return out

    col_blocks = runs([j for j in range(t.n_cols) if j not in sep_cols])
    row_blocks = runs([i for i in range(t.n_rows) if i not in sep_rows])
    for cb in map(set, col_blocks):          # 各ブロック≤1セル
        for rb in map(set, row_blocks):
            cnt = sum(1 for i in rb for j in cb if t.cells[i][j] >= 0)
            if cnt > 1:
                return False
    return True


def main():
    t = build_square_k5()
    print("構築した四角版テーブル（行=国、列ガジェットで辺を作る）:")
    print(t)
    print()
    print(f"弱い条件（各ブロック≤1セル・区切り十字）を満たす: {square_weak_ok(t)}")

    adj = constraint_graph(t)
    n_v = len(adj)
    n_e = sum(len(s) for s in adj.values()) // 2
    is_k5 = n_v == 5 and n_e == 10 and all(len(s) == 4 for s in adj.values())
    print(f"制約グラフ: 頂点 {n_v}、辺 {n_e}  → K5 か: {is_k5}")

    four = color_clusters(adj, 4)
    five = color_clusters(adj, 5)
    print(f"4色で塗れる: {four is not None}  5色で塗れる: {five is not None}")
    print()
    if square_weak_ok(t) and four is None:
        print("==> 四角版でも、弱い条件（ブロック≤1セル等）だけでは4色不能の表が作れる。")
        print("    国 i が「1本のデータ行に飛び飛びに散る」非連結な領域になっている")
        print("    のが原因。健全には『各国が辺で連結（ポリオミノ）』が要る。")


if __name__ == "__main__":
    main()

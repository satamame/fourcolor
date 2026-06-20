"""実験9: 5条件 + 連続性条件（条件6）で十分か（四角版、docs/10）。

exp8 で、5条件だけでは「同じ横ラベルのマスが連続セグメントにならない」表を
許してしまい不十分だった。そこで次を条件6として足す:

  条件6: 各横ラベル（列）の有色マスが占める行ブロックは連続している。
         各縦ラベル（行）の有色マスが占める列ブロックも連続している。
         （＝同じラベルのマスが格子上で連続セグメント＝各国が辺連結になる狙い）

「全ブロックを2×2で埋めた表」を小サイズで全列挙し、5条件+条件6 を満たすのに
格子に再構成できない（反例）ものが残るかを調べる。残らなければ 6条件で十分の証拠。

実行: python experiments/exp9_contiguity.py
"""

import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fourcolor.axistable import SEP
from fourcolor.squaretable import is_grid_realizable

from exp8_user_conditions import build_full_block_table, check_user_conditions


def _block_index_of(used, n):
    """非区切りインデックス列から、各インデックス→ブロック番号 を作る。"""
    out, b, prev = {}, 0, None
    for x in sorted(used):
        if prev is not None and x != prev + 1:
            b += 1
        out[x] = b
        prev = x
    return out


def contiguity_ok(table):
    """条件6: 各列/行の有色マスが占める行ブロック/列ブロックが連続。"""
    cells = table.cells
    nrow, ncol = table.n_rows, table.n_cols
    sep_rows = {i for i in range(nrow) if all(x == SEP for x in cells[i])}
    sep_cols = {j for j in range(ncol)
                if all(cells[i][j] == SEP for i in range(nrow))}
    rb_of = _block_index_of([i for i in range(nrow) if i not in sep_rows], nrow)
    cb_of = _block_index_of([j for j in range(ncol) if j not in sep_cols], ncol)

    def contiguous(s):
        s = sorted(s)
        return not s or s == list(range(s[0], s[-1] + 1))

    for j in range(ncol):
        rbs = {rb_of[i] for i in range(nrow) if cells[i][j] >= 1}
        if not contiguous(rbs):
            return False
    for i in range(nrow):
        cbs = {cb_of[j] for j in range(ncol) if cells[i][j] >= 1}
        if not contiguous(cbs):
            return False
    return True


def search(A, B):
    total = cond5 = cond6 = counter = 0
    example = None
    for choices in product(range(4), repeat=A * B):
        total += 1
        t = build_full_block_table(A, B, choices)
        if t.coloring_violations() or check_user_conditions(t):
            continue
        cond5 += 1
        if not contiguity_ok(t):
            continue
        cond6 += 1
        ok, reason = is_grid_realizable(t)
        if not ok:
            counter += 1
            if example is None:
                example = (choices, t, reason)
    print(f"A={A},B={B}: 全{total}  5条件OK {cond5}  "
          f"+条件6 OK {cond6}  そのうち再構成不可(反例) {counter}", flush=True)
    return example


def main():
    found = None
    for A, B in [(2, 2), (2, 3), (3, 2), (3, 3)]:
        ex = search(A, B)
        if ex and found is None:
            found = (A, B, ex)
    print()
    if found is None:
        print("==> 探索範囲では、5条件+条件6 を満たす表はすべて格子に再構成できた。")
        print("    6条件で十分（健全）の証拠（小サイズの全列挙）。")
    else:
        A, B, (choices, t, reason) = found
        print(f"==> 反例あり (A={A},B={B}): {reason}")
        print(t)


if __name__ == "__main__":
    main()

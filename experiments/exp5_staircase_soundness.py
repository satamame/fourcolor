"""実験5: 三角階段（強い条件 is_well_formed）まで課せば健全か (docs/09 §6 の続き)。

ハニカム由来の表は必ず平面地図なので 4色で塗れる。健全性を疑うには
「ハニカム由来でない well-formed 表」を探す必要がある。is_well_formed は
ブロックの寸法・ブロック内のセル位置・ブロック間の整列を縛らないので、
そこに自由度がある。

ここでは各ブロックを 2x2 に固定した well-formed 表を小さいサイズで全列挙し、
4色で塗れないもの（＝健全性の反例）があるかを調べる。
  - 上三角ブロック (bj>bi): 空
  - 対角ブロック (bj==bi): 1セル（4通りの位置）
  - 下三角ブロック (bj<bi): 1セル（4通り）または「／」2セル（1通り）= 5通り

実行: python experiments/exp5_staircase_soundness.py
"""

import random
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fourcolor.axistable import EMPTY, SEP, AxisTable
from fourcolor.baseline import color_clusters
from exp4_soundness import constraint_graph


def build(n, diag, off):
    """2x2 ブロックの well-formed 候補表を作る。"""
    size = 3 * n - 1
    cells = [[EMPTY] * size for _ in range(size)]
    for b in range(n - 1):                       # ブロック間の区切り（十字）
        s = 3 * b + 2
        for k in range(size):
            cells[s][k] = SEP
            cells[k][s] = SEP
    di = oi = 0
    for bi in range(n):                          # bi=列ブロック, bj=行ブロック
        for bj in range(bi + 1):
            r0, c0 = 3 * bj, 3 * bi
            poss = [(r0, c0), (r0, c0 + 1), (r0 + 1, c0), (r0 + 1, c0 + 1)]
            if bi == bj:
                i, j = poss[diag[di]]
                cells[i][j] = 1
                di += 1
            else:
                ch = off[oi]
                oi += 1
                if ch < 4:
                    i, j = poss[ch]
                    cells[i][j] = 1
                else:                            # 「／」: 左下 + 右上
                    cells[r0 + 1][c0] = 1
                    cells[r0][c0 + 1] = 1
    return AxisTable(cells)


def _configs(n, n_off, cap, seed):
    """全列挙、または件数が cap を超えるならランダムサンプリング。"""
    full = 4 ** n * 5 ** n_off
    if cap is None or full <= cap:
        for diag in product(range(4), repeat=n):
            for off in product(range(5), repeat=n_off):
                yield diag, off
    else:
        rng = random.Random(seed)
        for _ in range(cap):
            yield (tuple(rng.randrange(4) for _ in range(n)),
                   tuple(rng.randrange(5) for _ in range(n_off)))


def search(n, cap=None, seed=0):
    n_off = n * (n - 1) // 2
    full = 4 ** n * 5 ** n_off
    mode = "全列挙" if cap is None or full <= cap else f"サンプリング{cap}"
    total = well = bad_struct = 0
    not_4col = []
    max_colors = 0
    for diag, off in _configs(n, n_off, cap, seed):
        total += 1
        t = build(n, diag, off)
        if not t.is_well_formed():
            bad_struct += 1
            continue
        well += 1
        adj = constraint_graph(t)
        if not adj:
            continue
        if color_clusters(adj, 4) is None:
            not_4col.append((diag, off, t))
        for c in range(1, 6):
            if color_clusters(adj, c) is not None:
                max_colors = max(max_colors, c)
                break
    print(f"n={n} ({mode}, 全{full}通り): 試行 {total}  well-formed {well}  "
          f"構造NG {bad_struct}  4色不能 {len(not_4col)}  "
          f"最大彩色数 {max_colors}", flush=True)
    return not_4col


def main():
    for n, cap in [(2, None), (3, None), (4, 300000)]:
        found = search(n, cap=cap)
        if found:
            diag, off, t = found[0]
            print(f"  反例 (n={n}): diag={diag} off={off}")
            print(t)
            adj = constraint_graph(t)
            print(f"  グラフ: 頂点{len(adj)} 辺{sum(len(s) for s in adj.values())//2}")
            break


if __name__ == "__main__":
    main()

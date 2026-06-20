"""実験10: 6条件は「必要条件」か（格子由来の表は必ず6条件を満たすか）(docs/10)。

逆向きの問い: 格子グラフから作った表は、必ず6条件（条件1〜5＋連続性条件6）を
満たすか。満たすなら「表の健全性 = 6条件」と定義してよく、前向きの戦略
（6条件を満たす表をすべて4色で塗れれば、どんな地図も塗れる）が成り立つ。

各条件が格子由来の表で必ず成り立つ理由:
  1,2 同じ横/縦ラベル = 同じ横/縦セグメント = 同じ国 → 同色
  3,4 ラベル差1 = 隣の国（国境を1本またぐ） → 別色
  5   ブロック = (格子の行)×(格子の列) = マス1個（全マスが国を持つ）
  6   横ラベル = 1つの格子行の連続セグメント → 行ブロックも連続（縦も同様）

ここでは samples とランダムな連結格子地図で、6条件＋再構成可能を機械確認する。

実行: python experiments/exp10_necessity.py
"""

import random
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fourcolor.mapcheck import build_edges
from fourcolor.square import SquareGrid
from fourcolor.squaretable import build_square_table, is_grid_realizable

from exp8_user_conditions import check_user_conditions
from exp9_contiguity import contiguity_ok

import square_sample01
import square_sample02_point


def random_connected_map(rows, cols, k, seed):
    """多源 BFS で rows×cols を k 個の連結領域に分ける（各国は辺連結）。"""
    rng = random.Random(seed)
    cell = [[None] * cols for _ in range(rows)]
    seeds = rng.sample([(r, c) for r in range(rows) for c in range(cols)], k)
    dq = deque()
    for idx, (r, c) in enumerate(seeds):
        cell[r][c] = idx
        dq.append((r, c))
    while dq:
        r, c = dq.popleft()
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and cell[nr][nc] is None:
                cell[nr][nc] = cell[r][c]
                dq.append((nr, nc))
    return {(r, c): f"C{cell[r][c]}" for r in range(rows) for c in range(cols)}


def satisfies_six(table):
    """6条件すべてを満たすか（条件1-5 が空＝OK、かつ条件6）。"""
    return not check_user_conditions(table) and contiguity_ok(table)


def check_map(grid, country_of):
    edges = build_edges(grid, country_of)
    table, _, _ = build_square_table(grid, edges, country_of)
    ok6 = satisfies_six(table)
    real, _ = is_grid_realizable(table)
    return ok6, real


def main():
    # サンプル（無色ノード入りの02 も含む）
    for mod, name in [(square_sample01, "サンプル01 (K4)"),
                      (square_sample02_point, "サンプル02 (無色)")]:
        grid, country_of, edges = mod.build_sample()
        ok6, real = check_map(grid, country_of)
        print(f"{name}: 6条件={ok6}  再構成可={real}")

    # ランダム連結格子地図
    fails = 0
    n = 3000
    for seed in range(n):
        rows = random.Random(seed).randint(2, 6)
        cols = random.Random(seed + 7).randint(2, 6)
        k = random.Random(seed + 13).randint(1, rows * cols)
        grid = SquareGrid(rows, cols)
        ok6, real = check_map(grid, random_connected_map(rows, cols, k, seed))
        if not (ok6 and real):
            fails += 1
    print(f"ランダム連結格子地図 {n} 個: 6条件＆再構成不可 {fails}")
    if fails == 0:
        print("==> 格子由来の表はすべて6条件を満たす（必要条件であることの強い証拠）。")


if __name__ == "__main__":
    main()

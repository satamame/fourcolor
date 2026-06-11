"""実験2A: 4彩色のビット分解 (XOR クラス) と国境エッジの幾何方向の相関 (docs/07)。

各地図について、色の入れ替えを除く全ての4彩色を列挙し、
「方向→XORクラスの対応で説明できる国境の割合 (整合スコア)」の
最良値・最悪値を測る。国なしの盤はスコア 1.0 (完全整合) になるので、
国 (クラスタ) を作ることでどれだけ崩れるかが見える。

実行: python experiments/exp2a_tait.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))

from fourcolor.baseline import build_cluster_graph
from fourcolor.honeycomb import HoneycombTriangle
from fourcolor.mapcheck import build_edges
from fourcolor.mapgen import random_honeycomb_map
from fourcolor.tait import (aligned_coloring, alignment_score, analyze_map,
                            border_directions, class_table)

import sample01_k4
import sample02_seven
import sample03_point

DIR_NAMES = {0: "横(行間)", 1: "＼(左が▲)", 2: "／(左が▽)"}


def show(name, edges, cap=20000):
    result = analyze_map(edges, cap=cap)
    trunc = " (打ち切り)" if result["truncated"] else ""
    print(f"--- {name} ---")
    print(f"  国: {result['n_countries']}  国境エッジ: {result['n_borders']}  "
          f"彩色数(色入替を除く): {result['n_colorings']}{trunc}")
    print(f"  整合スコア: 最良 {result['best_score']:.3f} "
          f"({result['n_best']}彩色)  最悪 {result['worst_score']:.3f}")
    print("  最良彩色の表 (方向 × XORクラス):")
    print("              XOR=1  XOR=2  XOR=3")
    for d in (0, 1, 2):
        row = result["best_table"][d]
        print(f"    {DIR_NAMES[d]:　<7}{row[1]:5d}  {row[2]:5d}  {row[3]:5d}")
    print()
    return result


def main():
    # 参照点: 国なしの盤 (全ノードが別の国) には完全整合 (1.0) の彩色が存在する。
    # 彩色数が膨大で列挙では届かないので、構成した整合彩色を直接評価する
    grid = HoneycombTriangle(4)
    country_of = {n: f"N{n[0]}_{n[1]}" for n in grid.nodes()}
    edges = build_edges(grid, country_of)
    dsu, _ = build_cluster_graph(edges)
    table = class_table(border_directions(edges, dsu), aligned_coloring(grid))
    print("--- 国なしの盤 (1辺4, 16ノード) — 構成した整合彩色 ---")
    print(f"  整合スコア: {alignment_score(table):.3f}")
    print("              XOR=1  XOR=2  XOR=3")
    for d in (0, 1, 2):
        print(f"    {DIR_NAMES[d]:　<7}{table[d][1]:5d}  {table[d][2]:5d}  "
              f"{table[d][3]:5d}")
    print()

    for sample, name in [(sample01_k4, "サンプル01 (4カ国 K4)"),
                         (sample02_seven, "サンプル02 (7カ国)"),
                         (sample03_point, "サンプル03 (7カ国+無色ノード)")]:
        _, _, edges = sample.build_sample()
        show(name, edges)

    # ランダム地図 (ハニカムモデル、1辺6)
    for seed in range(6):
        grid, country_of, edges = random_honeycomb_map(6, p_merge=0.55,
                                                       seed=seed)
        n = len(set(country_of.values()))
        if n > 14:  # 列挙が重くなりすぎる地図はスキップ
            print(f"--- ランダム地図 seed={seed} --- 国{n}個 (多すぎるためスキップ)")
            print()
            continue
        show(f"ランダム地図 seed={seed} (1辺6)", edges)


if __name__ == "__main__":
    main()

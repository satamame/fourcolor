"""ランダムなクラスタ地図を生成して4彩色し、盤面を表示するデモ。

使い方: python demo.py [盤サイズm] [seed]
"""

import string
import sys

from fourcolor import random_cluster_map, solve, violations
from fourcolor.baseline import build_cluster_graph


def main():
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    # p_merge は三角格子のボンドパーコレーション閾値 (約0.35) 未満にすると
    # クラスタが適度な大きさに散らばり、地図らしくなる
    board, edges = random_cluster_map(m, p_merge=0.3, seed=seed)
    dsu, adj = build_cluster_graph(edges)

    reps = sorted(adj)
    label = {rep: string.ascii_uppercase[i % 26] for i, rep in enumerate(reps)}

    colors = solve(edges, num_colors=4)
    if colors is None:
        print("4彩色に失敗 (四色定理に反するので、コードのバグのはず!)")
        return

    bad = violations(edges, colors)
    max_deg = max(len(nbs) for nbs in adj.values()) if adj else 0

    print(f"盤サイズ m={m}, seed={seed}")
    print(f"セル数: {len(board.cells())}  クラスタ数: {len(reps)}  最大クラスタ次数: {max_deg}")
    print(f"検証: {'OK (違反なし)' if not bad else f'違反 {len(bad)} 件!'}")
    print()
    print("クラスタ (国):")
    print(board.render(lambda c: label[dsu.find(c)]))
    print()
    print("彩色 (0-3 の4色):")
    print(board.render(lambda c: colors[c]))


if __name__ == "__main__":
    main()

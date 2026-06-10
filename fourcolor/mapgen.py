"""テスト用のランダムなクラスタ地図を三角形ヘックス盤上に生成する。

隣接セル対をシャッフルし、確率 p_merge で併合していく。
隣接セルの併合だけでクラスタを作るので、各クラスタは必ず連結
(=「1つのエリアは連続するノード群」の条件を満たす)。
クラスタ縮約グラフは平面グラフのマイナーなので自動的に平面グラフになり、
四色定理により 4 彩色解が必ず存在する。
"""

import random

from .dsu import DSU
from .hexgrid import TriBoard
from .verify import edge_key


def random_cluster_map(m, p_merge=0.5, seed=None):
    """1辺 m の三角形盤上にランダムなクラスタ地図を作る。

    返り値: (board, edges)
      edges = {(u, v): {"same_value": bool}}  (u, v は隣接セル対)
    """
    rng = random.Random(seed)
    board = TriBoard(m)
    pairs = board.adjacent_pairs()
    rng.shuffle(pairs)

    dsu = DSU()
    for u, v in pairs:
        if rng.random() < p_merge:
            dsu.union(u, v)

    edges = {
        edge_key(u, v): {"same_value": dsu.same(u, v)}
        for u, v in board.adjacent_pairs()
    }
    return board, edges

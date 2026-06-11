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
from .honeycomb import HoneycombTriangle
from .mapcheck import build_edges
from .verify import edge_key


def random_honeycomb_map(size, p_merge=0.55, seed=None):
    """ハニカムモデル (HoneycombTriangle) 上にランダムなクラスタ地図を作る。

    隣接ノード対を確率 p_merge で併合するので各国は必ず連結。無色ノードは無し。
    返り値: (grid, country_of, edges)
    """
    rng = random.Random(seed)
    grid = HoneycombTriangle(size)
    pairs = grid.adjacent_pairs()
    rng.shuffle(pairs)

    dsu = DSU()
    for u, v in pairs:
        if rng.random() < p_merge:
            dsu.union(u, v)

    reps = sorted({dsu.find(n) for n in grid.nodes()})
    name_of = {rep: f"N{i:02d}" for i, rep in enumerate(reps)}
    country_of = {n: name_of[dsu.find(n)] for n in grid.nodes()}
    return grid, country_of, build_edges(grid, country_of)


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

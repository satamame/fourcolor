"""四色問題プロジェクトの基盤パッケージ。

地図は「セルの隣接エッジ + same_value 属性」で表現する (アイデア2):

    edges = {
        (u, v): {"same_value": True},   # u, v は同一クラスタ (同色強制)
        (u, w): {"same_value": False},  # u, w は別クラスタ (異色強制)
    }

キーは正規化のため (小さい方, 大きい方) のタプルとする (edge_key を使う)。
"""

from .dsu import DSU
from .hexgrid import TriBoard
from .mapgen import random_cluster_map
from .verify import edge_key, violations, is_valid_coloring
from .baseline import Contradiction, build_cluster_graph, solve

__all__ = [
    "DSU",
    "TriBoard",
    "random_cluster_map",
    "edge_key",
    "violations",
    "is_valid_coloring",
    "Contradiction",
    "build_cluster_graph",
    "solve",
]

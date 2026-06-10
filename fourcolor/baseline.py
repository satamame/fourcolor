"""基準実装 (オラクル): クラスタ縮約 + バックトラック彩色。

遅くても確実な答え合わせ用であり、
ここを高速化・洗練することはプロジェクトの目的ではない。
本命のアルゴリズム (貪欲 + Kempe 鎖修復など) はこのオラクルと突き合わせて評価する。
"""

from .dsu import DSU


class Contradiction(ValueError):
    """same_value=True で繋がった2セルに same_value=False が課されている。"""


def build_cluster_graph(edges):
    """same_value=True を縮約し、クラスタ間の異色制約グラフを作る。

    返り値: (dsu, adj)
      dsu: セル → クラスタ代表元 を引くための Union-Find
      adj: {クラスタ代表元: 隣接クラスタ代表元の集合}
    """
    dsu = DSU()
    for (u, v), attr in edges.items():
        if attr["same_value"] is True:
            dsu.union(u, v)

    adj = {}
    for (u, v), attr in edges.items():
        if attr["same_value"] is None:  # 無色ノードに接するエッジ: 制約なし
            continue
        cu, cv = dsu.find(u), dsu.find(v)
        adj.setdefault(cu, set())
        adj.setdefault(cv, set())
        if attr["same_value"] is False:
            if cu == cv:
                raise Contradiction(f"edge {(u, v)} requires diff but same cluster")
            adj[cu].add(cv)
            adj[cv].add(cu)
    return dsu, adj


def color_clusters(adj, num_colors=4):
    """クラスタ縮約グラフをバックトラックで彩色する。

    成功なら {クラスタ代表元: 色番号}、不可能なら None。
    次数の大きいクラスタから順に試す (失敗の早期検出のため)。
    """
    order = sorted(adj, key=lambda c: -len(adj[c]))
    assignment = {}

    def backtrack(i):
        if i == len(order):
            return True
        c = order[i]
        used = {assignment[n] for n in adj[c] if n in assignment}
        for color in range(num_colors):
            if color not in used:
                assignment[c] = color
                if backtrack(i + 1):
                    return True
                del assignment[c]
        return False

    return dict(assignment) if backtrack(0) else None


def solve(edges, num_colors=4):
    """edges から各セルの色を決める。成功なら {セル: 色番号}、不可能なら None。

    矛盾したエッジがあれば Contradiction を送出する。
    無色ノード (same_value=None のエッジしか持たないノード) には色を付けない。
    """
    dsu, adj = build_cluster_graph(edges)
    cluster_colors = color_clusters(adj, num_colors)
    if cluster_colors is None:
        return None
    nodes = {n for e, a in edges.items() if a["same_value"] is not None for n in e}
    return {n: cluster_colors[dsu.find(n)] for n in nodes}

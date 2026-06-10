"""ハニカムグラフ表現（アイデア1「地図のハニカムグラフ化」の定式化）。

ノード = ハニカムグラフの頂点。したがって各ノードの隣接数は最大3。

幾何的な対応:
    ハニカム格子の頂点は、三角格子の小三角形と1対1に対応する（双対関係）。
    つまり「地図を小三角形に分割し、1つの国を連結な小三角形の集合で表す」ことが、
    そのまま「地図をハニカムグラフで表現する」ことになる。
    本モジュールでは、大きな正三角形を1辺 size 個の小三角形に分割した盤面を扱う。

ノード座標 (r, p):
    r = 1..size       … 行（上から）
    p = 1..2r-1       … 行内位置（左から）
    p が奇数 = 上向き三角形 ▲、p が偶数 = 下向き三角形 ▽

隣接（最大3）:
    ▲ (r, p) … 左 (r, p-1)、右 (r, p+1)、下 (r+1, p+1)
    ▽ (r, p) … 左 (r, p-1)、右 (r, p+1)、上 (r-1, p-1)
"""

import math

SQRT3 = math.sqrt(3.0)


class HoneycombTriangle:
    """1辺 size 個の小三角形に分割された正三角形盤面。ノード総数は size**2。"""

    def __init__(self, size):
        if size < 1:
            raise ValueError("size >= 1")
        self.size = size

    def is_valid(self, node):
        r, p = node
        return 1 <= r <= self.size and 1 <= p <= 2 * r - 1

    @staticmethod
    def is_up(node):
        return node[1] % 2 == 1

    def nodes(self):
        return [(r, p) for r in range(1, self.size + 1) for p in range(1, 2 * r)]

    def neighbors(self, node):
        r, p = node
        candidates = [(r, p - 1), (r, p + 1)]
        if self.is_up(node):
            candidates.append((r + 1, p + 1))  # 真下の ▽
        else:
            candidates.append((r - 1, p - 1))  # 真上の ▲
        return [c for c in candidates if self.is_valid(c)]

    def adjacent_pairs(self):
        """隣接ノード対 (u < v に正規化) を重複なく列挙する。"""
        pairs = []
        for node in self.nodes():
            for nb in self.neighbors(node):
                if node < nb:
                    pairs.append((node, nb))
        return pairs

    # ---- 描画用の幾何 ----

    def triangle_vertices(self, node, side=80.0, origin=(0.0, 0.0)):
        """ノードに対応する小三角形の3頂点座標を返す。"""
        r, p = node
        ox0, oy0 = origin
        h = side * SQRT3 / 2
        ox = ox0 + (self.size - r) * side / 2
        yt = oy0 + (r - 1) * h
        yb = oy0 + r * h
        if self.is_up(node):
            k = (p - 1) // 2
            return [(ox + k * side, yb),
                    (ox + (k + 1) * side, yb),
                    (ox + k * side + side / 2, yt)]
        k = (p - 2) // 2
        return [(ox + k * side + side / 2, yt),
                (ox + k * side + 3 * side / 2, yt),
                (ox + (k + 1) * side, yb)]

    def node_center(self, node, side=80.0, origin=(0.0, 0.0)):
        """小三角形の重心 = ハニカムグラフのノードを描く位置。"""
        vs = self.triangle_vertices(node, side, origin)
        return (sum(x for x, _ in vs) / 3, sum(y for _, y in vs) / 3)

    def vertex_to_nodes(self, side=1.0):
        """格子点 → その点に接するノードのリスト。

        盤の内部の格子点には6個のノード (三角形) が接する。
        「点で接する」(辺を共有しない) 関係の検出に使う。
        """
        m = {}
        for node in self.nodes():
            for x, y in self.triangle_vertices(node, side, (0.0, 0.0)):
                m.setdefault((round(x, 3), round(y, 3)), []).append(node)
        return m

    def shared_edge(self, u, v, side=80.0, origin=(0.0, 0.0)):
        """隣接する2ノードの小三角形が共有する辺の両端座標を返す（境界線の描画用）。"""
        round_pt = lambda pt: (round(pt[0], 3), round(pt[1], 3))
        vu = {round_pt(pt) for pt in self.triangle_vertices(u, side, origin)}
        vv = {round_pt(pt) for pt in self.triangle_vertices(v, side, origin)}
        common = sorted(vu & vv)
        if len(common) != 2:
            raise ValueError(f"{u} と {v} は隣接していない")
        return common

"""格子グラフ表現（四角版プロトタイプ）。

ハニカム（三角分割・次数≤3）の代わりに、地図を四角形に分割する。
ノード = 小さな正方形。各ノードの隣接は上下左右の最大4。

ノード座標 (r, c):  r = 行 0..rows-1、c = 列 0..cols-1（0始まり）。

三角版との違い:
  - 次数が最大4（三角は3）。
  - 辺の方向は横・縦の2つだけ（三角は3方向）。
  - 縦スキャンが「列をまっすぐ下へ」で済む（三角のジグザグが不要）。
"""


class SquareGrid:
    """rows×cols の正方形グリッド。"""

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def is_valid(self, node):
        r, c = node
        return 0 <= r < self.rows and 0 <= c < self.cols

    def nodes(self):
        return [(r, c) for r in range(self.rows) for c in range(self.cols)]

    def neighbors(self, node):
        r, c = node
        cand = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [n for n in cand if self.is_valid(n)]

    def adjacent_pairs(self):
        """隣接ノード対 (u < v に正規化) を重複なく列挙する。"""
        pairs = []
        for node in self.nodes():
            for nb in self.neighbors(node):
                if node < nb:
                    pairs.append((node, nb))
        return pairs

"""三角形ヘックス盤 (初期モデル: ノード=六角形セル、隣接最大6)。

セル座標は P(n, k) の 0 始まり:
    - n は行 (0 が頂点の行)、k は行内位置 (0 <= k <= n)

隣接 (最大6): 同じ行の左右、上の行の2つ、下の行の2つ。
セル隣接グラフは三角格子であり、各セルの隣接数は 2 (角) / 4 (辺上) / 6 (内部)。
"""


class TriBoard:
    def __init__(self, m):
        """1辺 m セルの三角形盤。セル総数は m(m+1)/2。"""
        if m < 1:
            raise ValueError("m >= 1")
        self.m = m

    def is_valid(self, cell):
        n, k = cell
        return 0 <= k <= n <= self.m - 1

    def cells(self):
        return [(n, k) for n in range(self.m) for k in range(n + 1)]

    def neighbors(self, cell):
        n, k = cell
        candidates = [
            (n, k - 1), (n, k + 1),          # 同じ行
            (n - 1, k - 1), (n - 1, k),      # 上の行
            (n + 1, k), (n + 1, k + 1),      # 下の行
        ]
        return [c for c in candidates if self.is_valid(c)]

    def adjacent_pairs(self):
        """盤上の隣接セル対 (u < v に正規化) を重複なく列挙する。"""
        pairs = []
        for cell in self.cells():
            for nb in self.neighbors(cell):
                if cell < nb:
                    pairs.append((cell, nb))
        return pairs

    def render(self, label_of, cell_width=2):
        """各セルをラベル文字列にして三角形に整形する (デバッグ・デモ用)。"""
        lines = []
        for n in range(self.m):
            row = [str(label_of((n, k))).rjust(cell_width) for k in range(n + 1)]
            indent = " " * (cell_width * (self.m - 1 - n) // 2)
            lines.append(indent + " ".join(row))
        return "\n".join(lines)

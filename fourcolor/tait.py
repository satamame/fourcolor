"""案2A の道具: 4彩色のビット分解と「国境エッジの方向 × XOR クラス」分析 (docs/07)。

4色 {0,1,2,3} を2ビット (Z2×Z2) とみなすと、国境エッジの両端の色の XOR は
1, 2, 3 のどれか (Klein の4元群の非零元) になり、国境は3クラスに分かれる。
一方、盤面のエッジには幾何的な3方向がある:

  方向0 … 行間 (▲とその真下の▽)。共有辺は水平
  方向1 … 行内で左が▲ (p が奇数)。共有辺は「＼」
  方向2 … 行内で左が▽ (p が偶数)。共有辺は「／」

国なしの盤では「方向 d を越えると色が g_d だけ XOR で変わる」完全整合の
4彩色が存在する (aligned_coloring)。国 (クラスタ) を作ったとき、
この整合がどれだけ崩れるかを測るのが実験2A。
"""

from .baseline import build_cluster_graph


def edge_direction(u, v):
    """隣接ノード対のエッジの幾何方向 (0, 1, 2) を返す。"""
    if u[0] != v[0]:
        return 0  # 行間 (共有辺は水平)
    p = min(u[1], v[1])
    return 1 if p % 2 == 1 else 2  # 行内 (左が▲なら「＼」、▽なら「／」)


def xor_class(c1, c2):
    """2色 (0..3) の XOR クラス (1, 2, 3)。同色なら 0。"""
    return c1 ^ c2


def border_directions(edges, dsu):
    """国境エッジを (方向, 国1の代表, 国2の代表) のリストにする。"""
    result = []
    for (u, v), attr in edges.items():
        if attr["same_value"] is False:
            result.append((edge_direction(u, v), dsu.find(u), dsu.find(v)))
    return result


def class_table(borders, cluster_colors):
    """3×3 の集計表 table[方向][XORクラス] = 本数 を返す。"""
    table = {d: {x: 0 for x in (1, 2, 3)} for d in (0, 1, 2)}
    for d, a, b in borders:
        table[d][xor_class(cluster_colors[a], cluster_colors[b])] += 1
    return table


def alignment_score(table):
    """方向→XORクラスの対応 (全単射6通り) のうち、最も多くの国境を
    説明できる割合 (0..1)。1.0 = 完全整合。"""
    total = sum(n for row in table.values() for n in row.values())
    if total == 0:
        return 1.0
    perms = [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]
    best = max(sum(table[d][sigma[d]] for d in (0, 1, 2)) for sigma in perms)
    return best / total


def aligned_coloring(grid):
    """国なしの盤 (全ノードが別の国) に対する、方向と完全整合した4彩色。

    方向0で XOR 3、方向1で XOR 1、方向2で XOR 2 だけ色が変わる。
    """
    colors = {}
    row_start = 0
    for r in range(1, grid.size + 1):
        c = row_start
        for p in range(1, 2 * r):
            colors[(r, p)] = c
            c ^= 1 if p % 2 == 1 else 2
        row_start ^= 2  # 縦(3) と行内先頭(1) を経由: 3^1 = 2
    return colors


def enumerate_colorings(adj, num_colors=4, cap=None):
    """クラスタ隣接グラフの彩色を、色の入れ替えを除いて全列挙する。

    「新しい色は、既に使った色数+1番目しか使えない」という正準形で列挙する
    (first-occurrence 標準形)。返り値: (彩色のリスト, 打ち切ったか)。
    """
    order = sorted(adj, key=lambda c: (-len(adj[c]), c))
    results = []
    truncated = [False]
    assignment = {}

    def backtrack(i, used):
        if cap is not None and len(results) >= cap:
            truncated[0] = True
            return
        if i == len(order):
            results.append(dict(assignment))
            return
        node = order[i]
        forbidden = {assignment[n] for n in adj[node] if n in assignment}
        for col in range(min(used + 1, num_colors)):
            if col in forbidden:
                continue
            assignment[node] = col
            backtrack(i + 1, used + (1 if col == used else 0))
            del assignment[node]

    backtrack(0, 0)
    return results, truncated[0]


def analyze_map(edges, cap=20000):
    """地図1枚の実験2A: 全彩色を列挙し、整合スコアの分布と最良の表を返す。

    返り値: dict
      n_countries, n_borders, n_colorings, truncated,
      best_score, n_best (最良スコアの彩色数), worst_score, best_table
    """
    dsu, adj = build_cluster_graph(edges)
    borders = border_directions(edges, dsu)
    colorings, truncated = enumerate_colorings(adj, cap=cap)
    best_score, worst_score = -1.0, 2.0
    best_table, n_best = None, 0
    for coloring in colorings:
        table = class_table(borders, coloring)
        score = alignment_score(table)
        if score > best_score + 1e-12:
            best_score, best_table, n_best = score, table, 1
        elif abs(score - best_score) <= 1e-12:
            n_best += 1
        worst_score = min(worst_score, score)
    return {
        "n_countries": len(adj),
        "n_borders": len(borders),
        "n_colorings": len(colorings),
        "truncated": truncated,
        "best_score": best_score,
        "n_best": n_best,
        "worst_score": worst_score,
        "best_table": best_table,
    }

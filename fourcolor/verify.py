"""彩色の検証器。

どんなアルゴリズムを試しても、出力はここを通して機械的に確認する。
(自己申告の「成功」を信じないための独立した審判。)
"""


def edge_key(u, v):
    """エッジのキーを (小さい方, 大きい方) に正規化する。"""
    return (u, v) if u < v else (v, u)


def violations(edges, colors):
    """制約違反のリストを返す。空リストなら彩色は正しい。

    edges:  {(u, v): {"same_value": bool または None}}
            None は無色ノードに接するエッジで、制約なし (検査もしない)。
    colors: {node: 色 (任意のハッシュ可能値)}。無色ノードは含まれなくてよい。
    """
    found = []
    for (u, v), attr in edges.items():
        sv = attr["same_value"]
        if sv is None:
            continue
        if u not in colors or v not in colors:
            found.append(("uncolored", u, v))
            continue
        if sv and colors[u] != colors[v]:
            found.append(("same_violated", u, v))
        elif not sv and colors[u] == colors[v]:
            found.append(("diff_violated", u, v))
    return found


def is_valid_coloring(edges, colors):
    return not violations(edges, colors)

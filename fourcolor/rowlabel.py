"""行ラベリング: 行単位の仮ラベル付けと行間の併合 (docs/05)。

エッジの same_value だけを入力として、各ノードに仮ラベル (r, c) を付ける。
(r, c) は「行 r の c 番目のセグメント (国の断片)」の識別子。

行内の規則:
  - 行で最初の非無色ノードに (r, 1)
  - 前のエッジが True なら前と同じラベル / False なら c を +1
  - 前のノードが無色 (None) なら、最後にセットした c に +2
  - 無色ノードにはラベルを付けない

c が1違いのセグメントは異色が必要、2違いは「この場所では制約なし」。
"""

from .dsu import DSU
from .verify import edge_key


def colorless_nodes(grid, edges):
    """無色ノードの集合をエッジ情報だけから復元する。

    無色ノード = 接するエッジがすべて same_value=None のノード。
    (注意: 無色ノードだけに囲まれた1セルの国はエッジ情報からは
     無色ノードと区別できないが、そのような地図は扱わない)
    """
    incident = {n: [] for n in grid.nodes()}
    for (u, v), attr in edges.items():
        incident[u].append(attr["same_value"])
        incident[v].append(attr["same_value"])
    return {n for n, svs in incident.items()
            if svs and all(sv is None for sv in svs)}


def row_labels(grid, edges):
    """各ノードに仮ラベル (r, c) を付ける。無色ノードは含まれない。

    返り値: {ノード: (r, c)}
    """
    colorless = colorless_nodes(grid, edges)
    labels = {}
    for r in range(1, grid.size + 1):
        last_c = None  # この行で最後にセットした c
        for p in range(1, 2 * r):
            node = (r, p)
            if node in colorless:
                continue
            if last_c is None:
                c = 1  # 行で最初の非無色ノード
            else:
                sv = edges[edge_key((r, p - 1), node)]["same_value"]
                if sv is True:
                    c = last_c        # 前のノードと同じセグメント
                elif sv is False:
                    c = last_c + 1    # 国境を越えた
                else:
                    c = last_c + 2    # 前のノードが無色 (制約なしのギャップ)
            labels[node] = (r, c)
            last_c = c
    return labels


def merge_labels(grid, edges, labels):
    """行間の調整の前半: 縦の True エッジでセグメントを併合し、異色制約を集める。

    返り値: (dsu, constraints)
      dsu         … 仮ラベルの Union-Find (find(ラベル) が国の代表ラベル)
      constraints … {frozenset({代表ラベル1, 代表ラベル2})} 異色制約の集合
    """
    dsu = DSU()
    for node, label in labels.items():
        dsu.find(label)  # 全ラベルを登録 (孤立した国も代表を持つように)
    for (u, v), attr in edges.items():
        if attr["same_value"] is True:
            dsu.union(labels[u], labels[v])
    constraints = set()
    for (u, v), attr in edges.items():
        if attr["same_value"] is False:
            constraints.add(frozenset((dsu.find(labels[u]),
                                       dsu.find(labels[v]))))
    return dsu, constraints


def label_clusters(grid, edges):
    """行ラベリング → 併合の全体を実行し、国の分割と隣接を返す。

    返り値: (labels, countries, adjacency)
      labels    … {ノード: (r, c)}
      countries … {代表ラベル: frozenset(ノード)} 併合後の国
      adjacency … {frozenset({代表ラベル1, 代表ラベル2})} 国同士の異色制約
    """
    labels = row_labels(grid, edges)
    dsu, constraints = merge_labels(grid, edges, labels)
    countries = {}
    for node, label in labels.items():
        countries.setdefault(dsu.find(label), set()).add(node)
    countries = {rep: frozenset(nodes) for rep, nodes in countries.items()}
    return labels, countries, constraints

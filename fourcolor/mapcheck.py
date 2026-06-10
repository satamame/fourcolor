"""地図のハニカム表現を組み立て、表現として妥当かを機械検証する共通ヘルパー。

country_of の値が None のノードは「無色ノード」:
どの国にも属さず色も塗らない。元の地図で「4カ国以上 (盤面の都合では7カ国以上)
が1点に集まる場所」を、小さな無色の三角形に膨らませて表現するために使う。
無色ノードに接するエッジは same_value=None (制約なし) となる。
"""

from collections import deque

from .verify import edge_key


def build_edges(grid, country_of):
    """国の割り当てから「塗られていない地図」の入力形式 edges を作る。

    same_value: True=同じ国 / False=国境 / None=無色ノードに接する (制約なし)
    """
    def attr(u, v):
        if country_of[u] is None or country_of[v] is None:
            return None
        return country_of[u] == country_of[v]

    return {
        edge_key(u, v): {"same_value": attr(u, v)}
        for u, v in grid.adjacent_pairs()
    }


def _connected_components(cells, grid):
    cells = set(cells)
    components = []
    while cells:
        start = next(iter(cells))
        seen, queue = {start}, deque([start])
        while queue:
            cur = queue.popleft()
            for nb in grid.neighbors(cur):
                if nb in cells and nb not in seen:
                    seen.add(nb)
                    queue.append(nb)
        components.append(seen)
        cells -= seen
    return components


def representation_stats(grid, country_of, edges):
    """表現の妥当性を検証し、統計を返す。違反があれば AssertionError。

    検証項目:
      1. 全ノードに国 (または無色 None) が割り当てられている
      2. 隣接数は最大3 (ハニカムグラフの性質)
      3. edges の same_value が country_of と一致している
      4. 各国は連結 (「1つのエリア = 連続するノード群」)

    返り値:
      "borders"        … {frozenset({国1, 国2}): 国境エッジ本数}
      "meeting_points" … 無色ノードの連結成分 (=膨らませた点) ごとに、
                         そこに辺または点で接している国の一覧
    """
    nodes = grid.nodes()
    assert set(country_of) == set(nodes), "全ノードに国が割り当てられていること"

    max_deg = max(len(grid.neighbors(n)) for n in nodes)
    assert max_deg <= 3, f"隣接数が3を超えた: {max_deg}"

    for (u, v), attr in edges.items():
        if country_of[u] is None or country_of[v] is None:
            expected = None
        else:
            expected = country_of[u] == country_of[v]
        assert attr["same_value"] == expected, f"edge {(u, v)} の same_value が不整合"

    countries = sorted({c for c in country_of.values() if c is not None})
    for country in countries:
        members = {n for n in nodes if country_of[n] == country}
        assert len(_connected_components(members, grid)) == 1, \
            f"国 {country} が連結でない"

    borders = {}
    for (u, v), attr in edges.items():
        if attr["same_value"] is False:
            key = frozenset((country_of[u], country_of[v]))
            borders[key] = borders.get(key, 0) + 1

    # 無色ノードの連結成分ごとに「その点に集まっている国」を求める。
    # 点で接する関係 (辺は共有しない) も含むため、格子点の共有で判定する。
    colorless = [n for n in nodes if country_of[n] is None]
    vertex_map = grid.vertex_to_nodes()
    node_keys = {}
    for vkey, vnodes in vertex_map.items():
        for n in vnodes:
            node_keys.setdefault(n, []).append(vkey)
    meeting_points = []
    for blob in _connected_components(colorless, grid):
        touching = set()
        for cell in blob:
            for vkey in node_keys[cell]:
                touching.update(vertex_map[vkey])
        met = sorted({country_of[n] for n in touching
                      if country_of[n] is not None})
        meeting_points.append({"blob": sorted(blob), "countries": met})

    n_same = sum(1 for a in edges.values() if a["same_value"] is True)
    n_diff = sum(1 for a in edges.values() if a["same_value"] is False)
    return {
        "nodes": len(nodes),
        "edges": len(edges),
        "same_edges": n_same,
        "diff_edges": n_diff,
        "none_edges": len(edges) - n_same - n_diff,
        "countries": countries,
        "colorless_nodes": len(colorless),
        "max_degree": max_deg,
        "borders": borders,
        "meeting_points": meeting_points,
    }

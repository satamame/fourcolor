"""行ラベリング (docs/05) のデモ: 3つのサンプルにラベルを付けて結果を表示する。

実行: python samples/rowlabel_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fourcolor.baseline import build_cluster_graph
from fourcolor.rowlabel import label_clusters

import sample01_k4
import sample02_seven
import sample03_point


def triangle(grid, text_of, width=2):
    """盤面を三角形のテキストにする。"""
    lines = []
    for r in range(1, grid.size + 1):
        row = [str(text_of((r, p))).rjust(width) for p in range(1, 2 * r)]
        indent = " " * (width * (grid.size - r) // 2 + (grid.size - r))
        lines.append(indent + " ".join(row))
    return "\n".join(lines)


def show(sample, title):
    grid, country_of, edges = sample.build_sample()
    labels, countries, adjacency = label_clusters(grid, edges)

    print(f"=== {title} ===")
    print("国 (・=無色ノード):")
    print(triangle(grid, lambda n: country_of[n] or "・"))
    print()
    print("仮ラベルの c (・=無色ノード):")
    print(triangle(grid, lambda n: labels[n][1] if n in labels else "・"))
    print()

    n_segments = len(set(labels.values()))
    print(f"セグメント数: {n_segments} → 併合後の国: {len(countries)}")
    print("併合結果 (代表ラベル ← そのセグメントたち):")
    rep_to_country = {}
    for rep, nodes in sorted(countries.items()):
        segs = sorted({labels[n] for n in nodes})
        name = country_of[next(iter(nodes))]
        rep_to_country[rep] = name
        print(f"  {rep} = 国{name} ← {segs}")
    pairs = sorted(sorted((rep_to_country[a], rep_to_country[b]))
                   for pair in adjacency for a, b in [tuple(pair)])
    print(f"異色制約 ({len(adjacency)}組): " +
          ", ".join(f"{a}-{b}" for a, b in pairs))

    # baseline の縮約と一致するか (テストと同じ検証)
    dsu, adj = build_cluster_graph(edges)
    base_partition = {}
    for n in labels:
        base_partition.setdefault(dsu.find(n), set()).add(n)
    ok = set(map(frozenset, base_partition.values())) == set(countries.values())
    print(f"baseline の縮約と一致: {'OK' if ok else 'NG!'}")
    print()


def main():
    show(sample01_k4, "サンプル01 (4カ国 K4)")
    show(sample02_seven, "サンプル02 (7カ国)")
    show(sample03_point, "サンプル03 (7カ国が1点に集まる・無色ノード)")


if __name__ == "__main__":
    main()

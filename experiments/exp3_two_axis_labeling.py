"""実験3: 「横ラベル・縦ラベルの2軸」アイデアの検証 (会話メモ、未確定)。

ユーザーが思いついた手法:
  - 行ラベル (r, c) を、行間で +2 オフセットした「横ラベル」(1個の整数) にする。
  - 同じ要領で「縦ラベル」も作る (列 k = (p-1)//2 ごとにスキャンし、
    行と同じ True/False/None ルールで +1/+2 する)。
  - 横ラベル・縦ラベルを座標軸にして各ノードを表に置く。
  - 「横(縦)ラベルが同じなら同色」「横(縦)ラベルの差が1なら異色」というルールが、
    元の地図の「同じ国/国境」と一致するかを調べる。

ここでは2つを検証する:
  (1) 横ラベル同じ ∪ 縦ラベル同じ の推移閉包が、国の分割 (country_of) と一致するか。
  (2) 横ラベル差1 ∪ 縦ラベル差1 から得られる「国どうしの異色制約」が、
      EXPECTED_BORDERS (= baseline の縮約) とちょうど一致するか
      (過不足がないか)。

実行: python experiments/exp3_two_axis_labeling.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))

from fourcolor.axistable import (column_groups, cumulative_labels,
                                 row_groups)
from fourcolor.dsu import DSU
from fourcolor.rowlabel import colorless_nodes

import sample01_k4
import sample02_seven
import sample03_point


def check_sample(name, build_sample):
    grid, country_of, edges = build_sample()
    colorless = colorless_nodes(grid, edges)
    nodes = [n for n in grid.nodes() if n not in colorless]

    # 無色ノードにもラベルが付くが、ここでは非無色ノードだけを見る
    h_labels = cumulative_labels(row_groups(grid), edges)
    v_labels = cumulative_labels(column_groups(grid), edges)

    print(f"--- {name} ---")

    # (1) 横同じ ∪ 縦同じ の推移閉包 = 国の分割か
    dsu = DSU()
    for n in nodes:
        dsu.find(n)
    by_h = {}
    by_v = {}
    for n in nodes:
        by_h.setdefault(h_labels[n], []).append(n)
        by_v.setdefault(v_labels[n], []).append(n)
    for group in by_h.values():
        for a, b in zip(group, group[1:]):
            dsu.union(a, b)
    for group in by_v.values():
        for a, b in zip(group, group[1:]):
            dsu.union(a, b)

    # 推移閉包クラスタ vs 国
    clusters = {}
    for n in nodes:
        clusters.setdefault(dsu.find(n), set()).add(n)
    countries = {}
    for n in nodes:
        countries.setdefault(country_of[n], set()).add(n)

    cluster_sets = set(frozenset(s) for s in clusters.values())
    country_sets = set(frozenset(s) for s in countries.values())
    match1 = cluster_sets == country_sets
    print(f"  (1) 軸ラベルの推移閉包 = 国の分割: {match1}")
    if not match1:
        print(f"      クラスタ: {[sorted(s) for s in cluster_sets]}")
        print(f"      国      : {[sorted(s) for s in country_sets]}")

    # (2) 横差1 ∪ 縦差1 から得られる国どうしの異色制約
    def diff1_country_pairs(labels):
        by_label = {}
        for n in nodes:
            by_label.setdefault(labels[n], []).append(n)
        pairs = set()
        values = sorted(by_label)
        for val in values:
            if val + 1 in by_label:
                for u in by_label[val]:
                    for v in by_label[val + 1]:
                        cu, cv = country_of[u], country_of[v]
                        if cu != cv:
                            pairs.add(frozenset((cu, cv)))
                        else:
                            pairs.add(("SAME-COUNTRY", cu, u, v))
            # 一応、不正な「同じ国の中で差1」が無いかも見る
        return pairs

    h_pairs = diff1_country_pairs(h_labels)
    v_pairs = diff1_country_pairs(v_labels)

    bad = {p for p in (h_pairs | v_pairs) if not isinstance(p, frozenset)}
    border_pairs = {p for p in (h_pairs | v_pairs) if isinstance(p, frozenset)}

    expected = build_sample.__module__  # placeholder, real EXPECTED set below
    print(f"  (2) 横差1∪縦差1 から得た異色国ペア数: {len(border_pairs)}")
    if bad:
        print(f"      !! 同じ国の中で差1になっている箇所: {bad}")
    return border_pairs


def main():
    results = {}
    results["サンプル01"] = (check_sample("サンプル01 (4カ国 K4)", sample01_k4.build_sample),
                            sample01_k4.EXPECTED_BORDERS)
    results["サンプル02"] = (check_sample("サンプル02 (7カ国)", sample02_seven.build_sample),
                            sample02_seven.EXPECTED_BORDERS)
    results["サンプル03"] = (check_sample("サンプル03 (無色ノード)", sample03_point.build_sample),
                            sample03_point.EXPECTED_BORDERS)

    print()
    for name, (got, expected) in results.items():
        match = got == expected
        print(f"{name}: 横差1∪縦差1 の異色ペア == EXPECTED_BORDERS ? {match}")
        if not match:
            print(f"  得られた集合 : {sorted(map(sorted, got))}")
            print(f"  期待される集合: {sorted(map(sorted, expected))}")
            print(f"  不足 (missing): {sorted(map(sorted, expected - got))}")
            print(f"  余分 (extra)  : {sorted(map(sorted, got - expected))}")


if __name__ == "__main__":
    main()

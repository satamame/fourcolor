"""ハニカムグラフ → 横ラベル・縦ラベル2軸の表 (docs/09)。

各ノードに横ラベル h と縦ラベル v を付け（rowlabel と同じ規則。行・列の
区切りでは +2 する）、(h, v) を座標とする2次元の表を作る。

セルの値は3種類（数値で統一）:
  -1 (SEP)   … 区切りセル。横/縦ラベルが +2 で飛んだ位置（改行・無色ノード）。
               区切られたブロックの境界を表す。
   0 (EMPTY) … ブロック内だが対応ノードが無い空きセル。
  >=1        … ノードセルの仮色値。初期値は「国ごとに一意の整数」
               （= N色の正しい塗り分け。ここから色数を 4 以下へ減らす）。
"""

from .rowlabel import colorless_nodes
from .verify import edge_key

SEP = -1    # 区切りセル
EMPTY = 0   # ブロック内の空きセル


def row_groups(grid):
    """行スキャンの順序（行ごとのノード列）。"""
    return [[(r, p) for p in range(1, 2 * r)] for r in range(1, grid.size + 1)]


def column_groups(grid):
    """列スキャンの順序。列 k=(p-1)//2 ごとに、盤の左辺に沿う鋸歯状に辿る。"""
    groups = []
    for k in range(grid.size):
        seq = []
        r = k + 1
        while True:
            up = (r, 2 * k + 1)
            if not grid.is_valid(up):
                break
            seq.append(up)
            down = (r + 1, 2 * k + 2)
            if not grid.is_valid(down):
                break
            seq.append(down)
            r += 1
        groups.append(seq)
    return groups


def cumulative_labels(groups, edges, colorless):
    """グループごとに番号を振り、グループ間は最後の値 +2 から続ける。"""
    labels = {}
    offset = 0
    for group in groups:
        last_c = None
        prev = None
        for node in group:
            if node in colorless:
                prev = node
                continue
            if last_c is None:
                c = offset + 1
            else:
                sv = edges[edge_key(prev, node)]["same_value"]
                if sv is True:
                    c = last_c          # 同じセグメント
                elif sv is False:
                    c = last_c + 1      # 国境を越えた
                else:
                    c = last_c + 2      # 無色ノードを挟んだ
            labels[node] = c
            last_c = c
            prev = node
        if last_c is not None:
            offset = last_c + 1         # 次のグループの先頭は last_c + 2 になる
    return labels


def axis_labels(grid, edges):
    """各ノードの横ラベル h と縦ラベル v を返す。"""
    colorless = colorless_nodes(grid, edges)
    h = cumulative_labels(row_groups(grid), edges, colorless)
    v = cumulative_labels(column_groups(grid), edges, colorless)
    return h, v


def country_seed(nodes, country_of):
    """国ごとに一意の整数 (>=1) を、国名のソート順で割り当てる。"""
    names = sorted({country_of[n] for n in nodes},
                   key=lambda c: (c is None, str(c)))
    return {name: i + 1 for i, name in enumerate(names)}


def build_axis_table(grid, edges, country_of):
    """2軸ラベル表を作る。

    返り値: (table, h, v, cid)
      table … table[i][j] がセル値 (-1/0/>=1)。i 行目は縦ラベル v=i+1、
              j 列目は横ラベル h=j+1 に対応する。
      h, v  … {ノード: ラベル}（無色ノードは含まない）
      cid   … {国: 仮色値(>=1)}
    """
    h, v = axis_labels(grid, edges)
    nodes = list(h)  # ラベルを持つ（= 無色でない）ノード
    cid = country_seed(nodes, country_of)
    node_cell = {(h[n], v[n]): cid[country_of[n]] for n in nodes}
    used_h = set(h.values())
    used_v = set(v.values())
    max_h, max_v = max(used_h), max(used_v)
    table = []
    for vv in range(1, max_v + 1):
        row = []
        for hh in range(1, max_h + 1):
            if hh not in used_h or vv not in used_v:
                row.append(SEP)
            else:
                row.append(node_cell.get((hh, vv), EMPTY))
        table.append(row)
    return table, h, v, cid


def table_to_str(table):
    """表を見やすい文字列にする（区切り=空白, 空き=., ノード=仮色値）。"""
    def cell(x):
        if x == SEP:
            return "  "
        if x == EMPTY:
            return " ."
        return f"{x:2d}"
    return "\n".join("".join(cell(x) for x in row) for row in table)

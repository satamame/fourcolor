"""ハニカムグラフ → 横ラベル・縦ラベル2軸の表 (docs/09)。

各ノードに横ラベル h と縦ラベル v を付け（行・列の区切りでは +2 する）、
(h, v) を座標とする2次元の表を作る。無色ノードにも列・行を与える（表現B）。

セルの値（数値で統一。符号で「ノードの有無」が読める）:
  >=1 (有色)    … 有色ノードの仮色値。初期値は「国ごとに一意の整数」
                  （= N色の正しい塗り分け。ここから色数を 4 以下へ減らす）。
   0 (COLORLESS)… 無色ノードのセル（実在するノードだが色なし・制約なし）。
  -1 (EMPTY)    … ブロック内だがノードが無い空きセル。
  -2 (SEP)      … 区切りセル（ブロックの外、境界）。
  → 値 >= 0 ⇔ そのマスにハニカムのノードがある。
"""

from .rowlabel import colorless_nodes
from .verify import edge_key

SEP = -2        # 区切りセル
EMPTY = -1      # ブロック内の空きセル
COLORLESS = 0   # 無色ノードのセル


def _consecutive_runs(indices):
    """ソート済みの整数列を、連続するかたまりに分ける。"""
    runs = []
    for x in indices:
        if runs and x == runs[-1][-1] + 1:
            runs[-1].append(x)
        else:
            runs.append([x])
    return runs


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


def cumulative_labels(groups, edges):
    """グループごとに番号を振り、グループ間は最後の値 +2 から続ける。

    無色ノードにも番号を振る（None エッジは国境と同じ +1 として扱う）。
    こうすると無色ノードが列・行を1つ占め、規則的な三角階段が保たれる。
    """
    labels = {}
    offset = 0
    for group in groups:
        last_c = None
        prev = None
        for node in group:
            if last_c is None:
                c = offset + 1
            else:
                sv = edges[edge_key(prev, node)]["same_value"]
                c = last_c if sv is True else last_c + 1  # False も None も +1
            labels[node] = c
            last_c = c
            prev = node
        if last_c is not None:
            offset = last_c + 1         # 次のグループの先頭は last_c + 2 になる
    return labels


def axis_labels(grid, edges):
    """各ノード（無色ノードを含む）の横ラベル h と縦ラベル v を返す。"""
    h = cumulative_labels(row_groups(grid), edges)
    v = cumulative_labels(column_groups(grid), edges)
    return h, v


def country_seed(nodes, country_of):
    """国ごとに一意の整数 (>=1) を、国名のソート順で割り当てる。"""
    names = sorted({country_of[n] for n in nodes},
                   key=lambda c: (c is None, str(c)))
    return {name: i + 1 for i, name in enumerate(names)}


def build_axis_table(grid, edges, country_of):
    """2軸ラベル表を作る。

    返り値: (table, h, v, cid)
      table … table[i][j] がセル値。i 行目は縦ラベル v=i+1、j 列目は横ラベル h=j+1。
      h, v  … {ノード: ラベル}（無色ノードも含む）
      cid   … {国: 仮色値(>=1)}
    """
    h, v = axis_labels(grid, edges)
    colorless = colorless_nodes(grid, edges)
    colored = [n for n in h if n not in colorless]
    cid = country_seed(colored, country_of)
    node_cell = {}
    for n in h:
        node_cell[(h[n], v[n])] = (COLORLESS if n in colorless
                                   else cid[country_of[n]])
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
    """表を見やすい文字列にする（区切り=空白, 空き=., 無色=o, 有色=仮色値）。"""
    def cell(x):
        if x == SEP:
            return "  "
        if x == EMPTY:
            return " ."
        if x == COLORLESS:
            return " o"
        return f"{x:2d}"
    return "\n".join("".join(cell(x) for x in row) for row in table)


class AxisTable:
    """2軸ラベル表そのものを表す抽象データ構造 (docs/09 §5)。

    `cells[i][j]` が「縦ラベル v=i+1 行 × 横ラベル h=j+1 列」のセル値。
    値の意味はモジュール冒頭のとおり（>=1 有色 / 0 無色 / -1 空き / -2 区切り）。

    ハニカムグラフは構成方法の一つ (`from_honeycomb`)。表ができたあとは、
    ハニカムを参照せずに表だけで仮色値の操作・ルール検証・構造検証ができる。
    生の2次元リストから直接作る (`AxisTable(cells)`) のがハニカム以外の入口。
    """

    def __init__(self, cells):
        self.cells = [list(row) for row in cells]
        self.n_rows = len(self.cells)
        self.n_cols = len(self.cells[0]) if self.cells else 0
        self.cid = None  # from_honeycomb のとき {国: 仮色値}

    @classmethod
    def from_honeycomb(cls, grid, edges, country_of):
        table, _h, _v, cid = build_axis_table(grid, edges, country_of)
        obj = cls(table)
        obj.cid = cid
        return obj

    def __repr__(self):
        return (f"AxisTable({self.n_rows}x{self.n_cols}, "
                f"colors={self.n_colors()})")

    def __str__(self):
        return table_to_str(self.cells)

    # ---- 参照 ----

    def colored_positions(self):
        return [(i, j) for i in range(self.n_rows) for j in range(self.n_cols)
                if self.cells[i][j] >= 1]

    def colors(self):
        return {self.cells[i][j] for i, j in self.colored_positions()}

    def n_colors(self):
        return len(self.colors())

    def _col_colors(self, j):
        return {self.cells[i][j] for i in range(self.n_rows)
                if self.cells[i][j] >= 1}

    def _row_colors(self, i):
        return {x for x in self.cells[i] if x >= 1}

    # ---- 仮色値の操作 ----

    def recolor(self, old, new):
        """仮色値 old のセルをすべて new にする（old, new は 1 以上）。"""
        if old < 1 or new < 1:
            raise ValueError("仮色値は 1 以上")
        for row in self.cells:
            for j, x in enumerate(row):
                if x == old:
                    row[j] = new

    def merge(self, a, b):
        """色 b を色 a に併合する（b を消す。色数が1減る）。"""
        if a != b:
            self.recolor(b, a)

    # ---- ルール検証（塗り分けとして正しいか）----

    def coloring_violations(self):
        """等式・不等式ルール違反の一覧を返す。空なら正しい塗り分け。"""
        bad = []
        for i in range(self.n_rows):          # 等式: 各行は1色
            cs = self._row_colors(i)
            if len(cs) > 1:
                bad.append(("equality_row", i, sorted(cs)))
        for j in range(self.n_cols):          # 等式: 各列は1色
            cs = self._col_colors(j)
            if len(cs) > 1:
                bad.append(("equality_col", j, sorted(cs)))
        for j in range(self.n_cols - 1):      # 不等式: 隣の列は別色
            common = self._col_colors(j) & self._col_colors(j + 1)
            if common:
                bad.append(("inequality_col", j, sorted(common)))
        for i in range(self.n_rows - 1):      # 不等式: 隣の行は別色
            common = self._row_colors(i) & self._row_colors(i + 1)
            if common:
                bad.append(("inequality_row", i, sorted(common)))
        return bad

    def is_valid_coloring(self):
        return not self.coloring_violations()

    # ---- 構造検証（三角階段テーブルとして整合しているか）----

    def structure_errors(self):
        """三角階段の不変条件に反する点の一覧を返す。空なら整合。"""
        errs = []
        for i, row in enumerate(self.cells):           # 値の範囲
            for j, x in enumerate(row):
                if x < 1 and x not in (SEP, EMPTY, COLORLESS):
                    errs.append(f"値が不正 ({i},{j})={x}")
        sep_rows = {i for i in range(self.n_rows)
                    if all(x == SEP for x in self.cells[i])}
        sep_cols = {j for j in range(self.n_cols)
                    if all(self.cells[i][j] == SEP for i in range(self.n_rows))}
        for i in range(self.n_rows):                   # 区切りは十字をなす
            for j in range(self.n_cols):
                is_sep = i in sep_rows or j in sep_cols
                if (self.cells[i][j] == SEP) != is_sep:
                    errs.append(f"区切りが十字でない ({i},{j})")
        col_blocks = _consecutive_runs([j for j in range(self.n_cols)
                                        if j not in sep_cols])
        row_blocks = _consecutive_runs([i for i in range(self.n_rows)
                                        if i not in sep_rows])
        if len(col_blocks) != len(row_blocks):
            errs.append(f"列ブロック数 {len(col_blocks)} != "
                        f"行ブロック数 {len(row_blocks)}")
        for bi, cb in enumerate(col_blocks):
            for bj, rb in enumerate(row_blocks):
                nodes = [(i, j) for i in rb for j in cb
                         if self.cells[i][j] >= 0]
                if (len(nodes) > 0) != (bj <= bi):
                    errs.append(f"三角配置でない block(列{bi},行{bj}): "
                                f"ノード{len(nodes)}個")
                if len(nodes) > 2:
                    errs.append(f"ブロックにノード3個以上 block(列{bi},行{bj})")
                if bi == bj and nodes and len(nodes) != 1:
                    errs.append(f"対角ブロックが1セルでない block({bi})")
                if len(nodes) == 2:
                    a, b = sorted(nodes)
                    if (b[0] - a[0], b[1] - a[1]) != (1, -1):
                        errs.append(f"2セルが／向きでない block(列{bi},行{bj})")
        return errs

    def is_well_formed(self):
        return not self.structure_errors()

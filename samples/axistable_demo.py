"""デモ: ハニカムグラフから2軸ラベル表を作って表示する (docs/09)。

実行: python samples/axistable_demo.py

セルの値:  -2 = 区切り（表示は空白） / -1 = ブロック内の空き（表示は .） /
           0 = 無色ノード（表示は o） / 1以上 = 有色ノードの仮色値（表示はその番号）
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fourcolor.axistable import build_axis_table, table_to_str

import sample01_k4
import sample02_seven
import sample03_point


def main():
    for mod, name in [(sample01_k4, "サンプル01 (4カ国 K4)"),
                      (sample02_seven, "サンプル02 (7カ国)"),
                      (sample03_point, "サンプル03 (無色ノード)")]:
        grid, country_of, edges = mod.build_sample()
        table, h, v, cid = build_axis_table(grid, edges, country_of)
        print(f"=== {name} ===")
        print(f"国 → 仮色値: {cid}")
        print(f"表の大きさ: {len(table)} 行 × {len(table[0])} 列")
        print(table_to_str(table))
        print()


if __name__ == "__main__":
    main()

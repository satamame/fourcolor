"""実験7: 健全性を「色」でなく「格子への再構成」で判定する（四角版、docs/10）。

健全性の正しい定義（循環を避ける）:
  「格子由来なら持つべき構造条件」を満たす ⟹ 必ず格子グラフに再構成でき、
  それは平面地図である。4色で塗れることはそこから四色定理で従う結論であって、
  判定には使わない。

ここでは is_grid_realizable() を、
  - 正しい格子由来の表（square_sample01 / 02）→ 再構成できる（平面地図）
  - 弱い条件だけ満たす K5 の表（exp6）        → 再構成できない（どこで詰まるか）
で確認する。

実行: python experiments/exp7_square_reconstruct.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fourcolor.squaretable import build_square_table, is_grid_realizable

import square_sample01
import square_sample02_point
from exp6_square_soundness import build_square_k5


def show(name, table):
    ok, reason = is_grid_realizable(table)
    verdict = "格子に再構成できる（=平面地図）" if ok else f"再構成できない: {reason}"
    print(f"{name}: {verdict}")


def main():
    for mod, name in [(square_sample01, "サンプル01 (K4・格子由来)"),
                      (square_sample02_point, "サンプル02 (無色・格子由来)")]:
        grid, country_of, edges = mod.build_sample()
        table, _, _ = build_square_table(grid, edges, country_of)
        show(name, table)

    show("exp6 の K5 (弱い条件のみ・格子由来でない)", build_square_k5())


if __name__ == "__main__":
    main()

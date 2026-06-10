"""サンプル共通の SVG 描画。

「(1) 地図 / (2) 三角形に分割 / (3) ハニカムグラフ」の3面図を生成する。
(3) では各ノードに座標 (r, p) を添える。
▲ノードは真上・▽ノードは真下にエッジが無く空いているので、そこにラベルを置く。

無色ノード (孤立した1セル) は、(1) の地図では重心の1点に縮めて描く:
周りの国をくさび形に集めて、全部の国が本当に1点で合流している絵にする
(分割前の地図には「点」しか無く、膨らませた三角形は (2) 以降にだけ現れる)。
"""

import math

SQRT3 = 3 ** 0.5

# 国の塗り色 (国名のソート順に割り当てる)
COUNTRY_COLOR_CYCLE = [
    "#f2c14e",  # 黄
    "#7fb3d5",  # 青
    "#8fce9f",  # 緑
    "#e57373",  # 赤
    "#c39bd3",  # 紫
    "#e59866",  # 橙
    "#aab7b8",  # 灰
    "#76d7c4",  # 青緑
]

STYLE = {
    "boundary": "#333333",   # 国境エッジ
    "grid": "#aaaaaa",       # 三角形分割の補助線
    "same": "#999999",       # 内部エッジ (グラフ面)
    "none": "#c0c0c0",       # 無色ノードに接するエッジ (制約なし)
    "colorless": "#ffffff",  # 無色ノードの塗り
    "node_stroke": "#444444",
    "text": "#222222",
}


def build_palette(countries):
    return {c: COUNTRY_COLOR_CYCLE[i % len(COUNTRY_COLOR_CYCLE)]
            for i, c in enumerate(sorted(countries))}


def _along(p_from, p_to, dist):
    """p_from から p_to に向かって dist だけ進んだ点。"""
    dx, dy = p_to[0] - p_from[0], p_to[1] - p_from[1]
    length = math.hypot(dx, dy)
    return (p_from[0] + dx / length * dist, p_from[1] + dy / length * dist)


def _poly(points, **attrs):
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<polygon points="{pts}" {extra}/>'


def _line(p1, p2, **attrs):
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return (f'<line x1="{p1[0]:.2f}" y1="{p1[1]:.2f}" '
            f'x2="{p2[0]:.2f}" y2="{p2[1]:.2f}" {extra}/>')


def _text(x, y, s, size=15, anchor="middle", color=None, bold=False):
    w = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{color}"{w} '
            f'font-family="sans-serif">{s}</text>')


def _collapse_point(grid, country_of, x_cell, side, org):
    """無色ノード1セルを重心の1点 P に縮めた地図描画用の要素を計算する。

    返り値: (polys, border_segments, trims)
      polys           … 描き足す [(国, 多角形)]。X を埋めるくさび形と、
                        角だけで接する国を本体につなぐ通路 (削った角)
      border_segments … 国境として太線で描く線分 [(p1, p2)]
      trims           … [(正規化セル対, 頂点座標, 長さ)]。このセル対の国境線は
                        頂点から長さぶん描かない (そこは通路で同じ国になるため)
    描けない構成 (盤の縁に接する、1つの頂点に合流する国が多すぎる等) なら None。

    構成のポイント:
    - 辺で接する国は X のその辺を底辺とするくさびを受け取る
    - 角だけで接する国は頂点近くの小さな弧のくさび (トング) を受け取る
    - トングと国の本体は X の頂点で点接触になってしまうので、間に挟まる
      隣国セルの角を幅 w だけ削り、その国の通路にする。
      扇の並び順により、削られるセルは必ずトングの国と実際に隣接する国の
      ものなので、新しく描かれる境界もすべて本物の隣接になる。
    - w = eta (くさびの弧と同じ長さ) にすることで、角の切断点がくさびの
      基点や国境線の切り詰め点と一致し、境界が一筆書きで滑らかにつながる。
    """
    verts = grid.triangle_vertices(x_cell, side, org)
    P = grid.node_center(x_cell, side, org)

    def key(pt):
        return (round(pt[0], 2), round(pt[1], 2))

    vmap = {}
    tri_pts = {}
    for node in grid.nodes():
        tri_pts[node] = grid.triangle_vertices(node, side, org)
        for pt in tri_pts[node]:
            vmap.setdefault(key(pt), []).append(node)
    tri_pts[x_cell] = verts

    def ang(origin, node):
        c = grid.node_center(node, side, org)
        return math.atan2(c[1] - origin[1], c[0] - origin[0])

    eta = side * 0.30  # くさびの弧の長さ
    w = eta            # 通路の幅 (弧と揃えて滑らかにつなぐ)
    along = _along

    def cut_point(c, d, V):
        """セル c, d の共有辺に沿って V から w だけ進んだ点。"""
        kc = {key(p): p for p in tri_pts[c]}
        kd = {key(p) for p in tri_pts[d]}
        other = [p for k2, p in kc.items() if k2 in kd and k2 != key(V)]
        if len(other) != 1:
            return None
        return along(V, other[0], w)

    # 各辺の隣 (X と辺を共有するセル)
    en = []
    for i in range(3):
        a, b = verts[i], verts[(i + 1) % 3]
        for nb in grid.neighbors(x_cell):
            pts = {key(p) for p in tri_pts[nb]}
            if key(a) in pts and key(b) in pts:
                en.append(nb)
                break
        else:
            return None  # 盤の縁に接していて辺の隣がいない

    # 各頂点の扇を EN_prev → EN_next の順に並べ、トングの国と
    # 「削って通路にするセルの列」を求める
    in_info = [None] * 3   # 頂点 i の手前側: (国, 削るセル列)
    out_info = [None] * 3  # 頂点 i の先側:   (国, 削るセル列)
    for i in range(3):
        V = verts[i]
        en_prev, en_next = en[(i - 1) % 3], en[i]
        ring = sorted(vmap.get(key(V), []), key=lambda c: ang(V, c))
        if len(ring) != 6:
            return None  # 盤の縁の頂点
        m = len(ring)
        xi = ring.index(x_cell)
        if ring[(xi + 1) % m] == en_prev:
            order = [ring[(xi + j) % m] for j in range(1, m)]
        elif ring[(xi - 1) % m] == en_prev:
            order = [ring[(xi - j) % m] for j in range(1, m)]
        else:
            return None
        if order[-1] != en_next:
            return None
        if any(country_of[c] is None for c in order):
            return None  # 隣り合う無色ノードはこの描き方の対象外
        # order[1:-1] を国ごとのグループに分け、EN と同じ国の端グループは併合
        groups = []  # (国, orderでの開始位置, 終了位置)
        for t in range(1, len(order) - 1):
            cn = country_of[order[t]]
            if groups and groups[-1][0] == cn:
                groups[-1] = (cn, groups[-1][1], t)
            else:
                groups.append((cn, t, t))
        if groups and groups[0][0] == country_of[en_prev]:
            groups.pop(0)
        if groups and groups[-1][0] == country_of[en_next]:
            groups.pop()
        if len(groups) > 2:
            return None  # 1頂点に独立な国が3つ以上 → 無色ノードを増やす必要あり
        if len(groups) >= 1:
            cn, start, _end = groups[-1]
            out_info[i] = (cn, order, _end)
        if len(groups) == 2:
            cn, start, _end = groups[0]
            in_info[i] = (cn, order, start)

    polys, borders, seq, trims = [], [], [], []

    def add_slivers(V, country, chain, end_a, end_b):
        """chain の各セルの V の角を削り、country の通路にする。

        通路の断面は、扇の並び [end_a, *chain, end_b] の隣り合うセル同士の
        共有辺上 (V から w の位置) に置いた点列でつなぐ。
        """
        cells = [end_a] + chain + [end_b]
        pts = []
        for t in range(len(cells) - 1):
            q = cut_point(cells[t], cells[t + 1], V)
            if q is None:
                return False
            pts.append(q)
        for t, _cell in enumerate(chain):
            polys.append((country, [V, pts[t], pts[t + 1]]))
            borders.append((pts[t], pts[t + 1]))  # 削った角の境界 (本物の国境)
        return True

    for i in range(3):
        vi, vj = verts[i], verts[(i + 1) % 3]
        j = (i + 1) % 3
        out_t, in_t = out_info[i], in_info[j]
        s = along(vi, vj, eta) if out_t else vi
        e = along(vj, vi, eta) if in_t else vj
        if out_t:  # 頂点 i の先側のトング
            cn, order, last = out_t
            polys.append((cn, [vi, s, P]))
            seq.append((cn, vi))
            # 本体までの通路: own の次から EN_next まで (すべて EN_next の国) を削る
            if not add_slivers(vi, cn, order[last + 1:], order[last], x_cell):
                return None
            # 本体と通路の境目には国境を引かない (頂点から w だけ切り詰める)
            trims.append((tuple(sorted((order[last], order[last + 1]))), vi, w))
        polys.append((country_of[en[i]], [s, e, P]))
        seq.append((country_of[en[i]], s))
        if in_t:  # 頂点 i+1 の手前側のトング
            cn, order, first = in_t
            polys.append((cn, [e, vj, P]))
            seq.append((cn, e))
            # 本体までの通路: EN_prev から own の手前まで (すべて EN_prev の国) を削る
            if not add_slivers(vj, cn, order[:first], x_cell, order[first]):
                return None
            trims.append((tuple(sorted((order[first - 1], order[first]))), vj, w))

    # P から放射状に伸びる国境: 隣り合うくさびの国が違うところ
    for idx, (cn, start) in enumerate(seq):
        if cn != seq[idx - 1][0]:
            borders.append((start, P))
    return polys, borders, trims


def render_svg(grid, country_of, edges, side=80.0, country_colors=None):
    """3面図 SVG を文字列で返す。"""
    countries = {c for c in country_of.values() if c is not None}
    pal = country_colors or build_palette(countries)

    def fill_of(node):
        c = country_of[node]
        return STYLE["colorless"] if c is None else pal[c]

    h = side * SQRT3 / 2
    tri_w, tri_h = grid.size * side, grid.size * h
    margin_x = 30
    panel_w = tri_w + 60
    origin_y = 56
    width = 3 * panel_w + margin_x

    diff_pairs = [e for e, a in edges.items() if a["same_value"] is False]
    same_pairs = [e for e, a in edges.items() if a["same_value"] is True]
    none_pairs = [e for e, a in edges.items() if a["same_value"] is None]
    # 無色ノードと国の間のエッジ = 膨らませた点の輪郭 (地図面では境界線として描く)
    rim_pairs = [(u, v) for u, v in none_pairs
                 if (country_of[u] is None) != (country_of[v] is None)]

    height = origin_y + tri_h + 70 + (24 if none_pairs else 0)

    def origin(panel):
        return (margin_x + panel * panel_w + (panel_w - margin_x - tri_w) / 2,
                origin_y)

    out = [f'<svg viewBox="0 0 {width:.0f} {height:.0f}" '
           f'xmlns="http://www.w3.org/2000/svg">']
    titles = ["(1) 地図", "(2) 三角形に分割", "(3) ハニカムグラフ"]
    for i, t in enumerate(titles):
        out.append(_text(margin_x + i * panel_w + panel_w / 2 - margin_x / 2, 28,
                         t, size=17, color=STYLE["text"], bold=True))

    # 孤立した無色ノード: パネル1の地図では1点に縮めて描く
    lone_colorless = [c for c in grid.nodes() if country_of[c] is None
                      and all(country_of[nb] is not None
                              for nb in grid.neighbors(c))]

    # --- パネル1: 地図 (国の塗り + 国境線のみ) / パネル2: + 三角形の分割線 ---
    for panel in (0, 1):
        org = origin(panel)
        collapsed = {}
        if panel == 0:
            for c in lone_colorless:
                result = _collapse_point(grid, country_of, c, side, org)
                if result is not None:
                    collapsed[c] = result
        for node in grid.nodes():
            if node in collapsed:
                continue  # 点に縮めた無色ノードは周りの国のくさびで埋める
            fill = fill_of(node)
            stroke = STYLE["grid"] if panel == 1 else fill
            out.append(_poly(grid.triangle_vertices(node, side, org),
                             fill=fill, stroke=stroke, stroke_width=1))
        for _, (polys, _segs, _trims) in collapsed.items():
            for cn, pts in polys:
                out.append(_poly(pts, fill=pal[cn], stroke=pal[cn],
                                 stroke_width=1))
        # 通路で同じ国になった部分の国境線は、頂点から切り詰める
        trim_map = {}
        for _, (_polys, _segs, trims) in collapsed.items():
            for pair, V, w in trims:
                trim_map.setdefault(pair, []).append((V, w))
        # 国境 (+ 縮めなかった無色ノードの輪郭) を太線で
        thick = list(diff_pairs)
        thick += [(u, v) for u, v in rim_pairs
                  if u not in collapsed and v not in collapsed]
        for u, v in thick:
            p1, p2 = grid.shared_edge(u, v, side, org)
            for V, w in trim_map.get((u, v), []):
                if abs(p1[0] - V[0]) < 0.05 and abs(p1[1] - V[1]) < 0.05:
                    p1 = _along(V, p2, w)
                elif abs(p2[0] - V[0]) < 0.05 and abs(p2[1] - V[1]) < 0.05:
                    p2 = _along(V, p1, w)
            out.append(_line(p1, p2, stroke=STYLE["boundary"], stroke_width=4,
                             stroke_linecap="round"))
        for _, (_polys, segs, _trims) in collapsed.items():
            for p1, p2 in segs:
                out.append(_line(p1, p2, stroke=STYLE["boundary"],
                                 stroke_width=4, stroke_linecap="round"))
        apex = (org[0] + tri_w / 2, org[1])
        bl = (org[0], org[1] + tri_h)
        br = (org[0] + tri_w, org[1] + tri_h)
        out.append(_poly([apex, bl, br], fill="none", stroke=STYLE["boundary"],
                         stroke_width=3))
        if panel == 0:  # 国名ラベル
            for country in sorted(countries):
                centers = [grid.node_center(n, side, org)
                           for n in grid.nodes() if country_of[n] == country]
                cx = sum(x for x, _ in centers) / len(centers)
                cy = sum(y for _, y in centers) / len(centers)
                out.append(_text(cx, cy + 6, country, size=18,
                                 color=STYLE["text"], bold=True))

    # --- パネル3: ハニカムグラフ (ノード = 小三角形の重心) ---
    org = origin(2)
    for u, v in none_pairs:
        out.append(_line(grid.node_center(u, side, org),
                         grid.node_center(v, side, org),
                         stroke=STYLE["none"], stroke_width=1.2,
                         stroke_dasharray="2 3"))
    for u, v in same_pairs:
        out.append(_line(grid.node_center(u, side, org),
                         grid.node_center(v, side, org),
                         stroke=STYLE["same"], stroke_width=1.5,
                         stroke_dasharray="5 4"))
    for u, v in diff_pairs:
        out.append(_line(grid.node_center(u, side, org),
                         grid.node_center(v, side, org),
                         stroke=STYLE["boundary"], stroke_width=2.5))
    for node in grid.nodes():
        cx, cy = grid.node_center(node, side, org)
        dash = ' stroke-dasharray="3 2"' if country_of[node] is None else ""
        out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="8.5" '
                   f'fill="{fill_of(node)}" '
                   f'stroke="{STYLE["node_stroke"]}" stroke-width="1.2"{dash}/>')
        label_y = cy - 16.5 if grid.is_up(node) else cy + 23.5
        out.append(_text(cx, label_y, f"({node[0]},{node[1]})", size=12,
                         color=STYLE["text"]))

    # 凡例
    ly = origin_y + tri_h + 38
    lx = margin_x + 2 * panel_w
    out.append(_line((lx, ly), (lx + 44, ly), stroke=STYLE["same"],
                     stroke_width=1.5, stroke_dasharray="5 4"))
    out.append(_text(lx + 52, ly + 5, "同じ国 (same_value=True)", size=13,
                     anchor="start", color=STYLE["text"]))
    out.append(_line((lx + 240, ly), (lx + 284, ly), stroke=STYLE["boundary"],
                     stroke_width=2.5))
    out.append(_text(lx + 292, ly + 5, "国境 (False)", size=13, anchor="start",
                     color=STYLE["text"]))
    if none_pairs:
        out.append(_line((lx, ly + 24), (lx + 44, ly + 24), stroke=STYLE["none"],
                         stroke_width=1.2, stroke_dasharray="2 3"))
        out.append(_text(lx + 52, ly + 29, "無色ノードに接する (None: 制約なし)",
                         size=13, anchor="start", color=STYLE["text"]))
    out.append("</svg>")
    return "\n".join(out)

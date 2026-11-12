#!/usr/bin/env python3
"""Profile graphics for github.com/SaiArnav.

assets/header.svg  - a swarm of pointer cursors flies in and *draws* the name,
                     tagline and a terminal / </> / lock illustration stroke by
                     stroke (like multiplayer cursors sketching). Drawn once on
                     load; afterwards everything keeps gently moving.
assets/contrib.svg - the contribution calendar as a 3D city in GitHub greens,
                     built by a passing swarm, then alive with a light wave.

Stdlib only. Animations touch transform / opacity / dashoffset only.
"""
import math, os, random, re, sys, urllib.request

USER = os.environ.get("GH_USER", "SaiArnav")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# GitHub dark palette
BG, BG2, BORDER = "#0d1117", "#010409", "#30363d"
FG, MUTED, SUBTLE = "#e6edf3", "#8b949e", "#484f58"
BLUE, PURPLE, GREEN, PINK, ORANGE = "#58a6ff", "#bc8cff", "#3fb950", "#f778ba", "#ffa657"

f1 = lambda v: f"{v:.1f}".rstrip("0").rstrip(".")
CURSOR = ('<path d="M0 0L0 17L4.4 12.9L7.3 19.6L10 18.4L7.2 11.8L13 11.8Z" fill="{c}" '
          'stroke="{s}" stroke-width="1.2" stroke-linejoin="round"/>')


def cursor_svg(c=FG, s="#010409", scale=1.0):
    return f'<g transform="scale({scale:.2f})">{CURSOR.format(c=c, s=s)}</g>'


# ------------------------------------------------------------ stroke font
def earc(cx, cy, rx, ry, a0, a1, n=None):
    n = n or max(4, int(abs(a1 - a0) / 15))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


GLYPHS = {
    "A": [[(0, 6), (2, 0), (4, 6)], [(0.75, 4), (3.25, 4)]],
    "B": [[(0, 3), (0, 0), (2.5, 0)] + earc(2.5, 1.5, 1.4, 1.5, -90, 90)[1:] + [(0, 3), (2.7, 3)]
          + earc(2.7, 4.5, 1.3, 1.5, -90, 90)[1:] + [(0, 6), (0, 3)]],
    "C": [earc(2.1, 3, 2.1, 3, -40, -320)],
    "D": [[(0, 0), (0, 6), (1.6, 6)] + earc(1.6, 3, 2.4, 3, 90, -90)[1:] + [(0, 0)]],
    "E": [[(4, 0), (0, 0), (0, 6), (4, 6)], [(0, 3), (3, 3)]],
    "F": [[(4, 0), (0, 0), (0, 6)], [(0, 3), (3, 3)]],
    "G": [earc(2.1, 3, 2.1, 3, -40, -360) + [(2.3, 3)]],
    "H": [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]],
    "I": [[(1, 0), (3, 0)], [(2, 0), (2, 6)], [(1, 6), (3, 6)]],
    "J": [[(4, 0), (4, 4.1)] + earc(2, 4.1, 2, 1.9, 0, 180)[1:]],
    "K": [[(0, 0), (0, 6)], [(4, 0), (0, 3.8)], [(1.5, 2.6), (4, 6)]],
    "L": [[(0, 0), (0, 6), (4, 6)]],
    "M": [[(0, 6), (0, 0), (2, 3.8), (4, 0), (4, 6)]],
    "N": [[(0, 6), (0, 0), (4, 6), (4, 0)]],
    "O": [earc(2, 3, 2, 3, -90, 270)],
    "P": [[(0, 6), (0, 0), (2.4, 0)] + earc(2.4, 1.6, 1.6, 1.6, -90, 90)[1:] + [(0, 3.2)]],
    "Q": [earc(2, 3, 2, 3, -90, 270), [(2.7, 4.5), (4.1, 6.3)]],
    "R": [[(0, 6), (0, 0), (2.4, 0)] + earc(2.4, 1.6, 1.6, 1.6, -90, 90)[1:] + [(0, 3.2)], [(2.2, 3.2), (4, 6)]],
    "S": [earc(2, 1.5, 1.9, 1.5, -25, -270)[:-1] + earc(2, 4.5, 2, 1.5, -90, 155)],
    "T": [[(0, 0), (4, 0)], [(2, 0), (2, 6)]],
    "U": [[(0, 0), (0, 4)] + earc(2, 4, 2, 2, 180, 0)[1:] + [(4, 0)]],
    "V": [[(0, 0), (2, 6), (4, 0)]],
    "W": [[(0, 0), (1, 6), (2, 2.4), (3, 6), (4, 0)]],
    "X": [[(0, 0), (4, 6)], [(4, 0), (0, 6)]],
    "Y": [[(0, 0), (2, 3), (4, 0)], [(2, 3), (2, 6)]],
    "Z": [[(0, 0), (4, 0), (0, 6), (4, 6)]],
    "-": [[(0.6, 3), (3.4, 3)]],
    "/": [[(3.6, -0.4), (0.4, 6.4)]],
    "·": [earc(2, 3, .3, .3, 0, 360, 8)],
    "+": [[(2, 1.2), (2, 4.8)], [(0.2, 3), (3.8, 3)]],
}


def text_strokes(s, x, y, size, track=1.8):
    u = size / 6
    out, cx = [], x
    for ch in s:
        if ch != " ":
            for st in GLYPHS[ch]:
                out.append([(cx + px * u, y + py * u) for px, py in st])
        cx += (4 + track) * u
    return out


def text_width(s, size, track=1.8):
    return len(s) * (4 + track) * size / 6 - track * size / 6


def plen(pl):
    return sum(math.dist(pl[i], pl[i + 1]) for i in range(len(pl) - 1))


def pd(pl):
    return "M" + "L".join(f"{f1(x)} {f1(y)}" for x, y in pl)


def rrect(x0, y0, x1, y1, r):
    p = [(x0 + r, y0), (x1 - r, y0)] + earc(x1 - r, y0 + r, r, r, -90, 0, 6)[1:]
    p += [(x1, y1 - r)] + earc(x1 - r, y1 - r, r, r, 0, 90, 6)[1:]
    p += [(x0 + r, y1)] + earc(x0 + r, y1 - r, r, r, 90, 180, 6)[1:]
    p += [(x0, y0 + r)] + earc(x0 + r, y0 + r, r, r, 180, 270, 6)[1:]
    return p


# ------------------------------------------------------------------ header
def header():
    W, H = 1200, 400
    rnd = random.Random(21)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">',
         '<defs>',
         f'<radialGradient id="bg" cx=".3" cy=".2" r="1"><stop offset="0" stop-color="#161b22"/><stop offset=".6" stop-color="{BG}"/><stop offset="1" stop-color="{BG2}"/></radialGradient>',
         f'<radialGradient id="glowA" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{BLUE}" stop-opacity=".16"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>',
         f'<radialGradient id="glowB" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{PURPLE}" stop-opacity=".14"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>',
         # name gradient with a slow sheen
         f'<linearGradient id="ink" x1="70" y1="0" x2="700" y2="0" gradientUnits="userSpaceOnUse">'
         f'<stop offset="0" stop-color="{BLUE}"/><stop offset=".45" stop-color="{FG}"/><stop offset=".55" stop-color="{FG}"/><stop offset="1" stop-color="{PURPLE}"/>'
         f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;140 0;0 0" dur="9s" begin="4s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></linearGradient>',
         '<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="12" cy="12" r="1" fill="#21262d"/></pattern>',
         f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="16"/></clipPath>',
         '</defs><g clip-path="url(#clip)">',
         f'<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#dots)"/>']
    # drifting colour glows (ambient)
    for gid, cx, cy, r, dx, dur in [("glowA", 260, 120, 320, 90, 14), ("glowB", 950, 280, 300, -80, 17)]:
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})"><animateTransform attributeName="transform" type="translate" '
                 f'values="0 0;{dx} 20;0 0" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></circle>')

    jobs = []  # (strokes, stroke attrs, start time, speed, cursor colour)

    # name
    name, NS, NX, NY = "SAI ARNAV", 74, 84, 112
    nstrokes = text_strokes(name, NX, NY, NS, 1.9)
    letters, cx = [], NX
    for ch in name:
        if ch != " ":
            letters.append([[(NX + 0, 0)]])  # placeholder
    # group strokes per letter for one cursor each
    groups, i = [], 0
    for ch in name:
        if ch == " ":
            continue
        k = len(GLYPHS[ch]); groups.append(nstrokes[i:i + k]); i += k
    cols = [BLUE, PURPLE, GREEN, PINK, ORANGE, BLUE, PURPLE, GREEN]
    for j, g in enumerate(groups):
        jobs.append((g, 'stroke="url(#ink)" stroke-width="7"', .35 + j * .16, 360, cols[j % len(cols)]))
    # underline
    nw = text_width(name, NS, 1.9)
    jobs.append(([[(NX, 222), (NX + nw, 222)]], f'stroke="{SUBTLE}" stroke-width="1.5"', 1.6, 700, FG))
    # tagline
    tag, TS = "CODE · BUILD · SECURE", 17
    tstr = text_strokes(tag, NX, 248, TS, 3.2)
    words, i = [], 0
    for w in tag.split(" "):
        k = sum(len(GLYPHS[c]) for c in w); words.append(tstr[i:i + k]); i += k
    for j, g in enumerate(words):
        jobs.append((g, f'stroke="{MUTED}" stroke-width="2.4"', 1.9 + j * .22, 300, [FG, GREEN, FG, BLUE, FG][j % 5]))
    # small sub-line
    sub, SS = "CSE STUDENT  -  FULL STACK  +  AI", 11
    sstr = text_strokes(sub, NX, 288, SS, 3.0)
    half = len(sstr) // 2
    jobs.append((sstr[:half], f'stroke="{SUBTLE}" stroke-width="1.8"', 2.6, 420, FG))
    jobs.append((sstr[half:], f'stroke="{SUBTLE}" stroke-width="1.8"', 2.75, 420, PURPLE))

    # terminal illustration
    TX0, TY0, TX1, TY1 = 760, 78, 1120, 322
    jobs.append(([rrect(TX0, TY0, TX1, TY1, 14)], f'stroke="{BORDER}" stroke-width="2"', .5, 900, FG))
    jobs.append(([[(TX0, TY0 + 34), (TX1, TY0 + 34)]], f'stroke="{BORDER}" stroke-width="1.5"', 1.5, 700, FG))
    # </> drawn big
    cxm, cym = (TX0 + TX1) / 2, (TY0 + 34 + TY1) / 2 - 4
    jobs.append(([[(cxm - 52, cym - 46), (cxm - 98, cym), (cxm - 52, cym + 46)]], f'stroke="{BLUE}" stroke-width="5"', 1.2, 260, BLUE))
    jobs.append(([[(cxm + 22, cym - 64), (cxm - 22, cym + 64)]], f'stroke="{GREEN}" stroke-width="5"', 1.45, 260, GREEN))
    jobs.append(([[(cxm + 52, cym - 46), (cxm + 98, cym), (cxm + 52, cym + 46)]], f'stroke="{PURPLE}" stroke-width="5"', 1.7, 260, PURPLE))
    # padlock in the title bar
    lx, ly = TX1 - 30, TY0 + 17
    jobs.append(([[(lx - 5, ly), (lx - 5, ly - 4)] + earc(lx, ly - 4, 5, 5, 180, 360, 8)[1:] + [(lx + 5, ly)],
                  rrect(lx - 8, ly, lx + 8, ly + 11, 2) + [(lx - 8 + 2, ly)]], f'stroke="{MUTED}" stroke-width="1.6"', 2.3, 140, ORANGE))
    # prompt
    px, py = TX0 + 26, TY1 - 34
    jobs.append(([[(px, py - 8), (px + 9, py), (px, py + 8)]], f'stroke="{GREEN}" stroke-width="2.4"', 2.4, 160, GREEN))

    draw_end = 0
    for ji, (strokes, attrs, t0, v, col) in enumerate(jobs):
        # one cursor per job: fly in, trace every stroke (pen-up hops included), fly off
        path_pts, marks, acc = [], [], 0.0
        for st in strokes:
            if path_pts:
                acc += math.dist(path_pts[-1], st[0])
            s0 = acc; acc += plen(st); marks.append((s0, acc))
            path_pts += st
        total = acc or 1
        dur = max(.35, total / v)
        ang = rnd.uniform(0, math.tau)
        spawn = (600 + 760 * math.cos(ang), 200 + 330 * math.sin(ang))
        fly = .55
        t_draw = t0 + fly
        end = t_draw + dur
        draw_end = max(draw_end, end)
        exitp = (path_pts[-1][0] + rnd.uniform(-160, 160), H + 40 if rnd.random() < .5 else -40)
        for st, (s0, s1) in zip(strokes, marks):
            b = t_draw + dur * s0 / total
            d = max(.05, dur * (s1 - s0) / total)
            o.append(f'<path d="{pd(st)}" {attrs} stroke-linecap="round" stroke-linejoin="round" pathLength="1" '
                     f'stroke-dasharray="1 1.01" stroke-dashoffset="1"><animate attributeName="stroke-dashoffset" '
                     f'from="1" to="0" begin="{b:.2f}s" dur="{d:.2f}s" fill="freeze"/></path>')
        mx = (spawn[0] + path_pts[0][0]) / 2 + rnd.uniform(-80, 80)
        my = (spawn[1] + path_pts[0][1]) / 2 + rnd.uniform(-80, 80)
        fly_d = f"M{f1(spawn[0])} {f1(spawn[1])}Q{f1(mx)} {f1(my)} {f1(path_pts[0][0])} {f1(path_pts[0][1])}"
        ex, ey = path_pts[-1]
        out_d = f"M{f1(ex)} {f1(ey)}Q{f1(ex + rnd.uniform(-60, 60))} {f1(ey - 40)} {f1(exitp[0])} {f1(exitp[1])}"
        o.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t0:.2f}s"/>'
                 f'<animate attributeName="opacity" from="1" to="0" begin="{end + .25:.2f}s" dur=".6s" fill="freeze"/>'
                 f'<animateMotion path="{fly_d}" begin="{t0:.2f}s" dur="{fly}s" fill="freeze" calcMode="spline" keyPoints="0;1" keyTimes="0;1" keySplines=".25 .6 .3 1"/>'
                 f'<animateMotion path="{pd(path_pts)}" begin="{t_draw:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
                 f'<animateMotion path="{out_d}" begin="{end + .1:.2f}s" dur=".8s" fill="freeze" calcMode="spline" keyPoints="0;1" keyTimes="0;1" keySplines=".6 0 .9 .5"/>'
                 f'{cursor_svg(FG if ji % 3 else col, "#010409", .95)}</g>')

    # ---- alive after drawing
    T = draw_end + .3
    # window dots pop in
    for j, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        o.append(f'<circle cx="{TX0 + 22 + j * 18}" cy="{TY0 + 17}" r="5.5" fill="{c}" opacity="0">'
                 f'<animate attributeName="opacity" from="0" to=".9" begin="{1.6 + j * .12:.2f}s" dur=".3s" fill="freeze"/></circle>')
    # caret blink
    o.append(f'<rect x="{px + 18}" y="{py - 9}" width="10" height="18" rx="2" fill="{GREEN}" opacity="0">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" begin="{T:.2f}s" repeatCount="indefinite"/></rect>')
    # typing bars on the prompt line, looping
    for j, (w, c) in enumerate([(70, MUTED), (46, BLUE), (88, SUBTLE)]):
        x0 = px + 38 + sum([70, 46, 88][:j]) + j * 10
        k0, k1 = .08 + j * .14, .2 + j * .14
        o.append(f'<g transform="translate({x0} {py - 3})"><rect width="{w}" height="6" rx="3" fill="{c}" transform="scale(0 1)">'
                 f'<animateTransform attributeName="transform" type="scale" values="0 1;0 1;1 1;1 1;0 1" keyTimes="0;{k0:.2f};{k1:.2f};.88;1" '
                 f'dur="4s" begin="{T:.2f}s" repeatCount="indefinite"/></rect></g>')
    # </> breathes
    o.append(f'<circle cx="{cxm}" cy="{cym}" r="70" stroke="{PURPLE}" stroke-width="1.2" opacity="0">'
             f'<animate attributeName="opacity" values="0;.45;0" dur="3s" begin="{T:.2f}s" repeatCount="indefinite"/>'
             f'<animate attributeName="r" values="60;105" dur="3s" begin="{T:.2f}s" repeatCount="indefinite"/></circle>')
    # lock pulse
    o.append(f'<circle cx="{lx}" cy="{ly + 5}" r="2" fill="{ORANGE}" opacity="0"><animate attributeName="opacity" values="0;1;0" dur="2s" begin="{T:.2f}s" repeatCount="indefinite"/></circle>')
    # idle cursors drift around once the drawing is done
    for k in range(4):
        pts = [(rnd.uniform(60, W - 60), rnd.uniform(50, H - 50)) for _ in range(5)]
        d = "M" + " ".join(f"{f1(x)} {f1(y)}" for x, y in pts[:1])
        # smooth closed loop
        n = len(pts); seg = []
        for i2 in range(n):
            p0, p1, p2, p3 = pts[i2 - 1], pts[i2], pts[(i2 + 1) % n], pts[(i2 + 2) % n]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            seg.append(f"C{f1(c1[0])} {f1(c1[1])} {f1(c2[0])} {f1(c2[1])} {f1(p2[0])} {f1(p2[1])}")
        dd = d + "".join(seg)
        col = [BLUE, PURPLE, GREEN, PINK][k]
        o.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to=".85" begin="{T + k * .6:.2f}s" dur=".8s" fill="freeze"/>'
                 f'<animateMotion path="{dd}" dur="{26 + k * 5}s" begin="{T:.2f}s" repeatCount="indefinite"/>'
                 f'{cursor_svg(col, "#010409", .8)}'
                 f'<rect x="12" y="18" width="{18 + k * 6}" height="8" rx="4" fill="{col}" opacity=".9"/></g>')
    o.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" stroke="{BORDER}"/></g></svg>')
    return "".join(o)


# ------------------------------------------------------------ contributions
def fetch_levels():
    try:
        req = urllib.request.Request(f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "profile-gen"})
        html = urllib.request.urlopen(req, timeout=30).read().decode()
    except Exception as e:
        print("fetch failed:", e, file=sys.stderr)
        return None
    cells = {}
    for m in re.finditer(r'id="contribution-day-component-(\d)-(\d+)"[^>]*data-level="(\d)"', html):
        cells[(int(m.group(2)), int(m.group(1)))] = int(m.group(3))
    return cells or None


def shade(hexc, k):
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * k))) for c in (r, g, b))


def contrib(cells):
    rnd = random.Random(5)
    weeks = max(w for w, _ in cells) + 1
    STEP, CW, RX, RY, DX, DY = 18, 14, -6, 12, -4.5, 9
    X0, Y0 = 82, 92
    W = int(X0 + weeks * STEP + 50); H = 206
    green = {1: "#0e4429", 2: "#006d32", 3: "#26a641", 4: "#39d353"}
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">',
         '<defs>',
         f'<radialGradient id="gbg" cx=".5" cy=".2" r="1"><stop offset="0" stop-color="#161b22"/><stop offset=".7" stop-color="{BG}"/><stop offset="1" stop-color="{BG2}"/></radialGradient>',
         f'<clipPath id="gc"><rect width="{W}" height="{H}" rx="16"/></clipPath>',
         '</defs><g clip-path="url(#gc)">', f'<rect width="{W}" height="{H}" fill="url(#gbg)"/>']
    q = lambda pts: " ".join(f"{f1(x)},{f1(y)}" for x, y in pts)
    active = []
    for r in range(7):
        for w in range(weeks):
            lv = cells.get((w, r))
            if lv is None:
                continue
            x, y = X0 + w * STEP + r * RX, Y0 + r * RY
            tile = [(x, y), (x + CW, y), (x + CW + DX, y + DY), (x + DX, y + DY)]
            if lv == 0:
                o.append(f'<polygon points="{q(tile)}" fill="#161b22" stroke="#21262d" stroke-width=".6"/>')
                continue
            h = 6 + lv * 13
            top = [(a, b - h) for a, b in tile]
            front = [tile[3], tile[2], top[2], top[3]]
            side = [tile[1], tile[2], top[2], top[1]]
            c = green[lv]
            yb = y + DY
            begin = .35 + 2.6 * (x / W)
            body = (f'<polygon points="{q(side)}" fill="{shade(c, .55)}"/><polygon points="{q(front)}" fill="{shade(c, .78)}"/>'
                    f'<polygon points="{q(top)}" fill="{shade(c, 1.12)}"/>'
                    f'<polygon points="{q(top)}" fill="#aff5b4" opacity="0"><animate attributeName="opacity" values="0;.55;0" '
                    f'dur="4.5s" begin="{3.6 + w * .07:.2f}s" repeatCount="indefinite"/></polygon>')
            o.append(f'<g transform="translate(0 {f1(yb)})"><g transform="scale(1 0)">'
                     f'<animateTransform attributeName="transform" type="scale" values="1 0;1 1.12;1 1" keyTimes="0;.7;1" '
                     f'dur=".7s" begin="{begin:.2f}s" fill="freeze" calcMode="spline" keySplines=".3 0 .3 1;.4 0 .6 1"/>'
                     f'<g transform="translate(0 {f1(-yb)})">{body}</g></g></g>')
            active.append((x + CW / 2 + DX / 2, y + DY / 2 - h))

    # builder swarm: sweeps once, cursors upright like real pointers
    for i in range(14):
        y0 = 40 + rnd.random() * 130
        pts = [(-40 + j * (W + 80) / 6, y0 + 16 * math.sin(j * 1.4 + i)) for j in range(7)]
        d = "M" + "L".join(f"{f1(a)} {f1(b)}" for a, b in pts)
        delay = .2 + rnd.random() * .5
        o.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{delay:.2f}s"/>'
                 f'<animateMotion path="{d}" dur="3s" begin="{delay:.2f}s" fill="freeze"/>'
                 f'{cursor_svg([FG, GREEN, FG, "#7ee787"][i % 4], "#010409", .8)}</g>')
    if len(active) >= 4:
        for i in range(4):
            pts = rnd.sample(active, min(6, len(active)))
            pts.sort(key=lambda p: p[0]); pts = pts[::2] + pts[1::2][::-1]
            n = len(pts); seg = [f"M{f1(pts[0][0])} {f1(pts[0][1])}"]
            for k in range(n):
                p0, p1, p2, p3 = pts[k - 1], pts[k], pts[(k + 1) % n], pts[(k + 2) % n]
                c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
                c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
                seg.append(f"C{f1(c1[0])} {f1(c1[1])} {f1(c2[0])} {f1(c2[1])} {f1(p2[0])} {f1(p2[1])}")
            dur = 18 + rnd.random() * 8
            o.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to=".95" begin="3.6s" dur="1s" fill="freeze"/>'
                     f'<animateMotion path="{"".join(seg)}" dur="{dur:.1f}s" begin="{-rnd.random() * dur:.1f}s" repeatCount="indefinite"/>'
                     f'{cursor_svg([FG, "#7ee787", BLUE, FG][i], "#010409", .75)}</g>')
    o.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" stroke="{BORDER}"/></g></svg>')
    return "".join(o)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        OUT = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    # header.svg is built once offline (fonts) and committed; only the graph refreshes here
    cells = fetch_levels()
    if cells:
        open(os.path.join(OUT, "contrib.svg"), "w").write(contrib(cells))
    print("ok", len(cells or {}))

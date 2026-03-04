"""
Generate animated GIFs for the C Memory blog series.
One GIF per concept — saved to the same assets/ directory.
Run:  python3 gen_gifs.py
Requires:  matplotlib  Pillow
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import matplotlib.animation as animation
import numpy as np
from PIL import Image
import io

OUT = os.path.dirname(os.path.abspath(__file__))

# ── colour palette ───────────────────────────────────────────
C_STACK   = "#4f86c6"   # blue
C_HEAP    = "#e07b54"   # orange
C_BSS     = "#8ecf8e"   # green
C_DATA    = "#c6a84f"   # gold
C_TEXT    = "#b07cc6"   # purple
C_PAD     = "#f28b82"   # red-pink (padding)
C_ACTIVE  = "#f9c74f"   # yellow highlight
C_BG      = "#1e1e2e"   # dark bg
C_FG      = "#cdd6f4"   # light fg
C_BORDER  = "#45475a"   # border
C_FREE    = "#a6e3a1"   # freed / green
C_LIVE    = "#f38ba8"   # live / red
C_GRAY    = "#585b70"

FONT = "monospace"


def save_gif(fig, update_fn, frames, interval, path, dpi=90):
    """Render animation frames and save as GIF via Pillow."""
    imgs = []
    for i in range(frames):
        update_fn(i)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        buf.seek(0)
        imgs.append(Image.open(buf).copy())
    imgs[0].save(path, save_all=True, append_images=imgs[1:],
                 duration=interval, loop=0)
    plt.close(fig)
    print(f"  saved → {os.path.basename(path)}")


# ─────────────────────────────────────────────────────────────
# GIF 1 — Stack vs Heap growth
# ─────────────────────────────────────────────────────────────
def gif_stack_vs_heap():
    fig, (ax_s, ax_h) = plt.subplots(1, 2, figsize=(8, 6))
    fig.patch.set_facecolor(C_BG)
    for ax in (ax_s, ax_h):
        ax.set_facecolor(C_BG)
        ax.set_xlim(0, 4); ax.set_ylim(0, 10)
        ax.axis('off')

    ax_s.set_title("STACK\n(grows ↓)", color=C_FG, fontfamily=FONT, fontsize=12)
    ax_h.set_title("HEAP\n(grows ↑)", color=C_FG, fontfamily=FONT, fontsize=12)

    # Static address labels
    for y, lbl in [(9.2, "0xFFFF (high)"), (0.2, "0x0000 (low)")]:
        ax_s.text(2, y, lbl, ha='center', color=C_GRAY, fontsize=7, fontfamily=FONT)
        ax_h.text(2, y, lbl, ha='center', color=C_GRAY, fontsize=7, fontfamily=FONT)

    stack_labels = ["main()\n n=42", "func_a()\n x=3.14", "func_b()\n buf[8]",
                    "func_c()\n tmp=0"]
    heap_labels  = ["malloc\n  40B", "malloc\n  32B", "malloc\n 128B", "malloc\n  12B"]
    stack_patches, heap_patches = [], []

    def update(frame):
        for p in stack_patches + heap_patches: p.remove()
        stack_patches.clear(); heap_patches.clear()

        # Stack frames grow downward from top
        for i in range(min(frame + 1, len(stack_labels))):
            y = 8.5 - i * 1.8
            r = FancyBboxPatch((0.3, y-1.6), 3.4, 1.5,
                               boxstyle="round,pad=0.05",
                               fc=C_STACK, ec=C_FG, lw=1.2,
                               alpha=1.0 if i == min(frame, len(stack_labels)-1) else 0.7)
            ax_s.add_patch(r)
            stack_patches.append(r)
            t = ax_s.text(2, y - 0.75, stack_labels[i],
                          ha='center', va='center', color="white",
                          fontsize=9, fontfamily=FONT)
            stack_patches.append(t)

        # Heap blocks grow upward from bottom
        for i in range(min(frame + 1, len(heap_labels))):
            y = 0.5 + i * 1.8
            r = FancyBboxPatch((0.3, y), 3.4, 1.5,
                               boxstyle="round,pad=0.05",
                               fc=C_HEAP, ec=C_FG, lw=1.2,
                               alpha=1.0 if i == min(frame, len(heap_labels)-1) else 0.7)
            ax_h.add_patch(r)
            heap_patches.append(r)
            t = ax_h.text(2, y + 0.75, heap_labels[i],
                          ha='center', va='center', color="white",
                          fontsize=9, fontfamily=FONT)
            heap_patches.append(t)

    save_gif(fig, update, frames=6, interval=700,
             path=os.path.join(OUT, "gif_stack_vs_heap.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 2 — Pointer walking through an array
# ─────────────────────────────────────────────────────────────
def gif_pointer_arithmetic():
    n = 6
    values = [10, 20, 30, 40, 50, 60]
    base_addr = 0x1000

    fig, ax = plt.subplots(figsize=(9, 4))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(-0.5, n + 0.5); ax.set_ylim(-1.8, 3)
    ax.axis('off')
    ax.set_title("Pointer Walking — ptr steps sizeof(int)=4 bytes each time",
                 color=C_FG, fontfamily=FONT, fontsize=11)

    # Draw static array boxes
    for i in range(n):
        fc = C_GRAY
        ax.add_patch(FancyBboxPatch((i + 0.05, 0.1), 0.9, 1.8,
                     boxstyle="round,pad=0.02", fc=fc, ec=C_FG, lw=1.5))
        ax.text(i + 0.5, 1.0,  str(values[i]),  ha='center', va='center',
                color=C_FG, fontsize=13, fontfamily=FONT, fontweight='bold')
        ax.text(i + 0.5, 0.3,  f"[{i}]",        ha='center', color=C_GRAY,
                fontsize=9,  fontfamily=FONT)
        addr = f"0x{base_addr + i*4:04X}"
        ax.text(i + 0.5, -0.3, addr,             ha='center', color=C_GRAY,
                fontsize=7,  fontfamily=FONT)

    highlight = [None]
    arrow     = [None]
    label     = [None]
    eq_text   = [None]

    def update(frame):
        i = frame % (n + 1)
        # Remove old
        for obj in [highlight[0], arrow[0], label[0], eq_text[0]]:
            if obj: obj.remove()

        if i < n:
            highlight[0] = ax.add_patch(
                FancyBboxPatch((i + 0.05, 0.1), 0.9, 1.8,
                               boxstyle="round,pad=0.02",
                               fc=C_ACTIVE, ec="white", lw=2.5))
            ax.texts   # re-draw value on top
            arrow[0] = ax.annotate(
                "", xy=(i + 0.5, 0.1), xytext=(i + 0.5, -1.0),
                arrowprops=dict(arrowstyle="-|>", color=C_ACTIVE, lw=2))
            label[0] = ax.text(i + 0.5, -1.35, "ptr",
                               ha='center', color=C_ACTIVE,
                               fontsize=11, fontfamily=FONT, fontweight='bold')
            eq_text[0] = ax.text(n/2, 2.6,
                f"ptr + {i}  →  address 0x{base_addr+i*4:04X}  →  value = {values[i]}",
                ha='center', color=C_FG, fontsize=10, fontfamily=FONT,
                bbox=dict(fc=C_BORDER, ec='none', pad=4))
        else:
            highlight[0] = ax.text(n/2, 2.6, "Done!  arr[i] == *(arr+i) — identical.",
                ha='center', color=C_FREE, fontsize=11, fontfamily=FONT,
                bbox=dict(fc=C_BORDER, ec='none', pad=4))
            arrow[0] = label[0] = eq_text[0] = None

    save_gif(fig, update, frames=n + 2, interval=600,
             path=os.path.join(OUT, "gif_pointer_arithmetic.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 3 — 5 Memory Segments lighting up one by one
# ─────────────────────────────────────────────────────────────
def gif_memory_segments():
    segments = [
        ("TEXT\n(machine code — read only)",        C_TEXT,  "Functions, instructions"),
        ("DATA\n(initialised globals)",              C_DATA,  "global_int = 100;"),
        ("BSS\n(uninitialised globals — zeroed)",    C_BSS,   "int g;  // auto = 0"),
        ("HEAP\n(dynamic — malloc/free)",            C_HEAP,  "int *p = malloc(40);"),
        ("STACK\n(automatic — local vars)",          C_STACK, "int x = 42;  // frame"),
    ]

    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 6); ax.set_ylim(-0.5, len(segments) + 1.2)
    ax.axis('off')
    ax.text(3, len(segments) + 0.8, "Virtual Memory — 5 Segments",
            ha='center', color=C_FG, fontsize=13, fontfamily=FONT, fontweight='bold')
    ax.text(5.8, len(segments) + 0.3, "← High address", ha='right',
            color=C_GRAY, fontsize=8, fontfamily=FONT)
    ax.text(5.8, -0.3, "← Low address", ha='right',
            color=C_GRAY, fontsize=8, fontfamily=FONT)

    boxes, labels = [], []

    def update(frame):
        for b in boxes: b.remove()
        for t in labels: t.remove()
        boxes.clear(); labels.clear()

        for i, (name, color, example) in enumerate(segments):
            alpha = 1.0 if i < frame else 0.15
            lw    = 2.5 if i == frame - 1 else 1
            b = ax.add_patch(FancyBboxPatch(
                (0.3, i * 1.0 + 0.05), 5.4, 0.88,
                boxstyle="round,pad=0.04",
                fc=color, ec="white" if i == frame-1 else C_BORDER,
                lw=lw, alpha=alpha))
            boxes.append(b)
            t1 = ax.text(1.5, i * 1.0 + 0.49, name,
                         ha='left', va='center', color="white",
                         fontsize=9, fontfamily=FONT, fontweight='bold', alpha=alpha)
            t2 = ax.text(4.8, i * 1.0 + 0.49, example,
                         ha='right', va='center', color="white",
                         fontsize=8, fontfamily=FONT, fontstyle='italic', alpha=alpha)
            labels.extend([t1, t2])

    save_gif(fig, update, frames=len(segments) + 2, interval=800,
             path=os.path.join(OUT, "gif_memory_segments.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 4 — Dynamic 2D array allocation
# ─────────────────────────────────────────────────────────────
def gif_dynamic_2d_array():
    rows, cols = 3, 4
    row_colors = [C_STACK, C_HEAP, C_BSS]
    row_x = [5.5, 5.5, 5.5]
    row_y = [7.0, 4.5, 2.0]

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 11); ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_title("Dynamic 2D Array — Pointer Array + Scattered Row Blocks",
                 color=C_FG, fontfamily=FONT, fontsize=11)

    # Draw static pointer array spine
    ax.text(1.3, 8.5, "mat[ ] pointer array", color=C_FG, fontsize=9, fontfamily=FONT)
    for i in range(rows):
        ax.add_patch(FancyBboxPatch((0.3, 7.5 - i*1.2), 2.0, 0.9,
                     boxstyle="round,pad=0.04", fc=C_GRAY, ec=C_BORDER, lw=1))
        ax.text(1.3, 7.95 - i*1.2, f"mat[{i}]", ha='center', va='center',
                color=C_FG, fontsize=9, fontfamily=FONT)

    dynamic = []

    def update(frame):
        for obj in dynamic: obj.remove()
        dynamic.clear()

        for i in range(min(frame, rows)):
            color = row_colors[i]
            ry = row_y[i]
            rx = row_x[i]

            # Row data block
            for j in range(cols):
                b = ax.add_patch(FancyBboxPatch(
                    (rx + j*1.15, ry), 1.05, 0.85,
                    boxstyle="round,pad=0.03", fc=color, ec="white", lw=1.2,
                    alpha=0.9))
                dynamic.append(b)
                val = i * cols + j + 1
                t = ax.text(rx + j*1.15 + 0.52, ry + 0.42, str(val),
                            ha='center', va='center', color="white",
                            fontsize=10, fontfamily=FONT, fontweight='bold')
                dynamic.append(t)

            # Label
            lbl = ax.text(rx - 0.3, ry + 0.42,
                          f"row[{i}]\n@heap", ha='right', va='center',
                          color=color, fontsize=8, fontfamily=FONT)
            dynamic.append(lbl)

            # Arrow from pointer array to row block
            arr = ax.annotate("",
                xy=(rx - 0.05, ry + 0.42),
                xytext=(2.3, 7.95 - i*1.2),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5,
                                connectionstyle="arc3,rad=0.0"))
            dynamic.append(arr)

    save_gif(fig, update, frames=rows + 2, interval=900,
             path=os.path.join(OUT, "gif_dynamic_2d_array.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 5 — realloc: grow then move
# ─────────────────────────────────────────────────────────────
def gif_realloc():
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 11); ax.set_ylim(0, 5)
    ax.axis('off')

    states = [
        ("Step 1: malloc(4 ints = 16 bytes)",
         [(0.5, 2.2, 4, 1.2, C_HEAP, "[10|20|30|40]", "0x1000")],
         []),
        ("Step 2: realloc(8 ints) — enough space → extend in place",
         [(0.5, 2.2, 8, 1.2, C_HEAP, "[10|20|30|40|  |  |  |  ]", "0x1000 (same)")],
         []),
        ("Step 3: realloc(8 ints) — NO space → MOVE to new location",
         [(0.5, 2.2, 4, 1.2, C_GRAY, "old (freed)", "0x1000"),
          (5.5, 2.2, 8, 1.2, C_HEAP, "[10|20|30|40|50|60|70|80]", "0x2000 (new)")],
         ["realloc auto-copies old data → new block → frees old"]),
        ("Step 4: realloc(3 ints) — shrink",
         [(5.5, 2.2, 3, 1.2, C_HEAP, "[10|20|30]", "0x2000 (trimmed)"),
          (8.0+3*0.5, 2.2, 5, 1.2, C_GRAY, "(released)", "")],
         []),
    ]

    patches, texts = [], []

    def update(frame):
        for obj in patches + texts: obj.remove()
        patches.clear(); texts.clear()

        if frame >= len(states): frame2 = len(states) - 1
        else: frame2 = frame

        title, blocks, notes = states[frame2]
        t = ax.text(5.5, 4.5, title, ha='center', color=C_FG,
                    fontsize=11, fontfamily=FONT, fontweight='bold',
                    bbox=dict(fc=C_BORDER, ec='none', pad=5))
        texts.append(t)

        for (x, y, w, h, color, label, addr) in blocks:
            b = ax.add_patch(FancyBboxPatch((x, y), w * 0.85, h,
                             boxstyle="round,pad=0.05",
                             fc=color, ec="white", lw=1.5))
            patches.append(b)
            tl = ax.text(x + w*0.425, y + h/2, label,
                         ha='center', va='center', color="white",
                         fontsize=9, fontfamily=FONT)
            ta = ax.text(x + w*0.425, y - 0.3, addr,
                         ha='center', color=C_GRAY, fontsize=8, fontfamily=FONT)
            texts.extend([tl, ta])

        for j, note in enumerate(notes):
            n = ax.text(5.5, 1.5 - j*0.4, note, ha='center',
                        color=C_ACTIVE, fontsize=9, fontfamily=FONT)
            texts.append(n)

    save_gif(fig, update, frames=len(states) + 1, interval=1000,
             path=os.path.join(OUT, "gif_realloc.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 6 — Linked list node insertion
# ─────────────────────────────────────────────────────────────
def gif_linked_list():
    values = [10, 20, 30, 40, 50]
    colors = [C_STACK, C_HEAP, C_BSS, C_DATA, C_TEXT]
    # Scatter positions
    positions = [(1.0, 4.5), (4.5, 6.5), (7.5, 4.0), (3.5, 2.0), (6.5, 1.5)]

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 10); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title("Linked List — Nodes Scattered Across Heap",
                 color=C_FG, fontfamily=FONT, fontsize=12)

    dynamic = []

    def update(frame):
        for obj in dynamic: obj.remove()
        dynamic.clear()
        n_show = min(frame + 1, len(values))

        for i in range(n_show):
            x, y = positions[i]
            color = colors[i]
            # Node box
            b = ax.add_patch(FancyBboxPatch(
                (x - 0.7, y - 0.5), 1.5, 1.0,
                boxstyle="round,pad=0.06",
                fc=color, ec="white", lw=1.5))
            dynamic.append(b)
            tv = ax.text(x + 0.1, y + 0.1, str(values[i]),
                         ha='center', va='center', color="white",
                         fontsize=13, fontfamily=FONT, fontweight='bold')
            tl = ax.text(x + 0.1, y - 0.25, "data",
                         ha='center', va='center', color="white",
                         fontsize=7, fontfamily=FONT)
            addr = f"@0x{0x1000 + i*48:04X}"
            ta = ax.text(x + 0.1, y - 0.65, addr,
                         ha='center', color=color, fontsize=7, fontfamily=FONT)
            dynamic.extend([tv, tl, ta])

            # Arrow to next node
            if i < n_show - 1:
                x2, y2 = positions[i + 1]
                arr = ax.annotate("",
                    xy=(x2 - 0.7, y2),
                    xytext=(x + 0.8, y),
                    arrowprops=dict(arrowstyle="-|>", color="white", lw=1.8,
                                   connectionstyle="arc3,rad=0.2"))
                dynamic.append(arr)
                tp = ax.text((x + x2)/2, (y + y2)/2 + 0.2, "next →",
                             ha='center', color=C_GRAY, fontsize=7, fontfamily=FONT)
                dynamic.append(tp)
            else:
                tn = ax.text(x + 0.9, y, "→ NULL",
                             ha='left', va='center', color=C_GRAY,
                             fontsize=9, fontfamily=FONT)
                dynamic.append(tn)

        status = ax.text(5, 0.4,
            f"Nodes added: {n_show} / {len(values)}   "
            f"(addresses are NOT contiguous — heap scatter!)",
            ha='center', color=C_FG, fontsize=9, fontfamily=FONT,
            bbox=dict(fc=C_BORDER, ec='none', pad=4))
        dynamic.append(status)

    save_gif(fig, update, frames=len(values) + 2, interval=700,
             path=os.path.join(OUT, "gif_linked_list.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 7 — Struct padding byte reveal
# ─────────────────────────────────────────────────────────────
def gif_struct_padding():
    # Bad struct layout: char(1) | PAD(3) | int(4) | char(1) | PAD(7) | double(8) | char(1) | PAD(7)
    # Total = 32 bytes
    layout = [
        ("a", C_STACK, 1),   # char a
        ("PAD", C_PAD, 3),   # 3 pad
        ("b", C_HEAP, 4),    # int b
        ("c", C_BSS, 1),     # char c
        ("PAD", C_PAD, 7),   # 7 pad
        ("d", C_DATA, 8),    # double d
        ("e", C_TEXT, 1),    # char e
        ("PAD", C_PAD, 7),   # 7 pad
    ]

    total = sum(s for _, _, s in layout)
    byte_colors = []
    byte_labels = []
    for name, color, size in layout:
        for _ in range(size):
            byte_colors.append(color)
            byte_labels.append(name)

    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(-0.5, total + 0.5); ax.set_ylim(-1.5, 3.5)
    ax.axis('off')
    ax.set_title(
        f"struct Bad {{char a; int b; char c; double d; char e;}}  →  sizeof = {total} bytes  (15 members + 17 padding!)",
        color=C_FG, fontfamily=FONT, fontsize=10)

    dynamic = []

    def update(frame):
        for obj in dynamic: obj.remove()
        dynamic.clear()

        n_show = min(frame * 2 + 1, total)
        for i in range(n_show):
            fc = byte_colors[i]
            b = ax.add_patch(FancyBboxPatch(
                (i + 0.05, 0.3), 0.88, 1.4,
                boxstyle="round,pad=0.02",
                fc=fc, ec="white", lw=1))
            dynamic.append(b)
            lbl = byte_labels[i]
            t = ax.text(i + 0.49, 1.0, lbl,
                        ha='center', va='center', color="white",
                        fontsize=7, fontfamily=FONT, fontweight='bold')
            dynamic.append(t)
            bi = ax.text(i + 0.49, 0.1, str(i),
                         ha='center', color=C_GRAY, fontsize=6, fontfamily=FONT)
            dynamic.append(bi)

        # Legend
        legend_items = [("member", C_STACK), ("PAD (wasted!)", C_PAD)]
        for j, (lbl, color) in enumerate(legend_items):
            b = ax.add_patch(FancyBboxPatch(
                (j * 5, -1.2), 0.5, 0.5,
                boxstyle="round,pad=0.02", fc=color, ec="white", lw=1))
            t = ax.text(j * 5 + 0.7, -0.95, lbl,
                        va='center', color=C_FG, fontsize=9, fontfamily=FONT)
            dynamic.extend([b, t])

        pad_bytes = sum(s for n, _, s in layout if n == "PAD")
        stat = ax.text(total/2, 2.2,
            f"Revealed: {n_show}/{total} bytes   |   Padding so far: {sum(1 for l in byte_labels[:n_show] if l=='PAD')} wasted bytes",
            ha='center', color=C_FG, fontsize=9, fontfamily=FONT,
            bbox=dict(fc=C_BORDER, ec='none', pad=4))
        dynamic.append(stat)

    frames = total // 2 + 3
    save_gif(fig, update, frames=frames, interval=200,
             path=os.path.join(OUT, "gif_struct_padding.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 8 — Recursive call stack push/pop
# ─────────────────────────────────────────────────────────────
def gif_call_stack():
    calls = [
        "main()",
        "factorial(5)",
        "factorial(4)",
        "factorial(3)",
        "factorial(2)",
        "factorial(1)  ← base case: returns 1",
    ]
    results = [None, None, None, None, 2, 6, 24, 120]

    total_phases = len(calls) + len(calls)  # push all, then pop all

    fig, ax = plt.subplots(figsize=(7, 8))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 6); ax.set_ylim(-0.5, 10)
    ax.axis('off')

    dynamic = []

    def update(frame):
        for obj in dynamic: obj.remove()
        dynamic.clear()

        if frame <= len(calls):
            n_frames = frame
            phase = "PUSH"
        else:
            n_frames = total_phases - frame
            phase = "POP"

        n_frames = max(0, min(n_frames, len(calls)))

        title = ax.text(3, 9.5,
            f"{'→ PUSH frame' if phase=='PUSH' else '← POP frame'}  (stack grows DOWNWARD)",
            ha='center', color=C_ACTIVE if phase=='PUSH' else C_FREE,
            fontsize=11, fontfamily=FONT, fontweight='bold')
        dynamic.append(title)

        ax.text(0.2, 9.2, "HIGH addr", color=C_GRAY, fontsize=7, fontfamily=FONT)
        ax.text(0.2, 0.5, "LOW addr",  color=C_GRAY, fontsize=7, fontfamily=FONT)
        ar = ax.annotate("", xy=(5.5, 0.8), xytext=(5.5, 8.8),
                         arrowprops=dict(arrowstyle="-|>", color=C_GRAY, lw=1))
        dynamic.append(ar)
        albl = ax.text(5.6, 4.8, "stack\ngrows\ndown", color=C_GRAY,
                       fontsize=7, fontfamily=FONT, ha='left')
        dynamic.append(albl)

        for i in range(n_frames):
            y = 8.5 - i * 1.35
            is_top = (i == n_frames - 1)
            color = C_ACTIVE if is_top else C_STACK
            b = ax.add_patch(FancyBboxPatch(
                (0.5, y - 1.2), 4.8, 1.15,
                boxstyle="round,pad=0.05",
                fc=color, ec="white" if is_top else C_BORDER,
                lw=2 if is_top else 1))
            dynamic.append(b)
            t = ax.text(2.9, y - 0.6, calls[i],
                        ha='center', va='center', color="white",
                        fontsize=10, fontfamily=FONT,
                        fontweight='bold' if is_top else 'normal')
            dynamic.append(t)

    save_gif(fig, update, frames=total_phases + 2, interval=600,
             path=os.path.join(OUT, "gif_call_stack.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 9 — Buffer bounds / out-of-bounds danger
# ─────────────────────────────────────────────────────────────
def gif_buffer_bounds():
    n = 5
    arr = [10, 20, 30, 40, 50]
    base = 0x2000

    fig, ax = plt.subplots(figsize=(11, 4.5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(-2, 9); ax.set_ylim(-2, 4)
    ax.axis('off')

    # Draw static canary + array + canary
    for i, (val, lbl, fc) in enumerate([
        (0xDEAD, "canary\nbefore", C_FREE),
        *[(arr[j], f"arr[{j}]", C_HEAP) for j in range(n)],
        (0xBEEF, "canary\nafter",  C_FREE),
    ]):
        xi = i - 1
        ax.add_patch(FancyBboxPatch((xi + 0.05, 0.8), 0.9, 1.6,
                     boxstyle="round,pad=0.02", fc=fc, ec=C_BORDER, lw=1))
        ax.text(xi + 0.5, 1.9, str(val) if isinstance(val, int) else val,
                ha='center', va='center', color="white",
                fontsize=9 if xi != -1 and xi != n else 7, fontfamily=FONT)
        ax.text(xi + 0.5, 0.5, lbl,
                ha='center', color=C_GRAY, fontsize=7, fontfamily=FONT)
        addr = f"0x{base + (xi)*4:04X}" if 0 <= xi < n else ""
        ax.text(xi + 0.5, 0.1, addr, ha='center', color=C_GRAY, fontsize=6, fontfamily=FONT)

    # Label the valid zone
    ax.axvline(0.05,  color=C_FREE, lw=1.5, ls='--', ymin=0.35, ymax=0.85)
    ax.axvline(5.05, color=C_FREE, lw=1.5, ls='--', ymin=0.35, ymax=0.85)

    accesses = [
        (0,  C_FREE,  "arr[0] ✓ safe",   "SAFE"),
        (2,  C_FREE,  "arr[2] ✓ safe",   "SAFE"),
        (4,  C_FREE,  "arr[4] ✓ safe",   "SAFE"),
        (5,  C_LIVE,  "arr[5] ✗ OOB → CORRUPTS canary_after!", "DANGER"),
        (-1, C_LIVE,  "arr[-1] ✗ OOB → CORRUPTS canary_before!", "DANGER"),
        (100, C_LIVE, "arr[100] ✗ OOB → CRASH / undefined behaviour", "DANGER"),
    ]

    dynamic = []

    def update(frame):
        for obj in dynamic: obj.remove()
        dynamic.clear()

        if frame >= len(accesses): frame2 = len(accesses) - 1
        else: frame2 = frame

        idx, color, msg, status = accesses[frame2]
        xi = idx

        if -1 <= xi <= 5:
            hi = ax.add_patch(FancyBboxPatch(
                (xi + 0.05, 0.8), 0.9, 1.6,
                boxstyle="round,pad=0.02",
                fc=color, ec="white", lw=2.5, alpha=0.7))
            dynamic.append(hi)
            ar = ax.annotate("", xy=(xi + 0.5, 0.8),
                             xytext=(xi + 0.5, -0.5),
                             arrowprops=dict(arrowstyle="-|>", color=color, lw=2))
            dynamic.append(ar)
            ptr_lbl = ax.text(xi + 0.5, -0.8, "access\nhere",
                              ha='center', color=color, fontsize=8, fontfamily=FONT)
            dynamic.append(ptr_lbl)

        t = ax.text(3.0, 3.5, msg, ha='center', color=color,
                    fontsize=11, fontfamily=FONT, fontweight='bold',
                    bbox=dict(fc=C_BORDER, ec=color, lw=2, pad=5))
        dynamic.append(t)

    save_gif(fig, update, frames=len(accesses) + 1, interval=800,
             path=os.path.join(OUT, "gif_buffer_bounds.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 10 — Malloc tracker table filling up + leak detection
# ─────────────────────────────────────────────────────────────
def gif_malloc_tracker():
    allocs = [
        ("#01", "0x6b0", "40B",   "arr   (10 ints)"),
        ("#02", "0x6e0", "32B",   "name  (string)"),
        ("#03", "0x710", "12B",   "vec3  (floats)"),
        ("#04", "0x730", "1024B", "buf   (1 KB)  ← LEAKED!"),
    ]
    phases = [
        ("Allocating memory...", [0], []),
        ("Allocating memory...", [0,1], []),
        ("Allocating memory...", [0,1,2], []),
        ("Allocating memory...", [0,1,2,3], []),
        ("Freeing arr, name, vec3...", [0,1,2,3], [0,1,2]),
        ("LEAK DETECTED: buf not freed!", [0,1,2,3], [0,1,2]),
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7)
    ax.axis('off')

    dynamic = []

    def update(frame):
        for obj in dynamic: obj.remove()
        dynamic.clear()

        if frame >= len(phases): frame2 = len(phases)-1
        else: frame2 = frame

        title_str, live_ids, freed_ids = phases[frame2]
        t = ax.text(5, 6.5, title_str, ha='center', color=C_ACTIVE,
                    fontsize=12, fontfamily=FONT, fontweight='bold',
                    bbox=dict(fc=C_BORDER, ec='none', pad=5))
        dynamic.append(t)

        # Table header
        cols = ["ID", "Address", "Size", "Variable", "Status"]
        xs   = [0.5, 2.0, 3.5, 4.8, 8.0]
        hdr = ax.text(5, 5.8, "ALLOCATION TABLE", ha='center', color=C_FG,
                      fontsize=10, fontfamily=FONT, fontweight='bold')
        dynamic.append(hdr)
        for cx, ch in zip(xs, cols):
            ht = ax.text(cx, 5.4, ch, color=C_GRAY, fontsize=9, fontfamily=FONT)
            dynamic.append(ht)

        for i, (id_, addr, size, var) in enumerate(allocs):
            if i not in live_ids: continue
            y = 4.8 - i * 0.9
            freed = i in freed_ids
            is_leak = (i == 3 and frame2 == len(phases)-1)

            row_color = C_GRAY if freed else (C_LIVE if is_leak else C_HEAP)
            b = ax.add_patch(FancyBboxPatch(
                (0.2, y - 0.3), 9.0, 0.7,
                boxstyle="round,pad=0.03", fc=row_color, ec="white", lw=1,
                alpha=0.3 if freed else 0.85))
            dynamic.append(b)

            for cx, val in zip(xs, [id_, addr, size, var,
                                     "FREE ✓" if freed else ("LEAK ⚠" if is_leak else "LIVE")]):
                tc = C_LIVE if is_leak and val.startswith("LEAK") else \
                     (C_FREE if freed and val.startswith("FREE") else C_FG)
                t = ax.text(cx, y + 0.05, val, color=tc, fontsize=9, fontfamily=FONT,
                            fontweight='bold' if is_leak else 'normal')
                dynamic.append(t)

        # Heap bar
        live_bytes = sum(int(allocs[i][2][:-1]) for i in live_ids if i not in freed_ids)
        total_bytes = sum(int(a[2][:-1]) for a in allocs)
        bar_w = 8.0
        frac = live_bytes / max(total_bytes, 1)
        b1 = ax.add_patch(FancyBboxPatch((1.0, 0.3), bar_w, 0.5,
             boxstyle="round,pad=0.02", fc=C_GRAY, ec=C_BORDER, lw=1))
        b2 = ax.add_patch(FancyBboxPatch((1.0, 0.3), bar_w * frac, 0.5,
             boxstyle="round,pad=0.02",
             fc=C_LIVE if frame2 == len(phases)-1 else C_HEAP,
             ec="white", lw=1))
        bl = ax.text(5, 0.1, f"Live heap: {live_bytes} / {total_bytes} bytes",
                     ha='center', color=C_FG, fontsize=9, fontfamily=FONT)
        dynamic.extend([b1, b2, bl])

    save_gif(fig, update, frames=len(phases) + 1, interval=900,
             path=os.path.join(OUT, "gif_malloc_tracker.gif"))


# ─────────────────────────────────────────────────────────────
# RUN ALL
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating GIFs...")
    gif_stack_vs_heap()
    gif_pointer_arithmetic()
    gif_memory_segments()
    gif_dynamic_2d_array()
    gif_realloc()
    gif_linked_list()
    gif_struct_padding()
    gif_call_stack()
    gif_buffer_bounds()
    gif_malloc_tracker()
    print("All done!")

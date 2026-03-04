"""
Generate animated GIFs for the CUDA Mastery blog series.
One GIF per major concept — saved to the same assets/ directory.
Run:  python3 gen_cuda_gifs.py
Requires:  matplotlib  Pillow  numpy
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import matplotlib.patheffects as pe
import numpy as np
from PIL import Image
import io

OUT = os.path.dirname(os.path.abspath(__file__))

# ── colour palette ────────────────────────────────────────────
C_BG       = "#0f1117"   # very dark bg
C_BG2      = "#1a1f2e"   # slightly lighter bg
C_FG       = "#e2e8f0"   # light foreground
C_GRAY     = "#4a5568"   # dim gray
C_BORDER   = "#2d3748"   # border color

# CUDA concept colours
C_THREAD   = "#63b3ed"   # blue — thread
C_WARP     = "#9f7aea"   # purple — warp
C_BLOCK    = "#48bb78"   # green — block
C_GRID     = "#ed8936"   # orange — grid
C_SM       = "#f6ad55"   # amber — SM
C_GLOBAL   = "#fc8181"   # red — global memory (slow)
C_SHARED   = "#68d391"   # green — shared memory (fast)
C_REG      = "#63b3ed"   # blue — registers (fastest)
C_CONST    = "#b794f4"   # purple — constant
C_L2       = "#f6ad55"   # amber — L2
C_ACTIVE   = "#ffd166"   # yellow — active/highlighted
C_STALL    = "#e53e3e"   # red — stalled
C_COALESCED = "#68d391"  # green — good
C_STRIDED  = "#fc8181"   # red — bad

FONT = "monospace"


def save_gif(fig, update_fn, frames, interval, path, dpi=96):
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
# GIF 1 — Thread Hierarchy: Thread → Block → Grid
# ─────────────────────────────────────────────────────────────
def gif_thread_hierarchy():
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.axis('off')

    dynamic = []

    # Labels for phases
    phases = [
        "Step 1: One THREAD — executes one kernel instance",
        "Step 2: 16 threads form a BLOCK — can share memory via __shared__",
        "Step 3: Grid of 4 BLOCKS — all blocks execute the same kernel",
        "Step 4: Each block maps to an SM — blocks are independent!",
        "Full picture: Grid → Blocks → Warps → Threads",
    ]

    def draw_thread(ax, x, y, color, label="", small=False):
        size = 0.28 if small else 0.38
        b = ax.add_patch(FancyBboxPatch((x - size/2, y - size/2), size, size,
                         boxstyle="round,pad=0.03",
                         fc=color, ec="white", lw=0.8, alpha=0.9))
        if label:
            ax.text(x, y, label, ha='center', va='center',
                    color="white", fontsize=6 if small else 7,
                    fontfamily=FONT, fontweight='bold')
        return b

    def update(frame):
        for obj in dynamic:
            try: obj.remove()
            except: pass
        dynamic.clear()

        phase = min(frame, len(phases) - 1)

        # Title
        t = ax.text(6, 6.65, phases[phase], ha='center', color=C_ACTIVE,
                    fontsize=11, fontfamily=FONT, fontweight='bold',
                    bbox=dict(fc=C_BG2, ec=C_BORDER, lw=1, pad=6, boxstyle='round'))
        dynamic.append(t)

        if phase == 0:
            # Single thread
            b = draw_thread(ax, 6, 3.5, C_THREAD, "T0")
            dynamic.append(b)
            t1 = ax.text(6, 2.8, "threadIdx.x = 0", ha='center',
                         color=C_THREAD, fontsize=10, fontfamily=FONT)
            t2 = ax.text(6, 2.4, "blockIdx.x  = 0", ha='center',
                         color=C_GRAY, fontsize=10, fontfamily=FONT)
            dynamic.extend([t1, t2])

        elif phase == 1:
            # One block of 4x4=16 threads
            block_x, block_y = 4.0, 1.5
            bw, bh = 4.5, 4.0
            block_bg = ax.add_patch(FancyBboxPatch(
                (block_x - 0.2, block_y - 0.2), bw + 0.4, bh + 0.4,
                boxstyle="round,pad=0.1",
                fc=C_BLOCK, ec="white", lw=2, alpha=0.15))
            dynamic.append(block_bg)
            block_lbl = ax.text(block_x + bw/2, block_y + bh + 0.15,
                                "Block (0,0)  blockDim = 4×4 = 16 threads",
                                ha='center', color=C_BLOCK, fontsize=9, fontfamily=FONT,
                                fontweight='bold')
            dynamic.append(block_lbl)

            for row in range(4):
                for col in range(4):
                    tx = block_x + col * 1.1 + 0.35
                    ty = block_y + row * 0.95 + 0.3
                    b = draw_thread(ax, tx, ty, C_THREAD,
                                    f"T{row*4+col}")
                    dynamic.append(b)

        elif phase == 2:
            # Grid of 4 blocks
            block_labels = ["Block 0", "Block 1", "Block 2", "Block 3"]
            block_colors = [C_BLOCK, "#4299e1", "#68d391", "#f6ad55"]
            for bi, (blbl, bclr) in enumerate(zip(block_labels, block_colors)):
                bx = bi * 2.8 + 0.5
                by = 1.0
                bg = ax.add_patch(FancyBboxPatch(
                    (bx, by), 2.5, 4.5,
                    boxstyle="round,pad=0.1",
                    fc=bclr, ec="white", lw=1.5, alpha=0.12))
                dynamic.append(bg)
                lbl = ax.text(bx + 1.25, by + 4.65, blbl,
                              ha='center', color=bclr,
                              fontsize=9, fontfamily=FONT, fontweight='bold')
                dynamic.append(lbl)
                # 8 mini threads per block
                for t_idx in range(8):
                    tr = t_idx // 4
                    tc = t_idx % 4
                    tx = bx + tc * 0.58 + 0.3
                    ty = by + tr * 0.7 + 0.5
                    b2 = draw_thread(ax, tx, ty, bclr, f"T{t_idx}", small=True)
                    dynamic.append(b2)

            grid_lbl = ax.text(6, 6.0, "Grid: 4 blocks × 8 threads = 32 threads total",
                               ha='center', color=C_GRID,
                               fontsize=10, fontfamily=FONT)
            dynamic.append(grid_lbl)

        elif phase == 3:
            # Blocks → SMs
            sm_labels = ["SM 0", "SM 1", "SM 2", "SM 3"]
            block_labels = ["Block 0", "Block 1", "Block 2", "Block 3"]
            for i in range(4):
                # SM box
                sx = i * 2.8 + 0.4
                sm_bg = ax.add_patch(FancyBboxPatch(
                    (sx, 0.5), 2.6, 5.5,
                    boxstyle="round,pad=0.1",
                    fc=C_SM, ec="white", lw=1.5, alpha=0.08))
                dynamic.append(sm_bg)
                sm_lbl = ax.text(sx + 1.3, 6.1, sm_labels[i],
                                 ha='center', color=C_SM,
                                 fontsize=10, fontfamily=FONT, fontweight='bold')
                dynamic.append(sm_lbl)
                # Block inside SM
                blk_bg = ax.add_patch(FancyBboxPatch(
                    (sx + 0.2, 0.8), 2.2, 2.8,
                    boxstyle="round,pad=0.1",
                    fc=C_BLOCK, ec="white", lw=1.2, alpha=0.2))
                dynamic.append(blk_bg)
                blk_lbl = ax.text(sx + 1.3, 3.75, block_labels[i],
                                  ha='center', color=C_BLOCK,
                                  fontsize=8, fontfamily=FONT)
                dynamic.append(blk_lbl)
                # Threads
                for t_idx in range(8):
                    tr = t_idx // 4
                    tc = t_idx % 4
                    tx = sx + tc * 0.52 + 0.42
                    ty = 0.95 + tr * 0.65
                    b2 = draw_thread(ax, tx, ty, C_THREAD, f"T{t_idx}", small=True)
                    dynamic.append(b2)

            note = ax.text(6, 0.2,
                           "Blocks are assigned to SMs — you don't control which SM!",
                           ha='center', color=C_GRAY, fontsize=9, fontfamily=FONT)
            dynamic.append(note)

        else:
            # Summary diagram
            # Thread → Warp → Block → Grid
            items = [
                (1.5, 3.5, "Thread\n(1 execution unit)", C_THREAD, "0.5"),
                (4.0, 3.5, "Warp\n(32 threads in lockstep)", C_WARP, "1.0"),
                (7.0, 3.5, "Block\n(N warps, share __shared__)", C_BLOCK, "1.8"),
                (10.0, 3.5, "Grid\n(all blocks, 1 kernel launch)", C_GRID, "1.0"),
            ]
            for (x, y, lbl, clr, sz) in items:
                sz_f = float(sz)
                b = ax.add_patch(FancyBboxPatch(
                    (x - sz_f/2, y - 0.5), sz_f, 1.0,
                    boxstyle="round,pad=0.08",
                    fc=clr, ec="white", lw=1.5, alpha=0.85))
                dynamic.append(b)
                t = ax.text(x, y, lbl, ha='center', va='center',
                            color="white", fontsize=8, fontfamily=FONT,
                            fontweight='bold')
                dynamic.append(t)

            for (x1, x2) in [(2.0, 3.0), (5.0, 5.9), (8.9, 9.5)]:
                arr = ax.annotate("", xy=(x2, 3.5), xytext=(x1, 3.5),
                                  arrowprops=dict(arrowstyle="-|>",
                                                  color="white", lw=2))
                dynamic.append(arr)

            legend_items = [
                ("Thread: 1 CUDA core executing 1 kernel instance", C_THREAD),
                ("Warp: 32 threads — REAL execution unit (SIMT)", C_WARP),
                ("Block: group of warps sharing __shared__ memory", C_BLOCK),
                ("Grid: all blocks for one kernel launch", C_GRID),
            ]
            for j, (lbl, clr) in enumerate(legend_items):
                t = ax.text(0.4, 2.5 - j * 0.5, f"■ {lbl}",
                            color=clr, fontsize=8.5, fontfamily=FONT)
                dynamic.append(t)

    save_gif(fig, update, frames=len(phases) + 1, interval=1200,
             path=os.path.join(OUT, "gif_cuda_thread_hierarchy.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 2 — Memory Coalescing: coalesced vs strided
# ─────────────────────────────────────────────────────────────
def gif_memory_coalescing():
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    fig.patch.set_facecolor(C_BG)
    for ax in axes:
        ax.set_facecolor(C_BG)
        ax.axis('off')

    axes[0].set_xlim(0, 32); axes[0].set_ylim(-1, 4)
    axes[1].set_xlim(0, 32); axes[1].set_ylim(-1, 4)

    axes[0].set_title("COALESCED ACCESS (stride-1) → 1 memory transaction ✓",
                      color=C_COALESCED, fontfamily=FONT, fontsize=11, pad=8)
    axes[1].set_title("STRIDED ACCESS (stride-4) → 4 memory transactions ✗",
                      color=C_STRIDED, fontfamily=FONT, fontsize=11, pad=8)

    # Draw 32 memory cells per axis
    for ax in axes:
        for i in range(32):
            ax.add_patch(FancyBboxPatch(
                (i * 0.98 + 0.02, 1.2), 0.9, 0.9,
                boxstyle="round,pad=0.02",
                fc=C_BG2, ec=C_BORDER, lw=0.8))
            ax.text(i * 0.98 + 0.47, 1.65, str(i),
                    ha='center', va='center',
                    color=C_GRAY, fontsize=6, fontfamily=FONT)
        ax.text(16, 0.8, "Global Memory Addresses [0..31]",
                ha='center', color=C_GRAY, fontsize=8, fontfamily=FONT)

    dynamic_top = []
    dynamic_bot = []

    def update(frame):
        for obj in dynamic_top + dynamic_bot:
            try: obj.remove()
            except: pass
        dynamic_top.clear()
        dynamic_bot.clear()

        n_show = min(frame * 4 + 1, 32)
        n_threads = min(frame + 1, 8)

        # --- TOP: coalesced ---
        # Highlight contiguous cells 0..n_show-1
        highlight_end = min(32, n_threads * 4)
        for i in range(highlight_end):
            b = axes[0].add_patch(FancyBboxPatch(
                (i * 0.98 + 0.02, 1.2), 0.9, 0.9,
                boxstyle="round,pad=0.02",
                fc=C_COALESCED, ec="white", lw=1.2, alpha=0.85))
            dynamic_top.append(b)
            t = axes[0].text(i * 0.98 + 0.47, 1.65, str(i),
                             ha='center', va='center',
                             color="white", fontsize=6, fontfamily=FONT,
                             fontweight='bold')
            dynamic_top.append(t)

        # Thread arrows to contiguous cells
        for t_i in range(min(n_threads, 8)):
            addr = t_i  # contiguous
            arr = axes[0].annotate("",
                xy=(addr * 0.98 + 0.47, 2.1),
                xytext=(addr * 0.98 + 0.47, 3.5),
                arrowprops=dict(arrowstyle="-|>", color=C_THREAD, lw=1.5))
            dynamic_top.append(arr)
            tl = axes[0].text(addr * 0.98 + 0.47, 3.65, f"T{t_i}",
                              ha='center', color=C_THREAD, fontsize=7,
                              fontfamily=FONT, fontweight='bold')
            dynamic_top.append(tl)

        # One cache line box
        cl = axes[0].add_patch(FancyBboxPatch(
            (0.02, 1.0), min(n_threads, 8) * 0.98, 1.3,
            boxstyle="round,pad=0.05",
            fc='none', ec=C_COALESCED, lw=2.5, ls='--'))
        dynamic_top.append(cl)
        cl_lbl = axes[0].text(min(n_threads, 4) * 0.49, 0.7,
                              f"← {min(n_threads,8) * 4} bytes = {max(1, min(n_threads,8)//8)} cache line(s)",
                              ha='left', color=C_COALESCED, fontsize=9, fontfamily=FONT)
        dynamic_top.append(cl_lbl)

        # --- BOT: strided ---
        stride = 4
        for t_i in range(min(n_threads, 8)):
            addr = t_i * stride
            if addr < 32:
                b = axes[1].add_patch(FancyBboxPatch(
                    (addr * 0.98 + 0.02, 1.2), 0.9, 0.9,
                    boxstyle="round,pad=0.02",
                    fc=C_STRIDED, ec="white", lw=1.2, alpha=0.85))
                dynamic_bot.append(b)
                tv = axes[1].text(addr * 0.98 + 0.47, 1.65, str(addr),
                                  ha='center', va='center',
                                  color="white", fontsize=6, fontfamily=FONT,
                                  fontweight='bold')
                dynamic_bot.append(tv)
                arr = axes[1].annotate("",
                    xy=(addr * 0.98 + 0.47, 2.1),
                    xytext=(addr * 0.98 + 0.47, 3.5),
                    arrowprops=dict(arrowstyle="-|>", color=C_THREAD, lw=1.5))
                dynamic_bot.append(arr)
                tl = axes[1].text(addr * 0.98 + 0.47, 3.65, f"T{t_i}",
                                  ha='center', color=C_THREAD, fontsize=7,
                                  fontfamily=FONT, fontweight='bold')
                dynamic_bot.append(tl)

                # Each strided access spans a separate cache line
                cl_b = axes[1].add_patch(FancyBboxPatch(
                    (addr * 0.98 - 0.01, 1.05), 3.9, 1.3,
                    boxstyle="round,pad=0.05",
                    fc='none', ec=C_STRIDED, lw=1.5, ls='--', alpha=0.7))
                dynamic_bot.append(cl_b)

        n_transactions = min(n_threads, 8)
        stat = axes[1].text(16, 0.6,
                            f"{n_transactions} threads → {n_transactions} cache line transactions  (vs 1 for coalesced!)",
                            ha='center', color=C_STRIDED, fontsize=9, fontfamily=FONT,
                            fontweight='bold')
        dynamic_bot.append(stat)

    fig.tight_layout()
    save_gif(fig, update, frames=9, interval=500,
             path=os.path.join(OUT, "gif_cuda_memory_coalescing.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 3 — Warp Divergence: two paths, serialize
# ─────────────────────────────────────────────────────────────
def gif_warp_divergence():
    fig, axes = plt.subplots(1, 2, figsize=(13, 7))
    fig.patch.set_facecolor(C_BG)
    for ax in axes:
        ax.set_facecolor(C_BG)
        ax.axis('off')
        ax.set_xlim(0, 6)
        ax.set_ylim(0, 8)

    axes[0].set_title("NO DIVERGENCE\n(all threads same path)", color=C_COALESCED,
                      fontfamily=FONT, fontsize=11, pad=10)
    axes[1].set_title("WITH DIVERGENCE\n(if threadIdx.x < 16)", color=C_STRIDED,
                      fontfamily=FONT, fontsize=11, pad=10)

    dynamic = []
    warp_size = 8  # reduced for visual clarity (represents 32)

    phases = [
        "All 8 threads: same instruction → 1 pass",
        "Divergent: threads 0-3 take branch A",
        "Divergent: threads 4-7 take branch B (serialized!)",
        "Result: NO divergence = 1 pass | WITH divergence = 2 passes",
    ]

    def update(frame):
        for obj in dynamic:
            try: obj.remove()
            except: pass
        dynamic.clear()

        phase = min(frame, len(phases) - 1)

        # Phase label
        t = fig.text(0.5, 0.97, phases[phase],
                     ha='center', color=C_ACTIVE,
                     fontsize=11, fontfamily=FONT, fontweight='bold',
                     transform=fig.transFigure)
        dynamic.append(t)

        # Draw 8 thread boxes for each side
        for ax_idx, ax in enumerate(axes):
            for i in range(warp_size):
                x = (i % 4) * 1.3 + 0.5
                y = (1 - i // 4) * 2.2 + 4.5

                if ax_idx == 0:
                    # No divergence: all green when active
                    if phase == 0:
                        color = C_COALESCED
                        lbl = "exec"
                    else:
                        color = C_COALESCED
                        lbl = "done ✓"
                else:
                    # With divergence
                    if phase == 0:
                        color = C_GRAY
                        lbl = "wait"
                    elif phase == 1:
                        color = C_COALESCED if i < 4 else C_GRAY
                        lbl = "A" if i < 4 else "masked"
                    elif phase == 2:
                        color = C_STRIDED if i >= 4 else C_GRAY
                        lbl = "masked" if i < 4 else "B"
                    else:
                        color = C_COALESCED if i < 4 else C_STRIDED
                        lbl = "A✓" if i < 4 else "B✓"

                b = ax.add_patch(FancyBboxPatch(
                    (x - 0.45, y - 0.35), 0.9, 0.7,
                    boxstyle="round,pad=0.05",
                    fc=color, ec="white", lw=1.2, alpha=0.9 if color != C_GRAY else 0.3))
                dynamic.append(b)
                tl = ax.text(x, y + 0.02, f"T{i}\n{lbl}",
                             ha='center', va='center',
                             color="white", fontsize=7.5, fontfamily=FONT)
                dynamic.append(tl)

            # Branch code visualization
            if ax_idx == 0:
                code_lines = [
                    "// No branch — all threads",
                    "result[i] = data[i] * 2;",
                    "",
                    "→ 1 pass, all 8 threads active",
                ]
                color_lines = [C_GRAY, C_FG, C_GRAY, C_COALESCED]
            else:
                code_lines = [
                    "if (threadIdx.x < 4) {",
                    "   branch_A();  // T0-T3 run",
                    "} else {",
                    "   branch_B();  // T4-T7 run",
                    "}",
                    "→ 2 passes — serialized!",
                ]
                color_lines = [C_FG, C_COALESCED, C_FG, C_STRIDED, C_FG, C_STRIDED]

            for li, (line, lclr) in enumerate(zip(code_lines, color_lines)):
                ct = ax.text(0.3, 3.8 - li * 0.52, line,
                             color=lclr, fontsize=9, fontfamily=FONT)
                dynamic.append(ct)

            # Timing bar
            if ax_idx == 0:
                timing_lbl = "Time: ████  (1 pass)"
                t_color = C_COALESCED
            else:
                if phase <= 1:
                    timing_lbl = "Time: ████        (pass 1 of 2...)"
                    t_color = C_STRIDED
                else:
                    timing_lbl = "Time: ████ ████  (2 passes = 2× slower)"
                    t_color = C_STRIDED

            tbar = ax.text(3.0, 1.2, timing_lbl,
                           ha='center', color=t_color,
                           fontsize=9, fontfamily=FONT, fontweight='bold')
            dynamic.append(tbar)

    save_gif(fig, update, frames=len(phases) + 1, interval=1100,
             path=os.path.join(OUT, "gif_cuda_warp_divergence.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 4 — Memory Hierarchy: latency pyramid
# ─────────────────────────────────────────────────────────────
def gif_memory_hierarchy():
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 10); ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_title("CUDA Memory Hierarchy — Latency vs Size",
                 color=C_FG, fontfamily=FONT, fontsize=13, fontweight='bold', pad=10)

    levels = [
        # (y, width, color, name, latency, bandwidth, size)
        (7.5, 2.0, C_REG,    "Registers",     "~1 cycle",    "—",          "255/thread"),
        (6.2, 3.5, C_SHARED, "Shared Memory", "~5 cycles",   ">10 TB/s",   "48 KB/block"),
        (5.0, 5.0, C_L2,     "L1 / Tex Cache","~30 cycles",  "5+ TB/s",    "48 KB/SM"),
        (3.8, 6.5, "#4299e1","L2 Cache",      "~200 cycles", "2-3 TB/s",   "40 MB (A100)"),
        (2.4, 8.5, C_GLOBAL, "Global Memory", "~800 cycles", "2 TB/s",     "80 GB (A100)"),
        (1.0, 10.0, "#c53030","Host Memory",  "millions",    "32 GB/s PCIe","TBs (system)"),
    ]

    dynamic = []

    def update(frame):
        for obj in dynamic:
            try: obj.remove()
            except: pass
        dynamic.clear()

        n_show = min(frame + 1, len(levels))

        for i in range(n_show):
            y, w, color, name, lat, bw, size = levels[i]
            x_start = (10 - w) / 2
            alpha = 1.0 if i == n_show - 1 else 0.75
            b = ax.add_patch(FancyBboxPatch(
                (x_start, y), w, 1.0,
                boxstyle="round,pad=0.06",
                fc=color, ec="white", lw=2 if i == n_show - 1 else 1,
                alpha=alpha))
            dynamic.append(b)

            # Name
            tn = ax.text(5, y + 0.62, name,
                         ha='center', va='center', color="white",
                         fontsize=11, fontfamily=FONT, fontweight='bold')
            dynamic.append(tn)

            # Left: latency
            tl = ax.text(x_start - 0.15, y + 0.5, f"⏱ {lat}",
                         ha='right', va='center', color=color,
                         fontsize=9, fontfamily=FONT)
            dynamic.append(tl)

            # Right: size
            tr = ax.text(x_start + w + 0.15, y + 0.5, size,
                         ha='left', va='center', color=color,
                         fontsize=9, fontfamily=FONT)
            dynamic.append(tr)

        # Arrows
        if n_show > 1:
            arr_up = ax.annotate("", xy=(0.4, 8.6), xytext=(0.4, 0.8),
                                 arrowprops=dict(arrowstyle="-|>", color=C_COALESCED,
                                                 lw=2))
            arr_dn = ax.annotate("", xy=(0.4, 0.8), xytext=(0.4, 8.6),
                                 arrowprops=dict(arrowstyle="-|>", color=C_STRIDED,
                                                 lw=2))
            dynamic.extend([arr_up, arr_dn])
            lbl_speed = ax.text(0.2, 7.5, "Faster\n&\nSmaller",
                                ha='center', color=C_COALESCED,
                                fontsize=8, fontfamily=FONT)
            lbl_size = ax.text(0.2, 2.0, "Slower\n&\nBigger",
                               ha='center', color=C_STRIDED,
                               fontsize=8, fontfamily=FONT)
            dynamic.extend([lbl_speed, lbl_size])

    save_gif(fig, update, frames=len(levels) + 2, interval=800,
             path=os.path.join(OUT, "gif_cuda_memory_hierarchy.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 5 — Parallel Reduction: tree animation
# ─────────────────────────────────────────────────────────────
def gif_parallel_reduction():
    values = [8, 3, 7, 2, 5, 1, 4, 6]
    n = len(values)

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(-0.5, n + 0.5); ax.set_ylim(-0.5, 6.5)
    ax.axis('off')

    # Each step halves
    steps = [list(values)]
    curr = list(values)
    while len(curr) > 1:
        nxt = [curr[i] + curr[i+1] for i in range(0, len(curr), 2)]
        steps.append(nxt)
        curr = nxt

    step_labels = [
        "Initial values: each thread holds one element",
        "Step 1 (stride=4): T0+=T4, T1+=T5, T2+=T6, T3+=T7",
        "Step 2 (stride=2): T0+=T2, T1+=T3",
        "Step 3 (stride=1): T0+=T1 → FINAL SUM",
        f"Result: T0 holds sum = {sum(values)} ✓",
    ]

    dynamic = []

    colors_by_step = [C_THREAD, C_WARP, C_BLOCK, C_ACTIVE, C_COALESCED]

    def update(frame):
        for obj in dynamic:
            try: obj.remove()
            except: pass
        dynamic.clear()

        phase = min(frame, len(steps) - 1)
        step_values = steps[phase]
        n_active = len(step_values)

        # Title
        t = ax.text(n/2, 6.2, step_labels[min(phase, len(step_labels)-1)],
                    ha='center', color=C_ACTIVE, fontsize=11, fontfamily=FONT,
                    fontweight='bold',
                    bbox=dict(fc=C_BG2, ec=C_BORDER, pad=6, boxstyle='round'))
        dynamic.append(t)

        clr = colors_by_step[min(phase, len(colors_by_step)-1)]

        # Draw all original boxes dimmed
        for i in range(n):
            is_active = i < n_active
            alpha = 0.9 if is_active else 0.2
            b = ax.add_patch(FancyBboxPatch(
                (i * 1.1 + 0.05, 2.5), 0.95, 1.2,
                boxstyle="round,pad=0.05",
                fc=clr if is_active else C_GRAY,
                ec="white" if is_active else C_BORDER,
                lw=1.5 if is_active else 0.5,
                alpha=alpha))
            dynamic.append(b)

            # Value
            val = step_values[i] if i < n_active else None
            if val is not None:
                tv = ax.text(i * 1.1 + 0.52, 3.1, str(val),
                             ha='center', va='center',
                             color="white", fontsize=14, fontfamily=FONT,
                             fontweight='bold')
                dynamic.append(tv)

            # Thread label
            tl = ax.text(i * 1.1 + 0.52, 2.3, f"T{i}",
                         ha='center', color=C_GRAY if not is_active else C_THREAD,
                         fontsize=8, fontfamily=FONT)
            dynamic.append(tl)

        # Draw reduction arrows
        if phase > 0 and phase < len(steps):
            stride = n // (2 ** phase)
            for i in range(0, n_active):
                src = i + stride
                if src < n:
                    ax.annotate("",
                        xy=(i * 1.1 + 0.52, 3.7),
                        xytext=(src * 1.1 + 0.52, 3.7),
                        arrowprops=dict(arrowstyle="<-",
                                        color=C_ACTIVE, lw=2,
                                        connectionstyle="arc3,rad=-0.3"))

        # Bottom: show equation
        if phase > 0:
            eq_parts = [str(v) for v in steps[0]]
            eq = " + ".join(eq_parts)
            eq_result = sum(steps[0])
            eq_t = ax.text(n/2, 1.5, f"{eq} = {eq_result}",
                           ha='center', color=C_FG,
                           fontsize=10, fontfamily=FONT)
            dynamic.append(eq_t)

        # Step indicator
        for s in range(len(steps)):
            is_curr = (s == phase)
            step_b = ax.add_patch(FancyBboxPatch(
                (s * 1.3 + 0.5, 0.3), 1.1, 0.5,
                boxstyle="round,pad=0.05",
                fc=clr if is_curr else C_GRAY,
                ec="white", lw=1,
                alpha=1.0 if is_curr else 0.4))
            dynamic.append(step_b)
            step_t = ax.text(s * 1.3 + 1.05, 0.55, f"Step {s}",
                             ha='center', va='center',
                             color="white", fontsize=7.5, fontfamily=FONT)
            dynamic.append(step_t)

    save_gif(fig, update, frames=len(steps) + 2, interval=900,
             path=os.path.join(OUT, "gif_cuda_parallel_reduction.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 6 — Shared Memory Tiling
# ─────────────────────────────────────────────────────────────
def gif_shared_memory_tiling():
    TILE = 4
    N = 8  # total matrix size

    fig, (ax_global, ax_shared, ax_output) = plt.subplots(1, 3, figsize=(14, 7))
    fig.patch.set_facecolor(C_BG)
    for ax in (ax_global, ax_shared, ax_output):
        ax.set_facecolor(C_BG)
        ax.axis('off')
        ax.set_xlim(-0.5, N + 0.5)
        ax.set_ylim(-0.5, N + 1.5)

    ax_global.set_title("Global Memory\n(slow, ~800 cycles)", color=C_GLOBAL,
                        fontfamily=FONT, fontsize=10)
    ax_shared.set_title("Shared Memory Tile\n(fast, ~5 cycles)", color=C_SHARED,
                        fontfamily=FONT, fontsize=10)
    ax_output.set_title("Output Matrix C\n(being computed)", color=C_L2,
                        fontfamily=FONT, fontsize=10)

    # Draw base grids
    for ax in (ax_global, ax_output):
        for r in range(N):
            for c in range(N):
                ax.add_patch(FancyBboxPatch(
                    (c * 1.05, (N-1-r) * 1.05), 0.95, 0.95,
                    boxstyle="round,pad=0.02",
                    fc=C_BG2, ec=C_BORDER, lw=0.5))

    # Shared mem: TILE x TILE grid
    for r in range(TILE):
        for c in range(TILE):
            ax_shared.add_patch(FancyBboxPatch(
                (c * 2.05 + 0.5, (TILE-1-r) * 2.05 + 2.0), 1.95, 1.95,
                boxstyle="round,pad=0.05",
                fc=C_BG2, ec=C_BORDER, lw=0.8))

    dynamic = []

    tile_phases = [
        (0, 0, "Load tile A[0:4, 0:4] into shared memory (As)"),
        (0, 0, "Load tile B[0:4, 0:4] into shared memory (Bs)"),
        (0, 0, "Compute: C[0:4, 0:4] += As × Bs  (uses only shared memory!)"),
        (1, 0, "Load next tile: A[0:4, 4:8] and B[4:8, 0:4]"),
        (1, 0, "Compute: C[0:4, 0:4] += As × Bs  (accumulated)"),
        (0, 1, "Move to next block: A[4:8, 0:4] and B[0:4, 4:8]"),
        (0, 1, "Full result computed — only TILE global loads per tile!"),
    ]

    def update(frame):
        for obj in dynamic:
            try: obj.remove()
            except: pass
        dynamic.clear()

        phase = min(frame, len(tile_phases) - 1)
        tile_row, tile_col, desc = tile_phases[phase]

        # Title
        t = fig.text(0.5, 0.97, desc, ha='center', color=C_ACTIVE,
                     fontsize=11, fontfamily=FONT, fontweight='bold',
                     transform=fig.transFigure)
        dynamic.append(t)

        # Highlight tile in global A (left matrix)
        ar = tile_col  # A tile column
        ac_start = ar * TILE
        for r in range(TILE):
            for c in range(TILE):
                gr = tile_row * TILE + r
                gc = ac_start + c
                b = ax_global.add_patch(FancyBboxPatch(
                    (gc * 1.05, (N-1-gr) * 1.05), 0.95, 0.95,
                    boxstyle="round,pad=0.02",
                    fc=C_GLOBAL, ec="white", lw=1.5, alpha=0.8))
                dynamic.append(b)
                val = gr * N + gc + 1
                tv = ax_global.text(gc * 1.05 + 0.47, (N-1-gr) * 1.05 + 0.47,
                                    str(val % 10),
                                    ha='center', va='center',
                                    color="white", fontsize=8, fontfamily=FONT)
                dynamic.append(tv)

        # Fill shared memory tile
        for r in range(TILE):
            for c in range(TILE):
                clr = C_SHARED if phase >= 1 else C_GLOBAL
                b = ax_shared.add_patch(FancyBboxPatch(
                    (c * 2.05 + 0.5, (TILE-1-r) * 2.05 + 2.0), 1.95, 1.95,
                    boxstyle="round,pad=0.05",
                    fc=clr, ec="white", lw=1.5, alpha=0.8))
                dynamic.append(b)
                tv = ax_shared.text(c * 2.05 + 1.47, (TILE-1-r) * 2.05 + 2.97,
                                    f"a{r}{c}",
                                    ha='center', va='center',
                                    color="white", fontsize=9, fontfamily=FONT,
                                    fontweight='bold')
                dynamic.append(tv)

        lbl_smem = ax_shared.text(4.5, 1.3,
                                  "As[ ] — shared\n5 cycles to access",
                                  ha='center', color=C_SHARED,
                                  fontsize=9, fontfamily=FONT)
        dynamic.append(lbl_smem)

        # Highlight output tile
        for r in range(TILE):
            for c in range(TILE):
                gr = tile_row * TILE + r
                gc = tile_col * TILE + c
                clr = C_L2 if phase >= 2 else C_BG2
                lw = 1.5 if phase >= 2 else 0.5
                b = ax_output.add_patch(FancyBboxPatch(
                    (gc * 1.05, (N-1-gr) * 1.05), 0.95, 0.95,
                    boxstyle="round,pad=0.02",
                    fc=clr, ec="white", lw=lw, alpha=0.8))
                dynamic.append(b)
                if phase >= 2:
                    tv = ax_output.text(gc * 1.05 + 0.47, (N-1-gr) * 1.05 + 0.47,
                                        "✓",
                                        ha='center', va='center',
                                        color="white", fontsize=10, fontfamily=FONT)
                    dynamic.append(tv)

        # Arrow from global → shared
        if phase == 0:
            arr = fig.patches  # connection via text
            arr_t = fig.text(0.37, 0.5, "→\nload",
                             ha='center', color=C_GLOBAL,
                             fontsize=11, fontfamily=FONT, fontweight='bold',
                             transform=fig.transFigure)
            dynamic.append(arr_t)

        if phase >= 2:
            arr_t = fig.text(0.67, 0.5, "→\ncompute",
                             ha='center', color=C_SHARED,
                             fontsize=11, fontfamily=FONT, fontweight='bold',
                             transform=fig.transFigure)
            dynamic.append(arr_t)

    fig.tight_layout()
    save_gif(fig, update, frames=len(tile_phases) + 1, interval=1000,
             path=os.path.join(OUT, "gif_cuda_shared_memory_tiling.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 7 — Bank Conflicts
# ─────────────────────────────────────────────────────────────
def gif_bank_conflicts():
    fig, axes = plt.subplots(1, 2, figsize=(13, 7))
    fig.patch.set_facecolor(C_BG)
    for ax in axes:
        ax.set_facecolor(C_BG)
        ax.axis('off')
        ax.set_xlim(-0.5, 8.5)
        ax.set_ylim(-0.5, 9.5)

    axes[0].set_title("NO BANK CONFLICT\nStride-1 access", color=C_COALESCED,
                      fontfamily=FONT, fontsize=11, pad=10)
    axes[1].set_title("BANK CONFLICT\nStride-8 access (8-way conflict!)", color=C_STRIDED,
                      fontfamily=FONT, fontsize=11, pad=10)

    # Draw 8 banks × 8 rows (simplified from 32 banks)
    N_BANKS = 8
    N_ROWS = 3

    for ax in axes:
        # Bank labels
        for b in range(N_BANKS):
            ax.text(b + 0.5, 8.8, f"Bank {b}",
                    ha='center', color=C_GRAY, fontsize=7.5, fontfamily=FONT)
        # Draw cells
        for r in range(N_ROWS):
            for b in range(N_BANKS):
                idx = r * N_BANKS + b
                ax.add_patch(FancyBboxPatch(
                    (b + 0.05, 7.5 - r * 1.2), 0.9, 1.0,
                    boxstyle="round,pad=0.03",
                    fc=C_BG2, ec=C_BORDER, lw=0.8))
                ax.text(b + 0.5, 8.0 - r * 1.2, f"[{idx}]",
                        ha='center', va='center',
                        color=C_GRAY, fontsize=8, fontfamily=FONT)

    dynamic = []

    N_THREADS = 8
    phases = [
        "8 threads issue shared memory reads",
        "No conflict: each thread → different bank → 1 transaction ✓",
        "Conflict: all 8 threads → BANK 0 → 8 serial passes ✗",
    ]

    def update(frame):
        for obj in dynamic:
            try: obj.remove()
            except: pass
        dynamic.clear()

        phase = min(frame, len(phases) - 1)

        # Title
        t = fig.text(0.5, 0.97, phases[phase], ha='center', color=C_ACTIVE,
                     fontsize=11, fontfamily=FONT, fontweight='bold',
                     transform=fig.transFigure)
        dynamic.append(t)

        for ax_idx, ax in enumerate(axes):
            stride = 1 if ax_idx == 0 else N_BANKS

            for t_i in range(N_THREADS):
                access_idx = (t_i * stride) % (N_BANKS * N_ROWS)
                bank = access_idx % N_BANKS
                row = access_idx // N_BANKS

                # Thread boxes at the bottom
                tx = t_i + 0.5
                ty = 1.8

                clr = C_THREAD if phase >= 1 else C_GRAY
                b = ax.add_patch(FancyBboxPatch(
                    (t_i + 0.05, 1.4), 0.9, 0.8,
                    boxstyle="round,pad=0.05",
                    fc=clr, ec="white", lw=1.2, alpha=0.9))
                dynamic.append(b)
                tl = ax.text(tx, ty, f"T{t_i}",
                             ha='center', va='center',
                             color="white", fontsize=8, fontfamily=FONT,
                             fontweight='bold')
                dynamic.append(tl)

                if phase >= 1:
                    # Arrow from thread to memory cell
                    clr_arr = C_COALESCED if ax_idx == 0 else C_STRIDED
                    arr = ax.annotate("",
                        xy=(bank + 0.5, 7.5 - row * 1.2),
                        xytext=(tx, 2.2),
                        arrowprops=dict(arrowstyle="-|>",
                                        color=clr_arr, lw=1.5,
                                        connectionstyle=f"arc3,rad={0.1 if ax_idx==0 else -0.3}"))
                    dynamic.append(arr)

                    # Highlight accessed cell
                    b2 = ax.add_patch(FancyBboxPatch(
                        (bank + 0.05, 7.5 - row * 1.2), 0.9, 1.0,
                        boxstyle="round,pad=0.03",
                        fc=clr_arr, ec="white", lw=2, alpha=0.8))
                    dynamic.append(b2)
                    tv = ax.text(bank + 0.5, 8.0 - row * 1.2, f"[{access_idx}]",
                                 ha='center', va='center',
                                 color="white", fontsize=8, fontfamily=FONT,
                                 fontweight='bold')
                    dynamic.append(tv)

            # Result text
            if phase >= 1:
                if ax_idx == 0:
                    result_txt = "1 transaction\n(all banks different) ✓"
                    rclr = C_COALESCED
                else:
                    result_txt = "8 serial transactions\n(all hit Bank 0!) ✗"
                    rclr = C_STRIDED
                rt = ax.text(4, 0.8, result_txt, ha='center',
                             color=rclr, fontsize=10, fontfamily=FONT,
                             fontweight='bold',
                             bbox=dict(fc=C_BG2, ec=rclr, lw=1.5, pad=5, boxstyle='round'))
                dynamic.append(rt)

    save_gif(fig, update, frames=len(phases) + 1, interval=1000,
             path=os.path.join(OUT, "gif_cuda_bank_conflicts.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 8 — CUDA Streams: overlapping transfers and compute
# ─────────────────────────────────────────────────────────────
def gif_cuda_streams():
    fig, axes = plt.subplots(2, 1, figsize=(13, 8))
    fig.patch.set_facecolor(C_BG)
    for ax in axes:
        ax.set_facecolor(C_BG)
        ax.axis('off')

    axes[0].set_xlim(0, 12); axes[0].set_ylim(0, 4)
    axes[1].set_xlim(0, 12); axes[1].set_ylim(0, 5)

    axes[0].set_title("WITHOUT Streams (default stream — fully serialized)",
                      color=C_STRIDED, fontfamily=FONT, fontsize=11, pad=8)
    axes[1].set_title("WITH Streams (3 streams — H→D, compute, D→H overlap!)",
                      color=C_COALESCED, fontfamily=FONT, fontsize=11, pad=8)

    # Timeline units
    T = 1.0  # 1 unit of time per operation

    # Without streams: H2D, kernel, D2H, H2D, kernel, D2H... (serial)
    no_stream_ops = [
        (0.0,  T,   "#e07b54", "H→D\nchunk0"),
        (T,    T,   "#4f86c6", "kernel\n0"),
        (2*T,  T,   "#c6a84f", "D→H\nchunk0"),
        (3*T,  T,   "#e07b54", "H→D\nchunk1"),
        (4*T,  T,   "#4f86c6", "kernel\n1"),
        (5*T,  T,   "#c6a84f", "D→H\nchunk1"),
        (6*T,  T,   "#e07b54", "H→D\nchunk2"),
        (7*T,  T,   "#4f86c6", "kernel\n2"),
        (8*T,  T,   "#c6a84f", "D→H\nchunk2"),
    ]

    # With 3 streams: overlapped
    stream_ops = [
        # row, start, len, color, label
        (2, 0.0,  T,   "#e07b54", "H→D 0"),
        (1, 0.0,  0,   C_BG2,     ""),
        (0, 0.0,  0,   C_BG2,     ""),

        (2, T,    T,   "#4f86c6", "kernel 0"),
        (1, T,    T,   "#e07b54", "H→D 1"),

        (2, 2*T,  T,   "#c6a84f", "D→H 0"),
        (1, 2*T,  T,   "#4f86c6", "kernel 1"),
        (0, 2*T,  T,   "#e07b54", "H→D 2"),

        (1, 3*T,  T,   "#c6a84f", "D→H 1"),
        (0, 3*T,  T,   "#4f86c6", "kernel 2"),

        (0, 4*T,  T,   "#c6a84f", "D→H 2"),
    ]

    stream_row_labels = ["Stream 2", "Stream 1", "Stream 0"]
    stream_row_y      = [1.3, 2.4, 3.5]

    dynamic_top = []
    dynamic_bot = []

    def update(frame):
        for obj in dynamic_top + dynamic_bot:
            try: obj.remove()
            except: pass
        dynamic_top.clear()
        dynamic_bot.clear()

        n_ops_top = min(frame, len(no_stream_ops))
        n_ops_bot = min(frame * 2, len(stream_ops))

        # --- TOP: no streams ---
        for i in range(n_ops_top):
            start, length, color, label = no_stream_ops[i]
            b = axes[0].add_patch(FancyBboxPatch(
                (start + 0.05, 1.2), length * 1.2 - 0.1, 1.3,
                boxstyle="round,pad=0.06",
                fc=color, ec="white", lw=1.5, alpha=0.85))
            dynamic_top.append(b)
            t = axes[0].text(start + length * 0.6, 1.85, label,
                             ha='center', va='center',
                             color="white", fontsize=8.5, fontfamily=FONT,
                             fontweight='bold')
            dynamic_top.append(t)

        total_top = len(no_stream_ops) * T
        time_lbl = axes[0].text(0.3, 0.5,
                                f"Total time: {len(no_stream_ops)} operations × T = {int(total_top)}T",
                                color=C_STRIDED, fontsize=10, fontfamily=FONT)
        dynamic_top.append(time_lbl)

        # --- BOT: with streams ---
        for ri, (row_y, row_lbl) in enumerate(zip(stream_row_y, stream_row_labels)):
            rl = axes[1].text(0.1, row_y + 0.3, row_lbl,
                              color=C_GRAY, fontsize=8, fontfamily=FONT)
            dynamic_bot.append(rl)

        for i in range(n_ops_bot):
            if i >= len(stream_ops): break
            row, start, length, color, label = stream_ops[i]
            if length == 0: continue
            ry = stream_row_y[row]
            b = axes[1].add_patch(FancyBboxPatch(
                (start * 1.2 + 1.5 + 0.05, ry), length * 1.2 - 0.1, 0.85,
                boxstyle="round,pad=0.06",
                fc=color, ec="white", lw=1.2, alpha=0.85))
            dynamic_bot.append(b)
            if label:
                t = axes[1].text(start * 1.2 + 1.5 + length * 0.6, ry + 0.42,
                                 label, ha='center', va='center',
                                 color="white", fontsize=7.5, fontfamily=FONT,
                                 fontweight='bold')
                dynamic_bot.append(t)

        total_bot_text = "Total time: ≈ 5T  (3× faster than serial!)" if n_ops_bot > 6 else "Pipelining..."
        time_lbl2 = axes[1].text(0.3, 0.2, total_bot_text,
                                  color=C_COALESCED, fontsize=10, fontfamily=FONT)
        dynamic_bot.append(time_lbl2)

    fig.tight_layout()
    save_gif(fig, update, frames=10, interval=700,
             path=os.path.join(OUT, "gif_cuda_streams_overlap.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 9 — SM Warp Scheduling (latency hiding)
# ─────────────────────────────────────────────────────────────
def gif_warp_scheduling():
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 20); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title("SM Warp Scheduling — Hiding Global Memory Latency with Many Warps",
                 color=C_FG, fontfamily=FONT, fontsize=12, fontweight='bold', pad=10)

    N_WARPS = 4
    N_CYCLES = 18

    # States: E=executing, W=waiting(memory), R=ready
    # Each warp has a timeline
    timelines = [
        # warp 0: executes, then waits 6 cycles for memory, then executes again
        "E E E W W W W W W E E E E E E W W W",
        "_ _ E E E W W W W W W E E E E E E _",
        "_ _ _ _ E E E W W W W W W E E E E E",
        "_ _ _ _ _ _ E E E W W W W W W E E E",
    ]

    warp_colors = [C_THREAD, C_WARP, C_BLOCK, C_COALESCED]
    state_colors = {
        'E': None,  # filled by warp color
        'W': C_STALL,
        '_': C_BG2,
        'R': C_ACTIVE,
    }

    dynamic = []

    phases_desc = [
        "Cycle 1: Warp 0 executes — issues a global memory read",
        "Cycle 2-3: Warp 0 still executing local instructions",
        "Cycle 4-9: Warp 0 STALLS waiting for memory (~800 cycles in reality)",
        "Cycle 4-9: Warp 1, 2, 3 execute WHILE Warp 0 waits!",
        "Cycle 10+: Warp 0 resumes when memory returns — SM never idle!",
        "Key insight: many active warps = full SM utilization despite slow memory",
    ]

    def update(frame):
        for obj in dynamic:
            try: obj.remove()
            except: pass
        dynamic.clear()

        phase = min(frame, len(phases_desc) - 1)

        # Description
        t = ax.text(10, 7.5, phases_desc[phase], ha='center', color=C_ACTIVE,
                    fontsize=10.5, fontfamily=FONT, fontweight='bold',
                    bbox=dict(fc=C_BG2, ec=C_BORDER, lw=1, pad=6, boxstyle='round'))
        dynamic.append(t)

        n_cycles_show = min(phase * 4 + 2, N_CYCLES)

        # Draw cycle header
        for c in range(n_cycles_show):
            ct = ax.text(c * 1.0 + 1.8, 6.5, str(c + 1),
                         ha='center', color=C_GRAY, fontsize=7.5, fontfamily=FONT)
            dynamic.append(ct)

        # Draw warp timelines
        for wi, (timeline, warp_color) in enumerate(zip(timelines, warp_colors)):
            states = timeline.split()
            wy = 5.3 - wi * 1.3

            warp_lbl = ax.text(0.3, wy + 0.25, f"Warp {wi}",
                               ha='left', va='center', color=warp_color,
                               fontsize=9, fontfamily=FONT, fontweight='bold')
            dynamic.append(warp_lbl)

            for c in range(min(n_cycles_show, len(states))):
                state = states[c]
                if state == 'E':
                    clr = warp_color
                    lbl = "exec"
                elif state == 'W':
                    clr = C_STALL
                    lbl = "wait"
                else:
                    clr = C_BG2
                    lbl = ""

                alpha = 0.9 if state != '_' else 0.3
                b = ax.add_patch(FancyBboxPatch(
                    (c * 1.0 + 1.5, wy), 0.88, 0.75,
                    boxstyle="round,pad=0.04",
                    fc=clr, ec="white" if state != '_' else C_BORDER,
                    lw=1.2 if state != '_' else 0.5,
                    alpha=alpha))
                dynamic.append(b)

                if lbl:
                    tl = ax.text(c * 1.0 + 1.94, wy + 0.37, lbl,
                                 ha='center', va='center',
                                 color="white", fontsize=6.5, fontfamily=FONT)
                    dynamic.append(tl)

        # Legend
        legend_items = [
            ("Executing (SM busy)", warp_colors[0]),
            ("Waiting for memory (stalled)", C_STALL),
            ("Idle / not launched yet", C_BG2),
        ]
        for li, (llbl, lclr) in enumerate(legend_items):
            b = ax.add_patch(FancyBboxPatch(
                (li * 6.0 + 0.3, 0.2), 0.5, 0.4,
                boxstyle="round,pad=0.03",
                fc=lclr, ec="white", lw=0.8))
            dynamic.append(b)
            t = ax.text(li * 6.0 + 1.0, 0.4, llbl,
                        va='center', color=C_FG, fontsize=8.5, fontfamily=FONT)
            dynamic.append(t)

    save_gif(fig, update, frames=len(phases_desc) + 1, interval=1000,
             path=os.path.join(OUT, "gif_cuda_warp_scheduling.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 10 — Vector Addition: thread → element mapping
# ─────────────────────────────────────────────────────────────
def gif_vector_add():
    N = 12
    a = list(range(N))
    b = [N - i for i in range(N)]
    c = [a[i] + b[i] for i in range(N)]

    fig, axes = plt.subplots(4, 1, figsize=(13, 8))
    fig.patch.set_facecolor(C_BG)
    for ax in axes:
        ax.set_facecolor(C_BG)
        ax.axis('off')
        ax.set_xlim(-0.5, N + 0.5)
        ax.set_ylim(-0.3, 1.8)

    labels = ["Array A (device)", "Array B (device)", "Array C = A + B",
              "Threads (one per element)"]
    colors_arr = [C_THREAD, C_WARP, C_COALESCED, C_ACTIVE]

    # Draw array backgrounds
    for ax_i, (ax, lbl, clr) in enumerate(zip(axes, labels, colors_arr)):
        ax.text(-0.3, 1.5, lbl, color=clr, fontsize=9, fontfamily=FONT,
                fontweight='bold')

    # Draw static cells
    for i in range(N):
        for ax_i, (ax, clr) in enumerate(zip(axes[:3], colors_arr[:3])):
            ax.add_patch(FancyBboxPatch(
                (i + 0.05, 0.3), 0.9, 1.1,
                boxstyle="round,pad=0.04",
                fc=C_BG2, ec=C_BORDER, lw=0.8))

    dynamic = []

    def update(frame):
        for obj in dynamic:
            try: obj.remove()
            except: pass
        dynamic.clear()

        n_done = min(frame, N)

        for i in range(N):
            filled = i < n_done
            is_active = (i == n_done - 1)

            # Array A
            clr_a = colors_arr[0] if filled else C_BG2
            pa = axes[0].add_patch(FancyBboxPatch(
                (i + 0.05, 0.3), 0.9, 1.1,
                boxstyle="round,pad=0.04",
                fc=clr_a, ec="white" if filled else C_BORDER,
                lw=1.5 if is_active else 0.8, alpha=0.9))
            dynamic.append(pa)
            tv = axes[0].text(i + 0.5, 0.85, str(a[i]),
                              ha='center', va='center',
                              color="white", fontsize=10, fontfamily=FONT,
                              fontweight='bold')
            dynamic.append(tv)

            # Array B
            clr_b = colors_arr[1] if filled else C_BG2
            pb = axes[1].add_patch(FancyBboxPatch(
                (i + 0.05, 0.3), 0.9, 1.1,
                boxstyle="round,pad=0.04",
                fc=clr_b, ec="white" if filled else C_BORDER,
                lw=1.5 if is_active else 0.8, alpha=0.9))
            dynamic.append(pb)
            tv2 = axes[1].text(i + 0.5, 0.85, str(b[i]),
                               ha='center', va='center',
                               color="white", fontsize=10, fontfamily=FONT,
                               fontweight='bold')
            dynamic.append(tv2)

            # Array C (result)
            clr_c = colors_arr[2] if filled else C_BG2
            b3 = axes[2].add_patch(FancyBboxPatch(
                (i + 0.05, 0.3), 0.9, 1.1,
                boxstyle="round,pad=0.04",
                fc=clr_c, ec="white" if filled else C_BORDER,
                lw=1.5 if is_active else 0.8, alpha=0.9))
            dynamic.append(b3)
            if filled:
                tv3 = axes[2].text(i + 0.5, 0.85, str(c[i]),
                                   ha='center', va='center',
                                   color="white", fontsize=10, fontfamily=FONT,
                                   fontweight='bold')
                dynamic.append(tv3)

            # Thread
            clr_t = C_ACTIVE if is_active else (C_GRAY if not filled else C_THREAD)
            b4 = axes[3].add_patch(FancyBboxPatch(
                (i + 0.1, 0.3), 0.8, 1.0,
                boxstyle="round,pad=0.04",
                fc=clr_t, ec="white" if filled else C_BORDER,
                lw=1.5 if is_active else 0.8,
                alpha=0.9 if filled else 0.3))
            dynamic.append(b4)
            tl = axes[3].text(i + 0.5, 0.8, f"T{i}",
                              ha='center', va='center',
                              color="white", fontsize=8, fontfamily=FONT,
                              fontweight='bold')
            dynamic.append(tl)

        # Title
        t = fig.text(0.5, 0.98,
                     f"vectorAdd: {n_done}/{N} elements computed  |  Thread i computes c[i] = a[i] + b[i]",
                     ha='center', color=C_ACTIVE,
                     fontsize=11, fontfamily=FONT, fontweight='bold',
                     transform=fig.transFigure)
        dynamic.append(t)

    fig.tight_layout()
    save_gif(fig, update, frames=N + 2, interval=300,
             path=os.path.join(OUT, "gif_cuda_vector_add.gif"))


# ─────────────────────────────────────────────────────────────
# GIF 11 — Roofline Model
# ─────────────────────────────────────────────────────────────
def gif_roofline():
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0.05, 200); ax.set_ylim(0.5, 30)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel("Arithmetic Intensity (FLOPs / byte)", color=C_FG, fontsize=11,
                  fontfamily=FONT)
    ax.set_ylabel("Performance (TFLOPS)", color=C_FG, fontsize=11, fontfamily=FONT)
    ax.tick_params(colors=C_FG, labelsize=9)
    ax.set_facecolor(C_BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(C_BORDER)
    ax.set_title("Roofline Model — A100 GPU", color=C_FG,
                 fontfamily=FONT, fontsize=13, fontweight='bold', pad=10)

    # Roofline parameters (A100)
    peak_flops = 19.5      # TFLOPS
    bandwidth  = 2.0       # TB/s = 2000 GB/s
    ridge_point = peak_flops / bandwidth  # ~9.75 FLOPs/byte

    ai_range = np.logspace(np.log10(0.06), np.log10(150), 300)
    roofline  = np.minimum(peak_flops, bandwidth * ai_range)

    dynamic = []

    # Workloads to show
    workloads = [
        (0.083,  0.083 * bandwidth,  C_STRIDED,  "Vector Add\n(AI=0.08)",   "memory-bound"),
        (0.5,    0.5  * bandwidth,   C_STRIDED,  "Stencil\n(AI=0.5)",       "memory-bound"),
        (4.0,    4.0  * bandwidth,   C_ACTIVE,   "Conv2D\n(AI=4)",          "near ridge"),
        (50.0,   peak_flops,         C_COALESCED,"MatMul\n(AI=50)",         "compute-bound"),
        (100.0,  peak_flops,         C_COALESCED,"GEMM FP16\n(AI=100)",     "compute-bound"),
    ]

    def update(frame):
        for obj in dynamic:
            try: obj.remove()
            except: pass
        dynamic.clear()

        n_show_wl = min(frame, len(workloads))

        # Draw roofline
        line, = ax.plot(ai_range, roofline, color=C_ACTIVE, lw=3, alpha=0.9)
        dynamic.append(line)

        # Shade regions
        mem_shade = ax.fill_between(
            ai_range[ai_range <= ridge_point],
            roofline[ai_range <= ridge_point],
            0.5,
            color=C_STRIDED, alpha=0.08)
        dynamic.append(mem_shade)
        comp_shade = ax.fill_between(
            ai_range[ai_range >= ridge_point],
            roofline[ai_range >= ridge_point],
            0.5,
            color=C_COALESCED, alpha=0.08)
        dynamic.append(comp_shade)

        # Region labels
        if frame >= 1:
            mem_lbl = ax.text(0.3, 5, "Memory\nBound",
                              ha='center', color=C_STRIDED, fontsize=10,
                              fontfamily=FONT, fontweight='bold')
            comp_lbl = ax.text(60, 5, "Compute\nBound",
                               ha='center', color=C_COALESCED, fontsize=10,
                               fontfamily=FONT, fontweight='bold')
            dynamic.extend([mem_lbl, comp_lbl])

        # Ridge point
        if frame >= 1:
            rp_line = ax.axvline(ridge_point, color=C_ACTIVE, lw=1.5, ls='--', alpha=0.6)
            rp_lbl = ax.text(ridge_point * 1.1, 1.5, f"Ridge point\n~{ridge_point:.1f} FLOPs/byte",
                             color=C_ACTIVE, fontsize=8.5, fontfamily=FONT)
            dynamic.extend([rp_line, rp_lbl])

        # Peak lines
        peak_h = ax.axhline(peak_flops, color=C_FG, lw=1, ls=':', alpha=0.4)
        peak_l = ax.text(0.07, peak_flops * 1.05, f"Peak: {peak_flops} TFLOPS",
                         color=C_FG, fontsize=8.5, fontfamily=FONT)
        dynamic.extend([peak_h, peak_l])

        # Workload dots
        for wi in range(n_show_wl):
            ai, perf, clr, lbl, kind = workloads[wi]
            dot, = ax.plot(ai, perf, 'o', color=clr, ms=12, zorder=10)
            dynamic.append(dot)
            t = ax.text(ai * 1.15, perf * 0.8, lbl, color=clr,
                        fontsize=8.5, fontfamily=FONT, fontweight='bold')
            dynamic.append(t)

    save_gif(fig, update, frames=len(workloads) + 3, interval=700,
             path=os.path.join(OUT, "gif_cuda_roofline.gif"))


# ─────────────────────────────────────────────────────────────
# RUN ALL
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating CUDA Mastery GIFs...")
    gif_thread_hierarchy()
    gif_memory_coalescing()
    gif_warp_divergence()
    gif_memory_hierarchy()
    gif_parallel_reduction()
    gif_shared_memory_tiling()
    gif_bank_conflicts()
    gif_cuda_streams()
    gif_warp_scheduling()
    gif_vector_add()
    gif_roofline()
    print(f"\nAll done! 11 GIFs saved to {OUT}/")

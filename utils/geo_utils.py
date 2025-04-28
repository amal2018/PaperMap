# utils/geo_utils.py

import numpy as np
from matplotlib.patches import Rectangle as MplRectangle

def add_map_border(ax, linewidth=1.5, color='black'):
    rect = MplRectangle((0, 0), 1, 1, transform=ax.transAxes, linewidth=linewidth,
                        edgecolor=color, facecolor='none', zorder=100, clip_on=False)
    ax.add_patch(rect)

def add_latlon_ticks(ax, bounds, fontsize=15):
    xticks = np.round(np.linspace(bounds[0], bounds[1], 5), 1)
    yticks = np.round(np.linspace(bounds[2], bounds[3], 5), 1)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.set_xticklabels([f"{x:.1f}°" for x in xticks], fontsize=fontsize)
    ax.set_yticklabels([f"{y:.1f}°" for y in yticks], fontsize=fontsize)
    ax.tick_params(axis='x', which='both', top=True, bottom=True, labeltop=True, labelbottom=True,
                   length=8, width=1.5, direction='out', pad=10)
    ax.tick_params(axis='y', which='both', left=True, right=True, labelleft=True, labelright=True,
                   length=8, width=1.5, direction='out', pad=10)
    ax.grid(True, color="#cccccc", linestyle="--", linewidth=0.5, alpha=0.7, zorder=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

def square_bounds_with_buffer(bounds, buffer_ratio=0.05):
    xdiff = bounds[2] - bounds[0]
    ydiff = bounds[3] - bounds[1]
    maxdiff = max(xdiff, ydiff)
    xmid = (bounds[2] + bounds[0]) / 2
    ymid = (bounds[3] + bounds[1]) / 2
    half = maxdiff / 2
    buf = half * buffer_ratio
    return [xmid - half - buf, xmid + half + buf, ymid - half - buf, ymid + half + buf]

def add_scalebar(ax, length, unit="meters", linewidth=3, offset_x=0.75, offset_y=0.05):
    if unit == "kilometers":
        length_meters = length * 1000
        label = f"{length} km"
    else:
        length_meters = length
        label = f"{length} m"
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_span = xlim[1] - xlim[0]
    y_span = ylim[1] - ylim[0]
    x_start = xlim[0] + x_span * offset_x
    x_end = x_start + length_meters
    y_pos = ylim[0] + y_span * offset_y
    ax.plot([x_start, x_end], [y_pos, y_pos], color='black', linewidth=linewidth)
    ax.text((x_start + x_end) / 2, y_pos + y_span * 0.01, label,
            ha='center', va='bottom', fontsize=10, fontweight='bold')

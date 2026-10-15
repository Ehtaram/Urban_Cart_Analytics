import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import TextArea, HPacker, AnnotationBbox

os.makedirs("power_bi/assets", exist_ok=True)

# 1920x1080 canvas setup
fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
fig.patch.set_facecolor("#0B111E")
ax.set_facecolor("#0B111E")

def draw_card(x, y, w, h, stroke="#233354", fill="#151E32", lw=1.5):
    rect = patches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.01,rounding_size=14",
        facecolor=fill,
        edgecolor=stroke,
        linewidth=lw,
    )
    ax.add_patch(rect)

# Creating top banner
draw_card(24, 986, 1872, 74)

# Creating header typography
text_gold = TextArea(
    "FULFILLMENT & SLA AUDIT",
    textprops=dict(color="#FACC15", fontsize=18, fontweight="black", fontname="sans-serif")
)
text_pipe = TextArea(
    "|",
    textprops=dict(color="#94A3B8", fontsize=18, fontweight="bold", fontname="sans-serif")
)
text_cyan = TextArea(
    "DARKSTORE LOGISTICS ENGINE",
    textprops=dict(color="#38BDF8", fontsize=18, fontweight="black", fontname="sans-serif")
)

packed_header = HPacker(
    children=[text_gold, text_pipe, text_cyan],
    align="center",
    pad=0,
    sep=18
)

header_box = AnnotationBbox(
    packed_header,
    (960, 1023),
    xycoords="data",
    frameon=False
)
ax.add_artist(header_box)

# Creating left navigation and filter pillar
draw_card(24, 24, 230, 948)

# Designing slicer slots
for y in [648, 558, 468, 378]:
    draw_card(40, y, 198, 72, stroke="#38BDF8", fill="#0F172A", lw=1.2)

# Creating navigation buttons
draw_card(40, 168, 198, 42, stroke="#233354", fill="#151E32", lw=1.0)
ax.text(139, 189, "<- PAGE 1: MACRO", color="#94A3B8", fontsize=9, ha="center", va="center")
draw_card(40, 114, 198, 42, stroke="#38BDF8", fill="#1E293B", lw=1.5)
ax.text(139, 135, "PAGE 3: WHAT-IF SIM ->", color="#38BDF8", fontsize=9, fontweight="bold", ha="center", va="center")

# Creating KPI summary cards
draw_card(274, 832, 388, 140)
draw_card(682, 832, 388, 140)
draw_card(1090, 832, 388, 140)
draw_card(1498, 832, 398, 140)

# Center charts
draw_card(274, 414, 796, 400)
draw_card(1090, 414, 806, 400)

# Detailed data grid card
draw_card(274, 24, 1622, 372)

# Canvas dimensions
ax.set_xlim(0, 1920)
ax.set_ylim(0, 1080)
plt.axis("off")
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

output_path = "power_bi/assets/bg_page2_logistics_sla.png"
plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none", dpi=100)
plt.close()

print(f"Canvas layout exported: {output_path}")
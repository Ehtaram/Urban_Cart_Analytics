import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('power_bi/assets', exist_ok=True)

# 1920x1080 canvas at 100 DPI
fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
fig.patch.set_facecolor('#0B111E')
ax.set_facecolor('#0B111E')

def draw_card(x, y, w, h, stroke='#233354', fill='#151E32', lw=1.5):
    rect = patches.FancyBboxPatch(
        (x, y), w, h, 
        boxstyle='round,pad=0.01,rounding_size=14',
        facecolor=fill, edgecolor=stroke, linewidth=lw
    )
    ax.add_patch(rect)

# Designing top header banner
draw_card(24, 986, 1872, 74)

# Creating header typography
y_pos = 1023
font_size = 19

# Centered separator
ax.text(960, y_pos, '|', color='#E2E8F0', fontsize=font_size, fontweight='bold', 
        ha='center', va='center', fontfamily='sans-serif')
ax.text(940, y_pos, 'STRATEGIC SIMULATOR', color='#FACC15', fontsize=font_size, fontweight='heavy', 
        ha='right', va='center', fontfamily='sans-serif')
ax.text(980, y_pos, 'URBANCART MARGIN RECOVERY', color='#38BDF8', fontsize=font_size, fontweight='heavy', 
        ha='left', va='center', fontfamily='sans-serif')

# Creating left sidebar pillar
draw_card(24, 24, 230, 948)

# Designing Simulation guide card
draw_card(40, 580, 198, 220, stroke='#38BDF8', fill='#0F172A', lw=1.2)
ax.text(139, 765, 'SIMULATION GUIDE', color='#38BDF8', fontsize=10, fontweight='bold', ha='center', va='center')
ax.text(50, 725, '1. Adjust recovery slider', color='#FFFFFF', fontsize=8.5, fontweight='semibold', ha='left', va='center')
ax.text(50, 695, '2. Target: Recover 15%', color='#FFFFFF', fontsize=8.5, fontweight='semibold', ha='left', va='center')
ax.text(50, 675, '   of logistics bleed', color='#FFFFFF', fontsize=8.5, fontweight='semibold', ha='left', va='center')
ax.text(50, 645, '3. Check churn risk', color='#FFFFFF', fontsize=8.5, fontweight='semibold', ha='left', va='center')
ax.text(50, 615, '4. Review action matrix', color='#FFFFFF', fontsize=8.5, fontweight='semibold', ha='left', va='center')

# Creating navigation buttons
draw_card(40, 168, 198, 42, stroke='#233354', fill='#151E32', lw=1.0)
ax.text(139, 189, '<- PAGE 1: MACRO', color='#FFFFFF', fontsize=9, fontweight='bold', ha='center', va='center')
draw_card(40, 114, 198, 42, stroke='#233354', fill='#151E32', lw=1.0)
ax.text(139, 135, '<- PAGE 2: SLA AUDIT', color='#FFFFFF', fontsize=9, fontweight='bold', ha='center', va='center')

# Designing surcharge slider container
draw_card(274, 822, 1622, 150, stroke='#38BDF8', lw=1.8)

# Designing comparative scenario cards
draw_card(274, 594, 520, 208)
draw_card(824, 594, 520, 208)
draw_card(1374, 594, 522, 208)

# Designing strategic chart containers
draw_card(274, 24, 970, 546)
draw_card(1268, 24, 628, 546)

# Canvas limits
ax.set_xlim(0, 1920)
ax.set_ylim(0, 1080)
plt.axis('off')
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

output_path = 'power_bi/assets/bg_page3_whatif_simulator.png'
plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=100)
plt.close()

print(f"Canvas layout exported: {output_path}")
#!/usr/bin/env python3
"""
viz_pipeline_enhanced.py With mnemonics, branch highlighting, clean colors
"""
import re
import matplotlib.pyplot as plt
import numpy as np
import os

# CONFIG
TRACE_FILE = "m5out/trace.out"
IMG_FILE   = "screenshots/pipeline1.png"
MAX_INSTS  = 30
DPI        = 300  # sharper

os.makedirs("screenshots", exist_ok=True)

STAGES = ['fetch', 'decode', 'rename', 'dispatch', 'issue', 'complete', 'retire']
STAGE_IDX = {s: i for i, s in enumerate(STAGES)}

STAGE_RE = re.compile(r'O3PipeView:([a-z]+):(\d+)')
FETCH_RE = re.compile(r'O3PipeView:fetch:\d+:0x([0-9a-f]+):.*:(\d+):\s*(.*?)(?:\s*:\s*|$)')

# PARSE
instructions = []
current = None

with open(TRACE_FILE, 'r') as f:
    for line in f:
        line = line.strip()
        if not line: continue

        m_fetch = FETCH_RE.match(line)
        if m_fetch:
            if current: instructions.append(current)
            pc = m_fetch.group(1)
            seqnum = int(m_fetch.group(2))
            mnemonic = m_fetch.group(3).strip().split()[0]  # e.g., "MOV_R_R"
            cycle = int(STAGE_RE.match(line).group(2))

            current = {
                'pc': pc,
                'seqnum': seqnum,
                'mnemonic': mnemonic,
                'is_branch': mnemonic.startswith('J') or 'CALL' in mnemonic,
                'stages': {'fetch': cycle}
            }
            continue

        if not current: continue
        m = STAGE_RE.match(line)
        if not m: continue
        stage, cycle = m.group(1).lower(), int(m.group(2))
        if stage in STAGE_IDX:
            current['stages'][stage] = cycle

    if current: instructions.append(current)

# Sort by fetch
instructions.sort(key=lambda x: x['stages']['fetch'])
instructions = instructions[:MAX_INSTS]

# MATRIX
n = len(instructions)
matrix = np.full((n, len(STAGES)), np.nan)

for i, inst in enumerate(instructions):
    for stage in STAGES:
        cycle = inst['stages'].get(stage, np.nan)
        if cycle == 0:  # treat 0 as missing for coloring
            cycle = np.nan
        matrix[i, STAGE_IDX[stage]] = cycle

# Filter out NaN for color scaling
valid_cycles = matrix[~np.isnan(matrix)]
vmin, vmax = np.min(valid_cycles), np.max(valid_cycles)
norm = plt.Normalize(vmin, vmax)

# PLOT
fig, ax = plt.subplots(figsize=(15, max(7, n * 0.6)))

im = ax.imshow(matrix, cmap='turbo', norm=norm, aspect='auto', interpolation='none')

# Cell text
for row in range(n):
    for col in range(len(STAGES)):
        val = matrix[row, col]
        if not np.isnan(val):
            color = 'white' if val > (vmin + vmax) * 0.5 else 'black'
            ax.text(col, row, f"{int(val)}", ha='center', va='center',
                    color=color, fontsize=8, fontweight='bold')

# Colorbar
cbar = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
cbar.set_label('Cycle (non-zero)', rotation=270, labelpad=20)

# Labels
ax.set_xticks(range(len(STAGES)))
ax.set_xticklabels([s.capitalize() for s in STAGES], rotation=45, ha='right', fontsize=11)
ax.set_yticks(range(n))

# Y-labels: I# (mnemonic) [branch in red]
yticklabels = []
for i, inst in enumerate(instructions):
    label = f"I{i}"
    if inst['mnemonic']:
        label += f" {inst['mnemonic']}"
    if inst['is_branch']:
        yticklabels.append(plt.Text(0, i, label, color='red', fontweight='bold'))
    else:
        yticklabels.append(label)
ax.set_yticklabels(yticklabels)

ax.set_title("O3 Pipeline – First 30 Instructions (Enhanced)", fontsize=16, pad=20)

plt.subplots_adjust(left=0.22, right=0.78, top=0.90, bottom=0.25)
plt.savefig(IMG_FILE, dpi=DPI, bbox_inches='tight')
plt.close()

print(f"ENHANCED → {IMG_FILE}")
print(f"   {n} instructions, {sum(1 for inst in instructions if inst['is_branch'])} branches")
#!/usr/bin/env python3
"""
vizcompare.py - Compares all 5 configs + metrics
"""
import re
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict

# CONFIG
TRACES = {
    "With BP": "trace_bp_on.out",
    "No BP": "trace_bp_off.out",
    "Superscalar": "trace_super.out",
    "Single-Issue": "trace_single.out",
    "SMT (2 threads)": "trace_smt.out"
}
MAX_INSTS = 20
DPI = 300

STAGES = ['fetch','decode','rename','dispatch','issue','complete','retire']
STAGE_IDX = {s:i for i,s in enumerate(STAGES)}

STAGE_RE = re.compile(r'O3PipeView:([a-z]+):(\d+)')
FETCH_RE = re.compile(r'O3PipeView:fetch:\d+:0x([0-9a-f]+):.*:(\d+):\s*(.*?)(?:\s*:\s*|$)?')

def parse_trace(filename):
    insts = []
    current = None
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            m = FETCH_RE.match(line)
            if m:
                if current: insts.append(current)
                pc, seq, mnemonic = m.groups()
                cycle = int(STAGE_RE.match(line).group(2))
                current = {'pc':pc, 'seq':int(seq), 'mnemonic':mnemonic.split()[0],
                           'thread':0, 'stages':{'fetch':cycle}}
                continue
            if not current: continue
            m = STAGE_RE.match(line)
            if not m: continue
            stage, cycle = m.group(1).lower(), int(m.group(2))
            if stage in STAGE_IDX:
                current['stages'][stage] = cycle
            # Detect thread in non-fetch lines (SMT)
            if ':' in line and 'thread' not in current:
                parts = line.split(':')
                if len(parts) > 3 and parts[3].isdigit():
                    current['thread'] = int(parts[3])
    if current: insts.append(current)
    return insts

# Parse all
data = {}
for name, file in TRACES.items():
    if not os.path.exists(file):
        print(f"Missing: {file}")
        continue
    insts = parse_trace(file)
    insts.sort(key=lambda x: x['stages']['fetch'])
    data[name] = insts[:MAX_INSTS]

# Plot
fig, axes = plt.subplots(len(data), 1, figsize=(16, 4*len(data)), sharex=True)
if len(data) == 1: axes = [axes]

for ax, (title, insts) in zip(axes, data.items()):
    n = len(insts)
    matrix = np.full((n, len(STAGES)), np.nan)
    for i, inst in enumerate(insts):
        for s in STAGES:
            c = inst['stages'].get(s, np.nan)
            if c == 0: c = np.nan
            matrix[i, STAGE_IDX[s]] = c

    valid = matrix[~np.isnan(matrix)]
    norm = plt.Normalize(np.min(valid), np.max(valid)) if len(valid) else None
    im = ax.imshow(matrix, cmap='turbo', norm=norm, aspect='auto')

    # Text
    for i in range(n):
        for j in range(len(STAGES)):
            v = matrix[i,j]
            if not np.isnan(v):
                ax.text(j, i, f"{int(v)}", ha='center', va='center',
                        color='white' if v > np.nanmean(valid) else 'black', fontsize=7)

    # Labels
    ax.set_yticks(range(n))
    labels = [f"T{inst['thread']} {inst['mnemonic']}" for inst in insts]
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_title(f"{title} – IPC: {len(insts)/(np.nanmax(matrix[:,-1]) - np.nanmin(matrix[:,0])):.3f}", fontsize=12)

axes[-1].set_xticks(range(len(STAGES)))
axes[-1].set_xticklabels([s.capitalize() for s in STAGES], rotation=45, ha='right')

plt.tight_layout()
plt.savefig("screenshots/comparison_all.png", dpi=DPI, bbox_inches='tight')
print("COMPARISON PLOT → screenshots/comparison_all.png")
import csv, statistics, os, glob
import matplotlib.pyplot as plt
import numpy as np

results_dir = os.path.expanduser("~/pqc-tls/results/")

# Identify files by timestamp groups
# Localhost = 20260309_185xxx to 190xxx
# Broadband = last batch before intercontinental  
# Intercontinental = last batch

all_files = sorted(glob.glob(results_dir + "results_20260309_*.csv"))

# Load all data with timestamps to separate scenarios
scenarios = {'localhost': {}, 'broadband': {}, 'intercontinental': {}}

for f in all_files:
    with open(f) as fp:
        rows = list(csv.DictReader(fp))
        if not rows:
            continue
        try:
            grp = rows[0]['group']
            lats = [float(r['latency_ms']) for r in rows]
            mean = statistics.mean(lats)
            # Identify scenario by mean latency range
            if mean < 40:
                sc = 'localhost'
            elif mean < 150:
                sc = 'broadband'
            else:
                sc = 'intercontinental'
            scenarios[sc].setdefault(grp, []).extend(lats)
        except:
            pass

order = ['X25519','mlkem768','bikel1','x25519_bikel1','X25519MLKEM768','frodo640aes']
labels = ['X25519\n(Classical)','ML-KEM-768','BIKE-L1','X25519+\nBIKE-L1','X25519+\nML-KEM-768','FrodoKEM-640']
colors = ['#2196F3','#4CAF50','#FF9800','#FF5722','#9C27B0','#607D8B']

# Print full summary table
print("\n=== FULL RESULTS SUMMARY ===")
for sc in ['localhost','broadband','intercontinental']:
    print(f"\nScenario: {sc.upper()}")
    print(f"{'Algorithm':<22} {'N':>5} {'Mean':>8} {'Median':>8} {'StdDev':>8} {'P95':>8}")
    print("-" * 60)
    baseline = statistics.mean(scenarios[sc].get('X25519',[21]))
    for g in order:
        if g not in scenarios[sc]:
            continue
        lats = scenarios[sc][g]
        s = sorted(lats)
        mean = statistics.mean(lats)
        overhead = f"{((mean-baseline)/baseline*100):+.1f}%" if g != 'X25519' else "baseline"
        print(f"{g:<22} {len(lats):>5} {mean:>8.2f} {statistics.median(lats):>8.2f} {statistics.stdev(lats):>8.2f} {s[int(0.95*len(s))]:>8.2f}  {overhead}")

# Graph 1 - grouped bar chart across scenarios
fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=False)
fig.suptitle('PQC-TLS Handshake Latency across Network Scenarios\nReproducing Paquin et al. PQCrypto 2020 — Group L, INFO-F514, ULB 2025/26',
             fontsize=12, fontweight='bold')

for idx, sc in enumerate(['localhost','broadband','intercontinental']):
    means = []
    stdevs = []
    for g in order:
        if g in scenarios[sc]:
            means.append(statistics.mean(scenarios[sc][g]))
            stdevs.append(statistics.stdev(scenarios[sc][g]))
        else:
            means.append(0)
            stdevs.append(0)
    bars = axes[idx].bar(labels, means, yerr=stdevs, capsize=4,
                         color=colors, alpha=0.85, edgecolor='black', linewidth=0.5)
    axes[idx].set_title(f'{sc.capitalize()}\n(N=1000 per algorithm)')
    axes[idx].set_ylabel('Mean Latency (ms)')
    axes[idx].axhline(y=means[0], color='#2196F3', linestyle='--', alpha=0.4)
    for bar, mean in zip(bars, means):
        if mean > 0:
            axes[idx].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                          f'{mean:.0f}ms', ha='center', va='bottom', fontsize=7, fontweight='bold')

plt.tight_layout()
out1 = os.path.expanduser("~/pqc-tls/results/graph_scenarios.png")
plt.savefig(out1, dpi=150, bbox_inches='tight')
print(f"\nGraph 1 saved: {out1}")

# Graph 2 - overhead vs classical across scenarios
fig2, ax = plt.subplots(figsize=(12, 6))
sc_names = ['localhost','broadband','intercontinental']
x = np.arange(len(order)-1)
width = 0.25
algs_no_baseline = ['mlkem768','bikel1','x25519_bikel1','X25519MLKEM768','frodo640aes']
alg_labels = ['ML-KEM-768','BIKE-L1','X25519+BIKE-L1','X25519+ML-KEM-768','FrodoKEM-640']

for i, sc in enumerate(sc_names):
    baseline = statistics.mean(scenarios[sc].get('X25519',[21]))
    overheads = []
    for g in algs_no_baseline:
        if g in scenarios[sc]:
            mean = statistics.mean(scenarios[sc][g])
            overheads.append((mean - baseline) / baseline * 100)
        else:
            overheads.append(0)
    bars = ax.bar(x + i*width, overheads, width, label=sc.capitalize(),
                  alpha=0.85, edgecolor='black', linewidth=0.5)

ax.set_xlabel('Algorithm')
ax.set_ylabel('Overhead vs X25519 Classical (%)')
ax.set_title('PQC Overhead vs Classical Baseline across Network Scenarios\nGroup L, INFO-F514, ULB 2025/26')
ax.set_xticks(x + width)
ax.set_xticklabels(alg_labels)
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.legend()
plt.tight_layout()
out2 = os.path.expanduser("~/pqc-tls/results/graph_overhead.png")
plt.savefig(out2, dpi=150, bbox_inches='tight')
print(f"Graph 2 saved: {out2}")
print("\nDone! Open both graphs to view results.")
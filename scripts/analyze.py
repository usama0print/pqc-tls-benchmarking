import csv, statistics, os, glob
import matplotlib.pyplot as plt
import numpy as np

results_dir = os.path.expanduser("~/pqc-tls/results/")
files = sorted(glob.glob(results_dir + "results_20260309_*.csv"))

data = {}
for f in files:
    with open(f) as fp:
        for row in csv.DictReader(fp):
            try:
                data.setdefault(row['group'], []).append(float(row['latency_ms']))
            except:
                pass

order = ['X25519','mlkem768','bikel1','x25519_bikel1','X25519MLKEM768','frodo640aes']
labels = ['X25519\n(Classical)','ML-KEM-768\n(Lattice)','BIKE-L1\n(Code)','X25519+BIKE-L1\n(Hybrid)','X25519+\nML-KEM-768','FrodoKEM-640\n(Conservative)']
means = [statistics.mean(data[g]) for g in order]
stdevs = [statistics.stdev(data[g]) for g in order]
colors = ['#2196F3','#4CAF50','#FF9800','#FF5722','#9C27B0','#607D8B']

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('PQC-TLS Handshake Latency - Reproducing Paquin et al. PQCrypto 2020\nGroup L, INFO-F514, ULB 2025/26', fontsize=12, fontweight='bold')

# Bar chart
bars = axes[0].bar(labels, means, yerr=stdevs, capsize=5, color=colors, alpha=0.85, edgecolor='black', linewidth=0.5)
axes[0].axhline(y=means[0], color='#2196F3', linestyle='--', alpha=0.5, label='Classical baseline')
axes[0].set_ylabel('Mean Handshake Latency (ms)')
axes[0].set_title('Mean Latency per Algorithm (N=1000, localhost)')
axes[0].set_ylim(0, 50)
axes[0].legend()
for bar, mean in zip(bars, means):
    axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                f'{mean:.1f}ms', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Box plot
box_data = [data[g] for g in order]
bp = axes[1].boxplot(box_data, labels=labels, patch_artist=True, notch=False)
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
axes[1].set_ylabel('Handshake Latency (ms)')
axes[1].set_title('Latency Distribution per Algorithm (N=1000, localhost)')
axes[1].axhline(y=means[0], color='#2196F3', linestyle='--', alpha=0.5, label='Classical baseline')
axes[1].legend()

plt.tight_layout()
outpath = os.path.expanduser("~/pqc-tls/results/benchmark_results.png")
plt.savefig(outpath, dpi=150, bbox_inches='tight')
print(f"Graph saved to: {outpath}")

# Print summary table
baseline = means[0]
algo_names = ['X25519','frodo640aes','mlkem768','X25519MLKEM768','bikel1','x25519_bikel1']
print(f"\n{'Algorithm':<22} {'N':>5} {'Mean':>8} {'Median':>8} {'StdDev':>8} {'P95':>8} {'Overhead':>10}")
print("-" * 75)
for g in algo_names:
    if g not in data:
        continue
    lats = data[g]
    s = sorted(lats)
    mean = statistics.mean(lats)
    overhead = f"{((mean-baseline)/baseline*100):+.1f}%" if g != 'X25519' else "baseline"
    print(f"{g:<22} {len(lats):>5} {mean:>8.2f} {statistics.median(lats):>8.2f} {statistics.stdev(lats):>8.2f} {s[int(0.95*len(s))]:>8.2f} {overhead:>10}")
print("\n  (all times in milliseconds)")
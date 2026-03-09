# PQC-TLS Benchmarking — Group L, INFO-F514, ULB 2025/26

Reproduction and extension of:
> Paquin, Stebila, Tamvada — "Benchmarking Post-Quantum Cryptography in TLS", PQCrypto 2020, Springer LNCS vol. 12100

Secondary reference:
> Schwabe, Stebila, Wiggers — "Post-Quantum TLS Without Handshake Signatures", ACM CCS 2020, DOI: 10.1145/3372297.3423350

By : OUSSAMA EBN ATOU
---

## What This Repo Contains

- Benchmarking scripts for TLS handshake latency measurement
- Results from 1000 handshakes per algorithm across 3 network scenarios
- Analysis and graph generation scripts
- Full setup instructions to reproduce our environment

---

## Algorithms Tested

| Algorithm | Type | In Paquin et al. |
|-----------|------|-----------------|
| X25519 | Classical baseline | Yes |
| FrodoKEM-640-AES | Lattice PQC | Yes |
| ML-KEM-768 (NIST FIPS 203) | Lattice PQC | No - new contribution |
| BIKE-L1 | Code-based PQC | No - new contribution |
| X25519 + ML-KEM-768 | Hybrid | No - new contribution |
| X25519 + BIKE-L1 | Hybrid | No - new contribution |

---

## Key Findings

| Algorithm | Localhost | Broadband | Intercontinental |
|-----------|-----------|-----------|-----------------|
| X25519 (baseline) | 21.87ms | 60.87ms | 328.24ms |
| ML-KEM-768 | 21.01ms (-3.9%) | 62.29ms (+2.3%) | 333.98ms (+1.7%) |
| BIKE-L1 | 22.18ms (+1.4%) | 49.28ms (-19.0%) | 222.68ms (-32.2%) |
| X25519+BIKE-L1 | 22.26ms (+1.8%) | 52.42ms (-13.9%) | 229.91ms (-30.0%) |
| X25519+ML-KEM-768 | 29.76ms (+36.1%) | 74.54ms (+22.5%) | 342.95ms (+4.5%) |
| FrodoKEM-640 | 29.66ms (+35.6%) | 84.07ms (+38.1%) | 365.55ms (+11.4%) |

### Notable findings:
- ML-KEM-768 (the finalized NIST standard) matches or beats classical X25519 in all scenarios
- BIKE-L1 outperforms classical X25519 by **32%** on intercontinental connections
- Hybrid configurations (X25519+BIKE) add near-zero overhead over pure PQC
- FrodoKEM reflects its conservative design with larger keys and higher latency

---

## Environment

- OS: Ubuntu 22.04 LTS
- OpenSSL 3.3.2 (compiled from source)
- liboqs 0.12.0
- oqs-provider 0.12.0-dev
- Python 3.10 with matplotlib, numpy, scipy

---

## Repository Structure

```
pqc-tls-benchmarking/
├── scripts/
│   ├── benchmark.sh        # Main benchmarking script
│   ├── run_all.sh          # Runs all algorithms in sequence
│   ├── analyze.py          # Single scenario analysis
│   └── analyze_all.py      # Multi-scenario analysis and graphs
├── results/
│   └── *.csv               # Raw latency measurements
├── graphs/
│   ├── graph_scenarios.png     # Bar charts per scenario
│   ├── graph_overhead.png      # Overhead comparison
│   └── benchmark_results.png  # Localhost results
└── README.md
```

---

## Setup Instructions

### 1. Install dependencies
```bash
sudo apt-get install -y build-essential cmake ninja-build git libssl-dev python3-pip iproute2 bc
pip install matplotlib numpy scipy --break-system-packages
```

### 2. Build liboqs
```bash
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs && mkdir build && cd build
cmake -GNinja \
  -DCMAKE_INSTALL_PREFIX=$HOME/pqc-tls/liboqs-install \
  -DOQS_ENABLE_KEM_CLASSIC_MCELIECE=ON ..
ninja && ninja install
```

### 3. Build OpenSSL 3.3.2
```bash
wget https://www.openssl.org/source/openssl-3.3.2.tar.gz
tar xf openssl-3.3.2.tar.gz && cd openssl-3.3.2
./Configure --prefix=$HOME/pqc-tls/openssl-3.3
make -j4 && make install
```

### 4. Build oqs-provider
```bash
git clone https://github.com/open-quantum-safe/oqs-provider.git
cd oqs-provider && mkdir build && cd build
cmake -GNinja \
  -Dliboqs_DIR=$HOME/pqc-tls/liboqs-install/lib/cmake/liboqs \
  -DOPENSSL_ROOT_DIR=$HOME/pqc-tls/openssl-3.3 ..
ninja
mkdir -p $HOME/pqc-tls/openssl-3.3/lib64/ossl-modules
cp lib/oqsprovider.so $HOME/pqc-tls/openssl-3.3/lib64/ossl-modules/
```

### 5. Generate certificates
```bash
mkdir -p $HOME/pqc-tls/certs
openssl req -x509 -newkey rsa:2048 -keyout $HOME/pqc-tls/certs/server.key \
  -out $HOME/pqc-tls/certs/server.crt -days 365 -nodes \
  -subj "/CN=localhost"
```

### 6. Set environment variables
```bash
export LD_LIBRARY_PATH=$HOME/pqc-tls/liboqs-install/lib:$LD_LIBRARY_PATH
export OPENSSL_CONF=$HOME/pqc-tls/openssl-oqs.cnf
export PATH=$HOME/pqc-tls/openssl-3.3/bin:$PATH
```

### 7. Run benchmarks
```bash
bash scripts/run_all.sh
```

### 8. Generate graphs
```bash
python3 scripts/analyze_all.py
```

---

## Network Emulation

Matching Paquin et al. methodology using tc netem:

```bash
# Broadband (10ms RTT, 10Mbit/s)
sudo tc qdisc add dev lo root netem delay 5ms rate 10mbit

# Intercontinental (100ms RTT, 10Mbit/s)
sudo tc qdisc add dev lo root netem delay 50ms rate 10mbit

# Clear emulation when done
sudo tc qdisc del dev lo root
```

---

## Course Information

- Course: INFO-F514 — Protocols, cryptanalysis and mathematical cryptology 2025/26
- Institution: Universite Libre de Bruxelles (ULB)
- Group: L
- Supervisor: Prof. Christophe Petit

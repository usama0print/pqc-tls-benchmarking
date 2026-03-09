#!/bin/bash
ALGORITHMS=("X25519" "mlkem768" "bikel1" "X25519MLKEM768" "x25519_bikel1" "frodo640aes")
TOTAL=${#ALGORITHMS[@]}
COUNT=0

sudo kill $(sudo lsof -t -i:4433) 2>/dev/null
sleep 1

for ALG in "${ALGORITHMS[@]}"; do
    ((COUNT++))
    echo "============================================"
    echo "[$COUNT/$TOTAL] Running: $ALG"
    echo "============================================"
    bash $HOME/pqc-tls/scripts/benchmark.sh 1000 $ALG
    sudo kill $(sudo lsof -t -i:4433) 2>/dev/null
    sleep 2
done

echo ""
echo "ALL DONE! Results in $HOME/pqc-tls/results/"
ls -lh $HOME/pqc-tls/results/
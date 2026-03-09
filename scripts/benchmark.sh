#!/bin/bash
OPENSSL="$HOME/pqc-tls/openssl-3.3/bin/openssl"
CERTS="$HOME/pqc-tls/certs"
RESULTS="$HOME/pqc-tls/results"
NUM="${1:-5}"
GROUP="${2:-X25519}"
PORT="4433"
mkdir -p "$RESULTS"
OUTFILE="$RESULTS/results_$(date +%Y%m%d_%H%M%S).csv"
echo "id,group,latency_ms" > "$OUTFILE"

echo "Starting server..."
sudo kill $(sudo lsof -t -i:$PORT) 2>/dev/null
sleep 1

$OPENSSL s_server \
  -cert "$CERTS/server.crt" \
  -key "$CERTS/server.key" \
  -port $PORT -tls1_3 -groups $GROUP \
  -quiet 2>/dev/null &
SERVER_PID=$!
sleep 3
echo "Server started PID: $SERVER_PID"

echo "Running $NUM handshakes..."
for i in $(seq 1 $NUM); do
  START=$(date +%s%N)
  echo "Q" | $OPENSSL s_client \
    -connect localhost:$PORT \
    -CAfile "$CERTS/server.crt" \
    -tls1_3 -groups $GROUP \
    -quiet 2>/dev/null
  END=$(date +%s%N)
  MS=$(echo "scale=2; ($END-$START)/1000000" | bc)
  echo "$i,$GROUP,$MS" >> "$OUTFILE"
  echo "Handshake $i: ${MS}ms"
done

kill $SERVER_PID 2>/dev/null
echo "Done! Results: $OUTFILE"
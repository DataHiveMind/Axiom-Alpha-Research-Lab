#!/usr/bin/env bash
# Axiom-Alpha-Research-Lab: Network readiness probe
# Usage: ./wait-for-it.sh host:port [-t timeout] [-- command args]

TIMEOUT=15
HOST=""
PORT=""
CMD=""

# Parse arguments
while [[ $# -gt 0 ]]
do
    case "$1" in
        *:* )
        HOST=$(printf "%s\n" "$1"| cut -d : -f 1)
        PORT=$(printf "%s\n" "$1"| cut -d : -f 2)
        shift 1
        ;;
        -t)
        TIMEOUT="$2"
        if [[ $TIMEOUT == "" ]]; then break; fi
        shift 2
        ;;
        --)
        shift
        CMD="$@"
        break
        ;;
        *)
        echo "Unknown argument: $1"
        exit 1
        ;;
    esac
done

if [[ "$HOST" == "" || "$PORT" == "" ]]; then
    echo "Error: you need to provide a host and port to test (e.g., localhost:5432)"
    exit 1
fi

echo "⏳ Waiting for $HOST:$PORT to become available (Timeout: ${TIMEOUT}s)..."

# Loop to check if the port is open using native bash /dev/tcp
for i in $(seq $TIMEOUT) ; do
    (echo > /dev/tcp/$HOST/$PORT) >/dev/null 2>&1
    
    result=$?
    if [[ $result -eq 0 ]] ; then
        echo "✅ $HOST:$PORT is up and accepting connections!"
        if [[ "$CMD" != "" ]]; then
            echo "Executing command: $CMD"
            exec $CMD
        fi
        exit 0
    fi
    sleep 1
done

echo "❌ Operation timed out. $HOST:$PORT is still unreachable."
exit 1
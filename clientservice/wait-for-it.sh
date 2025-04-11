#!/bin/bash

hostport=$1
HOST=$(echo "$hostport" | cut -d: -f1)
PORT=$(echo "$hostport" | cut -d: -f2)

shift
shift # remove host and port
CMD="$@"

until nc -z "$HOST" "$PORT"; do
  echo "Waiting for $HOST:$PORT..."
  sleep 2
done

echo "$HOST:$PORT is available, running command"
exec $CMD
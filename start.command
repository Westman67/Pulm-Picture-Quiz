#!/bin/zsh
cd "$(dirname "$0")"
if [[ ! -d dist ]]; then
  node scripts/build.mjs || exit 1
fi
python3 scripts/serve.py 4173 dist &
server_pid=$!
sleep 1
open "http://localhost:4173"
wait $server_pid

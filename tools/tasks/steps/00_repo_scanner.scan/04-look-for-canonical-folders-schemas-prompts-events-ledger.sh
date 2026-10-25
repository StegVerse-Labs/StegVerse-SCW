echo "---- CANONICAL FOLDERS ----"
for d in schemas schema prompts prompt agents agent stegagents events event ledger ledgers logs log governance orchestrator ops; do
  if find . -maxdepth 4 -type d -iname "$d" | head -n 5 | grep -q .; then
    echo "Found dir name match: $d"
    find . -maxdepth 4 -type d -iname "$d" | head -n 20
    echo
  fi
done

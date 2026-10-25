echo "---- WORKFLOWS ----"
if [ -d ".github/workflows" ]; then
  ls -la .github/workflows
  echo
  for f in .github/workflows/*.yml .github/workflows/*.yaml; do
    [ -f "$f" ] || continue
    echo "== $f =="
    # show only the trigger section (first ~80 lines is usually enough)
    sed -n '1,120p' "$f"
    echo
  done
else
  echo "No .github/workflows directory."
fi

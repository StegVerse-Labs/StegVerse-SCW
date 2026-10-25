echo "---- LIKELY-RELEVANT FILENAMES ----"
find . -maxdepth 5 -type f \( \
  -iname "*orchestrator*" -o \
  -iname "*runner*" -o \
  -iname "*dispatcher*" -o \
  -iname "*work*item*" -o \
  -iname "*ledger*" -o \
  -iname "*event*" -o \
  -iname "*schema*" -o \
  -iname "*verdict*" -o \
  -iname "*governance*" -o \
  -iname "*constitution*" -o \
  -iname "*invariant*" -o \
  -iname "*agent*" -o \
  -iname "*prompt*" \
\) \
| sed 's|^\./||' \
| head -n 300

set -e
for f in \
  ui/public/index.html \
  ui/public/stegtalk.html \
  ui/public/manifest.json \
  ui/public/sw.js \
  ui/public/icons/icon-192.png \
  ui/public/icons/icon-512.png \
  README-LAYMAN.md \
  README-DEV.md
do
  if [ ! -e "$f" ]; then
    echo "Missing: $f"; exit 1
  else
    echo "Found: $f"
  fi
done
echo "All files present."

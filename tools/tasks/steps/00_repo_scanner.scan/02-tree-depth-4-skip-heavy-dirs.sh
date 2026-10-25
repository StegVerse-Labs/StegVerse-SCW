sudo apt-get update -y
sudo apt-get install -y tree ripgrep
echo "---- TREE (depth 4) ----"
tree -a -L 4 \
  -I ".git|node_modules|.venv|venv|__pycache__|dist|build|coverage|.next|.cache|.pytest_cache|.mypy_cache|.ruff_cache|.idea|.vscode" \
  .

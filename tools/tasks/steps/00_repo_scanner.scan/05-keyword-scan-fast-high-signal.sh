echo "---- KEYWORD SCAN (top hits) ----"
rg -n --hidden --no-follow \
  -S \
  "(workflow_dispatch|repository_dispatch|issue_comment|pull_request_target|orchestrator|dispatcher|runner|work[_-]?item|verdict|quorum|constitution|invariant|policy|token[_-]?vault|tvc|stegid|agent|router|builder|verifier|audit|append[- ]only|hash chain|chain[- ]of[- ]custody)" \
  . \
  -g'!.git/**' \
  -g'!node_modules/**' \
  -g'!.venv/**' \
  -g'!venv/**' \
  -g'!dist/**' \
  -g'!build/**' \
  -g'!coverage/**' \
  | head -n 300 || true

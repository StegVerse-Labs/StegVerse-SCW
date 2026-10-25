echo "## First-Aid Sweep" >> "$GITHUB_STEP_SUMMARY"
if [ -f ".github/autopatch_out/FIRST_AID_SUMMARY.json" ]; then
  cat ".github/autopatch_out/FIRST_AID_SUMMARY.json" >> "$GITHUB_STEP_SUMMARY"
else
  echo "_No summary file created._" >> "$GITHUB_STEP_SUMMARY"
fi

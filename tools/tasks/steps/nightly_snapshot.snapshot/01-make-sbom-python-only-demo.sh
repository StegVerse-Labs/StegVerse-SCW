pipx install cyclonedx-bom || python -m pip install cyclonedx-bom
cyclonedx-bom -o sbom.json -i api/requirements.txt || true

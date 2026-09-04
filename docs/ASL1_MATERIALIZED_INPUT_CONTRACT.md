# ASL-1 Materialized Input Contract

The repository-alignment checker consumes source only after an admitted source-read owner has materialized exact repository snapshots.

The checker itself:

- accepts no credential value;
- performs no GitHub or provider API call;
- performs no git fetch or clone;
- requires an exact 40-hex source commit for every configured repository;
- requires a secret-free receipt reference for every materialized target;
- rejects token/secret/credential fields in the input manifest;
- evaluates only local files and workflows;
- writes only local JSON/Markdown reports;
- grants no report-publication, repository-mutation, release, runtime, or credential authority.

Runtime manifest schema: `stegverse.scw.repo-alignment-materialization/v1`.

Source materialization and any later durable report publication are separate governed capabilities. TV/TVC remains the sole credential authority. GitHub Actions may validate or transport evidence but is not the production/runtime/control-plane owner.

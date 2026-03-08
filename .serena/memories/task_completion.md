# Task completion checklist
- Run `uv run pytest -q` after changes.
- If provider/config behavior changed, add or update pytest coverage under `tests/`.
- For remote-provider work, verify compatibility with existing `ProviderErrorCode` handling in scheduler.
- Keep plugin-facing config in `_conf_schema.json` synchronized with `app/config.py`.
- Update README when user-facing setup or deployment steps change.

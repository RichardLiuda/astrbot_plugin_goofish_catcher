# Style and conventions
- Python code uses type hints broadly and dataclasses with slots where appropriate.
- Keep logic split by responsibility: config, provider, scheduler, notifier, storage, recommender.
- Provider errors should use the shared `ProviderError` / `ProviderErrorCode` contract from `app/types.py`.
- Prefer small focused changes that fit current architecture; `remote_rest` should extend existing provider abstraction instead of bypassing it.
- Tests use pytest, including async tests with `pytest.mark.asyncio`.
- File encoding should remain UTF-8 without BOM for code changes.

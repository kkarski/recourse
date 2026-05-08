# Spectr CLI entrypoints

Interact with Spectr only by running these yourself—**not** by maintaining a separate helper script that wraps the tool (see **using-spectr** `SKILL.md`).

Implementation: **`spectr/src/spectr/cli.py`** (Click: `cli` group, `main()`).

1. **Installed package (recommended):** from the `spectr` directory with venv active, `pip install -e .`, then **`spectr`** on your `PATH`.
2. **Module:** from a cwd where the package resolves, **`python -m spectr`** (same subcommands as `spectr`).
3. **Dev tree, no install:** **`python spectr/src/spectr/cli.py`** (or run `cli.py` directly). It prepends `spectr/src` to `sys.path` so the package loads without an editable install.

Use **`--help`** on the top-level command or any group (e.g. `spectr uc --help`).

"""Configure the pinned Breek source for active-day collisions and 120 Hz physics."""
from pathlib import Path

def replace(path, before, after):
    text = path.read_text()
    assert before in text, f"Upstream code changed: {path}: {before}"
    path.write_text(text.replace(before, after))

root = Path("breek")
replace(root / "packages/solver/src/gameBoard.ts",
        "const level = contributionGrid[y][x];",
        "const level = contributionGrid[y][x];\n      if (level === 0) continue; // Empty days are background, never collision bricks.")

replace(root / "packages/solver/src/gameBoard.ts",
        "const BLOCKS_PER_ROW = 52; // One year has 52 weeks",
        "// The calendar can include a partial 53rd week.")
replace(root / "packages/solver/src/gameBoard.ts",
        "export function createGameBoard(contributionData: Cell[]): GameBoard {",
        "export function createGameBoard(contributionData: Cell[]): GameBoard {\n  const BLOCKS_PER_ROW = Math.max(1, ...contributionData.map(cell => cell.x + 1));")
replace(root / "packages/commons/index.ts",
        "frameDuration: 16, // ~60 fps", "frameDuration: 1000 / 120, // 120 Hz simulation")
replace(root / "packages/commons/index.ts",
        "export const EXTRA_SPACE = 200;", "export const EXTRA_SPACE = 80;")
replace(root / "packages/svg-creator/src/index.ts",
        "frames.length / 60; // 60 fps", "frames.length / 120; // 120 Hz motion timeline")

# Resolve workspace imports directly to pinned source; no package install is needed.
import os
modules = {
    "@breek/commons": root / "packages/commons/index.ts",
    "@breek/solver": root / "packages/solver/src/index.ts",
    "@breek/svg-creator": root / "packages/svg-creator/src/index.ts",
    "@breek/github-user-contribution": root / "packages/github-user-contribution/src/index.ts",
}
for package in ("solver", "svg-creator", "github-user-contribution"):
    for path in (root / "packages" / package / "src").glob("*.ts"):
        text = path.read_text()
        for name, target in modules.items():
            relative = os.path.relpath(target, path.parent).replace(os.sep, "/")
            if not relative.startswith("."):
                relative = "./" + relative
            text = text.replace(f'"{name}"', f'"{relative}"')
        path.write_text(text)

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

physics = root / "packages/solver/src/gameSimulation.ts"
for before, after in [
    ("const PADDLE_SPEED = 8;", "const PADDLE_SPEED = 4;"),
    ("const MAX_BALL_SPEED = 32;", "const MAX_BALL_SPEED = 16;"),
    ("const MIN_BALL_SPEED = 8;", "const MIN_BALL_SPEED = 4;"),
    ("dx: 6 *", "dx: 3 *"),
    ("dy: -6,", "dy: -3,"),
    ("ball.dx = 6 *", "ball.dx = 3 *"),
    ("ball.dy = -6;", "ball.dy = -3;"),
    (") / 10;", ") / 20;"),
    ("const maxIterations = 1000;", "const maxIterations = 2000;"),
]:
    replace(physics, before, after)

replace(root / "packages/commons/index.ts",
        "frameDuration: 16, // ~60 fps", "frameDuration: 1000 / 120, // 120 Hz simulation")
replace(root / "packages/svg-creator/src/index.ts",
        "frames.length / 60; // 60 fps", "frames.length / 120; // 120 Hz motion timeline")

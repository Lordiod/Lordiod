import { mkdirSync, writeFileSync } from "node:fs";
import { getGithubUserContribution } from "../../breek/packages/github-user-contribution/src/index.ts";
import { createGameBoard } from "../../breek/packages/solver/src/index.ts";
import { createSvg } from "../../breek/packages/svg-creator/src/index.ts";
import { basePalettes, defaultSimulationOptions } from "../../breek/packages/commons/index.ts";

import { simulateGame } from "./breakout-physics.mjs";

const username = process.env.INPUT_GITHUB_USER_NAME;
const token = process.env.INPUT_GITHUB_TOKEN;
if (!username || !token) throw new Error("Missing GitHub contribution credentials");
const cells = await getGithubUserContribution(username, token);
const board = createGameBoard(cells);
const active = new Set(cells.filter(c => c.level > 0).map(c => `${c.x * 16},${c.y * 16}`));
if (board.blocks.length !== active.size || board.blocks.some(b => !active.has(`${b.x},${b.y}`)))
  throw new Error("Empty contribution day became a collision brick");
console.log(`Generating 120 Hz motion for ${board.blocks.length} contributed days; empty days are background only`);
const states = simulateGame(board, defaultSimulationOptions);
const frames = states.map(s => ({ball: s.ball, paddle: s.paddle, board: s.board}));
mkdirSync("dist", {recursive: true});
for (const [palette, filename] of [
  ["github-light", "github-contribution-grid-breek.svg"],
  ["github-dark", "github-contribution-grid-breek-dark.svg"]
]) {
  const colors = basePalettes[palette];
  writeFileSync("dist/" + filename, createSvg(board, frames, {
    colorDots: colors.colorDots, colorEmpty: colors.colorEmpty, colorPaddle: "#4cd969"
  }));
}

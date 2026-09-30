import assert from "node:assert/strict";
import {advance,simulateGame,sweepCircle} from "./breakout-physics.mjs";
function state(ball,blocks=[]) {
  return {board:{width:832,height:112,blocks:blocks.map(b=>({...b,visible:true}))},
    ball:{...ball},paddle:{x:366,width:100},score:0};
}
for(let level=1;level<=4;level++) {
  const s=state({x:107,y:130,dx:0,dy:-190},[{x:100,y:64,lives:level+1}]);
  const events=advance(s,.3);
  assert.equal(s.score,1);assert.equal(s.board.blocks[0].visible,false);
  assert(s.ball.dy>0,"Bottom face must reflect vertically");
  assert.equal(events.filter(e=>e.kind==="brick").length,1);
  advance(s,.05);assert.equal(s.score,1,"Removed bricks cannot collide again");
}
const side=state({x:60,y:70,dx:190,dy:0},[{x:100,y:64,lives:5}]);
advance(side,.3);assert(side.ball.dx<0);assert.equal(side.score,1);
const fast=state({x:60,y:70,dx:1900,dy:0},[{x:100,y:64,lives:5}]);
advance(fast,.05);assert.equal(fast.score,1,"Fast paths must not tunnel through bricks");
const gap=state({x:60,y:88,dx:190,dy:0},[{x:100,y:64,lives:5}]);
advance(gap,.3);assert.equal(gap.score,0);assert(gap.ball.dx>0,"Empty space remains passable");
const corner=sweepCircle({x:80,y:44,dx:100,dy:100},{x:101,y:65,w:13,h:13},.3);
assert(corner && corner.nx<0 && corner.ny<0,"Rounded corner must register contact");
const adjacent=state({x:115.5,y:120,dx:0,dy:-190},[
  {x:100,y:64,lives:2},{x:116,y:64,lives:5}]);
advance(adjacent,.3);assert.equal(adjacent.score,2,"Simultaneous contacts clear both bricks");
for(const dense of [false,true]) {
  const blocks=[];
  for(let x=0;x<52;x++)for(let y=0;y<7;y++)
    if(dense||(x*7+y)%5===0)blocks.push({x:x*16,y:y*16,lives:2+x%4});
  const frames=simulateGame({width:832,height:112,blocks},{totalDuration:360000});
  assert.equal(frames.at(-1).score,blocks.length);
}
console.log("All face, corner, gap, tunneling, one-hit, sparse and dense calendar checks passed");

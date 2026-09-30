// Collision geometry matches the displayed 13px bricks and 5px ball.
const RADIUS = 5, BRICK = 13, PADDLE_HEIGHT = 10;
const EPS = 1e-7;

export function sweepCircle(ball, rect, dt) {
  const hits = [];
  function side(t, nx, ny, check) {
    if (t >= -EPS && t <= dt + EPS && ball.dx * nx + ball.dy * ny < -EPS && check(t))
      hits.push({t: Math.max(0, t), nx, ny});
  }
  if (ball.dx > 0) side((rect.x-RADIUS-ball.x)/ball.dx, -1, 0,
    t => ball.y+ball.dy*t >= rect.y-EPS && ball.y+ball.dy*t <= rect.y+rect.h+EPS);
  if (ball.dx < 0) side((rect.x+rect.w+RADIUS-ball.x)/ball.dx, 1, 0,
    t => ball.y+ball.dy*t >= rect.y-EPS && ball.y+ball.dy*t <= rect.y+rect.h+EPS);
  if (ball.dy > 0) side((rect.y-RADIUS-ball.y)/ball.dy, 0, -1,
    t => ball.x+ball.dx*t >= rect.x-EPS && ball.x+ball.dx*t <= rect.x+rect.w+EPS);
  if (ball.dy < 0) side((rect.y+rect.h+RADIUS-ball.y)/ball.dy, 0, 1,
    t => ball.x+ball.dx*t >= rect.x-EPS && ball.x+ball.dx*t <= rect.x+rect.w+EPS);
  for (const [cx, cy, sx, sy] of [
    [rect.x,rect.y,-1,-1], [rect.x+rect.w,rect.y,1,-1],
    [rect.x,rect.y+rect.h,-1,1], [rect.x+rect.w,rect.y+rect.h,1,1]]) {
    const ox=ball.x-cx, oy=ball.y-cy, a=ball.dx**2+ball.dy**2;
    if (a < EPS) continue;
    const b=2*(ox*ball.dx+oy*ball.dy), c=ox**2+oy**2-RADIUS**2;
    const disc=b*b-4*a*c;
    if (disc < 0) continue;
    const t=(-b-Math.sqrt(disc))/(2*a);
    if (t < -EPS || t > dt+EPS) continue;
    const nx=(ox+ball.dx*t)/RADIUS, ny=(oy+ball.dy*t)/RADIUS;
    if (nx*sx >= -EPS && ny*sy >= -EPS && ball.dx*nx+ball.dy*ny < -EPS)
      hits.push({t:Math.max(0,t),nx,ny});
  }
  return hits.sort((a,b)=>a.t-b.t)[0] ?? null;
}

function reflect(ball, nx, ny) {
  const dot=ball.dx*nx+ball.dy*ny;
  ball.dx-=2*dot*nx; ball.dy-=2*dot*ny;
}

export function advance(state, dt) {
  const {ball, board, paddle}=state;
  const height=board.height+80, paddleY=height-PADDLE_HEIGHT-5;
  let remaining=dt;
  const events=[];
  for (let iteration=0; remaining>EPS && iteration<12; iteration++) {
    const candidates=[];
    const boundary=(t,nx,ny,kind)=> {
      if(t>=-EPS && t<=remaining+EPS) candidates.push({t:Math.max(0,t),nx,ny,kind});
    };
    if(ball.dx<0) boundary((RADIUS-ball.x)/ball.dx,1,0,"wall");
    if(ball.dx>0) boundary((board.width-RADIUS-ball.x)/ball.dx,-1,0,"wall");
    if(ball.dy<0) boundary((RADIUS-ball.y)/ball.dy,0,1,"wall");
    if(ball.dy>0) {
      const hit=sweepCircle(ball,{x:paddle.x,y:paddleY,w:paddle.width,h:PADDLE_HEIGHT},remaining);
      if(hit) candidates.push({...hit,kind:"paddle"});
      boundary((height-RADIUS-ball.y)/ball.dy,0,-1,"floor");
    }
    board.blocks.forEach((block,index)=>{
      if(!block.visible) return;
      const hit=sweepCircle(ball,{x:block.x+1,y:block.y+1,w:BRICK,h:BRICK},remaining);
      if(hit) candidates.push({...hit,kind:"brick",index});
    });
    if(!candidates.length) {ball.x+=ball.dx*remaining;ball.y+=ball.dy*remaining;break;}
    candidates.sort((a,b)=>a.t-b.t);
    const first=candidates[0];
    ball.x+=ball.dx*first.t;ball.y+=ball.dy*first.t;
    remaining-=first.t;
    const contacts=candidates.filter(c=>Math.abs(c.t-first.t)<EPS);
    for(const hit of contacts) {
      if(hit.kind==="brick" && board.blocks[hit.index].visible) {
        board.blocks[hit.index].visible=false;
        state.score++;
        events.push({kind:"brick",index:hit.index,x:ball.x,y:ball.y,nx:hit.nx,ny:hit.ny});
      }
    }
    if(first.kind==="paddle") {
      // Aim toward a remaining brick while keeping a natural, bounded rebound angle.
      const targets=board.blocks.filter(b=>b.visible);
      if(targets.length) {
        const target=targets.reduce((a,b)=>
          Math.hypot(a.x+7-ball.x,a.y+7-ball.y) < Math.hypot(b.x+7-ball.x,b.y+7-ball.y)?a:b);
        const angle=Math.max(-1.05,Math.min(1.05,Math.atan2(target.x+7-ball.x,ball.y-target.y-7)));
        ball.dx=190*Math.sin(angle);ball.dy=-190*Math.cos(angle);
      } else ball.dy=-Math.abs(ball.dy);
    } else {
      let nx=contacts.reduce((s,h)=>s+h.nx,0),ny=contacts.reduce((s,h)=>s+h.ny,0);
      const norm=Math.hypot(nx,ny);
      if(norm>EPS) {nx/=norm;ny/=norm;} else {nx=first.nx;ny=first.ny;}
      reflect(ball,nx,ny);
    }
    if(first.kind==="floor") events.push({kind:"floor"});
    // Separate from the contact surface so the same brick cannot rebound twice.
    ball.x+=first.nx*1e-5;ball.y+=first.ny*1e-5;
  }
  return events;
}

function landingX(ball, width, y) {
  const t=Math.max(0,(y-ball.y)/ball.dy);
  const span=width-2*RADIUS;
  let x=((ball.x-RADIUS+ball.dx*t)%(2*span)+2*span)%(2*span);
  if(x>span)x=2*span-x;
  return x+RADIUS;
}

export function simulateGame(board, options) {
  const dt=1/120, duration=Math.max(options.totalDuration/1000,900);
  const state={
    board:{...board,blocks:board.blocks.map(b=>({...b,visible:true}))},
    ball:{x:board.width/2,y:board.height+30,dx:114,dy:-152},
    paddle:{x:board.width/2-50,width:100},score:0
  };
  const states=[];
  const hitCounts=new Map();
  let floorHits=0;
  const snapshot=()=>states.push({
    board:{...state.board,blocks:state.board.blocks.map(b=>({...b}))},
    ball:{...state.ball},paddle:{...state.paddle},score:state.score
  });
  snapshot();
  for(let frame=0;frame<duration*120;frame++) {
    const target=state.ball.dy>0?landingX(state.ball,board.width,board.height+80-20):state.ball.x;
    const goal=Math.max(0,Math.min(board.width-state.paddle.width,target-state.paddle.width/2));
    state.paddle.x+=Math.max(-520*dt,Math.min(520*dt,goal-state.paddle.x));
    for(const event of advance(state,dt)) {
      if(event.kind==="brick") hitCounts.set(event.index,(hitCounts.get(event.index)??0)+1);
      if(event.kind==="floor") floorHits++;
    }
    snapshot();
    if(state.board.blocks.every(b=>!b.visible)) break;
  }
  if([...hitCounts.values()].some(count=>count!==1)) throw new Error("A brick was hit more than once");
  console.log(`Physics check: ${hitCounts.size} bricks broken once, ${floorHits} missed paddle contacts, ${states.length} frames`);
  if(floorHits) throw new Error("Autopaddle missed the ball");
  if(state.board.blocks.some(b=>b.visible)) throw new Error("Animation did not clear all contributed days");
  return states;
}

/* PURPOSE: reveal + countdown + drawer + counters. Zero inline handlers. */
addEventListener('scroll', ()=>document.querySelector('.topbar').classList.toggle('scrolled', scrollY>4), {passive:true});
const io = new IntersectionObserver(es=>es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }}), {threshold:.12});
document.querySelectorAll('[data-stagger]').forEach(p=>[...p.children].forEach((c,i)=>{ c.style.setProperty('--rd',(i*80)+'ms'); c.classList.add('rv'); }));
document.querySelectorAll('.rv').forEach(el=>io.observe(el));

// Countdown to lights-out. Date lives in data/race.json (fallback inline = Baku 2026).
const FALLBACK_RACE = {gp:'Azerbaijan GP', circuit:'Baku City Circuit', lightsOut:'2026-09-26T07:00:00Z'};
function tick(to){
  let s = Math.max(0, Math.floor((new Date(to) - Date.now()) / 1000));
  const d = Math.floor(s/86400); s%=86400;
  const h = Math.floor(s/3600); s%=3600;
  const m = Math.floor(s/60); s%=60;
  document.getElementById('cd-d').textContent = String(d).padStart(2,'0');
  document.getElementById('cd-h').textContent = String(h).padStart(2,'0');
  document.getElementById('cd-m').textContent = String(m).padStart(2,'0');
  document.getElementById('cd-s').textContent = String(s).padStart(2,'0');
}
function startCountdown(race){
  document.getElementById('race-gp').textContent = race.gp;
  document.getElementById('race-circuit').textContent = race.circuit;
  tick(race.lightsOut);
  setInterval(()=>tick(race.lightsOut), 1000);
}
fetch('data/race.json').then(r=>r.json()).then(startCountdown).catch(()=>startCountdown(FALLBACK_RACE));

// Count-up stats when visible.
const cio = new IntersectionObserver(es=>es.forEach(e=>{
  if(!e.isIntersecting) return;
  const el = e.target, end = +el.dataset.count;
  cio.unobserve(el);
  const t0 = performance.now();
  (function f(t){
    const p = Math.min((t-t0)/1200, 1);
    el.textContent = Math.round(end * (1-Math.pow(1-p,3))) + '+';
    if(p<1) requestAnimationFrame(f);
  })(t0);
}), {threshold:.4});
document.querySelectorAll('[data-count]').forEach(el=>cio.observe(el));

// Delegated actions.
document.addEventListener('click', e=>{
  const el = e.target.closest('[data-act]');
  if(!el) return;
  if(el.tagName==='A') e.preventDefault();
  if(el.dataset.act==='drawer') document.getElementById('drawer').classList.toggle('open', el.dataset.open==='1');
  if(el.dataset.act==='news') document.getElementById('news-msg').textContent = 'You are on the list. See you at lights out.';
});
document.getElementById('yr').textContent = new Date().getFullYear();

// Runtime vector animation (Lottie, vendored — no CDN). Hand-authored loader.json.
// Runtime vector animation (real Rive .riv, authored as RML via the Rive CLI).
// Falls back to the text counter if the runtime or file fails.
var riveAnim = null; window.__riveState = 'init';
try{
  if(window.rive){
    if(window.rive.RuntimeLoader) window.rive.RuntimeLoader.setWasmUrl('vendor/rive/rive.wasm');
    riveAnim = new window.rive.Rive({
      src: 'assets/ln4-loader.riv',
      canvas: document.getElementById('rive-load'),
      autoplay: true,
      animations: ['Spin'],
      fit: window.rive.Fit.contain,
      alignment: window.rive.Alignment.center,
      onLoad: ()=>{ window.__riveState = 'loaded'; try{ riveAnim.resizeDrawingSurfaceToCanvas(); }catch(e){} },
      onLoadError: (e)=>{ window.__riveState = 'error:' + e; console.error('[rive]', e); }
    });
  } else { window.__riveState = 'no-runtime'; }
}catch(e){ window.__riveState = 'threw:' + e.message; }

// Procedural 3D wireframe helmet — lathe geometry, orthographic projection, no model file.
(function(){
  const cv = document.getElementById('helm3d');
  if(!cv || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const ctx = cv.getContext('2d');
  const PROF = [[1,-1],[1.03,-.7],[1,-.4],[.95,-.1],[.86,.2],[.72,.48],[.52,.72],[.3,.9],[.1,.99]];
  const SEG = 26, MER = 18, TAU = Math.PI*2;
  let W, H, mx = 0, my = 0, tx = 0, ty = 0, run = true;
  const stage = document.getElementById('helmstage');
  function size(){
    const r = cv.getBoundingClientRect(), d = Math.min(devicePixelRatio||1, 2);
    W = cv.width = Math.max(50, r.width*d); H = cv.height = 360*d;
  }
  size(); addEventListener('resize', size);
  stage.addEventListener('mousemove', e=>{
    const r = stage.getBoundingClientRect();
    tx = ((e.clientX-r.left)/r.width-.5)*2; ty = ((e.clientY-r.top)/r.height-.5)*2;
  });
  new IntersectionObserver(es=>{ run = es[0].isIntersecting; }).observe(cv);
  function P(x, y, z, A, B){
    const cA = Math.cos(A), sA = Math.sin(A), cB = Math.cos(B), sB = Math.sin(B);
    const x1 = x*cA - z*sA, z1 = x*sA + z*cA;
    return [x1, y*cB - z1*sB, y*sB + z1*cB];
  }
  (function loop(t){
    requestAnimationFrame(loop);
    if(!run) return;
    mx += (tx-mx)*.06; my += (ty-my)*.06;
    const A = t/1000*.45 + mx*.9, B = .3 + my*.35;
    const S = Math.min(W,H)*.4, cx = W/2, cy = H*.56;
    const pt = p=>[cx+p[0]*S, cy-p[1]*S];
    ctx.clearRect(0,0,W,H);
    ctx.lineWidth = Math.max(1, W/900);
    ctx.strokeStyle = 'rgba(255,106,0,.7)';
    PROF.forEach(([r,y])=>{
      const visor = (y > -.15 && y < .55);
      for(let s=0; s<SEG; s++){
        const a0 = s/SEG*TAU, a1 = (s+1)/SEG*TAU;
        const mid = (a0+a1)/2, d = Math.atan2(Math.sin(mid), Math.cos(mid));
        if(visor && Math.abs(d) < .6) continue; // visor opening faces +X
        const p0 = pt(P(r*Math.cos(a0), y, r*Math.sin(a0), A, B));
        const p1 = pt(P(r*Math.cos(a1), y, r*Math.sin(a1), A, B));
        ctx.beginPath(); ctx.moveTo(p0[0],p0[1]); ctx.lineTo(p1[0],p1[1]); ctx.stroke();
      }
    });
    ctx.strokeStyle = 'rgba(255,106,0,.35)';
    for(let m=0; m<MER; m++){
      const a = m/MER*TAU;
      ctx.beginPath();
      PROF.forEach(([r,y], i)=>{
        const p = pt(P(r*Math.cos(a), y, r*Math.sin(a), A, B));
        if(i) ctx.lineTo(p[0],p[1]); else ctx.moveTo(p[0],p[1]);
      });
      ctx.stroke();
    }
    // Translucent lime visor across the opening.
    const V = (ang,y)=>pt(P(.97*Math.cos(ang), y, .97*Math.sin(ang), A, B));
    const c = [V(-.6,-.15), V(.6,-.15), V(.6,.55), V(-.6,.55)];
    ctx.beginPath(); ctx.moveTo(c[0][0],c[0][1]);
    c.slice(1).forEach(p=>ctx.lineTo(p[0],p[1])); ctx.closePath();
    ctx.fillStyle = 'rgba(200,245,46,.20)'; ctx.fill();
    ctx.strokeStyle = 'rgba(200,245,46,.8)'; ctx.stroke();
    // Ground shadow ellipse.
    ctx.beginPath(); ctx.ellipse(cx, cy+S*1.02, S*.8, S*.12, 0, 0, TAU);
    ctx.strokeStyle = 'rgba(255,255,255,.15)'; ctx.stroke();
  })(0);
})();
document.body.classList.add('js');

// Loader: count to 100, then open the gates (safety timeout included).
(function(){
  const loader = document.getElementById('loader');
  const num = document.getElementById('load-num'), bar = document.getElementById('load-bar');
  const t0 = performance.now(), DUR = 900;
  let done = false;
  function open(){ if(done) return; done = true; if(riveAnim){ try{ riveAnim.cleanup(); }catch(e){} } loader.classList.add('done'); document.body.classList.add('ready'); }
  (function f(t){
    const p = Math.min((t-t0)/DUR, 1);
    num.textContent = String(Math.round(p*100)).padStart(2,'0');
    bar.style.width = (p*100) + '%';
    if(p<1) requestAnimationFrame(f); else open();
  })(t0);
  setTimeout(open, 3000);
  document.addEventListener('visibilitychange', ()=>{ if(!document.hidden) open(); });
})();

// Split-text: wrap words for rise-in (keeps <em> styling). JS-gated CSS does the rest.
document.querySelectorAll('[data-split]').forEach(el=>{
  if(!el.classList.contains('rv')){ el.classList.add('rv'); io.observe(el); }
  (function walk(node){
    [...node.childNodes].forEach(n=>{
      if(n.nodeType===3){
        const frag = document.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach(part=>{
          if(!part) return;
          if(/^\s+$/.test(part)){ frag.appendChild(document.createTextNode(' ')); return; }
          const w = document.createElement('span'); w.className = 'w';
          const i = document.createElement('i'); i.textContent = part;
          w.appendChild(i); frag.appendChild(w);
        });
        node.replaceChild(frag, n);
      } else if(n.nodeType===1) walk(n);
    });
  })(el);
  [...el.querySelectorAll('.w>i')].forEach((w,i)=>w.style.setProperty('--rd',(i*35)+'ms'));
});

// Scroll progress bar (transform-only).
const prog = document.getElementById('prog');
addEventListener('scroll', ()=>{
  const h = document.documentElement;
  prog.style.transform = `scaleX(${h.scrollTop / (h.scrollHeight - h.clientHeight)})`;
}, {passive:true});

// Tilt helmets + magnetic buttons (fine pointers only, transform-only).
if(matchMedia('(hover:hover) and (prefers-reduced-motion: no-preference)').matches){
  document.querySelectorAll('.helm').forEach(card=>{
    card.addEventListener('mousemove', e=>{
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      card.style.transform = `perspective(900px) rotateX(${-y*8}deg) rotateY(${x*8}deg) translateY(-4px)`;
    });
    card.addEventListener('mouseleave', ()=>{ card.style.transform = ''; });
  });
  document.querySelectorAll('.hero .btn, .store .btn').forEach(btn=>{
    btn.addEventListener('mousemove', e=>{
      const r = btn.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      btn.style.transform = `translate(${x*6}px, ${y*6}px)`;
    });
    btn.addEventListener('mouseleave', ()=>{ btn.style.transform = ''; });
  });
}

// Canvas speed-dust in the hero (papaya particles drifting right).
(function(){
  const cv = document.getElementById('dust');
  if(!cv || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const ctx = cv.getContext('2d');
  let W, H, pts = [], run = true;
  function size(){
    const r = cv.parentElement.getBoundingClientRect(), dpr = Math.min(devicePixelRatio||1, 2);
    W = cv.width = r.width * dpr; H = cv.height = r.height * dpr;
    pts = Array.from({length: Math.min(90, W/14)}, ()=>({x: Math.random()*W, y: Math.random()*H, v: (.4+Math.random()*1.2)*dpr, r: (1+Math.random()*2)*dpr, o: Math.random()*6.28}));
  }
  size(); addEventListener('resize', size);
  new IntersectionObserver(es=>{ run = es[0].isIntersecting; }).observe(cv);
  (function loop(){
    requestAnimationFrame(loop);
    if(!run) return;
    ctx.clearRect(0,0,W,H);
    const t = performance.now()/1000;
    pts.forEach(p=>{
      p.x += p.v; p.y += Math.sin(t + p.o) * .3;
      if(p.x > W+10){ p.x = -10; p.y = Math.random()*H; }
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.29);
      ctx.fillStyle = 'rgba(255,106,0,.45)'; ctx.fill();
    });
    ctx.strokeStyle = 'rgba(255,106,0,.14)'; ctx.lineWidth = 1;
    for(let a=0; a<pts.length; a++) for(let b=a+1; b<pts.length; b++){
      const dx = pts[a].x-pts[b].x, dy = pts[a].y-pts[b].y, d2 = dx*dx+dy*dy, max = 130*130;
      if(d2 < max){ ctx.globalAlpha = 1-d2/max; ctx.beginPath(); ctx.moveTo(pts[a].x,pts[a].y); ctx.lineTo(pts[b].x,pts[b].y); ctx.stroke(); }
    }
    ctx.globalAlpha = 1;
  })();
})();

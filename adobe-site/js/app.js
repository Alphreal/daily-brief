/* PURPOSE: all behavior. 4 patterns: carousel / filter / toggle+search / reveal. */
let cur = 0;
const slides = [...document.querySelectorAll('.slide')];
const dots = [...document.querySelectorAll('.dot')];
const thumbs = [...document.querySelectorAll('.thumb')];
function go(i){
  cur = (i + slides.length) % slides.length;
  slides.forEach((s,k)=>{ s.classList.toggle('active',k===cur); s.setAttribute('aria-hidden', k!==cur); });
  dots.forEach((d,k)=>{ d.classList.toggle('active',k===cur); if(k===cur) d.setAttribute('aria-current','true'); else d.removeAttribute('aria-current'); });
  thumbs.forEach((t,k)=>{ t.classList.toggle('active',k===cur); if(t.getAttribute('role')==='tab') t.setAttribute('aria-selected', k===cur); });
  restart();
}
// All UI actions delegate here — HTML carries data-act, zero inline onclick (CSP-safe, testable).
document.addEventListener('click', e=>{
  const el = e.target.closest('[data-act]');
  if(!el) return;
  if(el.tagName==='A') e.preventDefault();
  const a = el.dataset.act;
  if(a==='go') go(+el.dataset.i);
  else if(a==='step') step(+el.dataset.d);
  else if(a==='scroll') document.getElementById(el.dataset.to)?.scrollIntoView();
  else if(a==='bill') bill(el.dataset.w);
  else if(a==='mnav') document.getElementById('mnav').style.display = el.dataset.open==='1' ? 'flex' : 'none';
  else if(a==='search') document.getElementById('sov').classList.toggle('open', el.dataset.open==='1');
  else if(a==='signin') alert('Demo only — sign-in would open here.');
});
document.addEventListener('input', e=>{ if(e.target.matches('[data-filter]')) filterTools(e.target.value); });
function step(d){ go(cur+d); }
let timer = setInterval(()=>go(cur+1), 6000);
function restart(){ clearInterval(timer); timer = setInterval(()=>go(cur+1), 6000); }

document.getElementById('pills').addEventListener('click', e=>{
  if(e.target.tagName!=='BUTTON') return;
  document.querySelectorAll('#pills button').forEach(b=>b.classList.remove('active'));
  e.target.classList.add('active');
  const f = e.target.dataset.f;
  document.querySelectorAll('#bento .bcard').forEach(c=>{
    c.style.display = (f==='all' || c.dataset.cat.includes(f)) ? '' : 'none';
  });
});

function bill(w){
  document.getElementById('bM').classList.toggle('on', w==='m');
  document.getElementById('bY').classList.toggle('on', w==='y');
  document.getElementById('price').textContent = w==='m' ? '$11.99' : '$143.88';
  document.getElementById('per').textContent = w==='m' ? '/mo first year, then $23.99' : '/yr first year, billed annually';
}
function filterTools(v){
  v = (v||'').toLowerCase();
  document.querySelectorAll('#tgrid .tool').forEach(t=>{
    t.style.display = t.dataset.n.includes(v) ? '' : 'none';
  });
}

addEventListener('scroll', ()=>document.getElementById('top').classList.toggle('scrolled', scrollY>4), {passive:true});
const io = new IntersectionObserver(es=>es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }}), {threshold:.12});
document.querySelectorAll('.rv').forEach(el=>io.observe(el));
// Stagger: children of [data-stagger] cascade in 70ms apart (Adobe card-rise feel).
document.querySelectorAll('[data-stagger]').forEach(p=>[...p.children].forEach((c,i)=>{ c.style.setProperty('--rd',(i*70)+'ms'); c.classList.add('rv'); io.observe(c); }));
// Parallax: hero art drifts slower than scroll (transform-only, rAF-throttled, motion-safe).
const arts = [...document.querySelectorAll('.slide-art')];
if(!matchMedia('(prefers-reduced-motion: reduce)').matches && arts.length){
  let tick=false;
  addEventListener('scroll', ()=>{
    if(tick) return; tick=true;
    requestAnimationFrame(()=>{
      const y = Math.min(scrollY*.12, 120);
      arts.forEach(a=>{ a.style.transform = `translateY(${y}px)`; });
      tick=false;
    });
  }, {passive:true});
}
document.getElementById('yr').textContent = new Date().getFullYear();
document.getElementById('sov').addEventListener('click', e=>{ if(e.target.id==='sov') e.target.classList.remove('open'); });
addEventListener('keydown', e=>{ if(e.key==='Escape') document.getElementById('sov').classList.remove('open'); });

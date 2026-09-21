/* BACKEND MIMIC — how adobe.com really works, in 30 lines.
 * Real: AEM fragments (header/footer via gnav-source/footer-source), MAS merch API
 * (mas.adobe.com/studio → price/CTA per locale), personalization manifests (.json per
 * region), IMS auth token, georouting + hreflang sitemaps, lana logging.
 * Here: same SHAPE, fake DATA. Open DevTools → Network to see data/merch.json load.
 * To use: add data-merch="cc-pro" on any element; this fills [data-promo]/[data-price]/[data-cta].
 */
async function loadMerch(){
  try{
    const r = await fetch('data/merch.json');
    const db = await r.json();
    document.querySelectorAll('[data-merch]').forEach(el=>{
      const c = db.cards[el.dataset.merch];
      if(!c) return;
      const pr = el.querySelector('[data-promo]'); if(pr && c.promo) pr.textContent = c.promo;
      const p = el.querySelector('[data-price]'); if(p) p.textContent = c.price;
      const b = el.querySelector('[data-cta]'); if(b) b.textContent = c.cta;
    });
  }catch(e){ /* offline file:// → keep hardcoded fallback text */ }
}
// Adobe loads header/footer as fragments; we keep them inline (faster for learning).
// Promote to fragments only when header is shared across 2+ pages:
//   fetch('fragments/header.html').then(r=>r.text()).then(h=>document.getElementById('top').innerHTML=h);
document.addEventListener('DOMContentLoaded', loadMerch);

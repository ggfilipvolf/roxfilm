/* Roxfilm — interakce webu */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const range = (v, a, b) => clamp((v - a) / (b - a));
  const ease = t => 1 - Math.pow(1 - t, 3);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const touch = matchMedia('(hover: none)').matches;
  let VH = innerHeight;
  addEventListener('resize', () => { VH = innerHeight; });

  /* ---------- plynulý scroll ---------- */
  let lenis = null;
  if (!reduce && window.Lenis) {
    lenis = new Lenis({ lerp: 0.11, smoothWheel: true, wheelMultiplier: 1 });
  }
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href*="#"]');
    if (!a) return;
    const url = new URL(a.href, location.href);
    if (url.pathname !== location.pathname || !url.hash) return;
    const t = url.hash === '#top' ? 0 : $(url.hash);
    if (t === null) return;
    e.preventDefault();
    if (lenis) lenis.scrollTo(t, { duration: 1.6 });
    else (t === 0 ? scrollTo({ top: 0, behavior: 'smooth' }) : t.scrollIntoView({ behavior: 'smooth' }));
  });

  /* ---------- navigace ---------- */
  const nav = $('.nav');
  const hero = $('.hero');
  let lastY = 0;
  function navState(y) {
    const heroEnd = hero ? hero.offsetTop + hero.offsetHeight - VH : 40;
    nav.classList.toggle('is-solid', y > (hero ? heroEnd - 10 : 40));
    const hide = y > lastY + 1 && y > (hero ? heroEnd + 300 : 400) && !nav.classList.contains('is-open');
    if (Math.abs(y - lastY) > 1) nav.classList.toggle('is-hidden', hide);
    lastY = y;
  }
  const toggle = $('.nav__toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open);
      if (lenis) open ? lenis.stop() : lenis.start();
    });
    $$('.nav__links a').forEach(a => a.addEventListener('click', () => {
      nav.classList.remove('is-open'); toggle.setAttribute('aria-expanded', false); if (lenis) lenis.start();
    }));
  }

  /* ---------- HERO: RED Komodo-X, scroll a pohyb myši ---------- */
  let heroTick = () => {};
  if (hero) {
    const canvas = $('.hero__canvas', hero);
    const ctx = canvas.getContext('2d');
    const cam = $('.hero__cam', hero);
    const small = innerWidth < 760;
    const N = small ? +hero.dataset.framesM : +hero.dataset.framesD;
    const base = small ? hero.dataset.pathM : hero.dataset.pathD;
    const frames = new Array(N);
    // ostré snímky pro velké a retina obrazovky (načítají se až po rychlé sadě)
    const NH = +hero.dataset.framesH || 0, baseH = hero.dataset.pathH;
    const wantHD = !small && NH === N && innerWidth * Math.min(devicePixelRatio || 1, 2) > 1700;
    const hd = new Array(N);
    let drawn = null, target = 0, cur = 0;
    const src = i => `${base}${String(i + 1).padStart(3, '0')}.webp`;
    const srcH = i => `${baseH}${String(i + 1).padStart(3, '0')}.webp`;
    function load(i) {
      if (frames[i] !== undefined) return;
      frames[i] = null;
      const im = new Image();
      im.onload = () => { frames[i] = im; if (!drawn) draw(Math.round(cur), true); };
      im.src = src(i);
    }
    function loadH(i) {
      if (hd[i] !== undefined) return;
      hd[i] = null;
      const im = new Image();
      im.onload = () => { hd[i] = im; if (Math.abs(i - Math.round(cur)) < 2) draw(Math.round(cur), true); };
      im.src = srcH(i);
    }
    const order = [];
    [16, 8, 4, 2, 1].forEach(st => { for (let i = 0; i < N; i += st) if (!order.includes(i)) order.push(i); });
    let qi = 0, hi = 0;
    function pump() {
      for (let k = 0; k < 8 && qi < order.length; k++) load(order[qi++]);
      if (qi < order.length) return setTimeout(pump, 30);
      if (wantHD) pumpH();
    }
    function pumpH() {
      // nejdřív snímky kolem aktuální pozice, pak zbytek
      const c = Math.round(cur);
      let best = -1, bd = 1e9;
      for (let i = 0; i < N; i++) if (hd[i] === undefined) { const d = Math.abs(i - c); if (d < bd) { bd = d; best = i; } }
      if (best < 0) return;
      for (let k = 0; k < 4; k++) { const i = best + k; if (i < N) loadH(i); }
      setTimeout(pumpH, 60);
    }
    load(0); pump();

    function nearest(i) {
      if (hd[i]) return hd[i];
      if (frames[i]) return frames[i];
      for (let d = 1; d < N; d++) {
        if (hd[i - d] && d < 2) return hd[i - d];
        if (frames[i - d]) return frames[i - d];
        if (frames[i + d]) return frames[i + d];
      }
      return null;
    }
    function size() {
      const dpr = Math.min(devicePixelRatio || 1, 2);
      canvas.width = Math.round(cam.clientWidth * dpr);
      canvas.height = Math.round(cam.clientHeight * dpr);
      ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
      drawn = null; draw(Math.round(cur), true);
    }
    function draw(i, force) {
      const im = nearest(i);
      if (!im) return;
      if (!force && im === drawn) return;
      drawn = im;
      const cw = canvas.width, ch = canvas.height;
      const s = Math.max(cw / im.naturalWidth, ch / im.naturalHeight);
      const w = im.naturalWidth * s, h = im.naturalHeight * s;
      ctx.fillStyle = '#000'; ctx.fillRect(0, 0, cw, ch);
      ctx.drawImage(im, (cw - w) / 2, (ch - h) / 2, w, h);
      hero.classList.add('is-ready');
    }
    addEventListener('resize', size);
    addEventListener('load', size);
    if ('ResizeObserver' in window) new ResizeObserver(size).observe(cam);
    size();

    // jemné natočení kamery za myší – scéna reaguje
    let mx = 0, my = 0, tx = 0, ty = 0;
    if (!touch) hero.addEventListener('pointermove', e => { mx = e.clientX / innerWidth - 0.5; my = e.clientY / innerHeight - 0.5; });

    const copy = $('.hero__copy', hero), hint = $('.scrollhint', hero);
    const focus = $('.focus', hero), fmL = $('.fm--l', hero), fmR = $('.fm--r', hero);
    const reel = $('.hero__reel', hero), reelV = $('video', reel);
    const end = $('.hero__end', hero), tc = $('.tc', hero);
    let reelLoaded = false;
    const xc = $('.hero__xc', hero), xctx = xc.getContext('2d');
    const reelPoster = new Image(); reelPoster.src = reelV.getAttribute('poster');
    if (small && reelV.dataset.srcM) reelV.dataset.src = reelV.dataset.srcM;

    heroTick = y => {
      const total = hero.offsetHeight - VH;
      const p = clamp((y - hero.offsetTop) / total);
      if (y > hero.offsetTop + hero.offsetHeight) return;
      const fp = clamp(p / 0.78);
      target = fp * (N - 1);
      cur += (target - cur) * 0.22;
      if (Math.abs(target - cur) < 0.05) cur = target;
      draw(Math.round(cur));

      tx += (mx - tx) * 0.06; ty += (my - ty) * 0.06;
      const k = 1 - range(p, 0.55, 0.8);
      cam.style.transform = `translate3d(${-tx * 22 * k}px,${-ty * 14 * k}px,0) rotateY(${tx * 2.2 * k}deg) rotateX(${-ty * 1.6 * k}deg)`;

      const f24 = Math.round(fp * 192), ss = Math.floor(f24 / 24), ff = f24 % 24;
      if (tc) tc.textContent = `00:00:${String(ss).padStart(2, '0')}:${String(ff).padStart(2, '0')}`;
      hero.classList.toggle('is-rec', fp > 0.1);

      const o1 = 1 - range(p, 0.02, 0.09);
      copy.style.opacity = o1; copy.style.transform = `translate3d(0,${(1 - o1) * -24}px,0)`;
      if (hint) hint.style.opacity = o1;

      // dvě poloviny X z loga se sjedou, spojí se v logo a X vyroste do showreelu
      const csL = getComputedStyle(fmL), csR = getComputedStyle(fmR);
      const wL = parseFloat(csL.width), wR = parseFloat(csR.width);
      const leftL = parseFloat(csL.left), leftR = innerWidth - parseFloat(csR.right) - wR;
      const s0 = wL / 144;                              // px na jednotku loga
      const cx = innerWidth / 2, cy = VH / 2;
      const t = ease(range(p, 0.28, 0.56));
      const joinL = cx - 151 * s0;                      // (144 + 158) / 2 = 151 → střed mezery mezi hroty
      const joinR = joinL + 158 * s0;
      fmL.style.transform = `translate3d(${((joinL - leftL) * t).toFixed(1)}px,-50%,0)`;
      fmR.style.transform = `translate3d(${((joinR - leftR) * t).toFixed(1)}px,-50%,0)`;
      focus.style.opacity = Math.min(range(p, 0.24, 0.3), 1 - range(p, 0.6, 0.64));

      if (p > 0.12 && !reelLoaded) { reelV.src = reelV.dataset.src; reelV.load(); reelLoaded = true; }
      const g = range(p, 0.62, 0.92);
      const ge = g * g * (3 - 2 * g);
      const sF = Math.max(innerWidth / 38, VH / 200);   // měřítko, kdy X pokryje celou obrazovku
      const sc = s0 * Math.pow(sF / s0, ge);
      const ox = 158 - 57 * ge;                         // poloviny do sebe zaklesnou, ať střed zůstane plný
      const vis = range(p, 0.58, 0.62);
      const showFull = g >= 1;
      // celé video až po přechodu: kamera se schová, pod ní běží showreel
      cam.style.visibility = showFull ? 'hidden' : '';
      if (vis > 0.01) { if (reelV.paused) reelV.play().catch(() => {}); }
      else if (!reelV.paused) reelV.pause();
      // X přechod kreslíme do vlastního plátna (spolehlivé v Safari i na iPhonu)
      if (vis > 0.001 && !showFull) {
        const dpr = Math.min(devicePixelRatio || 1, 1.5);
        const W = Math.round(innerWidth * dpr), Hh = Math.round(VH * dpr);
        if (xc.width !== W || xc.height !== Hh) { xc.width = W; xc.height = Hh; }
        xctx.clearRect(0, 0, W, Hh);
        const srcEl = reelV.readyState >= 2 ? reelV : (reelPoster.complete && reelPoster.naturalWidth ? reelPoster : null);
        const x0 = (cx - ((144 + ox) / 2) * sc) * dpr, y0 = (cy - 124 * sc) * dpr, k = sc * dpr;
        const path = new Path2D();
        const add = pts => { pts.forEach(([x, y], j) => j ? path.lineTo(x0 + x * k, y0 + y * k) : path.moveTo(x0 + x * k, y0 + y * k)); path.closePath(); };
        add([[0,0],[123,0],[144,124],[123,248],[0,248],[100,124]]);
        add([[ox+22,0],[ox+139,0],[ox+42,124],[ox+139,248],[ox+22,248],[ox,124]]);
        xctx.save(); xctx.globalAlpha = vis; xctx.clip(path);
        if (srcEl) {
          const iw = srcEl.videoWidth || srcEl.naturalWidth, ih = srcEl.videoHeight || srcEl.naturalHeight;
          const f = Math.max(W / iw, Hh / ih), w = iw * f, h = ih * f;
          xctx.drawImage(srcEl, (W - w) / 2, (Hh - h) / 2, w, h);
        } else { xctx.fillStyle = '#F2F0EB'; xctx.fillRect(0, 0, W, Hh); }
        xctx.restore();
        xc.style.visibility = 'visible';
      } else if (xc.style.visibility !== 'hidden') { xctx.clearRect(0, 0, xc.width, xc.height); xc.style.visibility = 'hidden'; }
      const eo = range(p, 0.9, 0.98);
      end.style.opacity = eo; end.classList.toggle('is-on', eo > 0.5);
    };
  }

  /* ---------- spolupráce: slova se rozsvěcí podle scrollu ---------- */
  const statements = $$('.statement').map(sec => {
    const text = $('.statement__text', sec);
    const words = text.textContent.trim().split(/\s+/);
    text.innerHTML = words.map(w => `<span class="w">${w}</span>`).join(' ');
    return { sec, ws: $$('.w', text) };
  });
  function statementTick() {
    statements.forEach(({ sec, ws }) => {
      const r = sec.getBoundingClientRect();
      if (r.bottom < 0 || r.top > VH) return;
      const p = clamp(-r.top / (r.height - VH));
      const bg = sec._bg || (sec._bg = $('.statement__bg', sec)), img = sec._img || (sec._img = $('.statement__bg img', sec));
      const sh = sec._sh || (sec._sh = $('.statement__shade', sec)), cp = sec._cp || (sec._cp = $('.statement__copy', sec));
      // fotka podání ruky se rozevře za textem
      const o = ease(range(p, 0, 0.42));
      const ins = `inset(${((1 - o) * 18).toFixed(2)}% ${((1 - o) * 22).toFixed(2)}%)`;
      if (bg) { bg.style.clipPath = ins; bg.style.webkitClipPath = ins; }
      if (img) img.style.transform = `scale(${(1.18 - 0.18 * o).toFixed(4)}) translate3d(0,${((p - 0.5) * -4).toFixed(2)}%,0)`;
      if (sh) sh.style.opacity = range(p, 0.12, 0.4).toFixed(3);
      // text plyne jinou rychlostí než fotka
      if (cp) cp.style.transform = `translate3d(0,${((1 - p) * VH * 0.22).toFixed(1)}px,0)`;
      const lit = Math.round(range(p, 0.28, 0.72) * ws.length);
      ws.forEach((w, i) => w.classList.toggle('on', i < lit));
      sec.classList.toggle('is-done', p > 0.74);
    });
  }

  /* ---------- fotka, která se rozevře ---------- */
  const reveals = $$('.reveal-photo__frame');
  function revealTick() {
    reveals.forEach(f => {
      const r = f.getBoundingClientRect();
      if (r.bottom < 0 || r.top > VH) return;
      const t = ease(range(VH - r.top, 0, VH * 0.85));
      const ins = `inset(0 ${(1 - t) * 9}%)`;
      f.style.clipPath = ins; f.style.webkitClipPath = ins;
      f.firstElementChild.style.transform = `scale(${1.12 - 0.12 * t})`;
    });
  }

  /* ---------- parallax ---------- */
  const pxs = reduce ? [] : $$('.px').map(el => ({ el, in: $('.px__in', el), sp: +(el.dataset.speed || 0.07) })).filter(o => o.in);
  function pxTick() {
    for (const o of pxs) {
      const r = o.el.getBoundingClientRect();
      if (r.bottom < -50 || r.top > VH + 50) continue;
      const prog = (r.top + r.height / 2 - VH / 2) / (VH / 2 + r.height / 2);
      o.in.style.transform = `translate3d(0,${(-prog * o.sp * r.height).toFixed(1)}px,0)`;
    }
  }

  /* ---------- nekonečné pásy (loga, fotky) – každá položka se posouvá zvlášť, žádná obří vrstva ---------- */
  $$('.marquee').forEach(mq => {
    const tr = $('.marquee__track', mq);
    const photos = mq.classList.contains('marquee--photos');
    const speed = photos ? 40 : 44;              // px za sekundu
    const gap = photos ? 12 : Math.max(48, Math.min(96, innerWidth * 0.06));
    let items = [], total = 0, offset = 0, last = 0, hover = false, vis = false;
    const base = [...tr.children];
    function measure() {
      // doplň kopie, dokud pás není aspoň o šířku obrazovky delší
      items = [...tr.children];
      let w = items.reduce((s, li) => s + li.getBoundingClientRect().width + gap, 0);
      let guard = 0;
      while (w > 0 && w < mq.clientWidth * 2 + 400 && guard++ < 6) {
        base.forEach(li => { const c = li.cloneNode(true); c.setAttribute('aria-hidden', 'true'); c.querySelectorAll('button').forEach(b => b.tabIndex = -1); tr.appendChild(c); });
        items = [...tr.children];
        w = items.reduce((s, li) => s + li.getBoundingClientRect().width + gap, 0);
      }
      let x = 0;
      items.forEach(li => { li._x = x; li._w = li.getBoundingClientRect().width; x += li._w + gap; });
      total = x;
    }
    function tick(t) {
      const dt = last ? Math.min(64, t - last) : 16; last = t;
      if (vis && !(photos && hover) && total) {
        offset = (offset + speed * dt / 1000) % total;
        for (const li of items) {
          let x = li._x - offset; if (x < -li._w - gap) x += total;
          li.style.transform = `translate3d(${x.toFixed(2)}px,-50%,0)`;
        }
      }
      requestAnimationFrame(tick);
    }
    mq.addEventListener('mouseenter', () => hover = true);
    mq.addEventListener('mouseleave', () => hover = false);
    new IntersectionObserver(es => { vis = es[0].isIntersecting; }, { rootMargin: '200px' }).observe(mq);
    const imgs = $$('img', tr);
    Promise.all(imgs.map(im => im.complete ? 0 : new Promise(r => { im.onload = im.onerror = r; }))).then(() => { measure(); vis = true; });
    addEventListener('resize', () => { measure(); });
    requestAnimationFrame(tick);
  });

  /* ---------- fotka přes celou obrazovku ---------- */
  const lb = document.createElement('div');
  lb.className = 'lightbox'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true');
  lb.innerHTML = '<img alt="">';
  document.body.appendChild(lb);
  const lbImg = $('img', lb);
  document.addEventListener('click', e => {
    const z = e.target.closest('.zoom'); if (!z) return;
    lbImg.src = z.dataset.img; lbImg.alt = z.getAttribute('aria-label') || '';
    lb.classList.add('is-open'); if (lenis) lenis.stop();
  });
  const lbClose = () => { lb.classList.remove('is-open'); if (lenis) lenis.start(); };
  lb.addEventListener('click', lbClose);
  addEventListener('keydown', e => { if (e.key === 'Escape' && lb.classList.contains('is-open')) lbClose(); });

  /* ---------- reveal ---------- */
  if ('IntersectionObserver' in window) {
    const rio = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('is-in'); rio.unobserve(e.target); }
    }), { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    $$('[data-reveal]').forEach(el => rio.observe(el));
  } else document.documentElement.classList.add('js-off');

  /* ---------- hlavní smyčka ---------- */
  function frame(time) {
    if (lenis) lenis.raf(time);
    const y = lenis ? lenis.scroll : scrollY;
    heroTick(y); navState(y); statementTick(); revealTick(); pxTick();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  /* ---------- náhledová videa ---------- */
  function ensure(vp) {
    let v = $('video', vp);
    if (!v) {
      v = document.createElement('video');
      // Safari: atributy muted/playsinline/autoplay musí být na místě dřív než src
      v.muted = true; v.defaultMuted = true; v.loop = true; v.playsInline = true;
      v.setAttribute('muted', ''); v.setAttribute('playsinline', ''); v.setAttribute('webkit-playsinline', '');
      v.preload = 'auto';
      vp.appendChild(v);
      v.src = vp.dataset.prev;
      v.addEventListener('playing', () => { vp._playT = performance.now(); vp.classList.add('is-playing'); });
    }
    return v;
  }
  // spustí video a když ho prohlížeč napoprvé odmítne, zkusí to znovu, jakmile má data
  function kickPlay(v, ok) {
    let tries = 0;
    const go = () => {
      if (!ok() || !v.paused) return;
      if (v.networkState === 0) v.load();
      const pr = v.play(); if (pr) pr.catch(() => {});
    };
    go();
    ['loadedmetadata', 'loadeddata', 'canplay', 'canplaythrough'].forEach(ev => v.addEventListener(ev, go, { once: true }));
    const t = setInterval(() => { if (!ok() || !v.paused || ++tries > 12) return clearInterval(t); go(); }, 350);
  }
  function play(vp) { const v = ensure(vp); vp._want = true; if (!v.paused) vp.classList.add('is-playing'); kickPlay(v, () => vp._want); }
  function stop(vp) { vp._want = false; const v = $('video', vp); if (v) v.pause(); vp.classList.remove('is-playing'); }
  const io = new IntersectionObserver(es => es.forEach(e => {
    const vp = e.target, mode = vp.dataset.mode || 'view';
    if (mode === 'deck') return;
    if (mode === 'hover' && !touch) { if (!e.isIntersecting) stop(vp); return; }
    e.isIntersecting ? play(vp) : stop(vp);
  }), { threshold: 0.3 });
  $$('.vp[data-prev]').forEach(vp => {
    io.observe(vp);
    if ((vp.dataset.mode || 'view') === 'hover' && !touch) {
      const host = vp.closest('.item, .reel') || vp;
      host.addEventListener('mouseenter', () => play(vp));
      host.addEventListener('mouseleave', () => stop(vp));
      host.addEventListener('focus', () => play(vp));
      host.addEventListener('blur', () => stop(vp));
    }
  });

  /* ---------- deck: karusel (fyzika jako na iPhonu: táhnutí, trackpad, šipky, sám se točí) ---------- */
  $$('[data-deck]').forEach(deck => {
    const stage = $('.deck__stage', deck);
    const cards = $$('.deck__card', deck);
    const count = $('.deck__count b', deck), label = $('.deck__label', deck);
    const n = cards.length;
    const mod = i => ((i % n) + n) % n;
    let pos = 0, tpos = 0, inView = false, hover = false, lastTouch = 0, settled = -1, shown = -1, running = false;
    let cw = 300;
    const measure = () => { cw = cards[0].offsetWidth || 300; };
    const vis = cards.map(() => true);
    function layout() {
      const gap = cw * (innerWidth < 700 ? 0.8 : 0.9);
      for (let i = 0; i < n; i++) {
        let o = i - pos; o = o - n * Math.round(o / n);
        const a = Math.abs(o), c = cards[i];
        if (a > 3.6) { if (vis[i]) { c.style.visibility = 'hidden'; vis[i] = false; } continue; }
        if (!vis[i]) { c.style.visibility = ''; vis[i] = true; }
        const s = 1 - Math.min(a, 3) * 0.12;
        const x = o * gap - Math.sign(o) * Math.max(0, a - 1) * gap * 0.3;
        c.style.transform = `translate(-50%,-50%) translate3d(${x.toFixed(1)}px,0,0) rotateY(${(clamp(o, -3, 3) * -8).toFixed(2)}deg) scale(${s.toFixed(4)})`;
        c.style.zIndex = String(100 - Math.round(a * 10));
        c.style.setProperty('--dim', (Math.min(a, 2.5) * 0.26).toFixed(3));
      }
    }
    // videa: hraje jen karta uprostřed, sousedé se jen přednačtou
    function playActive(i) {
      cards.forEach((c, k) => {
        const vp = $('.vp', c); if (!vp) return;
        const d = Math.min(Math.abs(k - i), n - Math.abs(k - i));
        if (k === i && inView) {
          const v = ensure(vp); vp._want = true;
          if (!v.paused) vp.classList.add('is-playing');
          kickPlay(v, () => vp._want && settled === k && inView);
        } else {
          stop(vp);
          // sousedé se načtou dopředu, ať se po příjezdu rozjedou hned
          if (d <= 2) { const v = ensure(vp); if (v.readyState < 2 && v.networkState !== 2) v.load(); }
        }
        c.classList.toggle('is-active', k === i);
        c.tabIndex = k === i ? 0 : -1;
      });
    }
    function setLabel(i) {
      if (i === shown) return; shown = i;
      count.textContent = String(i + 1).padStart(2, '0');
      label.textContent = cards[i].dataset.label || '';
    }
    let dragging = false, wheeling = false, idleT = 0, lastT = 0, playingSince = 0;
    function loop(now) {
      const dt = Math.min(64, lastT ? now - lastT : 16); lastT = now;
      // dojezd nezávislý na snímkové frekvenci (60 i 120 Hz se chová stejně)
      const k = 1 - Math.pow(dragging ? 1e-9 : 2e-4, dt / 1000);
      pos += (tpos - pos) * k;
      if (Math.abs(tpos - pos) < 0.01) pos = tpos;
      layout();
      const act = mod(Math.round(pos));
      setLabel(act);
      // video se pouští už při dojíždění, ne až v úplném klidu
      const near = Math.abs(tpos - pos) < 0.3 && !dragging && !wheeling && Math.round(tpos) === Math.round(pos);
      if (near) { if (settled !== act) { settled = act; playingSince = performance.now(); playActive(act); } }
      else if (settled !== -1) { settled = -1; cards.forEach(c => c.classList.remove('is-active')); }
      if (pos === tpos && !dragging && !wheeling) { running = false; lastT = 0; return; }
      requestAnimationFrame(loop);
    }
    function kick() { if (!running) { running = true; requestAnimationFrame(loop); } }
    function to(t) { tpos = t; kick(); }
    const poke = () => { lastTouch = performance.now(); };
    $('.deck__prev', deck).addEventListener('click', () => { poke(); to(Math.round(tpos) - 1); });
    $('.deck__next', deck).addEventListener('click', () => { poke(); to(Math.round(tpos) + 1); });
    deck.addEventListener('keydown', e => {
      if (e.key === 'ArrowLeft') { e.preventDefault(); poke(); to(Math.round(tpos) - 1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); poke(); to(Math.round(tpos) + 1); }
    });
    deck.addEventListener('mouseenter', () => hover = true);
    deck.addEventListener('mouseleave', () => hover = false);

    // tažení myší i prstem, se setrvačností
    let down = false, sx = 0, sy = 0, moved = false, horiz = null, start = 0, lx = 0, lt = 0, vel = 0;
    stage.addEventListener('pointerdown', e => { down = true; moved = false; horiz = null; sx = lx = e.clientX; sy = e.clientY; lt = performance.now(); vel = 0; start = tpos; poke(); });
    addEventListener('pointermove', e => {
      if (!down) return;
      const dx = e.clientX - sx, dy = e.clientY - sy;
      if (horiz === null && (Math.abs(dx) > 6 || Math.abs(dy) > 6)) horiz = Math.abs(dx) > Math.abs(dy);
      if (!horiz) return;
      moved = true; dragging = true; deck.classList.add('is-drag');
      const now = performance.now(), dt = Math.max(1, now - lt);
      vel = 0.8 * vel + 0.2 * ((e.clientX - lx) / dt); lx = e.clientX; lt = now;
      tpos = start - dx / (cw * 0.9); kick();
    }, { passive: true });
    addEventListener('pointerup', () => {
      if (!down) return; down = false; dragging = false; deck.classList.remove('is-drag');
      if (moved) { const fling = -vel * 0.35; to(Math.round(tpos + clamp(fling, -6, 6))); }
    });
    stage.addEventListener('click', e => {
      const c = e.target.closest('.deck__card'); if (!c) return;
      if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; return; }
      const i = cards.indexOf(c), act = mod(Math.round(tpos));
      if (i !== act) {
        e.preventDefault(); e.stopPropagation(); poke();
        let d = i - act; d = d - n * Math.round(d / n); to(Math.round(tpos) + d);
      }
    }, true);

    // dva prsty na trackpadu do strany
    deck.addEventListener('wheel', e => {
      const dx = e.deltaX, dy = e.deltaY;
      if (Math.abs(dx) <= Math.abs(dy) || Math.abs(dx) < 1) return;
      e.preventDefault(); e.stopPropagation(); poke();
      wheeling = true;
      tpos += dx / (cw * 1.15);
      kick();
      clearTimeout(idleT);
      idleT = setTimeout(() => { wheeling = false; to(Math.round(tpos)); }, 120);
    }, { passive: false });

    // sám se pomalu točí, když se na něj díváte a nesaháte na něj
    setInterval(() => {
      if (!inView || hover || down || wheeling || document.hidden || reduce) return;
      if (performance.now() - lastTouch < 8000) return;
      // posune se dál, až když aktivní video opravdu chvíli hrálo (nebo se nenačte ani po 9 s)
      const vp = settled >= 0 ? $('.vp', cards[settled]) : null, v = vp && $('video', vp);
      const now = performance.now(), t = now - playingSince;
      const ran = v && !v.paused && now - Math.max(playingSince, vp._playT || 0) > 4000;
      if (v ? !(ran || t > 9000) : t < 4200) return;
      to(Math.round(tpos) + 1);
    }, 500);

    new IntersectionObserver(es => {
      inView = es[0].isIntersecting;
      settled = -1;
      if (inView) kick(); else cards.forEach(c => { const vp = $('.vp', c); if (vp) stop(vp); });
    }, { threshold: 0.2 }).observe(deck);
    addEventListener('resize', () => { measure(); layout(); });
    measure(); layout(); kick();
  });

  /* ---------- přehrávač ---------- */
  const player = $('.player');
  if (player) {
    const pv = $('video', player), title = $('.player__top b', player);
    let lastFocus = null;
    function open(btn) {
      lastFocus = btn;
      pv.src = btn.dataset.full;
      if (btn.dataset.poster) pv.poster = btn.dataset.poster;
      title.textContent = btn.dataset.title || '';
      player.classList.toggle('is-vertical', btn.dataset.vertical === '1');
      player.classList.add('is-open');
      if (lenis) lenis.stop();
      pv.play().catch(() => {});
      $('.player__close', player).focus();
    }
    function close() {
      player.classList.remove('is-open'); pv.pause(); pv.removeAttribute('src'); pv.load();
      if (lenis) lenis.start();
      if (lastFocus) lastFocus.focus({ preventScroll: true });
    }
    document.addEventListener('click', e => {
      const b = e.target.closest('[data-full]');
      if (b) { e.preventDefault(); open(b); }
    });
    $('.player__close', player).addEventListener('click', close);
    player.addEventListener('click', e => { if (e.target === player) close(); });
    addEventListener('keydown', e => { if (e.key === 'Escape' && player.classList.contains('is-open')) close(); });
  }

  /* ---------- filtr portfolia ---------- */
  $$('.filters').forEach(f => {
    const items = $$('.grid .item');
    f.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      $$('button', f).forEach(x => x.setAttribute('aria-pressed', x === b));
      const cat = b.dataset.cat;
      items.forEach(it => { it.hidden = cat !== 'all' && !it.dataset.cat.split(' ').includes(cat); });
      if (lenis) lenis.resize();
    });
  });

  $$('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
})();

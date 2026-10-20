/* Roxfilm — interakce webu */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const range = (v, a, b) => clamp((v - a) / (b - a));
  const ease = t => 1 - Math.pow(1 - t, 3);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const touch = matchMedia('(hover: none)').matches;

  /* ---------- navigace ---------- */
  const nav = $('.nav');
  const hero = $('.hero');
  let lastY = 0;
  function navState() {
    const y = scrollY;
    const heroEnd = hero ? hero.offsetTop + hero.offsetHeight - innerHeight : 40;
    nav.classList.toggle('is-solid', y > (hero ? heroEnd - 10 : 40));
    const hide = y > lastY && y > (hero ? heroEnd + 200 : 400) && !nav.classList.contains('is-open');
    nav.classList.toggle('is-hidden', hide);
    lastY = y;
  }
  const toggle = $('.nav__toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
    $$('.nav__links a').forEach(a => a.addEventListener('click', () => {
      nav.classList.remove('is-open'); toggle.setAttribute('aria-expanded', false); document.body.style.overflow = '';
    }));
  }

  /* ---------- HERO: scroll kamera RED Komodo-X ---------- */
  let heroTick = () => {};
  if (hero && !reduce) {
    const canvas = $('.hero__canvas', hero);
    const ctx = canvas.getContext('2d');
    const small = innerWidth < 760;
    const N = small ? +hero.dataset.framesM : +hero.dataset.framesD;
    const base = small ? hero.dataset.pathM : hero.dataset.pathD;
    const frames = new Array(N);
    let current = -1, wanted = 0;
    const src = i => `${base}${String(i + 1).padStart(3, '0')}.webp`;
    function load(i) {
      if (frames[i]) return;
      const im = new Image();
      im.decoding = 'async';
      im.onload = () => { frames[i] = im; if (Math.abs(i - wanted) < 3 || current < 0) draw(wanted); };
      im.src = src(i);
      frames[i] = null;
    }
    // nejdřív kostra (každý 16. snímek), pak zhušťujeme
    const order = [];
    [16, 8, 4, 2, 1].forEach(st => { for (let i = 0; i < N; i += st) if (!order.includes(i)) order.push(i); });
    let qi = 0;
    function pump(n = 6) { for (let k = 0; k < n && qi < order.length; k++) load(order[qi++]); if (qi < order.length) setTimeout(() => pump(6), 40); }
    load(0); pump();

    function nearest(i) {
      if (frames[i]) return frames[i];
      for (let d = 1; d < N; d++) {
        if (frames[i - d]) return frames[i - d];
        if (frames[i + d]) return frames[i + d];
      }
      return null;
    }
    function size() {
      const dpr = Math.min(devicePixelRatio || 1, 2);
      canvas.width = Math.round(innerWidth * dpr);
      canvas.height = Math.round(innerHeight * dpr);
      current = -1; draw(wanted);
    }
    function draw(i) {
      const im = nearest(i);
      if (!im) return;
      const key = i + (im === frames[i] ? 0 : 0.5);
      if (key === current) return;
      current = key;
      const cw = canvas.width, ch = canvas.height;
      const s = Math.max(cw / im.naturalWidth, ch / im.naturalHeight) * (small ? 1.04 : 1);
      const w = im.naturalWidth * s, h = im.naturalHeight * s;
      ctx.fillStyle = '#000'; ctx.fillRect(0, 0, cw, ch);
      ctx.drawImage(im, (cw - w) / 2 + (small ? cw * 0.12 : 0), (ch - h) / 2, w, h);
    }
    addEventListener('resize', size);
    size();

    const copy = $('.hero__copy', hero), hint = $('.scrollhint', hero);
    const focus = $('.focus', hero), line = $('.focus__line', hero);
    const fmL = $('.fm--l', hero), fmR = $('.fm--r', hero);
    const reel = $('.hero__reel', hero), reelV = $('video', reel);
    const end = $('.hero__end', hero), tc = $('.tc', hero);
    let reelLoaded = false;

    heroTick = () => {
      const total = hero.offsetHeight - innerHeight;
      const p = clamp((scrollY - hero.offsetTop) / total);
      if (p <= 0 && current >= 0 && wanted === 0) {}
      const fp = clamp(p / 0.8);
      wanted = Math.round(fp * (N - 1));
      draw(wanted);

      // timecode a REC
      const f24 = Math.round(fp * 192);
      const ss = Math.floor(f24 / 24), ff = f24 % 24;
      if (tc) tc.textContent = `00:00:${String(ss).padStart(2, '0')}:${String(ff).padStart(2, '0')}`;
      hero.classList.toggle('is-rec', fp > 0.13);

      // úvodní text
      const o1 = 1 - range(p, 0.05, 0.13);
      copy.style.opacity = o1; copy.style.transform = `translateY(${(1 - o1) * -30}px)`;
      if (hint) hint.style.opacity = o1;

      // značky ostření míří na řádek „Zaostřeno na výsledek.“
      const fin = range(p, 0.26, 0.32), fout = 1 - range(p, 0.6, 0.68);
      focus.style.opacity = Math.min(fin, fout);
      const t = ease(range(p, 0.28, 0.5));
      const lr = line.getBoundingClientRect();
      const mw = fmL.getBoundingClientRect().width;
      const gap = innerWidth < 700 ? 6 : 26;
      const lText = lr.left + parseFloat(getComputedStyle(line).paddingLeft);
      const rText = lr.right - parseFloat(getComputedStyle(line).paddingRight);
      const startL = parseFloat(getComputedStyle(fmL).left);
      const targetL = Math.max(startL, lText - mw - gap);
      const targetR = Math.min(innerWidth - startL - mw, rText + gap);
      fmL.style.transform = `translate(${(targetL - startL) * t}px,-50%)`;
      fmR.style.transform = `translate(${(targetR - (innerWidth - startL - mw)) * t}px,-50%)`;
      line.style.filter = `blur(${(1 - ease(range(p, 0.34, 0.5))) * 14}px)`;

      // za objektivem začíná showreel
      if (p > 0.6 && !reelLoaded) { reelV.src = reelV.dataset.src; reelV.load(); reelLoaded = true; }
      const ir = ease(range(p, 0.79, 0.95));
      reel.style.clipPath = `circle(${ir * 78}% at 50% 50%)`;
      if (ir > 0.01) { if (reelV.paused) reelV.play().catch(() => {}); }
      else if (!reelV.paused) reelV.pause();
      const eo = range(p, 0.92, 0.99);
      end.style.opacity = eo; end.classList.toggle('is-on', eo > 0.5);
    };
  } else if (hero) {
    $('.hero__poster', hero).src = $('.hero__poster', hero).dataset.src;
    const end = $('.hero__end', hero); end.style.opacity = 1; end.classList.add('is-on');
    $('.hero__copy', hero).style.display = 'none';
  }

  let ticking = false;
  function onScroll() {
    if (ticking) return; ticking = true;
    requestAnimationFrame(() => { heroTick(); navState(); ticking = false; });
  }
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll);
  onScroll();

  /* ---------- náhledová videa ---------- */
  const vps = $$('.vp[data-prev]');
  function ensure(vp) {
    let v = $('video', vp);
    if (!v) {
      v = document.createElement('video');
      v.muted = true; v.loop = true; v.playsInline = true; v.setAttribute('playsinline', ''); v.preload = 'none';
      v.src = vp.dataset.prev;
      vp.appendChild(v);
    }
    return v;
  }
  function play(vp) { const v = ensure(vp); const pr = v.play(); vp.classList.add('is-playing'); if (pr) pr.catch(() => vp.classList.remove('is-playing')); }
  function stop(vp) { const v = $('video', vp); if (v) v.pause(); vp.classList.remove('is-playing'); }
  if (!reduce) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      const vp = e.target;
      const mode = vp.dataset.mode || 'view';
      if (mode === 'deck') return;
      if (mode === 'hover' && !touch) { if (!e.isIntersecting) stop(vp); return; }
      if (e.isIntersecting) play(vp); else stop(vp);
    }), { threshold: 0.45 });
    vps.forEach(vp => {
      io.observe(vp);
      if ((vp.dataset.mode || 'view') === 'hover' && !touch) {
        const host = vp.closest('.item, .reel') || vp;
        host.addEventListener('mouseenter', () => play(vp));
        host.addEventListener('mouseleave', () => stop(vp));
        host.addEventListener('focus', () => play(vp));
        host.addEventListener('blur', () => stop(vp));
      }
    });
  }

  /* ---------- deck: swipovací karusel ---------- */
  $$('[data-deck]').forEach(deck => {
    const stage = $('.deck__stage', deck);
    const cards = $$('.deck__card', deck);
    const count = $('.deck__count b', deck), label = $('.deck__label', deck);
    const n = cards.length;
    let active = 0, drag = 0, inView = false;
    function layout() {
      const w = cards[0].getBoundingClientRect().width || 300;
      const gap = w * (innerWidth < 700 ? 0.78 : 0.86);
      cards.forEach((c, i) => {
        let o = i - active - drag;
        const a = Math.abs(o);
        const s = 1 - Math.min(a, 3) * 0.13;
        const x = o * gap - Math.sign(o) * Math.max(0, a - 1) * gap * 0.28;
        c.style.transform = `translate(-50%,-50%) translateX(${x}px) rotateY(${clamp(o, -3, 3) * -9}deg) scale(${s})`;
        c.style.zIndex = String(100 - Math.round(a * 10));
        c.style.opacity = a > 3.6 ? 0 : 1;
        c.style.setProperty('--dim', Math.min(a, 2.5) * 0.28);
        c.classList.toggle('is-active', i === active && drag === 0);
        c.tabIndex = i === active ? 0 : -1;
        c.setAttribute('aria-hidden', i === active ? 'false' : 'true');
      });
    }
    function sync() {
      count.textContent = String(active + 1).padStart(2, '0');
      label.textContent = cards[active].dataset.label || '';
      cards.forEach((c, i) => {
        const vp = $('.vp', c);
        if (!vp) return;
        // přednačti sousedy, pusť jen aktivní
        if (Math.abs(i - active) <= 1) ensure(vp);
        if (i === active && inView && !reduce) play(vp); else stop(vp);
      });
    }
    function go(i) { active = (i + n) % n; drag = 0; layout(); sync(); }
    $('.deck__prev', deck).addEventListener('click', () => go(active - 1));
    $('.deck__next', deck).addEventListener('click', () => go(active + 1));
    deck.addEventListener('keydown', e => {
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(active - 1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); go(active + 1); }
    });
    // tažení myší i prstem
    let down = false, sx = 0, sy = 0, moved = false, horiz = null, t0 = 0;
    stage.addEventListener('pointerdown', e => { down = true; moved = false; horiz = null; sx = e.clientX; sy = e.clientY; t0 = performance.now(); });
    addEventListener('pointermove', e => {
      if (!down) return;
      const dx = e.clientX - sx, dy = e.clientY - sy;
      if (horiz === null && (Math.abs(dx) > 6 || Math.abs(dy) > 6)) horiz = Math.abs(dx) > Math.abs(dy);
      if (!horiz) return;
      moved = true; deck.classList.add('is-drag');
      const w = cards[0].getBoundingClientRect().width;
      drag = clamp(-dx / (w * 0.86), -3, 3); layout();
    }, { passive: true });
    addEventListener('pointerup', e => {
      if (!down) return; down = false; deck.classList.remove('is-drag');
      if (moved) {
        const fast = (performance.now() - t0) < 260 && Math.abs(drag) > 0.12;
        const step = fast ? Math.sign(drag) * Math.max(1, Math.round(Math.abs(drag))) : Math.round(drag);
        go(active + step);
      }
    });
    stage.addEventListener('click', e => {
      const c = e.target.closest('.deck__card'); if (!c) return;
      if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; return; }
      const i = cards.indexOf(c);
      if (i !== active) { e.preventDefault(); e.stopPropagation(); go(i); }
    }, true);
    new IntersectionObserver(es => { inView = es[0].isIntersecting; sync(); }, { threshold: 0.35 }).observe(deck);
    addEventListener('resize', layout);
    go(0);
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
      document.body.style.overflow = 'hidden';
      pv.play().catch(() => {});
      $('.player__close', player).focus();
    }
    function close() {
      player.classList.remove('is-open'); pv.pause(); pv.removeAttribute('src'); pv.load();
      document.body.style.overflow = '';
      if (lastFocus) lastFocus.focus();
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
    });
  });

  /* ---------- reels: tažení a šipky ---------- */
  $$('.reels').forEach(r => {
    const tr = $('.reels__track', r);
    const step = () => tr.querySelector('.reel').getBoundingClientRect().width + 16;
    const prev = $('.reels__nav .prev', r.parentElement), next = $('.reels__nav .next', r.parentElement);
    if (prev) prev.addEventListener('click', () => tr.scrollBy({ left: -step() * 2, behavior: 'smooth' }));
    if (next) next.addEventListener('click', () => tr.scrollBy({ left: step() * 2, behavior: 'smooth' }));
    let down = false, sx = 0, sl = 0, moved = false;
    tr.addEventListener('pointerdown', e => { if (e.pointerType !== 'mouse') return; down = true; moved = false; sx = e.clientX; sl = tr.scrollLeft; });
    addEventListener('pointermove', e => { if (!down) return; const dx = e.clientX - sx; if (Math.abs(dx) > 5) { moved = true; tr.classList.add('is-drag'); } tr.scrollLeft = sl - dx; });
    addEventListener('pointerup', () => { down = false; tr.classList.remove('is-drag'); });
    tr.addEventListener('click', e => { if (moved) { e.stopPropagation(); e.preventDefault(); moved = false; } }, true);
  });

  /* rok v patičce */
  $$('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
})();

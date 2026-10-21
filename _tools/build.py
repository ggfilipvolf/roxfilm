#!/usr/bin/env python3
"""Generátor statických stránek webu Roxfilm.
Obsah upravujte tady (texty, videa, fotky) a pusťte: python3 _tools/build.py
Výstup: index.html, alux.html, krasochatky.html, ladislav-bradna.html, balonio.html, 404.html
(půjčovnu generuje a šifruje _tools/pujcovna.sh)
"""
import json, os, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = json.load(open(os.path.join(ROOT, '_tools', 'media.json')))  # slug -> {w,h,dur,full}
E = html.escape
V = '11'  # verze CSS/JS (při změně zvyšte, ať se nenačítá stará z cache)

PHONE = '777 272 802'; PHONE_TEL = '+420777272802'
EMAIL = 'ggfilipvolf@gmail.com'
IG_ROX = 'https://www.instagram.com/roxfilm.cz/'
IG_FILIP = 'https://www.instagram.com/filipvolf_official/'

# šipka = levá polovina X z loga
ARROW = '<svg class="arr" viewBox="0 0 144 248" aria-hidden="true"><polygon fill="currentColor" points="0,0 123,0 144,124 123,248 0,248 100,124"/></svg>'
CLOSE = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M1 1l14 14M15 1L1 15" stroke="currentColor" stroke-width="1.4"/></svg>'

def tc(sec):
    sec = int(round(sec or 0)); return f'{sec//60:02d}:{sec%60:02d}'

def m(slug): return META.get(slug, {})
def vertical(slug): mm = m(slug); return mm.get('h', 0) > mm.get('w', 1)

def vp(slug, mode='view', base='media'):
    return (f'<div class="vp" data-prev="{base}/prev/{slug}.mp4" data-mode="{mode}">'
            f'<img src="{base}/post/{slug}.jpg" alt="" loading="lazy" decoding="async"></div>')

def full_attrs(slug, title, base='media'):
    if not os.path.exists(os.path.join(ROOT, base, 'full', slug + '.mp4')): return ''
    return (f' data-full="{base}/full/{slug}.mp4" data-poster="{base}/post/{slug}.jpg" data-title="{E(title)}"'
            f' data-vertical="{1 if vertical(slug) else 0}"')

def vp_any(ref, mode='view'):
    """ref 'slug' (staré video) nebo 'slozka/x' (nové výstupy)"""
    if '/' in ref:
        d, s = ref.split('/')
        return (f'<div class="vp" data-prev="media/{d}/{s}.prev.mp4" data-mode="{mode}">'
                f'<img src="media/{d}/{s}.jpg" alt="" loading="lazy" decoding="async"></div>')
    return vp(ref, mode)

def full_any(ref, title):
    if '/' in ref:
        d, s = ref.split('/')
        if not os.path.exists(os.path.join(ROOT, 'media', d, s + '.mp4')): return ''
        v = META.get(ref, {}).get('vertical', 1)
        return f' data-full="media/{d}/{s}.mp4" data-poster="media/{d}/{s}.jpg" data-title="{E(title)}" data-vertical="{v}"'
    return full_attrs(ref, title)

def photo(src, alt, cls='', speed=None, eager=False):
    """fotka s parallaxou"""
    sp = f' data-speed="{speed}"' if speed else ''
    ld = '' if eager else ' loading="lazy"'
    return f'<div class="px {cls}"{sp}><div class="px__in"><img src="assets/img/{src}.jpg" alt="{E(alt)}"{ld} decoding="async"></div></div>'

# ---------------- hlavička, patička ----------------
def head(title, desc, canonical, og='assets/hero/poster.jpg'):
    return f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="https://www.roxfilm.cz/{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="https://www.roxfilm.cz/{og}">
<meta property="og:locale" content="cs_CZ">
<meta name="theme-color" content="#0F0F0E">
<link rel="icon" href="assets/logo/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/logo/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono:wght@500&family=Montserrat:wght@800&display=swap&subset=latin-ext" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v={V}">
<!-- Metricool -->
<script>function loadScript(a){{var b=document.getElementsByTagName("head")[0],c=document.createElement("script");c.type="text/javascript",c.src="https://tracker.metricool.com/resources/be.js",c.onreadystatechange=a,c.onload=a,b.appendChild(c)}}loadScript(function(){{beTracker.t({{hash:"606bc3c5e93c01d2116e8aad1960a148"}})}});</script>
</head>
<body>
<a class="sr" href="#obsah">Přeskočit na obsah</a>
'''

def nav(home=False):
    p = '' if home else 'index.html'
    return f'''<header class="nav" id="nav">
  <a class="nav__logo" href="{p or '#top'}" aria-label="Roxfilm – úvod"><img src="assets/logo/logo-white.png" alt="Roxfilm" width="46" height="30"></a>
  <button class="nav__toggle" aria-label="Menu" aria-expanded="false" aria-controls="menu"><span></span></button>
  <ul class="nav__links" id="menu">
    <li><a href="{p}#reels">Reels</a></li>
    <li><a href="{p}#case-studies">Case studies</a></li>
    <li><a href="{p}#prace">Práce</a></li>
    <li><a href="{p}#o-nas">O nás</a></li>
    <li><a href="pujcovna.html">Půjčovna</a></li>
    <li><a class="btn" href="{p}#kontakt">Napište nám {ARROW}</a></li>
  </ul>
</header>
'''

PLAYER = f'''<div class="player" role="dialog" aria-modal="true" aria-label="Přehrávač videa">
  <div class="player__box">
    <div class="player__top"><b></b><button class="player__close" aria-label="Zavřít video">{CLOSE}</button></div>
    <video controls playsinline preload="none"></video>
  </div>
</div>
'''

def contact_block():
    return f'''<section class="sec" id="kontakt">
  <div class="wrap contact">
    <div data-reveal>
      <span class="label"><i class="rec-dot"></i>Kontakt</span>
      <h2 class="t-h2" style="margin-top:16px">Napište nám.</h2>
      <p>Zavolejte nebo napište. Domluvíme si krátkou schůzku a navrhneme, jak na to.</p>
    </div>
    <ul class="clist" data-reveal style="--d:.1s">
      <li><a href="tel:{PHONE_TEL}"><span>Telefon</span><b>{PHONE}</b>{ARROW}</a></li>
      <li><a href="mailto:{EMAIL}"><span>E-mail</span><b>{EMAIL}</b>{ARROW}</a></li>
      <li><a href="{IG_ROX}" target="_blank" rel="noopener"><span>Instagram</span><b>@roxfilm.cz</b>{ARROW}</a></li>
      <li><a href="{IG_FILIP}" target="_blank" rel="noopener"><span>Zakladatel</span><b>@filipvolf_official</b>{ARROW}</a></li>
    </ul>
  </div>
</section>
'''

def foot():
    return f'''<footer class="foot">
  <div class="wrap">
    <img src="assets/logo/logo-white.png" alt="Roxfilm" width="37" height="24" loading="lazy">
    <span>Produkce Roxfilm · Brno · točíme kdekoli · © <span data-year>2026</span></span>
    <nav aria-label="Patička">
      <a href="pujcovna.html">Půjčovna techniky</a>
      <a href="https://www.balonio.cz" target="_blank" rel="noopener">Balonio</a>
      <a href="{IG_ROX}" target="_blank" rel="noopener">Instagram</a>
    </nav>
  </div>
</footer>
{PLAYER}<script src="assets/js/lenis.min.js" defer></script>
<script src="assets/js/site.js?v={V}" defer></script>
</body>
</html>
'''

def sec_head(label, title, text=''):
    return (f'<div class="head" data-reveal><div><span class="label">{E(label)}</span><h2 class="t-h2">{E(title)}</h2></div>'
            + (f'<p>{E(text)}</p>' if text else '<span></span>') + '</div>')

# ---------------- data ----------------
PORTFOLIO = [
  ('porsche','Porsche','Kamera riggovaná ze všech stran auta.','spot'),
  ('ben-cristovao-omluva','Ben Cristovao – Omluva','Klip postavený na siluetách.','klip'),
  ('opatija-angels','Opatija Angels','Teambuilding a obsah pro majitele vil.','spot'),
  ('tesco-velikonoce','Tesco – Velikonoce','Velikonoční TV spot.','spot'),
  ('drive/ec-parfums','EC Parfums','Firemní spot z výroby a skladu.','spot'),
  ('sarka-stiborova','Šárka Stiborová – chirurgie','Klid, preciznost, důvěra.','spot'),
  ('vut-opera','VUT – chemická opera','Tři natáčecí dny, jedna premiéra.','event'),
  ('hopa-group','HOPA Group','Letní spot pro developera. S kapkou humoru.','spot'),
  ('3d-art','3D art','Klip, kde vznikal 3D svět scénu po scéně.','klip'),
  ('day-vlog','Day vlog','Celý den s klientem v jednom vlogu.','event'),
  ('pandies','Pandies','Módní značka mikin. Elegance v detailu.','spot'),
  ('drive/promoce-fch','Promoce FCH VUT','Celý obřad v jednom filmu.','event'),
  ('sergei-barracuda','Sergei Barracuda – Hvězdný prach','Obří jeřáb, několik lokací, dva dny.','klip'),
  ('drive/az-tower','AZ Tower','Spot pro reklamní plochu na nejvyšší budově v Česku.','spot'),
  ('drive/kerndl-tesco','Kerndl × Tesco','Spot pro vína Kerndl přímo v prodejně Tesco.','spot'),
  ('drive/villa-naya','Villa Naya','Luxusní vila v Chorvatsku. Dron, interiér, moře.','spot'),
  ('drive/rich-fouad-lets-slide','Rich Fouad – Let’s Slide','Klip ve formátu kina.','klip'),
  ('yzomandias','Yzomandias – koncert','Jedna kamera, celý večer v pohybu.','event'),
  ('semspoko','Semspoko','Klip z Vídně.','klip'),
  ('chorvatsko-spot','Kreativní spot','Mindful spot z teambuildingu v Chorvatsku.','spot'),
  ('vlog-workshop','Vlog z workshopu','Od příprav po poslední potlesk.','event'),
]
CATS = [('all','Vše'),('spot','Spoty a reklamy'),('klip','Klipy'),('event','Eventy a instituce')]
REELS = [
  ('drive/r-vecirek','Firemní večírek'),('polepim/polepim-5','Polepim – wrap'),('drive/r-villa-oresin','Villa Ořešín'),
  ('drive/r-svatojanska-noc','Svatojánská noc – STELAR Advisory'),('r2/hubert','Hubert Krochmalný'),('polepim/audi-1-broll-warrior','Polepim – Audi'),
  ('drive/r-influland','Report z Influlandu'),('r2/denis-1','Denis Lazarov'),('drive/r-eli-prekvapko','Překvapení pro Eli'),
  ('balonio-ads/11','Balonio – hala'),('drive/r-gurdau','Gurdau'),('r2/kacka-1','Kateřina Moravová'),
  ('drive/r-attila','Attila'),('lada2/ko-kriteria','Ladislav Bradna – 3 KO kritéria'),('drive/r-villa-naya-3','Villa Naya'),
  ('r2/infina-1','Infina'),('drive/r-kora-1','Architektura'),('r2/kora-rozhovor','Architektura – proměna dispozice'),
  ('r2/natalie-d35','Natálie Kratochvílová'),('drive/r-infina','Infina – kancelář'),('r2/saiko','Balonio – Saiko'),
  ('drive/r-ai-tvorba','Tvorba s AI'),('r2/infina-miska-1','Infina – Miška'),('r2/svatba-luky','Svatba'),
  ('drive/r-reklamni','Reklamní reels'),('balonio/lr-realizace','Balonio – LR Health & Beauty'),('r2/denis-3','Denis Lazarov – studio'),
  ('drive/r-vut-medailonek','VUT FCH – medailonek'),('r2/infl-ugc','Balonio – Influland'),('r2/natalie-5','Natálie Kratochvílová – rozpočet'),
  ('drive/r-eli-oslava','Oslava'),('r2/svatba5','Balonio – svatba'),('r2/infina-2b18','Infina – nábor'),
  ('drive/r-kora-3','Kora – zahrada'),('r2/recenze-maison','Recenze – Maison'),('balonio/recenze-borgo','Recenze – Borgo Agnese'),
  ('polepim/polepim-8','Polepim – PPF'),('r2/kacka-2','Kateřina Moravová – konzultace'),('balonio/neon','Balonio – neon'),
  ('balonio-ads/09','Balonio – Filip'),('r2/infina-miska-2','Infina – Miška 2'),('polepim/polepim-2-predni-sklo-chameleon','Zatmavení skel'),
]
KRAS_DECK = [(f'kras-r{i}', f'Krasochatky – reels {i}') for i in range(1,7)] + \
  [(f'kras/krasonos-{i}', f'Krasonoš {i}') for i in range(1,8)] + [(f'kras/dron-{i}', f'Dron {i}') for i in range(1,7)]
BALONIO_ADS = [
  ('balonio-ads/01','Fashion Week'),('balonio-ads/explainer','Jak Balonio funguje'),('balonio-ads/ugc-doporuceni','UGC – doporučení'),
  ('balonio-ads/05','LR Health & Beauty'),('balonio-ads/02','Influland'),('balonio-ads/04','Saiko Fashion Show'),
  ('balonio-ads/03a','Vánoční večírek'),('balonio-ads/ugc-vzdavam','UGC – vzdávám to'),('balonio-ads/09','Balonio v hale'),
  ('balonio-ads/svatba-1','Svatba'),('balonio-ads/06','Sabri'),('balonio-ads/07','Filip & Sabri'),
  ('balonio-ads/ugc-1','UGC 1'),('balonio-ads/10','Hala – titulky'),('balonio-ads/branding','Firemní branding'),
  ('balonio-ads/08','SMS Finance'),('balonio-ads/ugc-4','UGC 4'),('balonio-ads/svatba-2','Svatba 2'),
  ('balonio-ads/11','Hala – detail'),('balonio-ads/strom','Vražení do stromu'),('balonio-ads/oktagon','Oktagon'),
  ('balonio-ads/ugc-2','UGC 2'),('balonio-ads/12','Hala – neon'),('balonio-ads/ugc-3','UGC 3'),
  ('balonio/ples','Ples – realizace'),('balonio/lr-realizace','LR – realizace'),('balonio/neon','Personalizovaný neon'),
  ('r2/infl-ugc','Influland – UGC'),('r2/svatba5','Svatba – reklama'),('r2/neon-filip','Filip a neon'),('r2/saiko','Saiko – realizace'),
]

LOGOS = [  # (soubor, název, výška relativně)
  ('sony','Sony',0.62),('alux','Alux',1.15),('stelar','STELAR Advisory',0.9),('tesco','Tesco',0.95),('ecparfums','EC Parfums',0.9),
  ('borgo','Borgo Agnese',1.15),('kras','Krasochatky',0.95),('hopa','HOPA Group',0.42),('vut','VUT Brno',1),('lada','Ladislav Bradna',0.95),
  ('polepim','Polepim',1.15),('infina','Infina',1),('kora','KORA',0.95),
]
BTS = [  # (soubor v assets/img, popis)
  ('bts/dsc09060','Tým Roxfilmu a Balonia na Czech Fashion Week'),('set-theatre','Natáčení v divadle'),('bts/rec-20d9c7ef','Filip Volf při konzultaci na placu'),
  ('bts/13a2546','Natáčení s gimbalem'),('set-medical','Natáčení na klinice'),('bts/dsc08005','Filip Volf s klientem na Fashion Week'),
  ('set-interview','Rozhovor na placu'),('bts/rec-971d47f7','Štáb při natáčení rozhovoru'),('filip-camera-1','Filip Volf s kamerou'),
  ('bts/dsc08765','Filip Volf na Czech Fashion Week'),('bts/rec-b7705676','Příprava mikrofonu před natáčením'),('set-monitor','Kontrola záběru na monitoru'),
  ('bts/13a1568','Natáčení v hale'),('bts/rec-15a9f438','Domluva záběru s klientkou'),('set-chair','Příprava scény'),
  ('bts/dsc08996','Filip Volf natáčí na Fashion Week'),('bts/rec-74e830ec','Natáčení v restauraci'),('set-28','Štáb Roxfilmu'),
  ('bts/dsc08171','Filip Volf v rozhovoru s hostem'),('bts/13a2106','Domluva s modelkou'),('team-boom','Štáb Roxfilmu při natáčení'),
  ('bts/dsc08961','Filip Volf s modelkami'),
]

def collage(items, cls=''):
    """koláž fotek v přirozeném poměru, klik otevře fotku přes celou obrazovku"""
    return (f'<div class="collage {cls}">' + ''.join(
        f'<figure data-reveal style="--d:{(i%3)*0.06:.2f}s"><button type="button" class="zoom" data-img="assets/img/{s}.jpg" aria-label="{E(a)}">'
        f'<img src="assets/img/{s}.jpg" alt="{E(a)}" loading="lazy" decoding="async"></button></figure>'
        for i, (s, a) in enumerate(items)) + '</div>')

def filmstrip(items):
    """plynulý pás fotek, který sám jede dokola"""
    imgs = ''.join(f'<li><button type="button" class="zoom" data-img="assets/img/{s}.jpg" aria-label="{E(a)}"><img src="assets/img/{s}.jpg" alt="{E(a)}" decoding="async"></button></li>' for s, a in items)
    return f'<div class="marquee marquee--photos" data-reveal><ul class="marquee__track">{imgs}</ul></div>'

def deck(items, label):
    cards = ''.join(
        f'<button class="deck__card" type="button" data-label="{E(t)}"{full_any(r, t)}>{vp_any(r, "deck")}</button>'
        for r, t in items)
    n = len(items)
    return (f'<div class="deck" data-deck tabindex="0" role="region" aria-roledescription="karusel" aria-label="{E(label)}" data-reveal>'
            f'<div class="deck__stage">{cards}</div>'
            f'<div class="deck__ui"><button class="deck__prev" type="button" aria-label="Předchozí">{ARROW}</button>'
            f'<div class="deck__info"><span class="deck__count"><b>01</b> / {n:02d}</span><span class="deck__label"></span></div>'
            f'<button class="deck__next" type="button" aria-label="Další">{ARROW}</button></div>'
            f'<p class="deck__hint label">Táhněte do strany · kliknutím pustíte se zvukem</p></div>')

# pořadí na úvodní stránce
CASES = [
  dict(slug='alux', name='Alux', sub='Hliníkové pergoly', file='alux.html',
       line='Kampaně, reels a produktová videa u skutečných zákazníků. Více než rok spolupráce.',
       fig='150+ videí', frame=('h','alux-family')),
  dict(slug='balonio', name='Balonio', sub='Naše vlastní značka', file='balonio.html',
       line='Luxusní fotobox, do kterého se vchází. Vizuál, obsah, sítě i reklama z jednoho týmu.',
       fig='100+ reklamních videí', frame=('r',['balonio-ads/11','balonio-ads/09','balonio-ads/07','balonio/recenze-borgo','r2/neon-filip'])),
  dict(slug='kras', name='Krasochatky', sub='Chatky Jedovnice', file='krasochatky.html',
       line='Celá identita na Instagramu postavená na atmosféře místa pomocí fotek a záběrů.',
       fig='300+ materiálů', frame=('r',['kras-r1','kras-r3','kras-r4','kras-r6'])),
  dict(slug='lada', name='Ladislav Bradna', sub='Osobní značka · financování', file='ladislav-bradna.html',
       line='Osobní značka finančního experta od nuly: web, brand manuál, natáčení každý měsíc, sítě.',
       fig='10+ videí každý měsíc', frame=('r',['lada2/ko-kriteria','lada/bonita','lada2/t12','lada/rozchod'])),
]

def media_block(kind, ref, cls):
    if kind == 'h':
        return f'<div class="px {cls}" data-speed="0.06"><div class="px__in">{vp_any(ref)}</div></div>'
    return f'<div class="px {cls} {cls}--reels" data-speed="0.06"><div class="px__in" style="grid-template-columns:repeat({len(ref)},1fr)">' + ''.join(vp_any(r) for r in ref) + '</div></div>'

# ---------------- úvodní stránka ----------------
def index():
    o = [head('Roxfilm – produkce, která dotáhne i marketing',
              'Video, foto, sítě a reklama z Brna. Jeden tým od nápadu po výsledek. Osobní značky, firmy s příběhem, instituce a eventy.',
              ''), nav(True)]
    # HERO
    o.append(f'''<main id="obsah">
<section class="hero" id="top" data-frames-d="193" data-frames-m="97" data-path-d="assets/hero/d/" data-path-m="assets/hero/m/" data-frames-h="193" data-path-h="assets/hero/h/" aria-label="Úvod">
  <div class="hero__stage">
    <div class="hero__cam">
      <picture><source media="(max-width:759px)" srcset="assets/hero/poster-m.jpg"><img class="hero__poster" src="assets/hero/poster.jpg" alt="Kamera RED Komodo-X s objektivem DZOFilm Arles" fetchpriority="high"></picture>
      <canvas class="hero__canvas" aria-hidden="true"></canvas>
    </div>
    <div class="hero__reel" aria-hidden="true"><video muted loop playsinline preload="none" data-src="media/showreel.mp4" data-src-m="media/showreel-m.mp4" poster="media/showreel.jpg"></video></div>
    <canvas class="hero__xc" aria-hidden="true"></canvas>
    <div class="hero__shade"></div>
    <div class="bar" aria-hidden="true"><span class="bar__l">RED Komodo-X · Arles 35 · T1.4</span><span class="rec"><i class="rec-dot"></i>REC</span><span class="tc">00:00:00:00</span></div>
    <div class="hero__copy">
      <h1 class="t-display">Natočíme to.</h1>
      <p>Video, foto, sítě a reklama. Jeden tým od nápadu po výsledek.</p>
    </div>
    <div class="scrollhint label" aria-hidden="true">Scrollujte<i></i></div>
    <div class="focus" aria-hidden="true">
      <svg class="fm fm--l" viewBox="0 0 144 248"><polygon fill="currentColor" points="0,0 123,0 144,124 123,248 0,248 100,124"/></svg>
      <svg class="fm fm--r" viewBox="0 0 139 248"><polygon fill="currentColor" points="22,0 139,0 42,124 139,248 22,248 0,124"/></svg>
    </div>
    <div class="hero__end">
      <span class="label" style="color:var(--paper)">Showreel 2026</span>
      <a class="btn btn--solid" href="#reels">Ukázky práce {ARROW}</a>
    </div>
  </div>
</section>
''')
    # SPOLUPRÁCE – hned po animaci: text plyne přes fotku podání ruky
    o.append('''<section class="statement" id="spoluprace" aria-label="Dlouhodobá spolupráce">
  <div class="statement__pin">
    <div class="statement__bg"><img src="assets/img/handshake.jpg" alt="Filip Volf si podává ruku s klientem" decoding="async"></div>
    <div class="statement__shade"></div>
    <div class="wrap statement__copy">
      <h2 class="t-statement statement__text">Zakládáme si na dlouhodobé spolupráci.</h2>
      <p class="statement__sub">Dobré video vzniká tam, kde je důvěra. Kde si rozumíme a máme společný cíl. Spolupráce musí dávat smysl oběma stranám.</p>
    </div>
  </div>
</section>
''')
    # PRO KOHO (světlá) – tým, kdo, pás log klientů
    logos = ''.join(f'<li><img src="assets/logos/{n}.png" alt="{E(t)}" style="--h:{h}"></li>' for n, t, h in LOGOS)
    o.append(f'''<section class="sec sec--light sec--clients" id="pro-koho">
  <div class="wrap"><span class="label" data-reveal>Točili jsme pro</span></div>
  <div class="marquee" data-reveal aria-label="Klienti a partneři"><ul class="marquee__track">{logos}</ul></div>
  <div class="wrap who-wrap">
    <div class="who">
      <div class="who__text" data-reveal>
        <span class="label">Pro koho točíme</span>
        <h2 class="t-h2" style="margin-top:16px">Produkce, která táhne za jeden provaz.</h2>
      </div>
      <figure style="margin:0;--d:.1s" data-reveal>{photo('set-44', 'Tým Roxfilmu s klienty na natáčení', 'who__team')}</figure>
    </div>
    <div class="aud">
      <figure data-reveal>{photo('set-red-2', 'Rozhovor před kamerou ve studiu')}<h3 class="t-h3">Osobní značky</h3><p>Finanční poradci, makléři, lékaři a odborníci, kteří chtějí být tváří svého oboru.</p></figure>
      <figure data-reveal style="--d:.08s">{photo('set-restaurant', 'Natáčení v restauraci')}<h3 class="t-h3">Firmy s příběhem</h3><p>Gastro, architektura, služby a výroba. Majitel ví, co umí, jen to zatím není vidět.</p></figure>
      <figure data-reveal style="--d:.16s">{photo('set-opera', 'Natáčení v divadle')}<h3 class="t-h3">Instituce a eventy</h3><p>Školy, obchodní centra a velké firmy, které potřebují točit ve velkém a bez chyby.</p></figure>
    </div>
  </div>
</section>
''')
    # REELS – první práce
    o.append(f'''<section class="sec" id="reels">
  <div class="wrap">{sec_head('Reels', 'Krátká videa, která lidi zastaví.', 'Pro osobní značky, firmy i eventy. Natočená pro mobil a střižená na první tři vteřiny.')}</div>
  {deck(REELS, 'Reels od Roxfilmu')}
</section>
''')
    # CASE STUDIES
    o.append(f'<section class="sec sec--tight" id="case-studies">\n  <div class="wrap">\n    {sec_head("Case studies", "Spolupráce, na kterých je vidět, jak pracujeme.", "Od prvního natáčecího dne po poptávky.")}\n    <div class="cases">\n')
    for i, c in enumerate(CASES, 1):
        kind, ref = c['frame']
        o.append(f'''      <a class="case" href="{c['file']}" data-reveal>
        {media_block(kind, ref, 'case__media')}
        <div class="case__meta">
          <div><span class="label">{i:02d} · {E(c['sub'])}</span><h3 class="t-h2">{E(c['name'])}</h3></div>
          <div><p>{E(c['line'])}</p><span class="case__fig">{E(c['fig'])}</span></div>
          <span class="more">Case study {ARROW}</span>
        </div>
      </a>
''')
    o.append('    </div>\n  </div>\n</section>\n')
    # PORTFOLIO
    o.append(f'''<section class="sec" id="prace">
  <div class="wrap">
    {sec_head('Další práce', 'Spoty, klipy a eventy.', 'Stovky videí od roku 2020. Každé s jiným cílem a stejným důrazem na výsledek.')}
    <div class="filters" role="group" aria-label="Filtr portfolia" data-reveal>
''' + ''.join(f'      <button type="button" data-cat="{k}" aria-pressed="{"true" if k=="all" else "false"}">{v}</button>\n' for k, v in CATS) + '''    </div>
    <div class="grid">
''')
    for n, (slug, title, desc, cat) in enumerate(PORTFOLIO):
        o.append(f'''      <button class="item" type="button" data-cat="{cat}"{full_any(slug, title)} data-reveal style="--d:{(n%3)*0.08:.2f}s">
        <div class="item__frame">{vp_any(slug,'hover')}<span class="item__play"><i class="rec-dot"></i>Přehrát</span><span class="item__tc">{tc(m(slug).get('dur'))}</span></div>
        <h3>{E(title)}</h3><p>{E(desc)}</p>
      </button>
''')
    o.append('    </div>\n  </div>\n</section>\n')
    # ZA KAMEROU – koláž
    o.append(f'''<section class="sec sec--tight" id="za-kamerou">
  <div class="wrap">
    {sec_head('Za kamerou', 'Skutečné záběry z našich natáčení.', 'Žádná fotobanka. Lidé chtějí vidět, kdo stojí za kamerou.')}
    {collage(BTS, 'bts')}
  </div>
</section>
''')
    # O NÁS (světlá)
    o.append(f'''<section class="sec sec--light" id="o-nas">
  <div class="wrap about">
    <div data-reveal>{photo('filip-bw', 'Filip Volf, zakladatel Roxfilmu', 'about__img')}</div>
    <div data-reveal style="--d:.1s">
      <span class="label">Zakladatel</span>
      <h2 class="t-h2">Filip Volf</h2>
      <p class="about__bio">Video točí od roku 2020. Propojuje vizuální kvalitu s obchodním přemýšlením: každé video má mít cíl, strategii a výsledek. Posledních pár let se Roxfilm nejvíc věnuje osobním značkám a Instagramu, od strategie po samotný obsah. Vedle Roxfilmu stojí Filip za značkou Balonio.</p>
      <blockquote>„Spolupráci nevnímám jako jednorázovou zakázku, ale jako partnerství, které má dlouhodobý směr.“</blockquote>
      <p class="about__team">V týmu: projektový manažer, fotograf a grafik, kameraman, střihač a colorista, ilustrátor a správce sítí s Meta reklamou.</p>
    </div>
  </div>
</section>
''')
    o.append(contact_block())
    o.append('</main>\n')
    o.append(foot())
    return ''.join(o)

# ---------------- případové studie ----------------
def case_page(c, d):
    o = [head(f'{c["name"]} – case study | Roxfilm', d['desc'], c['file'], og=d.get('og','assets/hero/poster.jpg')), nav()]
    kind, ref = d['hero']
    o.append(f'''<main id="obsah">
<section class="cs-hero">
  {media_block(kind, ref, 'cs-hero__frame')}
</section>
<section class="cs-title">
  <div class="wrap">
    <span class="label" data-reveal><i class="rec-dot"></i>Case study · {E(c['sub'])}</span>
    <h1 class="t-display" style="margin-top:16px" data-reveal>{E(c['name'])}</h1>
    <p data-reveal style="--d:.08s">{E(d['lead'])}</p>
    <dl class="facts" data-reveal style="--d:.14s">
''' + ''.join(f'      <div><dt class="label">{E(k)}</dt><dd>{E(v)}</dd></div>\n' for k, v in d['facts']) + f'''    </dl>
  </div>
</section>
<section class="sec sec--light" style="margin-top:clamp(64px,8vw,120px)">
  <div class="wrap">
    <div class="cut">
      <div data-reveal><span class="label">Před</span><h2 class="t-h2">Výzva</h2><p>{E(d['before'])}</p></div>
      <div data-reveal style="--d:.1s"><span class="label">Po</span><h2 class="t-h2">Co jsme udělali</h2><ul>''' +
      ''.join(f'<li>{E(x)}</li>' for x in d['did']) + '''</ul></div>
    </div>
    <div class="nums" data-reveal>
''' + ''.join(f'      <div><b>{E(n)}</b><span>{E(l)}</span></div>\n' for n, l in d['nums']) + '''    </div>
  </div>
</section>
''')
    for blk in d['blocks']:
        t = blk['type']
        o.append(f'<section class="sec" style="padding-bottom:0">\n  <div class="wrap">\n    {sec_head(blk.get("label", "Ukázky"), blk["title"], blk.get("text", ""))}\n')
        if t == 'videos':
            o.append('    <div class="vgrid">\n')
            for n, (ref, title) in enumerate(blk['items']):
                fa = full_any(ref, title)
                tag = 'button type="button"' if fa else 'div'
                o.append(f'      <{tag} class="item"{fa} data-reveal style="--d:{(n%2)*0.08:.2f}s"><div class="item__frame">{vp_any(ref,"hover")}' + ('<span class="item__play"><i class="rec-dot"></i>Přehrát</span>' if fa else '') + f'</div><h3>{E(title)}</h3></{tag.split()[0]}>\n')
            o.append('    </div>\n')
        elif t == 'reels':
            o.append('    <div class="rgrid">\n')
            for n, (ref, title) in enumerate(blk['items']):
                fa = full_any(ref, title)
                tag = 'button type="button"' if fa else 'div'
                o.append(f'      <{tag} class="reel"{fa} data-reveal style="--d:{(n%5)*0.06:.2f}s"><div class="reel__frame">{vp_any(ref,"view")}</div>' + (f'<p>{E(title)}</p>' if blk.get('captions') else '') + f'</{tag.split()[0]}>\n')
            o.append('    </div>\n')
        elif t == 'deck':
            o.append('  </div>\n  ' + deck(blk['items'], blk['title']) + '\n  <div class="wrap">\n')
        elif t == 'collage':
            o.append('    ' + collage(blk['items']) + '\n')
        elif t == 'filmstrip':
            o.append('  </div>\n  ' + filmstrip(blk['items']) + '\n  <div class="wrap">\n')
        elif t == 'photos':
            o.append('    <div class="pgrid">\n' + ''.join(f'      <figure data-reveal style="--d:{(n%3)*0.07:.2f}s">{photo(s, a)}</figure>\n' for n, (s, a) in enumerate(blk['items'])) + '    </div>\n')
        o.append('  </div>\n</section>\n')
    nx = d['next']
    o.append(f'''<section class="sec" style="padding-bottom:0">
  <div class="wrap">
    <a class="next" href="{nx[0]}" data-reveal><span><span class="label">Další case study</span><span class="t-h2">{E(nx[1])}</span></span>{ARROW}</a>
  </div>
</section>
''')
    o.append(contact_block())
    o.append('</main>\n')
    o.append(foot())
    return ''.join(o)

CASE_DATA = {
 'alux': dict(
   desc='Alux – hliníkové pergoly. Videa pro kampaně, reels a produktová videa od Roxfilmu. 150+ videí, až 2× víc poptávek v sezóně.',
   hero=('h','alux-family'),
   lead='Kompletní video pro marketingové kampaně: od scénáře přes natáčení po výstupy pro reklamu a sociální sítě. Produkt vždy v reálném prostředí, u skutečných zákazníků.',
   facts=[('Klient','Alux – hliníkové pergoly'),('Spolupráce','Více než rok'),('Rozsah','Scénáře, natáčení, střih, reklama'),('Formáty','Spoty, reels, produktová videa')],
   before='Pergola je produkt, který si zákazník musí představit u sebe doma. Katalogové fotky na to nestačí a jedno video za rok taky ne.',
   did=['Scénáře a natáčení u skutečných realizací','Reels s lidmi z firmy před kamerou','Spoty a produktová videa pro výkonnostní reklamu','Jednotný vizuál napříč kampaněmi'],
   nums=[('150+','videí pro kampaně a sítě'),('2×','víc poptávek v sezónních obdobích'),('1+','rok pravidelné spolupráce')],
   blocks=[
     dict(type='videos', label='Spoty', title='Spoty a produktová videa', text='Produkt v reálném prostředí, detail a konzistentní vizuál značky.',
          items=[('alux-family','Rodinný spot'),('alux-1','Realizace'),('alux-3','Produktové video'),('alux-6','Showroom'),('alux-2','Realizace u zákazníka'),('alux-4','Detail produktu')]),
     dict(type='reels', label='Reels', title='Lidé z firmy před kamerou', text='Jedna z nejsilnějších komunikačních forem tohoto klienta.',
          items=[(f'alux-r{i:02d}', f'Alux – reels {i:02d}') for i in range(1,11)]),
   ],
   next=('balonio.html','Balonio')),
 'lada': dict(
   desc='Ladislav Bradna – osobní značka finančního experta. Web, brand manuál, každý měsíc 10+ videí a 15+ výstupů na sítě. Case study Roxfilm.',
   hero=('r',['lada2/ko-kriteria','lada/bonita','lada2/t12','lada/rozchod','lada2/t08']), og='assets/img/lada-portrait.jpg',
   lead='Osobní značku experta na hypotéky a financování nemovitostí stavíme od června 2026. Nejdřív portrétní focení, web, brand manuál a struktura obsahu. Od července natáčíme každý měsíc.',
   facts=[('Klient','Ladislav Bradna'),('Obor','Hypotéky a financování'),('Od','Června 2026'),('Měsíčně','10+ videí, 15+ výstupů')],
   before='Finanční expert s praxí a výsledky, kterého znali hlavně klienti z doporučení. Cíl: aby ho lidé znali dřív, než mu zavolají.',
   did=['Portrétní focení, web, brand manuál a struktura obsahu','Témata vymýšlíme spolu s ním, natáčení s klidem na placu','Každý měsíc reels, vlog „Den s Laďou“ a teasery','Sprint 32 dní v kuse: každý den jeden výstup'],
   nums=[('10+','videí každý měsíc'),('15+','výstupů měsíčně na sítě'),('32','dní v kuse s denním výstupem')],
   blocks=[
     dict(type='filmstrip', label='Foto', title='Portrétní focení', text='Tím to celé začalo. Fotky pro web, sítě i brand manuál.',
          items=[('lada/ld-01', 'Ladislav Bradna, portrétní focení'), ('lada/ld-02', 'Ladislav Bradna, portrétní focení'), ('lada/ld-03', 'Ladislav Bradna, portrétní focení'), ('lada/ld-04', 'Ladislav Bradna, portrétní focení'), ('lada/ld-05', 'Ladislav Bradna, portrétní focení'), ('lada/ld-06', 'Ladislav Bradna, portrétní focení'), ('lada/ld-07', 'Ladislav Bradna, portrétní focení'), ('lada/ld-08', 'Ladislav Bradna, portrétní focení'), ('lada/ld-09', 'Ladislav Bradna, portrétní focení'), ('lada/ld-10', 'Ladislav Bradna, portrétní focení'), ('lada/ld-11', 'Ladislav Bradna, portrétní focení'), ('lada/ld-12', 'Ladislav Bradna, portrétní focení'), ('lada/ld-13', 'Ladislav Bradna, portrétní focení'), ('lada/ld-14', 'Ladislav Bradna, portrétní focení'), ('lada/ld-15', 'Ladislav Bradna, portrétní focení'), ('lada/ld-16', 'Ladislav Bradna, portrétní focení'), ('lada-portrait', 'Ladislav Bradna, portrét'), ('lada-process', 'Ladislav Bradna na ulici'), ('lada-about', 'Ladislav Bradna v zahradě'), ('lada-steps', 'Ladislav Bradna s tabletem')]),
     dict(type='reels', label='Reels', title='Otázky, které klienti opravdu řeší', text='Jedno téma, jedna myšlenka, titulky.', captions=True,
          items=[('lada2/ko-kriteria','3 KO kritéria v účetnictví'),('lada/bonita','Bonita a skladba příjmů'),('lada/rozchod','Rozchod a hypotéka'),('lada/auto','Nekupuj auto, kup byt'),('lada/deset-milionu','10 milionů a čerpání')]),
     dict(type='deck', label='YouTube', title='Vlog „Den s Laďou“', text='Delší formát na YouTube. Ke každému vlogu čtyři teasery před vydáním i po něm.',
          items=[('lada2/t01','Startuje série vlogů'),('lada2/t02','Díra ve střeše'),('lada/teaser-flip','Flip nemovitosti za 6 hodin'),('lada2/t04','Židle na 4 nohy'),
                 ('lada/teaser-kojetin','Trailer: Kojetín'),('lada2/t06','Levný pozemek od města'),('lada2/t07','Ušetřil čtvrt milionu'),('lada2/t08','Leoš a vlastní tank'),
                 ('lada2/t09','Evidenční list bytu'),('lada2/t10','Moudro: odpočinek'),('lada2/t11','Moudro: stejní lidé'),('lada2/t12','1000 ryb za 4 hodiny'),
                 ('lada/teaser-zavody','Den na závodech'),('lada2/t14','Trailer: rybářský závod')]),
   ],
   next=('alux.html','Alux')),
 'kras': dict(
   desc='Krasochatky, Jedovnice – brand manuál, foto, video a sítě od Roxfilmu. 300+ materiálů z jednoho vizuálního světa.',
   hero=('r',['kras-r1','kras-r2','kras-r3','kras-r4','kras-r6']), og='assets/img/kras-1.jpg',
   lead='Projekt, kde šla značka do hloubky. S majitelem jsme detailně navnímali energii místa, propojení s přírodou a principy feng shui. Z toho vznikl brand manuál a na něj navázal veškerý obsah.',
   facts=[('Klient','Krasochatky, Jedovnice'),('Obor','Ubytování v přírodě'),('Rozsah','Brand manuál, foto, video, sítě'),('Výstupy','300+ materiálů')],
   before='Ukázat ne jen prostor, ale atmosféru. Aby host věděl, jak se tam bude cítit, ještě než přijede.',
   did=['Brand manuál a vizuální směr značky','Fotografie interiérů, detailů a krajiny','Reels a krátká videa pro sítě','Promo materiály ve stejném jazyce'],
   nums=[('300+','materiálů: foto, video, sítě, promo'),('1','vizuální svět napříč všemi kanály'),('20+','reels a záběrů z dronu')],
   blocks=[
     dict(type='deck', label='Reels', title='Reels a drony', text='Ráno, oheň, čaj, les. Atmosféra místa v pár vteřinách.',
          items=KRAS_DECK),
     dict(type='photos', label='Foto', title='Foto', items=[(f'kras-{i}', 'Krasochatky') for i in (1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19) ]),
   ],
   next=('ladislav-bradna.html','Ladislav Bradna')),
 'balonio': dict(
   desc='Balonio – luxusní fotobox, do kterého se vchází. Vlastní značka, pro kterou Roxfilm dělá vizuál, obsah, sítě i reklamu.',
   hero=('r',['balonio-ads/11','balonio-ads/09','balonio-ads/07','balonio/recenze-borgo','r2/neon-filip']), og='assets/img/balonio-1.jpg',
   lead='Balonio není fotokoutek. Je to zážitek, do kterého se vchází. Je to naše vlastní značka a Roxfilm pro ni dělá celý marketing: vizuál, obsah, sítě i reklamu.',
   facts=[('Značka','Balonio'),('Obor','Luxusní fotobox na akce'),('Rozsah','Vizuál, foto, video, sítě, Meta reklama'),('Web','balonio.cz')],
   before='Zážitek, který se na fotce těžko popisuje. A akce, ze kterých jde vytěžit obsah na další týdny, když se na to myslí dopředu.',
   did=['Recenzní reels přímo od klientů na akcích','Realizační videa z eventů','Reklamní videa pro Meta kampaně','Systém: z jedné akce sedm a více výstupů'],
   nums=[('7+','výstupů z každé akce'),('100+','reklamních videí pro UGC a Meta'),('4×','týdně nový obsah na sítích')],
   blocks=[
     dict(type='deck', label='Meta reklama', title='Reklamy, UGC a realizace',
          text='Všechno, co pro Balonio vzniklo do kampaní a na sítě.',
          items=BALONIO_ADS),
     dict(type='reels', label='Recenze', title='Klienti mluví sami za sebe', text='Přímo na akci.', captions=True,
          items=[('balonio/recenze-borgo','Recenze – Borgo Agnese'),('r2/recenze-maison','Recenze – Maison'),('balonio/recenze-artis','Recenze – Artis'),('balonio/recenze-losterie',"Recenze – L'Osteria"),('balonio/recenze-sms','Recenze – SMS')]),
     dict(type='collage', label='Foto', title='Z natáčení a z akcí', text='Kliknutím fotku zvětšíte.', items=[
          ('balonio-1','Balonio na akci'),('bts/13a1426','Natáčení Balonia v hale'),('bts/13a2087','Příprava záběru'),('balonio-2','Balonio na akci'),
          ('bts/13a1574','Natáčení v hale'),('bts/13a2089','Domluva s modelkou'),('balonio-3','Balonio na akci'),('bts/13a1430','Natáčení Balonia v hale'),
          ('bts/13a2114','Příprava scény'),('balonio-4','Balonio na akci'),('bts/13a1569','Natáčení v hale'),('bts/13a2228','Natáčení modelky'),
          ('balonio-5','Balonio na akci'),('bts/13a2109','Úprava balónků'),('bts/dsc09042','Balonio na Czech Fashion Week'),('balonio-6','Balonio na akci'),
          ('bts/13a2081','Balonio v hale'),('bts/13a1472','Kameraman při natáčení'),('balonio-7','Balonio na akci'),('bts/dsc08733','Balonio na Czech Fashion Week')]),
   ],
   next=('krasochatky.html','Krasochatky')),
}

def page_404():
    o = [head('Stránka nenalezena | Roxfilm','Tahle stránka neexistuje.','404.html'), nav()]
    o.append(f'''<main id="obsah"><section class="sec" style="min-height:80vh;display:flex;align-items:center"><div class="wrap">
<span class="label"><i class="rec-dot"></i>Take 404</span>
<h1 class="t-display" style="margin-top:18px">Tenhle záběr nemáme.</h1>
<p style="margin-top:20px;color:var(--muted)">Stránka neexistuje nebo se přesunula.</p>
<p style="margin-top:32px"><a class="btn btn--solid" href="index.html">Zpět na úvod {ARROW}</a></p>
</div></section></main>
''')
    o.append(foot()); return ''.join(o)

# ---------------- půjčovna techniky (šifrovaná) ----------------
RENTAL = [
 ('Kamery', [('Sony FX3','1 600'),('Sony A7S III','1 500'),('Insta360 X5','600')]),
 ('Objektivy', [('Sony FE 50mm f/1.2 GM','800'),('Sony FE 24–70mm f/2.8 GM II','900'),('Laowa 10mm f/2.8 Zero-D','500'),('Helios M42 + redukce M42 → Sony FE','500')]),
 ('Dron', [('DJI Mavic 4 Pro Cinema Combo','4 500')]),
 ('Světla', [('Aputure 600d Pro (skladem 2 ks)','1 100'),('Aputure 600x Pro Bi-Color','1 300'),('Aputure amaran F22x Bi-Color','600'),('SmallRig RC60 Bi-Color','200'),('Aputure Infinibar PB12 120 cm (skladem 8 ks)','500'),('Aputure MT Pro','200'),('Aputure MC Pro','250'),('Blesk Godox pro Sony','100')]),
 ('Baterie a napájení', [('SmallRig 212Wh V-mount (skladem 2 ks)','350'),('FxLion 99Wh (skladem 3 ks)','250'),('FxLion 150Wh','300'),('FxLion 300Wh','400'),('Sony NP-FZ100 (skladem 8 ks)','150'),('Sony NP-FZ100 dummy adaptér (skladem 2 ks)','100'),('Ugreen 300W nabíječka (skladem 3 ks)','100'),('DJI Ronin battery handle (skladem 3 ks)','100')]),
 ('Ostatní', [('Atomos Ninja V','400'),('DJI Transmission Advanced pack + 5 baterií','3 300'),('DJI High-Bright monitor (skladem 2 ks)','400'),('DJI Mic 3 set','300'),('DJI Mic 2 set','300'),('JBL Charge 5','150'),('PolarPro Variable ND 2–5 stop (skladem 2 ks)','150'),('PolarPro Variable ND 6–9 stop','150'),('PolarPro CPL filtr','150'),('PolarPro Promist 1/4 filtr','200'),('Rode VideoMic Pro+','1 200'),('DJI Ronin RS3 Pro','1 400'),('DJI Ronin RS4 Pro','na dotaz')]),
]
def page_rental():
    o = [head('Půjčovna techniky | Roxfilm','Půjčovna filmové techniky Roxfilm, Brno.','pujcovna.html'), nav()]
    o.append('''<main id="obsah"><section class="sec" style="padding-top:clamp(120px,14vw,180px)"><div class="wrap">
<span class="label"><i class="rec-dot"></i>Pro klienty</span>
<h1 class="t-display" style="margin-top:18px">Půjčovna techniky</h1>
<p style="margin-top:20px;color:var(--screen);max-width:52ch">Ceny za den bez DPH. Veškeré kabely, příslušenství a redukce jsou v ceně pronájmu. Rezervace telefonem nebo e-mailem.</p>
<div class="rent">''')
    for cat, rows in RENTAL:
        o.append(f'<div class="rent__cat"><h2 class="t-h3">{E(cat)}</h2><table><tbody>' +
                 ''.join(f'<tr><td>{E(n)}</td><td>{p}{" Kč" if p[0].isdigit() else ""}</td></tr>' for n, p in rows) + '</tbody></table></div>')
    o.append(f'''</div>
<div class="rent__set"><div><span class="label">Výhodný set</span><h2 class="t-h2" style="margin-top:10px">Kamera na den</h2>
<p class="muted small" style="margin-top:12px">Sony FX3 nebo A7S III · Sony FE 24–70mm f/2.8 GM II · 4× baterie NP-FZ100 · DJI Ronin RS3 Pro · Ronin battery grip · PolarPro VND 2–5 stop · 2× SD Angelbird V90 256 GB</p></div>
<div class="rent__price"><s>4 450 Kč</s><b>2 500 Kč</b></div></div>
<p style="margin-top:44px"><a class="btn btn--solid" href="tel:{PHONE_TEL}">Rezervovat: {PHONE} {ARROW}</a></p>
</div></section></main>
''')
    o.append(foot()); return ''.join(o)

def main():
    w = lambda f, s: open(os.path.join(ROOT, f), 'w').write(s)
    w('index.html', index())
    for c in CASES: w(c['file'], case_page(c, CASE_DATA[c['slug']]))
    w('404.html', page_404())
    w(os.path.join('_tools', 'pujcovna-src.html'), page_rental())
    print('ok')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Generátor statických stránek webu Roxfilm.
Obsah upravujte tady (texty, videa, fotky) a pusťte: python3 _tools/build.py
Výstup: index.html, alux.html, krasochatky.html, ladislav-bradna.html, balonio.html, pujcovna-src.html, 404.html
"""
import json, os, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = json.load(open(os.path.join(ROOT, '_tools', 'media.json')))  # slug -> {w,h,dur,full}
E = html.escape

PHONE = '777 272 802'; PHONE_TEL = '+420777272802'
EMAIL = 'ggfilipvolf@gmail.com'
IG_ROX = 'https://www.instagram.com/roxfilm.cz/'
IG_FILIP = 'https://www.instagram.com/filipvolf_official/'

# šipka posuň = levá polovina X z loga
ARROW = '<svg viewBox="0 0 144 248" aria-hidden="true"><polygon fill="currentColor" points="0,0 123,0 144,124 123,248 0,248 100,124"/></svg>'
ARROW_R = '<svg viewBox="0 0 139 248" aria-hidden="true"><polygon fill="currentColor" points="22,0 139,0 42,124 139,248 22,248 0,124"/></svg>'
CLOSE = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M1 1l14 14M15 1L1 15" stroke="currentColor" stroke-width="1.6"/></svg>'

def tc(sec):
    sec = int(round(sec or 0)); return f'{sec//60:02d}:{sec%60:02d}'

def m(slug): return META.get(slug, {})
def vertical(slug): mm = m(slug); return mm.get('h', 0) > mm.get('w', 1)

def vp(slug, mode='view', base='media'):
    """náhledová smyčka (poster + video na pozadí)"""
    return (f'<div class="vp" data-prev="{base}/prev/{slug}.mp4" data-mode="{mode}">'
            f'<img src="{base}/post/{slug}.jpg" alt="" loading="lazy" decoding="async"></div>')

def full_attrs(slug, title, base='media'):
    if not os.path.exists(os.path.join(ROOT, base, 'full', slug + '.mp4')): return ''
    return (f' data-full="{base}/full/{slug}.mp4" data-poster="{base}/post/{slug}.jpg" data-title="{E(title)}"'
            f' data-vertical="{1 if vertical(slug) else 0}"')

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
<link rel="stylesheet" href="assets/css/site.css?v=1">
</head>
<body>
<a class="sr" href="#obsah">Přeskočit na obsah</a>
'''

def nav(home=False):
    p = '' if home else 'index.html'
    return f'''<header class="nav" id="nav">
  <a class="nav__logo" href="{p or '#top'}" aria-label="Roxfilm – úvod"><img src="assets/logo/logo-white.png" alt="Roxfilm" width="58" height="38"></a>
  <button class="nav__toggle" aria-label="Menu" aria-expanded="false" aria-controls="menu"><span></span></button>
  <ul class="nav__links" id="menu">
    <li><a href="{p}#vysledky">Výsledky</a></li>
    <li><a href="{p}#prace">Práce</a></li>
    <li><a href="{p}#za-kamerou">Za kamerou</a></li>
    <li><a href="{p}#o-nas">O nás</a></li>
    <li><a class="btn btn--ghost" href="{p}#kontakt">Napište nám {ARROW}</a></li>
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
    <div>
      <span class="mono muted"><i class="rec-dot"></i>Kontakt</span>
      <h2 class="h-xl caps" style="margin-top:22px">Napište nám.</h2>
      <p class="lead contact__note">Zavolejte nebo napište. Domluvíme si krátkou schůzku a navrhneme, jak na to.</p>
    </div>
    <ul class="contact__list">
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
    <img src="assets/logo/logo-white.png" alt="Roxfilm" width="46" height="30" loading="lazy">
    <span>Produkce Roxfilm · Brno · točíme kdekoli · © <span data-year>2026</span></span>
    <nav aria-label="Patička">
      <a href="pujcovna.html">Půjčovna techniky</a>
      <a href="https://www.balonio.cz" target="_blank" rel="noopener">Balonio</a>
      <a href="{IG_ROX}" target="_blank" rel="noopener">Instagram</a>
    </nav>
  </div>
</footer>
{PLAYER}<script src="assets/js/site.js?v=1" defer></script>
</body>
</html>
'''

# ---------------- data ----------------
PORTFOLIO = [
  ('drive/kerndl-tesco','Kerndl × Tesco','Spot pro vína Kerndl přímo v prodejně Tesco. Ochutnávka, lidé, emoce.','spot'),
  ('drive/villa-naya','Villa Naya','Luxusní vila v Chorvatsku. Dron, interiér, výhled na moře.','spot'),
  ('drive/richie-flawless-ice','Richie ft. Elkoo – Flawless Ice','Hudební klip. Neon, pohyb, noc.','klip'),
  ('drive/ec-parfums','EC Parfums','Firemní spot z výroby a skladu. Lidé, kteří za značkou stojí.','spot'),
  ('drive/az-tower','AZ Tower – reklamní plocha','Spot pro reklamní plochu na nejvyšší budově v Česku.','spot'),
  ('drive/rich-fouad-lets-slide','Rich Fouad – Let’s Slide','Hudební klip ve formátu kina. Les, západ slunce, město.','klip'),
  ('drive/gymnazium-blansko','Gymnázium Blansko','Trailer pro školu. Třídy, lidé a atmosféra, která přesvědčí uchazeče.','event'),
  ('drive/promoce-fch','Promoce FCH VUT','Promoce Fakulty chemické. Celý obřad v jednom filmu.','event'),
  ('drive/zs-erbenova','ZŠ Erbenova','Video pro základní školu v Blansku.','event'),
  ('opatija-angels','Opatija Angels','Teambuilding a obsah pro majitele vil v Chorvatsku v jednom.','spot'),
  ('porsche','Porsche','Naše první automotive. Kamera riggovaná ze všech stran auta.','spot'),
  ('ben-cristovao-omluva','Ben Cristovao – Omluva','Klip postavený na siluetách. Tanečnice sestavu zatančily 48×.','klip'),
  ('tesco-velikonoce','Tesco – Velikonoce','Velikonoční TV spot. Natáčeno v Castellana Trattoria v Brně.','spot'),
  ('vut-opera','VUT – chemická opera','Tři natáčecí dny, jedna premiéra.','event'),
  ('sergei-barracuda','Sergei Barracuda – Hvězdný prach','Obří jeřáb a několik lokací za dva dny.','klip'),
  ('sarka-stiborova','Šárka Stiborová – chirurgie','Video pro chirurgickou praxi. Klid, preciznost, důvěra.','spot'),
  ('hopa-group','HOPA Group','Letní spot pro developera Jana Musila z Blanska. S kapkou humoru.','spot'),
  ('yzomandias','Yzomandias – koncert','Report z koncertu. Jedna kamera, celý večer v pohybu.','event'),
  ('semspoko','Semspoko','Klip z Vídně. Po něm známe pravidla létání dronem nazpaměť.','klip'),
  ('pandies','Pandies','Módní značka mikin. Elegance v detailu.','spot'),
  ('chorvatsko-spot','Kreativní spot','Akční mindful spot z teambuildingu v Chorvatsku.','spot'),
  ('3d-art','3D art','První klip, kde vznikal 3D svět scénu po scéně.','klip'),
  ('day-vlog','Day vlog','Celý den s klientem v jednom vlogu.','event'),
  ('vlog-workshop','Vlog z workshopu','Workshop od příprav po poslední potlesk.','event'),
]
CATS = [('all','Vše'),('spot','Spoty a reklamy'),('klip','Klipy'),('event','Eventy a instituce')]
# tvůj výběr nejlepších reels (Disk: Finest Invest / Výběr reelů pro pitch) + Villa Naya + Kora
REELS = [
  ('drive/r-vecirek','Firemní večírek'),('polepim/polepim-5','Polepim – wrap'),('drive/r-villa-oresin','Villa Ořešín'),
  ('drive/r-svatojanska-noc','Svatojánská noc – STELAR Advisory'),('polepim/audi-1-broll-warrior','Polepim – Audi'),
  ('drive/r-influland','Report z Influlandu'),('drive/r-eli-prekvapko','Překvapení pro Eli'),('drive/r-gurdau','Gurdau'),
  ('drive/r-attila','Attila'),('drive/r-vzdelavaci','Vzdělávací reels'),('drive/r-villa-naya-3','Villa Naya'),
  ('drive/r-kora-1','Kora × Švancara'),('drive/r-infina','Infina'),('drive/r-ai-tvorba','Tvorba s AI'),
  ('drive/r-reklamni','Reklamní reels'),('drive/r-vut-medailonek','VUT FCH – medailonek'),('drive/r-eli-oslava','Oslava'),
  ('drive/r-villa-naya-1','Villa Naya – dron'),('drive/r-kora-3','Kora – pergola'),('polepim/polepim-8','Polepim – PPF'),
  ('polepim/polepim-2-predni-sklo-chameleon','Polepim – chameleon'),
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
]

def deck(items, label):
    cards = ''.join(
        f'<button class="deck__card" type="button" data-label="{E(t)}"{full_any(r, t)}>{vp_any(r, "deck")}</button>'
        for r, t in items)
    n = len(items)
    return (f'<div class="deck" data-deck tabindex="0" role="region" aria-roledescription="karusel" aria-label="{E(label)}">'
            f'<div class="deck__stage">{cards}</div>'
            f'<div class="deck__ui"><button class="deck__prev" type="button" aria-label="Předchozí">{ARROW}</button>'
            f'<div class="deck__info"><span class="deck__count mono"><b>01</b> / {n:02d}</span><span class="deck__label"></span></div>'
            f'<button class="deck__next" type="button" aria-label="Další">{ARROW}</button></div></div>')

CASES = [
  dict(slug='alux', name='Alux', sub='Hliníkové pergoly', file='alux.html',
       line='Kampaně, reels a produktová videa u skutečných zákazníků. Více než rok pravidelné spolupráce.',
       num='150+', numl='videí pro kampaně a sítě', frame=('h','alux-family')),
  dict(slug='lada', name='Ladislav Bradna', sub='Osobní značka · financování', file='ladislav-bradna.html',
       line='Osobní značka finančního experta od nuly: web, brand manuál, natáčení každý měsíc, sítě.',
       num='4–5', numl='poptávek ze sítí za první čtyři měsíce', frame=('h','lada/vlog')),
  dict(slug='kras', name='Krasochatky', sub='Chatky Jedovnice', file='krasochatky.html',
       line='Brand manuál a veškerý obsah. Celá identita postavená na atmosféře místa.',
       num='300+', numl='materiálů z jednoho vizuálního světa', frame=('r',['kras-r1','kras-r3','kras-r4','kras-r6'])),
  dict(slug='balonio', name='Balonio', sub='Naše vlastní značka', file='balonio.html',
       line='Luxusní fotobox, do kterého se vchází. Vizuál, obsah, sítě i reklama z jednoho týmu.',
       num='7+', numl='výstupů z každé akce', frame=('r',['balonio/recenze-artis','balonio/ples','balonio/lr-realizace','balonio/neon'])),
]

def vp_any(ref, mode='view'):
    """ref 'slug' (staré video) nebo 'lada/x' / 'balonio/x' (nové výstupy)"""
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

# ---------------- úvodní stránka ----------------
def index():
    o = [head('Roxfilm – produkce, která dotáhne i marketing',
              'Video, foto, sítě a reklama z Brna. Jeden tým od nápadu po výsledek. Osobní značky, firmy s příběhem, instituce a eventy.',
              ''), nav(True)]
    # HERO
    o.append(f'''<main id="obsah">
<section class="hero" id="top" data-frames-d="193" data-frames-m="97" data-path-d="assets/hero/d/" data-path-m="assets/hero/m/" aria-label="Úvod">
  <div class="hero__stage">
    <canvas class="hero__canvas" aria-hidden="true"></canvas>
    <img class="hero__poster" data-src="assets/hero/poster.jpg" alt="Kamera RED Komodo-X s objektivem DZOFilm Arles">
    <div class="hero__reel" aria-hidden="true"><video muted loop playsinline preload="none" data-src="media/showreel.mp4" poster="media/showreel.jpg"></video></div>
    <div class="hero__shade"></div>
    <div class="bar bar--top" aria-hidden="true"></div>
    <div class="bar bar--bottom mono" aria-hidden="true"><span class="bar__l">RED Komodo-X · Arles 35 · T1.4</span><span class="rec"><i class="rec-dot"></i>REC</span><span class="tc">00:00:00:00</span></div>
    <div class="hero__copy">
      <span class="mono">Brno · 6 let · 7 lidí</span>
      <h1 class="h-xl caps">Natočíme to.</h1>
      <p class="lead">Video, foto, sítě a reklama. Jeden tým od nápadu po výsledek.</p>
    </div>
    <div class="scrollhint mono" aria-hidden="true">Scrollujte<i></i></div>
    <div class="focus" aria-hidden="true">
      <svg class="fm fm--l" viewBox="0 0 144 248"><polygon fill="currentColor" points="0,0 123,0 144,124 123,248 0,248 100,124"/></svg>
      <p class="focus__line">Zaostřeno na výsledek.</p>
      <svg class="fm fm--r" viewBox="0 0 139 248"><polygon fill="currentColor" points="22,0 139,0 42,124 139,248 22,248 0,124"/></svg>
    </div>
    <div class="hero__end">
      <h2 class="h-m">Natočíme to, postavíme z toho obsah a dostaneme ho k lidem.</h2>
      <a class="btn btn--solid" href="#vysledky">Ukázky práce {ARROW}</a>
    </div>
  </div>
</section>
''')
    # DEFINICE (světlá)
    o.append(f'''<section class="sec sec--light on-light" id="o-produkci">
  <div class="wrap">
    <div class="intro">
      <h2 class="h-l caps">Produkce, která dotáhne i marketing.</h2>
      <div>
        <p class="body">Postaráme se o celý marketing: strategii, natáčení, foto, střih, správu sítí i placenou reklamu. Dobrý obsah nevzniká náhodou, ale zaostřením na jednu myšlenku, jeden záběr, jeden výsledek.</p>
        <p class="body" style="margin-top:18px">Nemusíte skládat tým z pěti dodavatelů. Máte jeden, který to natočí, postaví z toho obsah a dostane ho k lidem, kterým patří.</p>
      </div>
    </div>
    <div class="stats">
      <div class="stat"><b>6</b><span>let na trhu</span></div>
      <div class="stat"><b>7</b><span>lidí v týmu</span></div>
      <div class="stat"><b>1</b><span>dodavatel místo pěti</span></div>
    </div>
    <ol class="chain" style="margin-top:clamp(48px,6vw,80px)" aria-label="Jak pracujeme">
      <li>Strategie</li><li>Natáčení</li><li>Foto</li><li>Střih</li><li>Sítě</li><li>Reklama</li>
    </ol>
    <div class="audience">
      <div><h3>Osobní značky</h3><p>Finanční poradci, makléři, lékaři a odborníci, kteří chtějí být tváří svého oboru.</p><small>Ladislav Bradna · STELAR Advisory · Šárka Stiborová</small></div>
      <div><h3>Firmy s příběhem</h3><p>Gastro, architektura, služby a výroba. Majitel ví, co umí, jen to zatím není vidět.</p><small>Borgo Agnese · Biegun Cafe · Alux · Polepim</small></div>
      <div><h3>Instituce a eventy</h3><p>Školy, obchodní centra a velké firmy, které potřebují točit ve velkém a bez chyby.</p><small>VUT Brno · Tesco · HOPA Group</small></div>
    </div>
  </div>
</section>
''')
    # VÝSLEDKY
    o.append('''<section class="sec" id="vysledky">
  <div class="wrap">
    <div class="sec__head">
      <h2 class="h-l caps">Čísla místo přídavných jmen.</h2>
      <p class="body">Čtyři spolupráce, na kterých je vidět, jak pracujeme. Od prvního natáčecího dne po poptávky.</p>
    </div>
    <div class="cases">
''')
    for i, c in enumerate(CASES, 1):
        kind, ref = c['frame']
        if kind == 'h':
            frame = f'<div class="case__frame">{vp_any(ref)}<div class="case__bars mono"><span><span>Scéna {i:02d}</span><span>{E(c["sub"])}</span></span><span><span><i class="rec-dot"></i>Case study</span><span></span></span></div></div>'
        else:
            frame = '<div class="case__frame case__frame--reels">' + ''.join(vp_any(r) for r in ref) + f'<div class="case__bars mono"><span><span>Scéna {i:02d}</span><span>{E(c["sub"])}</span></span><span><span><i class="rec-dot"></i>Case study</span><span></span></span></div></div>'
        o.append(f'''      <a class="case" href="{c['file']}">
        {frame}
        <div class="case__meta">
          <div><h3 class="h-l caps">{E(c['name'])}</h3><p>{E(c['line'])}</p><span class="link case__cta">Celá case study {ARROW}</span></div>
          <div class="case__num"><b>{E(c['num'])}</b><span>{E(c['numl'])}</span></div>
        </div>
      </a>
''')
    o.append('    </div>\n  </div>\n</section>\n')
    # PORTFOLIO
    o.append('''<section class="sec" id="prace" style="padding-top:0">
  <div class="wrap">
    <div class="sec__head">
      <h2 class="h-l caps">Další práce</h2>
      <p class="body">Spoty, klipy a eventy. Stovky videí od roku 2020, každé s jiným cílem a stejným důrazem na výsledek.</p>
    </div>
    <div class="filters" role="group" aria-label="Filtr portfolia">
''' + ''.join(f'      <button type="button" data-cat="{k}" aria-pressed="{"true" if k=="all" else "false"}">{v}</button>\n' for k, v in CATS) + '''    </div>
    <div class="grid">
''')
    for slug, title, desc, cat in PORTFOLIO:
        o.append(f'''      <button class="item" type="button" data-cat="{cat}"{full_any(slug, title)}>
        <div class="item__frame">{vp_any(slug,'hover')}<span class="item__play mono"><i class="rec-dot"></i>Přehrát</span><span class="item__tc mono">{tc(m(slug).get('dur'))}</span></div>
        <h3>{E(title)}</h3><p>{E(desc)}</p>
      </button>
''')
    o.append('    </div>\n  </div>\n</section>\n')
    # REELS
    o.append(f'''<section class="sec" id="reels" style="padding-top:0">
  <div class="wrap">
    <div class="sec__head">
      <h2 class="h-l caps">Reels</h2>
      <p class="body">Krátká videa pro osobní značky, firmy a eventy. Natočená pro mobil, střižená na první tři vteřiny. Táhněte do strany, klikněte pro zvuk.</p>
    </div>
  </div>
  {deck(REELS, 'Reels od Roxfilmu')}
</section>
''')
    # SPOLUPRÁCE
    o.append('''<section class="cine" aria-label="Dlouhodobá spolupráce">
  <div class="cine__bar mono"><span>Scéna 05</span><span>Take 01</span></div>
  <img class="cine__img" src="assets/img/handshake.jpg" alt="Filip Volf si podává ruku s klientem" loading="lazy">
  <div class="cine__bar mono"><span><i class="rec-dot"></i>Za kamerou</span><span>Brno</span></div>
  <div class="cine__text">
    <h2 class="h-l caps">Zakládáme si na dlouhodobé spolupráci.</h2>
    <p>Dobré video vzniká tam, kde je důvěra. Kde si rozumíme a máme společný cíl. Spolupráce musí dávat smysl oběma stranám.</p>
  </div>
</section>
<section class="sec" style="padding-top:clamp(64px,8vw,120px)">
  <div class="wrap">
    <div class="pillars">
      <div><h3>Řemeslo</h3><p>Záběr je hlavní hrdina. Světlo, zvuk, střih a barva na filmové úrovni.</p></div>
      <div><h3>Celý proces</h3><p>Od strategie po reklamu v jednom týmu. Nic se neztratí mezi dodavateli.</p></div>
      <div><h3>Výsledek</h3><p>Neměříme krásu, ale dopad: dosah, poptávky, klienty.</p></div>
      <div><h3>Klid na placu</h3><p>Scénář připravíme, před kamerou provedeme. Vy jen přijdete a jste sami sebou.</p></div>
    </div>
  </div>
</section>
''')
    # ZA KAMEROU
    bts = [('a','set-theatre','Natáčení v divadle'),('b','set-medical','Natáčení na klinice'),('c','set-interview','Rozhovor na placu'),
           ('d','filip-camera-1','Filip Volf s kamerou'),('e','set-monitor','Kontrola záběru na monitoru'),('f','set-chair','Příprava scény'),
           ('g','set-opera','Natáčení opery'),('h','team-boom','Štáb Roxfilmu při natáčení')]
    o.append('''<section class="sec" id="za-kamerou" style="padding-top:0">
  <div class="wrap">
    <div class="sec__head">
      <h2 class="h-l caps">Za kamerou</h2>
      <p class="body">Skutečné záběry z našich natáčení. Žádná fotobanka. Lidé chtějí vidět, kdo stojí za kamerou.</p>
    </div>
    <div class="bts">
''' + ''.join(f'      <figure class="{c}"><img src="assets/img/{s}.jpg" alt="{E(a)}" loading="lazy" decoding="async"></figure>\n' for c, s, a in bts) + '''    </div>
  </div>
</section>
''')
    # O MNĚ (světlá)
    o.append('''<section class="sec sec--light on-light" id="o-nas">
  <div class="wrap about">
    <img class="about__img" src="assets/img/filip-bw.jpg" alt="Filip Volf, zakladatel Roxfilmu" loading="lazy">
    <div>
      <span class="mono" style="color:var(--graphite)">Zakladatel a CEO</span>
      <h2 class="h-l caps" style="margin-top:18px">Filip Volf</h2>
      <p class="body">Video točí od roku 2020. Propojuje vizuální kvalitu s obchodním přemýšlením: každé video má mít cíl, strategii a výsledek. Posledních pár let se Roxfilm nejvíc věnuje osobním značkám a Instagramu, od strategie po samotný obsah. Vedle Roxfilmu stojí Filip za značkou Balonio.</p>
      <blockquote>„Spolupráci nevnímám jako jednorázovou zakázku, ale jako partnerství, které má dlouhodobý směr.“</blockquote>
      <p class="about__sign">V týmu: projektový manažer, fotograf a grafik, kameraman, střihač a colorista, ilustrátor a správce sítí s Meta reklamou.</p>
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
    if kind == 'h':
        fr = f'<div class="cs-hero__frame">{vp_any(ref)}</div>'
    else:
        fr = '<div class="cs-hero__frame cs-hero__frame--reels">' + ''.join(vp_any(r) for r in ref) + '</div>'
    o.append(f'''<main id="obsah">
<section class="cs-hero">
  {fr}
  <div class="cs-hero__bar mono"><span><i class="rec-dot"></i>Case study</span><span>{E(c['sub'])}</span></div>
</section>
<section class="cs-title">
  <div class="wrap">
    <h1 class="h-xl caps">{E(c['name'])}</h1>
    <p class="lead">{E(d['lead'])}</p>
    <dl class="facts">
''' + ''.join(f'      <div><dt class="mono">{E(k)}</dt><dd>{E(v)}</dd></div>\n' for k, v in d['facts']) + f'''    </dl>
  </div>
</section>
<section class="sec sec--light on-light" style="margin-top:clamp(72px,9vw,140px)">
  <div class="wrap">
    <div class="cut">
      <div><span class="mono" style="color:var(--graphite)">Před</span><h2 class="h-m caps" style="margin-top:14px">Výzva</h2><p class="body" style="color:var(--ink)">{E(d['before'])}</p></div>
      <div><span class="mono" style="color:var(--graphite)">Po</span><h2 class="h-m caps" style="margin-top:14px">Co jsme udělali</h2><ul>''' +
      ''.join(f'<li>{E(x)}</li>' for x in d['did']) + '''</ul></div>
    </div>
    <div class="bignums">
''' + ''.join(f'      <div><b>{E(n)}</b><span>{E(l)}</span></div>\n' for n, l in d['nums']) + '''    </div>
  </div>
</section>
''')
    for blk in d['blocks']:
        t = blk['type']
        o.append(f'<section class="sec" style="padding-bottom:0">\n  <div class="wrap">\n    <div class="sec__head"><h2 class="h-m caps">{E(blk["title"])}</h2>' + (f'<p class="body">{E(blk["text"])}</p>' if blk.get('text') else '<span></span>') + '</div>\n')
        if t == 'videos':
            o.append('    <div class="vgrid">\n')
            for ref, title in blk['items']:
                fa = full_any(ref, title)
                tag = 'button type="button"' if fa else 'div'
                o.append(f'      <{tag} class="item"{fa}><div class="item__frame">{vp_any(ref,"hover")}' + ('<span class="item__play mono"><i class="rec-dot"></i>Přehrát</span>' if fa else '') + f'</div><h3>{E(title)}</h3></{tag.split()[0]}>\n')
            o.append('    </div>\n')
        elif t == 'reels':
            o.append('    <div class="rgrid">\n')
            for ref, title in blk['items']:
                fa = full_any(ref, title)
                tag = 'button type="button"' if fa else 'div'
                o.append(f'      <{tag} class="reel"{fa}><div class="reel__frame">{vp_any(ref,"hover")}</div>' + (f'<p class="muted" style="margin:10px 0 0;font-size:14px">{E(title)}</p>' if blk.get('captions') else '') + f'</{tag.split()[0]}>\n')
            o.append('    </div>\n')
        elif t == 'deck':
            o.append('  </div>\n  ' + deck(blk['items'], blk['title']) + '\n  <div class="wrap">\n')
        elif t == 'photos':
            o.append('    <div class="pgrid">\n' + ''.join(f'      <figure><img src="assets/img/{s}.jpg" alt="{E(a)}" loading="lazy" decoding="async"></figure>\n' for s, a in blk['items']) + '    </div>\n')
        o.append('  </div>\n</section>\n')
    nx = d['next']
    o.append(f'''<section class="sec" style="padding-bottom:0">
  <div class="wrap">
    <a class="next" href="{nx[0]}"><span><span class="mono muted">Další case study</span><span class="h-l caps" style="display:block;margin-top:14px">{E(nx[1])}</span></span>{ARROW}</a>
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
     dict(type='videos', title='Spoty a produktová videa', text='Produkt v reálném prostředí, detail a konzistentní vizuál značky.',
          items=[('alux-family','Rodinný spot'),('alux-1','Realizace'),('alux-3','Produktové video'),('alux-6','Showroom'),('alux-2','Realizace u zákazníka'),('alux-4','Detail produktu')]),
     dict(type='reels', title='Reels', text='Jedna z nejsilnějších komunikačních forem tohoto klienta. Lidé z firmy před kamerou.',
          items=[(f'alux-r{i:02d}', f'Alux – reels {i:02d}') for i in range(1,11)]),
   ],
   next=('ladislav-bradna.html','Ladislav Bradna')),
 'lada': dict(
   desc='Ladislav Bradna – osobní značka finančního experta. Web, brand manuál, měsíčně 8 reels a vlog. Case study Roxfilm.',
   hero=('h','lada/vlog'), og='assets/img/lada-portrait.jpg',
   lead='Osobní značku experta na hypotéky a financování nemovitostí stavíme od června 2026. Nejdřív web, brand manuál a struktura obsahu. Od července natáčíme každý měsíc.',
   facts=[('Klient','Ladislav Bradna'),('Obor','Hypotéky a financování'),('Od','Června 2026'),('Měsíčně','8 reels, 1 vlog, 2–3 karusely')],
   before='Finanční expert s praxí a výsledky, kterého znali hlavně klienti z doporučení. Cíl: aby ho lidé znali dřív, než mu zavolají.',
   did=['Web, brand manuál a struktura obsahu','Témata vymýšlíme spolu s ním, natáčení s klidem na placu','Každý měsíc reels, vlog „Den s Laďou“ a teasery','Sprint 32 dní v kuse: každý den jeden výstup'],
   nums=[('4–5','poptávek ze sítí za první čtyři měsíce'),('8 + 1','reels a vlog každý měsíc'),('32','dní v kuse s denním výstupem')],
   blocks=[
     dict(type='reels', title='Reels', text='Jedno téma, jedna myšlenka, titulky. Otázky, které klienti opravdu řeší.', captions=True,
          items=[('lada/bonita','Bonita a skladba příjmů'),('lada/auto','Nekupuj auto, kup byt'),('lada/deset-milionu','10 milionů a čerpání'),('lada/rozchod','Rozchod a hypotéka'),('lada/teaser-zavody','Teaser: den na závodech')]),
     dict(type='reels', title='Vlog „Den s Laďou“', text='Delší formát na YouTube. Ke každému vlogu teasery před vydáním i po něm.', captions=True,
          items=[('lada/teaser-kojetin','Trailer: Kojetín'),('lada/teaser-flip','Flip nemovitosti za 6 hodin'),('lada/teaser-zavody','Rybářské závody')]),
     dict(type='photos', title='Foto pro web a sítě', items=[('lada-portrait','Ladislav Bradna, portrét'),('lada-process','Ladislav Bradna na ulici'),('lada-about','Ladislav Bradna v zahradě'),('lada-steps','Ladislav Bradna s tabletem')]),
   ],
   next=('krasochatky.html','Krasochatky')),
 'kras': dict(
   desc='Krasochatky, Jedovnice – brand manuál, foto, video a sítě od Roxfilmu. 300+ materiálů z jednoho vizuálního světa.',
   hero=('r',['kras-r1','kras-r2','kras-r3','kras-r4','kras-r6']), og='assets/img/kras-1.jpg',
   lead='Projekt, kde šla značka do hloubky. S majitelem jsme detailně navnímali energii místa, propojení s přírodou a principy feng shui. Z toho vznikl brand manuál a na něj navázal veškerý obsah.',
   facts=[('Klient','Krasochatky, Jedovnice'),('Obor','Ubytování v přírodě'),('Rozsah','Brand manuál, foto, video, sítě'),('Výstupy','300+ materiálů')],
   before='Ukázat ne jen prostor, ale atmosféru. Aby host věděl, jak se tam bude cítit, ještě než přijede.',
   did=['Brand manuál a vizuální směr značky','Fotografie interiérů, detailů a krajiny','Reels a krátká videa pro sítě','Promo materiály ve stejném jazyce'],
   nums=[('300+','materiálů: foto, video, sítě, promo'),('1','vizuální svět napříč všemi kanály')],
   blocks=[
     dict(type='deck', title='Reels a drony', text='Ráno, oheň, čaj, les. Atmosféra místa v pár vteřinách. Včetně série Krasonoš a záběrů z dronu.',
          items=KRAS_DECK),
     dict(type='photos', title='Foto', items=[(f'kras-{i}', 'Krasochatky') for i in (1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19) ]),
   ],
   next=('balonio.html','Balonio')),
 'balonio': dict(
   desc='Balonio – luxusní fotobox, do kterého se vchází. Vlastní značka, pro kterou Roxfilm dělá vizuál, obsah, sítě i reklamu.',
   hero=('r',['balonio/recenze-artis','balonio/ples','balonio/lr-realizace','balonio/recenze-borgo','balonio/neon']), og='assets/img/balonio-1.jpg',
   lead='Balonio není fotokoutek. Je to zážitek, do kterého se vchází. Je to naše vlastní značka a Roxfilm pro ni dělá celý marketing: vizuál, obsah, sítě i reklamu.',
   facts=[('Značka','Balonio'),('Obor','Luxusní fotobox na akce'),('Rozsah','Vizuál, foto, video, sítě, Meta reklama'),('Web','balonio.cz')],
   before='Zážitek, který se na fotce těžko popisuje. A akce, ze kterých jde vytěžit obsah na další týdny, když se na to myslí dopředu.',
   did=['Recenzní reels přímo od klientů na akcích','Realizační videa z eventů','Reklamní videa pro Meta kampaně','Systém: z jedné akce sedm a více výstupů'],
   nums=[('7+','výstupů z každé akce'),('25+','reklamních videí a UGC pro Meta'),('4×','týdně nový obsah na sítích')],
   blocks=[
     dict(type='deck', title='Reklamy, UGC a realizace',
          text='Všechno, co pro Balonio vzniklo do Meta kampaní a na sítě. Táhněte do strany, kliknutím pustíte se zvukem.',
          items=BALONIO_ADS),
     dict(type='reels', title='Recenze klientů', text='Klienti mluví sami za sebe, přímo na akci.', captions=True,
          items=[('balonio/recenze-artis','Recenze – Artis'),('balonio/recenze-borgo','Recenze – Borgo Agnese'),('balonio/recenze-losterie',"Recenze – L'Osteria"),('balonio/recenze-sms','Recenze – SMS')]),
     dict(type='photos', title='Foto', items=[(f'balonio-{i}','Balonio') for i in range(1,8)]),
   ],
   next=('alux.html','Alux')),
}

def page_404():
    o = [head('Stránka nenalezena | Roxfilm','Tahle stránka neexistuje.','404.html'), nav()]
    o.append(f'''<main id="obsah"><section class="sec" style="min-height:80vh;display:flex;align-items:center"><div class="wrap">
<span class="mono muted"><i class="rec-dot"></i>Take 404</span>
<h1 class="h-xl caps" style="margin-top:22px">Tenhle záběr nemáme.</h1>
<p class="lead" style="margin-top:24px;color:var(--screen)">Stránka neexistuje nebo se přesunula.</p>
<p style="margin-top:36px"><a class="btn btn--solid" href="index.html">Zpět na úvod {ARROW}</a></p>
</div></section></main>
''')
    o.append(foot()); return ''.join(o)

def main():
    w = lambda f, s: open(os.path.join(ROOT, f), 'w').write(s)
    w('index.html', index())
    for c in CASES: w(c['file'], case_page(c, CASE_DATA[c['slug']]))
    w('404.html', page_404())
    print('ok')

if __name__ == '__main__':
    main()

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
<span class="mono muted"><i class="rec-dot"></i>Pro klienty</span>
<h1 class="h-xl caps" style="margin-top:22px">Půjčovna techniky</h1>
<p class="lead" style="margin-top:24px;color:var(--screen)">Ceny za den bez DPH. Veškeré kabely, příslušenství a redukce jsou v ceně pronájmu. Rezervace telefonem nebo e-mailem.</p>
<div class="rent">''')
    for cat, rows in RENTAL:
        o.append(f'<div class="rent__cat"><h2 class="h-m caps">{E(cat)}</h2><table><tbody>' +
                 ''.join(f'<tr><td>{E(n)}</td><td class="mono">{p}{' Kč' if p[0].isdigit() else ''}</td></tr>' for n, p in rows) + '</tbody></table></div>')
    o.append(f'''</div>
<div class="rent__set"><div><span class="mono muted">Výhodný set</span><h2 class="h-m caps" style="margin-top:12px">Kamera na den</h2>
<p class="muted" style="margin-top:14px">Sony FX3 nebo A7S III · Sony FE 24–70mm f/2.8 GM II · 4× baterie NP-FZ100 · DJI Ronin RS3 Pro · Ronin battery grip · PolarPro VND 2–5 stop · 2× SD Angelbird V90 256 GB</p></div>
<div class="rent__price"><s>4 450 Kč</s><b>2 500 Kč</b></div></div>
<p style="margin-top:48px"><a class="btn btn--solid" href="tel:{PHONE_TEL}">Rezervovat: {PHONE} {ARROW}</a></p>
</div></section></main>
''')
    o.append(foot()); return ''.join(o)

if __name__ == '__main__':
    open(os.path.join(ROOT, '_tools', 'pujcovna-src.html'), 'w').write(page_rental())

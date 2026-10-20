# Web Roxfilm — roxfilm.cz

Statický web (HTML + CSS + JS), běží na GitHub Pages stejně jako bradnaladislav.cz.

## Struktura
- `index.html` – úvod (scroll animace RED Komodo-X → showreel), výsledky, práce, reels, za kamerou, o nás, kontakt
- `alux.html`, `ladislav-bradna.html`, `krasochatky.html`, `balonio.html` – case studies
- `pujcovna.html` – půjčovna techniky, **zašifrovaná heslem** (StatiCrypt)
- `assets/` – styly, skripty, logo, fotky, snímky úvodní animace (`assets/hero/d` desktop, `assets/hero/m` mobil)
- `media/` – videa: `prev/…` krátké smyčky, `post/…` náhledy, `full/…` a ostatní složky plná videa do přehrávače
- `_tools/build.py` – **všechny texty a seznamy videí jsou tady**; po úpravě spusťte `python3 _tools/build.py`
- `_tools/pujcovna.sh` – úprava/změna hesla půjčovny: `bash _tools/pujcovna.sh "noveheslo"`

Složka `_tools` obsahuje jen generátor; nezašifrovaný zdroj půjčovny se nikdy necommituje (je v `.gitignore` a skript ho po zašifrování maže).

## Nasazení
1. Na GitHubu vytvořte repozitář `roxfilm-web` a nahrajte do něj obsah této složky (`git init`, `git add .`, `git commit`, `git push`).
2. Settings → Pages → Source: *Deploy from a branch*, větev `main`, složka `/ (root)`.
3. Nejdřív si web projděte na `https://ggfilipvolf.github.io/roxfilm/`. Až bude vše OK, v Settings → Pages vyplňte Custom domain `www.roxfilm.cz` (GitHub sám vytvoří soubor `CNAME`) a zapněte *Enforce HTTPS*.
4. U domény (Forpsi) nastavte DNS:
   - `www` → CNAME → `ggfilipvolf.github.io`
   - kořen `roxfilm.cz` → A záznamy `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
5. Až web běží, zrušte předplatné Canvy.

## Videa a limity
GitHub Pages má limit 1 GB na web a 100 MB na soubor. Plná videa jsou proto komprimovaná (max. 60 s ukázky u dlouhých videí).
Kdyby videí přibylo hodně, přesuňte složku `media/` na Cloudflare R2 nebo Bunny CDN a v `_tools/build.py` změňte cestu.

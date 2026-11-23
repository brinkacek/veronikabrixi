# Web veronikabrixi.cz — pokyny pro Clauda

Tento repozitář je web **Veroniky Brixí**, výživové poradkyně a terapeutky klinické naturopatie (Říčany a online). Úpravy zadává hlavně Veronika sama — česky a bez technických znalostí. Komunikuj s ní česky, jednoduše a bez žargonu. Netechnické věci (Git, build, HTML) jí nevysvětluj, pokud se nezeptá; řekni jen, co jsi změnil a kde to uvidí.

## Jak web funguje (pro tebe)

- Statický web na **Netlify**, nasazuje se automaticky z větve `main` na https://veronikabrixi.cz (doména bez www).
- HTML stránky v kořeni a v `blog/` se **generují** skriptem `_build/build.py`. **Nikdy needituj vygenerované HTML přímo** — příští build změnu přepíše.
- Zdroje obsahu:
  - `_build/pages/*.html` — stránky. První řádek je komentář `<!--{json}-->` s metadaty (title, description, ceny v `aside`, `facts`, `faq`, `related`…), zbytek je HTML obsahu.
  - `_build/posts/*.html` — články blogu, stejný formát. Název souboru = adresa článku (`/blog/post/<název>`).
  - `_build/build.py` — společná hlavička, menu (`NAV`), patička, schema, sitemap, robots.
  - `css/style.css`, `js/main.js` — vzhled a drobné skripty.
- Po každé změně zdrojů spusť z kořene repozitáře `python3 _build/build.py` a commitni zdroje **i** vygenerované soubory.

## Pracovní postup (vždy)

1. Vytvoř novou větev (např. `uprava-ceny-akutni-dotaz`). **Nikdy necommituj ani nepushuj přímo do `main`.**
2. Uprav zdroje v `_build/…`, spusť `python3 _build/build.py`.
3. Zkontroluj `git diff` — mění se jen to, co Veronika chtěla.
4. Pushni větev a otevři **pull request** do `main` s českým názvem a krátkým popisem změn srozumitelným pro Veroniku.
5. Netlify k pull requestu za 1–2 minuty vytvoří náhled na adrese `https://deploy-preview-<číslo PR>--veronikabrixi.netlify.app`. Pošli Veronice odkaz na náhled a konkrétní stránku, kde změnu uvidí.
6. **Sluč do `main` jen tehdy, když to Veronika výslovně potvrdí** („ano, nasaď“, „pusť to ven“ apod.). Sloučením jde změna naostro.

Když si nejsi jistý, co přesně chce, nejdřív se zeptej. Raději jedna otázka navíc než špatná změna na živém webu.

## Kde co měnit

| Co | Kde |
|---|---|
| Texty stránky služby / testu | `_build/pages/<stránka>.html` (obsah pod metadaty) |
| Cena služby | **na všech místech zároveň** — viz níže |
| Časté dotazy u služby | pole `faq` v metadatech dané stránky (stránka Časté dotazy se z nich skládá sama) |
| Obecné časté dotazy | `faq` v `_build/pages/index.html` |
| Položky menu a jejich popisky | `NAV` v `_build/build.py` |
| Patička | `FOOTER` v `_build/build.py` |
| Kontaktní údaje | `FOOTER` v `build.py`, `_build/pages/kontakt.html`, schema v `_build/pages/index.html`, `llms.txt` |
| Reference klientek | `_build/pages/index.html` (sekce Reference) |
| Text „O mně“, vzdělání | `_build/pages/o-mne.html` |

### Změna ceny — musí sedět všude

Cena služby se objevuje na více místech. Při změně ji uprav ve všech a pak je projdi hledáním staré ceny (`grep -rn "1 990" _build llms.txt`):

1. stránka služby: `aside.price`, `aside.priceValue` (číslo bez mezer), `facts`, případně text a `faq`
2. karty služeb na úvodní stránce `_build/pages/index.html`
3. rozcestník `_build/pages/sluzby.html` nebo `_build/pages/testy.html`
4. karty v `related` na ostatních stránkách služeb
5. popisky v menu `NAV` v `_build/build.py`
6. `llms.txt` (souhrn pro AI vyhledávače)

Ceny piš ve tvaru `1 990 Kč` (nezlomitelná mezera není nutná, ale mezera mezi tisíci ano).

## Nový článek na blog

1. Zkopíruj kterýkoli soubor z `_build/posts/` pod novým názvem: krátký, malými písmeny, bez diakritiky, slova oddělená pomlčkou, např. `vitamin-d-v-zime-jak-na-nej.html`.
2. Uprav metadata:
   - `title` (do ~60 znaků, končí ` | Veronika Brixí`), `h1`, `description` (do ~155 znaků, výstižný popis s klíčovými slovy),
   - `category` (např. Výživa, Suplementace, Imunita · Děti, DNA test),
   - `teaser` (1 věta na kartu článku), `imgAlt` (popis obrázku),
   - `related` = `["/adresa-sluzby", "Název služby", "krátký popis"]` — služba, která k článku nejlépe sedí,
   - `order` = o 1 menší než nejnižší `order` mezi stávajícími články (nejnižší číslo je na blogu první, na úvodní stránce se ukazují první tři).
3. Obsah piš jako HTML (`<p>`, `<h2>`, `<h3>`, `<ul><li>`, `<strong>`, `<blockquote>`). Žádné `<h1>` v obsahu, žádné inline styly.
4. Obrázek: `pip install pillow` (pokud chybí) a `python3 _build/obrazek.py <název-článku> <cesta-k-obrázku>`. Vytvoří všechny tři potřebné velikosti. Obrázek musí být Veroničin vlastní nebo s licencí k volnému použití (např. Pexels, Unsplash) — nikdy nestahuj cizí obrázky z webu bez licence.
5. Build, kontrola, pull request (postup výše).

**Datum se u článků nikde nezobrazuje** — nepřidávej ho do textu, metadat ani schema.

Pokud Veronika chce, abys článek napsal: piš v první osobě jejím hlasem (žena: „doporučuji“, „ráda vám pomohu“), lidsky, prakticky a bez extrémů. Fakta neověřená z důvěryhodných zdrojů nevymýšlej. Na konec článku nepiš vlastní výzvu ke kontaktu — šablona ji přidá sama.

## Obsahová pravidla

- Veronika **není lékařka**. Nikdy nepiš, že diagnostikuje, léčí nebo vyléčí nemoc, ani neslibuj výsledky. Služby mají podpůrný a preventivní charakter. Právní upozornění na stránkách služeb neodstraňuj.
- Nevymýšlej fakta o službách (ceny, délky, postupy, laboratoře). Co nevíš, zjisti od Veroniky.
- Tón: klidný, empatický, srozumitelný, bez dogmat a bez marketingových superlativů.
- Česká typografie: uvozovky „takto“, pomlčka – nebo — mezi slovy, mezera mezi číslem a jednotkou (`90 min`, `500 Kč`).

## Vzhled

Drž stávající design, neměň barvy, písma ani rozložení, pokud o to Veronika výslovně nepožádá.

- Barvy (proměnné v `css/style.css`): šalvějová `#4A6741` (hlavní), terakota `#A9532F` (akcent), krémové pozadí `#F7F2EA`, text `#22261F`.
- Písma: **Fraunces** (nadpisy), **DM Sans** (text) — hostovaná lokálně ve `fonts/`.
- Používej existující třídy (`card`, `checks`, `steps`, `faq`, `btn btn-primary`, `callout`, `prose`…). Ikony jako tenké SVG, **žádné emoji**.
- Web musí fungovat na mobilu. Po vizuální změně zkontroluj šířku 375 px i desktop.

## SEO a GEO — neporušit

- Adresy stránek neměň. Když je změnit musíš, přidej přesměrování `301` do `_redirects`.
- Každá stránka má unikátní `title` a `description`; canonical i schema generuje `build.py` (doména bez www).
- `sitemap.xml`, `robots.txt` a hlavičky se generují buildem — neupravuj je ručně.
- Při nové službě nebo změně nabídky aktualizuj i `llms.txt`.

## Co zatím chybí (doplnit, až Veronika dodá podklady)

- **Platba a storno podmínky** — přidat jako otázku do obecného FAQ v `_build/pages/index.html`.
- **Vzorový report DNA Health** — nahrát PDF do `files/` a odkomentovat blok „Ukázka reportu“ v `_build/pages/dna-test.html` (název souboru v odkazu upravit podle skutečného).
- Texty 3měsíčního programu a stránky Přednášky napsal Claude — Veronika je má zkontrolovat.

## Na co nesahat

- `googlebffcc84bc8e5a977.html` (ověření Google Search Console), `_redirects` (jen přidávat), `files/E-book_Pruvodce_imunitou.pdf`, kontaktní formulář (`name="contact"` a jeho pole — na ně jsou navázané e-mailové notifikace v Netlify).
- Nastavení Netlify, DNS ani e-mailu se tento repozitář netýká — při takovém požadavku odkaž Veroniku na Martina.

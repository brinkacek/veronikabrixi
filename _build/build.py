#!/usr/bin/env python3
"""Generátor statického webu veronikabrixi.cz.

Obsah stránek je v _build/pages/*.html a články v _build/posts/*.html.
Každý soubor začíná řádkem <!--{json}--> s metadaty; zbytek je HTML obsahu.
Spuštění z kořene repozitáře:  python3 _build/build.py
Výstup se zapisuje přímo do kořene (index.html, o-mne.html, blog/…),
plus sitemap.xml, robots.txt a llms.txt.

Postup úprav a přidávání článků popisuje CLAUDE.md v kořeni repozitáře.
"""
import datetime
import hashlib
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_build")
SITE = "https://veronikabrixi.cz"
TODAY = datetime.date.today().isoformat()


def _asset_version():
    """Otisk CSS a JS: při jejich změně se sám změní a prohlížeče načtou novou verzi."""
    h = hashlib.sha1()
    for f in ("css/style.css", "js/main.js"):
        with open(os.path.join(ROOT, f), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:10]


ASSET_V = _asset_version()
BIZ = SITE + "/#business"
PERSON = SITE + "/#veronika"

NAV = [
    ("o-mne", "O mně", "/o-mne", []),
    ("sluzby", "Služby", "/sluzby", [
        ("uvodni", "Úvodní komplexní konzultace", "/uvodni-komplexni-konzultace", "90 min · 1 990 Kč"),
        ("program", "3měsíční program", "/3-mesicni-program", "Postupné změny s podporou"),
        ("akutni", "Akutní dotaz", "/akutni-dotaz", "Rychlá odpověď · 400 Kč"),
        ("suplementace", "Chytrá suplementace", "/chytra-suplementace", "Doplňky na míru · 990 Kč"),
        ("krev", "Rozbor krevních výsledků", "/mini-rozbor-krevnich-vysledku", "Výsledky lidsky · 500 Kč"),
    ]),
    ("testy", "Testy", "/testy", [
        ("dna", "DNA Health", "/dna-test", "Genetický test · 9 990 Kč"),
        ("stolice", "Test ze stolice", "/test-ze-stolice", "Biovis Diagnostik"),
    ]),
    ("prednasky", "Přednášky", "/prednasky", []),
    ("blog", "Blog", "/blog/", []),
]

LEAF = ('<svg width="{s}" height="{s}" viewBox="0 0 64 64" aria-hidden="true">'
        '<path d="M31 60C31 46 30 32 34 10" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round"/>'
        '<ellipse cx="22" cy="42" rx="10" ry="4.6" transform="rotate(-32 22 42)" fill="{c}"/>'
        '<ellipse cx="42" cy="31" rx="10" ry="4.6" transform="rotate(32 42 31)" fill="{c}"/>'
        '<ellipse cx="25" cy="20" rx="8.5" ry="4" transform="rotate(-48 25 20)" fill="{a}"/></svg>')

ICONS = {
    "arrow": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "download": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>',
    "mail": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
    "phone": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
    "pin": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    "insta": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8" fill="currentColor"/></svg>',
    "shield": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z"/></svg>',
    "wave": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="8"/><path d="M4.5 12c2.5-3 5-3 7.5 0s5 3 7.5 0"/></svg>',
    "apple": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 7c-3-2-7 0-7 5 0 4 3 8 5 8 1 0 1.5-.5 2-.5s1 .5 2 .5c2 0 5-4 5-8 0-5-4-7-7-5z"/><path d="M12 7c0-2 1-3 3-4"/></svg>',
    "heart": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/></svg>',
    "leaf": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 19c0-8 6-14 14-14 0 8-6 14-14 14z"/><path d="M5 19l7-7"/></svg>',
    "sprout": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21v-8"/><path d="M12 13c0-4 3-6 7-6 0 4-3 6-7 6z"/><path d="M12 13c0-3-2-5-6-5 0 3 2 5 6 5z"/></svg>',
    "chev": '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>',
}


def esc(s):
    return html.escape(s, quote=True)


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def url(path):
    return SITE + path


def read_src(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"\s*<!--(\{.*?\})-->\s*", raw, re.S)
    if not m:
        sys.exit("Chybí metadata v " + path)
    return json.loads(m.group(1)), raw[m.end():]


def expand(body):
    """{{icon:name}} a {{leaf:size}} zkratky v obsahu."""
    body = re.sub(r"\{\{icon:(\w+)\}\}", lambda m: ICONS[m.group(1)], body)
    body = re.sub(r"\{\{leaf:(\d+)\}\}", lambda m: LEAF.format(s=m.group(1), c="var(--primary)", a="var(--accent)"), body)
    return body


# ---------- layout ----------

def header(active):
    items = []
    mob = []
    for key, label, href, sub in NAV:
        cur = ' aria-current="page"' if key == active or any(k == active for k, *_ in sub) else ""
        if sub:
            dd = "".join(
                f'<li><a href="{h}"{" aria-current=\"page\"" if k == active else ""}>{esc(l)}<small>{esc(d)}</small></a></li>'
                for k, l, h, d in sub)
            items.append(f'<li class="has-dd"><a class="top" href="{href}"{cur}>{label}{ICONS["chev"]}</a>'
                         f'<ul class="dropdown">{dd}</ul></li>')
            msub = "".join(f'<li><a href="{h}">{esc(l)}</a></li>' for k, l, h, d in sub)
            mob.append(f'<li><a href="{href}"{cur}>{label}</a><ul class="sub">{msub}</ul></li>')
        else:
            items.append(f'<li><a class="top" href="{href}"{cur}>{label}</a></li>')
            mob.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return f'''<a class="skip" href="#obsah">Přeskočit na obsah</a>
<header class="site-header">
  <div class="wrap nav">
    <a class="logo" href="/" aria-label="Veronika Brixí — úvodní stránka">
      {LEAF.format(s=34, c="#4A6741", a="#A9532F")}
      <span class="logo-text"><span class="logo-name">Veronika Brixí</span><span class="logo-tag">Klinická naturopatie · výživa</span></span>
    </a>
    <nav aria-label="Hlavní navigace">
      <ul class="menu">
        {"".join(items)}
        <li><a class="btn btn-primary" href="/kontakt"{' aria-current="page"' if active == "kontakt" else ""}>Kontakt</a></li>
      </ul>
    </nav>
    <button class="burger" type="button" aria-expanded="false" aria-controls="mobilni-menu" aria-label="Otevřít menu">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
  </div>
  <nav class="mobile-nav" id="mobilni-menu" aria-label="Mobilní navigace">
    <ul>{"".join(mob)}<li><a href="/caste-dotazy">Časté dotazy</a></li></ul>
    <a class="btn btn-primary" href="/kontakt">Kontaktovat Veroniku</a>
  </nav>
</header>'''


FOOTER = f'''<footer class="site-footer">
  <div class="wrap">
    <div class="foot">
      <div class="brand">
        <span class="logo-name" style="color:#fff">Veronika Brixí</span>
        <p>Výživová poradkyně a terapeutka klinické naturopatie. Konzultace online, v Říčanech a v Praze-východ.</p>
      </div>
      <div><h2>Služby</h2><ul>
        <li><a href="/uvodni-komplexni-konzultace">Úvodní konzultace</a></li>
        <li><a href="/3-mesicni-program">3měsíční program</a></li>
        <li><a href="/akutni-dotaz">Akutní dotaz</a></li>
        <li><a href="/chytra-suplementace">Chytrá suplementace</a></li>
        <li><a href="/mini-rozbor-krevnich-vysledku">Rozbor krevních výsledků</a></li>
        <li><a href="/prednasky">Přednášky pro firmy</a></li></ul></div>
      <div><h2>Testy a čtení</h2><ul>
        <li><a href="/dna-test">DNA Health</a></li>
        <li><a href="/test-ze-stolice">Test ze stolice</a></li>
        <li><a href="/e-booky">E-booky</a></li>
        <li><a href="/blog/">Blog</a></li></ul></div>
      <div><h2>Kontakt</h2><ul>
        <li><a href="mailto:konzultace@veronikabrixi.cz">konzultace@veronikabrixi.cz</a></li>
        <li><a href="tel:+420723263623">+420 723 263 623</a></li>
        <li><a href="https://www.instagram.com/veronika.zdravi.celostne/" rel="noopener" target="_blank">Instagram</a></li>
        <li><a href="/caste-dotazy">Časté dotazy</a></li>
        <li><a href="/prirodni-medicina-a-naturopatie-v-ricanech-a-praze-vychod">Říčany &amp; Praha-východ</a></li></ul></div>
    </div>
    <div class="foot-bottom">
      <span>© 2026 Veronika Brixí</span>
      <span>Služby mají podpůrný a preventivní charakter a nenahrazují lékařskou péči.</span>
    </div>
  </div>
</footer>'''


def head(meta, canonical, og_image, schema):
    title = meta["title"]
    desc = meta["description"]
    return f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{'<meta name="robots" content="noindex">' if meta.get("noindex") else ""}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{meta.get("ogType", "website")}">
<meta property="og:locale" content="cs_CZ">
<meta property="og:site_name" content="Veronika Brixí">
<meta property="og:title" content="{esc(meta.get("ogTitle", title))}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F7F2EA">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/fonts/dm-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/fraunces-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/style.css?v={ASSET_V}">
<script src="/js/main.js?v={ASSET_V}" defer></script>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>
</head>
<body>'''


def crumbs_html(crumbs):
    lis = []
    for i, (name, href) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            lis.append(f'<li aria-current="page">{esc(name)}</li>')
        else:
            lis.append(f'<li><a href="{href}">{esc(name)}</a></li>')
    return f'<nav aria-label="Drobečková navigace"><ol class="crumbs">{"".join(lis)}</ol></nav>'


def crumbs_schema(crumbs):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": url(h)} for i, (n, h) in enumerate(crumbs)]}


def faq_html(faq, title="Časté dotazy", intro=None):
    items = "".join(
        f'<details><summary>{esc(q)}</summary><div class="answer">{a}</div></details>' for q, a in faq)
    return items


def faq_schema(faq):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faq]}


LEGAL = ('<p class="legal"><strong>Upozornění:</strong> Moje služby mají podpůrný a preventivní charakter a nenahrazují '
         'lékařskou péči ani zdravotní služby ve smyslu zákona č. 372/2011 Sb. Nejsem lékařka a neposkytuji zdravotní '
         'diagnostiku, léčbu ani předepisování léčiv. V případě zdravotních obtíží vždy doporučuji konzultaci s vaším '
         'ošetřujícím lékařem.</p>')

CTA = '''<section class="section--tight"><div class="wrap">
  <div class="cta-panel">
    <h2>{h}</h2>
    <p>{p}</p>
    <div class="btns">
      <a class="btn btn-light" href="/kontakt">Napsat zprávu</a>
      <a class="btn btn-ghost-light" href="tel:+420723263623">+420 723 263 623</a>
    </div>
  </div>
</div></section>'''


def cta(h="Udělejte první krok. Zbytek půjdeme spolu.", p="Napište mi nebo zavolejte. Obvykle odpovídám do 24–48 hodin."):
    return CTA.format(h=h, p=p)


# ---------- page renderers ----------

ALL_FAQ = []  # (group, q, a, href) for /caste-dotazy
PAGES = []    # (path, priority) for sitemap


def write(path_out, html_text):
    full = os.path.join(ROOT, path_out)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html_text)


def biz_ref():
    return {"@id": BIZ}


def render_service(meta, body):
    path = meta["path"]
    crumbs = meta["crumbs"]
    faq = meta.get("faq", [])
    for q, a in faq:
        ALL_FAQ.append((meta["faqGroup"], q, a, path))
    aside = meta["aside"]
    price_cls = "price price--text" if aside.get("priceText") else "price"
    inc = "".join(f"<li>{x}</li>" for x in aside["includes"])
    facts = "".join(f'<span class="fact">{f}</span>' for f in meta.get("facts", []))
    related = meta.get("related", [])
    rel_html = ""
    if related:
        cards = "".join(
            f'<a class="card card--line" href="{h}"><span class="meta">{esc(m)}</span><h3>{esc(t)}</h3>'
            f'<p class="grow">{esc(d)}</p><span class="more">Detail →</span></a>' for h, t, m, d in related)
        rel_html = f'''<section class="section section--soft"><div class="wrap stack-lg">
  <div class="head"><span class="eyebrow">Mohlo by vás zajímat</span><h2>Další možnosti spolupráce</h2></div>
  <div class="grid-3">{cards}</div></div></section>'''
    faq_block = ""
    if faq:
        faq_block = f'''<section id="dotazy"><h2>Časté dotazy</h2><div class="faq">{faq_html(faq)}</div></section>'''
    offer = {"@type": "Offer", "priceCurrency": "CZK", "availability": "https://schema.org/InStock", "url": url(path)}
    if aside.get("priceValue"):
        offer["price"] = aside["priceValue"]
    service = {"@type": "Service", "@id": url(path) + "#sluzba", "name": meta["h1"], "description": meta["description"],
               "serviceType": meta.get("serviceType", meta["h1"]), "provider": biz_ref(),
               "areaServed": ["Říčany", "Praha-východ", "Praha", "Česká republika"], "offers": offer, "url": url(path)}
    graph = [service, crumbs_schema(crumbs)]
    if faq:
        graph.append(faq_schema(faq))
    schema = {"@context": "https://schema.org", "@graph": graph}
    out = head(meta, url(path), meta.get("og", SITE + "/img/og/default.jpg"), schema)
    out += header(meta["nav"])
    out += f'''
<main id="obsah">
<section class="page-hero"><div class="wrap">
  {crumbs_html(crumbs)}
  <div class="head">
    <span class="eyebrow">{esc(meta["eyebrow"])}</span>
    <h1>{meta["h1"]}</h1>
    <p class="lead">{meta["lead"]}</p>
    {f'<div class="facts">{facts}</div>' if facts else ""}
  </div>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap svc">
  <div class="svc-main">
{expand(body)}
{faq_block}
{LEGAL}
  </div>
  <aside class="aside" aria-label="Shrnutí služby">
    <span class="eyebrow">{esc(aside.get("label", "Cena"))}</span>
    <span class="{price_cls}">{aside["price"]}</span>
    {f'<span class="note">{aside["note"]}</span>' if aside.get("note") else ""}
    <hr>
    <ul class="checks checks--sm">{inc}</ul>
    <a class="btn btn-primary" href="{aside.get("ctaHref", "/kontakt?tema=" + meta["nav"])}">{aside.get("cta", "Domluvit konzultaci")}</a>
    <span class="alt">nebo zavolejte <a href="tel:+420723263623">+420 723 263 623</a></span>
  </aside>
</div></section>
{rel_html}
{cta(meta.get("ctaH", "Nevíte, co vybrat? Napište mi."), meta.get("ctaP", "Ráda vám poradím, která forma spolupráce bude pro vás nejvhodnější. Obvykle odpovídám do 24–48 hodin."))}
</main>
{FOOTER}
</body>
</html>
'''
    write(meta["file"], out)
    PAGES.append((path, meta.get("priority", "0.8")))


def render_plain(meta, body):
    path = meta["path"]
    crumbs = meta.get("crumbs")
    graph = list(meta.get("schema", []))
    if crumbs:
        graph.append(crumbs_schema(crumbs))
    faq = meta.get("faq")
    if faq:
        graph.append(faq_schema(faq))
        for q, a in faq:
            ALL_FAQ.append((meta.get("faqGroup", "Obecné"), q, a, path))
        body = body.replace("{{faq}}", faq_html(faq))
    if "{{allfaq}}" in body:
        body = body.replace("{{allfaq}}", "")  # filled in second pass
    schema = {"@context": "https://schema.org", "@graph": graph}
    hero = ""
    if meta.get("h1"):
        hero = f'''<section class="page-hero"><div class="wrap">
  {crumbs_html(crumbs) if crumbs else ""}
  <div class="head"><span class="eyebrow">{esc(meta["eyebrow"])}</span><h1>{meta["h1"]}</h1>
  {f'<p class="lead">{meta["lead"]}</p>' if meta.get("lead") else ""}</div>
</div></section>'''
    out = head(meta, url(path), meta.get("og", SITE + "/img/og/default.jpg"), schema)
    out += header(meta.get("nav", ""))
    out += f'\n<main id="obsah">\n{hero}\n{expand(body)}\n'
    if not meta.get("noCta"):
        out += cta(meta.get("ctaH", "Udělejte první krok. Zbytek půjdeme spolu."),
                   meta.get("ctaP", "Napište mi nebo zavolejte. Obvykle odpovídám do 24–48 hodin."))
    out += f"\n</main>\n{FOOTER}\n</body>\n</html>\n"
    write(meta["file"], out)
    if meta.get("sitemap", True):
        PAGES.append((path, meta.get("priority", "0.7")))
    return out


POSTS = []


def render_post(slug, meta, body):
    path = f"/blog/post/{slug}"
    crumbs = [("Úvod", "/"), ("Blog", "/blog/"), (meta["h1"], path)]
    img = f"/img/blog/{slug}.jpg"
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "BlogPosting", "@id": url(path) + "#clanek", "headline": meta["h1"], "description": meta["description"],
         "image": url(img), "url": url(path), "inLanguage": "cs", "mainEntityOfPage": url(path),
         "articleSection": meta["category"], "author": {"@id": PERSON}, "publisher": biz_ref()},
        crumbs_schema(crumbs)]}
    meta = dict(meta, ogType="article")
    out = head(meta, url(path), f"{SITE}/img/og/blog-{slug}.jpg", schema)
    out += header("blog")
    rel = meta.get("related")
    rel_html = ""
    if rel:
        rel_html = f'<p class="callout">Související služba: <a href="{rel[0]}"><strong>{esc(rel[1])}</strong></a> — {esc(rel[2])}</p>'
    out += f'''
<main id="obsah">
<article>
<section class="page-hero"><div class="wrap" style="max-width:860px">
  {crumbs_html(crumbs)}
  <div class="head" style="max-width:none"><span class="eyebrow">{esc(meta["category"])}</span><h1>{meta["h1"]}</h1>
  <p class="lead muted">{esc(meta["description"])}</p></div>
</div></section>
<div class="article-hero"><img src="{img}" alt="{esc(meta["imgAlt"])}" width="1600" height="900"></div>
<div class="wrap"><div class="article">
  <div class="prose">
{body.strip()}
  </div>
  <div class="stack" style="margin-top:48px">
    {rel_html}
    <div class="author">
      <img src="/img/veronika-portret.jpg" alt="" width="64" height="64" loading="lazy">
      <div><b>Veronika Brixí</b><span>Výživová poradkyně a terapeutka klinické naturopatie</span></div>
    </div>
  </div>
</div></div>
</article>
{{{{related_posts}}}}
{cta("Chcete to řešit na míru?", "Obecné rady jsou dobrý začátek. Na konzultaci se podíváme přímo na vaši situaci.")}
</main>
{FOOTER}
</body>
</html>
'''
    POSTS.append({"slug": slug, "path": path, "meta": meta, "html": out})
    PAGES.append((path, "0.6"))


def post_card(p, small=True):
    m = p["meta"]
    return (f'<a class="post-card" href="{p["path"]}"><img src="/img/blog/{p["slug"]}-sm.jpg" alt="" width="900" height="600" loading="lazy">'
            f'<span class="body"><span class="cat">{esc(m["category"])}</span><h3>{m["h1"]}</h3>'
            f'<p>{esc(m["teaser"])}</p></span></a>')


def main():
    # posts first (homepage + blog index need them)
    pdir = os.path.join(SRC, "posts")
    for fn in sorted(os.listdir(pdir)):
        if fn.endswith(".html"):
            meta, body = read_src(os.path.join(pdir, fn))
            render_post(fn[:-5], meta, body)
    POSTS.sort(key=lambda p: p["meta"].get("order", 99))
    for p in POSTS:
        others = [o for o in POSTS if o is not p][:3]
        rp = (f'<section class="section section--soft"><div class="wrap stack-lg"><div class="head"><span class="eyebrow">Blog</span>'
              f'<h2>Další články</h2></div><div class="grid-3">{"".join(post_card(o) for o in others)}</div></div></section>')
        write(p["path"].lstrip("/") + ".html", p["html"].replace("{{related_posts}}", rp))

    pages = []
    for fn in sorted(os.listdir(os.path.join(SRC, "pages"))):
        if fn.endswith(".html"):
            meta, body = read_src(os.path.join(SRC, "pages", fn))
            pages.append((meta, body))
    pages.sort(key=lambda mb: 1 if "{{allfaq}}" in mb[1] else 0)  # FAQ hub last
    for meta, body in pages:
        body = body.replace("{{posts3}}", "".join(post_card(p) for p in POSTS[:3]))
        body = body.replace("{{posts_all}}", "".join(post_card(p) for p in POSTS))
        if "{{allfaq}}" in body:
            groups = {}
            for g, q, a, href in ALL_FAQ:
                groups.setdefault(g, []).append((q, a, href))
            parts = []
            for g, items in groups.items():
                det = "".join(
                    f'<details><summary>{esc(q)}</summary><div class="answer">{a}'
                    + (f'<p><a class="link-arrow" href="{h}">Více na stránce služby →</a></p>' if h not in ("/", "/caste-dotazy") else "")
                    + "</div></details>" for q, a, h in items)
                parts.append(f'<section class="stack"><h2 style="font-size:1.7rem">{esc(g)}</h2><div class="faq">{det}</div></section>')
            body = body.replace("{{allfaq}}", "".join(parts))
            meta = dict(meta)
            meta.setdefault("schema", [])
            meta["schema"] = meta["schema"] + [faq_schema([(q, a) for g, q, a, h in ALL_FAQ])]
        if meta.get("layout") == "service":
            render_service(meta, body)
        else:
            render_plain(meta, body)

    # sitemap, robots, llms
    seen = set()
    rows = []
    for path, prio in sorted(PAGES, key=lambda x: (x[0] != "/", x[0])):
        if path in seen:
            continue
        seen.add(path)
        rows.append(f"  <url><loc>{url(path)}</loc><lastmod>{TODAY}</lastmod><priority>{prio}</priority></url>")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "\n".join(rows) + "\n</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /_build/\n\nSitemap: {SITE}/sitemap.xml\n")
    print(f"OK: {len(PAGES)} stránek, {len(POSTS)} článků, {len(ALL_FAQ)} FAQ")


if __name__ == "__main__":
    main()

"""Builds the treatment pages, blog articles, blog index and sitemap.

Content lives in content/pages.py. The shared header, footer, mobile bar and
styles are copied from index.html, so pages always match the homepage.

Run:  python build.py
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content'))
from pages import TREATMENTS, POSTS  # noqa: E402
from product_uses import USES  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://www.aandzclinic.com'
NAME = 'A&Z Healthcare Centre'
WA = 'https://wa.me/917208433163?text=Assalamualaikum%2C%20I%20would%20like%20to%20book%20a%20visit%20at%20A%26Z%20Healthcare%20Centre.'
LASTMOD = '2026-11-24'
e = html.escape

home = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
style = re.search(r'<style>(.*?)</style>', home, re.S).group(1)
fonts = re.search(r'<link rel="preconnect" href="https://fonts.googleapis.com">.*?rel="stylesheet">', home, re.S).group(0)


def sitewide(block):
    block = block.replace('href="#top"', 'href="/"')
    return re.sub(r'href="#([a-z]+)"', r'href="/#\1"', block)


header = sitewide(re.search(r'<header>.*?</header>', home, re.S).group(0))
footer = sitewide(re.search(r'<div class="band" aria-hidden="true"></div>\n<footer>.*?</footer>', home, re.S).group(0))
mbar = re.search(r'<div class="mbar".*?</div>\n<a class="wa" id="waFloat".*?</a>', home, re.S).group(0)
assert 'base64' not in header + footer + mbar

EXTRA_CSS = '''
.crumbs{font-size:14px;color:var(--muted);margin-bottom:22px}
.crumbs a{color:var(--green-700);text-decoration:none;font-weight:500}
.crumbs a:hover{text-decoration:underline}
.prose{max-width:760px}
.prose h2{font-size:clamp(23px,3vw,28px);margin:38px 0 12px}
.prose p{margin-bottom:18px;font-size:17.5px;line-height:1.8;color:var(--ink)}
.prose ul{margin:0 0 20px 0;padding-left:22px}
.prose li{margin-bottom:8px;font-size:17px;line-height:1.7}
.prose li::marker{color:var(--gold)}
.related{margin-top:26px;padding:14px 18px;background:var(--cream-2);border-left:3px solid var(--gold);border-radius:8px;font-size:16px!important}
.related a{color:var(--green-700);font-weight:600;text-decoration:none}
.related a:hover{text-decoration:underline}
.art-cta{margin:44px 0 10px;background:var(--green-900);color:#fff;border-radius:var(--radius);padding:28px 30px;position:relative;overflow:hidden;border:2px solid var(--gold)}
.art-cta::before{content:"";position:absolute;inset:0;background-image:var(--geo-gold);background-size:80px;opacity:.3;pointer-events:none}
.art-cta>*{position:relative}
.art-cta h2{color:#fff;font-size:24px;margin:0 0 8px}
.art-cta p{color:#d6e4da!important;font-size:16px!important;margin-bottom:18px!important}
.art-cta .btn{background:var(--gold);border-color:var(--gold);color:#fff}
.art-note{font-size:13.5px!important;color:var(--muted)!important;border-top:1px solid var(--line);padding-top:16px;margin-top:28px}
.more-posts{background:var(--cream-2);padding:64px 0 80px}
.more-posts h2{font-size:clamp(24px,3vw,30px)}
.t-hero{padding:56px 0 40px}
.t-hero .grid{display:grid;grid-template-columns:1.2fr .8fr;gap:48px;align-items:center}
.t-hero h1{font-size:clamp(32px,4.6vw,50px);margin:8px 0 16px}
.t-hero .lead{font-size:18.5px}
.t-hero .acts{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}
.t-img{border-radius:160px 160px 16px 16px;overflow:hidden;aspect-ratio:4/4.4;box-shadow:0 0 0 3px var(--cream),0 0 0 5px var(--gold);max-width:380px;justify-self:center;width:100%}
.t-img img{width:100%;height:100%;object-fit:cover;display:block}
.t-body{padding:20px 0 70px}
.faq-block{margin-top:44px}
.faq-block h2{margin-bottom:6px}
.blog-hero{padding:64px 0 24px}
.blog-hero h1{font-size:clamp(32px,5vw,48px);margin:8px 0 12px}
.article .prose{max-width:none}
@media(max-width:860px){
  .t-hero .grid{grid-template-columns:1fr}
  .t-img{max-width:300px}
  .article{padding:40px 22px 60px}
  .posts{grid-template-columns:1fr}
}
'''


def blocks(body):
    out = []
    for kind, val in body:
        if kind == 'p':
            out.append(f'<p>{e(val)}</p>')
        elif kind == 'h2':
            out.append(f'<h2>{e(val)}</h2>')
        elif kind == 'ul':
            out.append('<ul>' + ''.join(f'<li>{e(i)}</li>' for i in val) + '</ul>')
        elif kind == 'links':  # ("links", [("Label", "/url"), ...])
            out.append('<p class="related"><b>Related:</b> ' +
                       ' · '.join(f'<a href="{e(u)}">{e(t)}</a>' for t, u in val) + '</p>')
    return '\n  '.join(out)


def faq_html(faq):
    return ('<div class="faq-block"><h2>Frequently asked questions</h2><div class="faq" style="margin-top:12px">' +
            ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faq) +
            '</div></div>')


def cta(title='Book a consultation'):
    return f'''<div class="art-cta">
    <h2>{e(title)}</h2>
    <p>Visit the clinic in Jogeshwari West (Mon – Sat, 7 PM – 10 PM) or consult Dr. Hafsa Patel online, 10 AM – 10 PM.</p>
    <a class="btn" href="{WA}" target="_blank" rel="noopener">Book on WhatsApp</a>
  </div>'''


def post_card(p):
    return (f'<a class="post-card" href="/blog/{p["slug"]}"><span class="tag">{e(p["tag"])}</span>'
            f'<h3>{e(p["title"])}</h3><p>{e(p["excerpt"])}</p><span class="more">Read article →</span></a>')


def treat_card(t):
    return (f'<a class="post-card" href="/{t["slug"]}"><span class="tag">Treatment</span>'
            f'<h3>{e(t["title"])}</h3><p>{e(t["description"][:110].rsplit(" ", 1)[0])}…</p><span class="more">Learn more →</span></a>')


ORG = {"@type": "MedicalClinic", "name": NAME, "url": SITE + "/", "logo": SITE + "/img/logo.webp",
       "telephone": "+91-72084-33163",
       "address": {"@type": "PostalAddress", "streetAddress": "19-C, Grace Plaza Shopping Centre, opp. Sabri Masjid",
                   "addressLocality": "Jogeshwari West, Mumbai", "addressRegion": "Maharashtra",
                   "postalCode": "400102", "addressCountry": "IN"}}


def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def page(title, desc, path, body, graph, og_type='website', image='/img/share.jpg'):
    url = SITE + path
    ld = {"@context": "https://schema.org", "@graph": graph}
    return f'''<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" href="/img/icon-192.png" sizes="192x192">
<link rel="apple-touch-icon" href="/img/icon-192.png">
<meta name="theme-color" content="#1e6b2f">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{e(NAME)}">
<meta property="og:locale" content="en_IN">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{json.dumps(ld, indent=2, ensure_ascii=False)}
</script>
{fonts}
<style>{style}{EXTRA_CSS}</style>
</head>
<body>
{header}
{body}
{footer}
{mbar}
<script>document.getElementById('yr').textContent=new Date().getFullYear();document.querySelectorAll('#menu a').forEach(function(a){{a.addEventListener('click',function(){{document.getElementById('menu').classList.remove('open')}})}});</script>
</body>
</html>
'''


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for attempt in range(5):  # OneDrive can briefly lock files while syncing
        try:
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(text)
            return
        except OSError:
            if attempt == 4:
                raise
            import time
            time.sleep(1.5)


# ---------- treatment pages ----------
for t in TREATMENTS:
    path = '/' + t['slug']
    others = [o for o in TREATMENTS if o is not t]
    body = f'''<main>
<section class="t-hero">
  <div class="wrap grid">
    <div>
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › <a href="/#services">Treatments</a> › {e(t["nav"])}</nav>
      <div class="eyebrow">{e(t["eyebrow"])}</div>
      <h1>{e(t["title"])}</h1>
      <p class="lead">{e(t["lead"])}</p>
      <div class="acts">
        <a class="btn btn-primary" href="{WA}" target="_blank" rel="noopener">Book on WhatsApp</a>
        <a class="btn btn-ghost" href="tel:+917208433163">Call +91 72084 33163</a>
      </div>
    </div>
    <div class="t-img"><img src="{t["image"]}" alt="{e(t["image_alt"])}" width="720" height="800" fetchpriority="high"></div>
  </div>
</section>
<section class="t-body">
  <div class="wrap">
  <div class="prose">
  {blocks(t["body"])}
  {faq_html(t["faq"])}
  {cta()}
  <p class="art-note">This page is general information and not a substitute for personal medical advice. Unani care is complementary and does not replace emergency or surgical treatment. In an emergency, contact your nearest hospital.</p>
  </div>
  </div>
</section>
</main>
<section class="more-posts">
  <div class="wrap">
    <div class="eyebrow">Other treatments</div>
    <h2>More at A&amp;Z Healthcare Centre</h2>
    <div class="posts">{"".join(treat_card(o) for o in others)}</div>
  </div>
</section>'''
    graph = [
        {"@type": "MedicalWebPage", "name": t['seo_title'], "url": SITE + path, "description": t['description'],
         "inLanguage": "en-IN", "about": {"@type": "MedicalTherapy", "name": t['therapy']},
         "publisher": ORG, "lastReviewed": LASTMOD},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t['faq']]},
        crumbs_ld([("Home", "/"), ("Treatments", "/#services"), (t['nav'], path)]),
    ]
    write(f'pages/{t["slug"]}.html', page(t['seo_title'], t['description'], path, body, graph))

# ---------- blog posts ----------
for p in POSTS:
    path = '/blog/' + p['slug']
    others = [q for q in POSTS if q is not p][:3]
    faq = p.get('faq', [])
    body = f'''<main>
<article class="article">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › <a href="/blog">Blog</a> › {e(p["tag"])}</nav>
  <span class="tag">{e(p["tag"])}</span>
  <h1>{e(p["title"])}</h1>
  <div class="meta">{e(NAME)}, Jogeshwari West, Mumbai · {e(p["date"])}</div>
  <div class="prose">
  {blocks(p["body"])}
  {faq_html(faq) if faq else ''}
  </div>
  {cta('Talk to Dr. Hafsa Patel')}
  <p class="art-note">This article is general information and not a substitute for personal medical advice. In an emergency, contact your nearest hospital.</p>
</article>
</main>
<section class="more-posts">
  <div class="wrap">
    <div class="eyebrow">Keep reading</div>
    <h2>More from our blog</h2>
    <div class="posts">{"".join(post_card(q) for q in others)}</div>
  </div>
</section>'''
    graph = [
        {"@type": "BlogPosting", "headline": p['title'], "description": p.get('description', p['excerpt']),
         "mainEntityOfPage": SITE + path, "url": SITE + path, "inLanguage": "en-IN",
         "image": SITE + "/img/share.jpg", "author": ORG, "publisher": ORG},
        crumbs_ld([("Home", "/"), ("Blog", "/blog"), (p['title'], path)]),
    ]
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    write(f'blog/{p["slug"]}.html', page(p.get('seo_title', p['title'] + ' | ' + NAME),
                                        p.get('description', p['excerpt']), path, body, graph, 'article'))

# ---------- blog index ----------
body = f'''<main>
<section class="blog-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › Blog</nav>
    <div class="eyebrow">Blog</div>
    <h1>Notes on natural healing</h1>
    <p class="lead">Simple, reliable reading on Unani medicine, hijama and everyday wellness from {e(NAME)}, Jogeshwari West, Mumbai.</p>
  </div>
</section>
<section style="padding-top:20px">
  <div class="wrap"><div class="posts">{"".join(post_card(q) for q in POSTS)}</div></div>
</section>
</main>'''
graph = [{"@type": "Blog", "name": NAME + " Blog", "url": SITE + "/blog", "publisher": ORG,
          "blogPost": [{"@type": "BlogPosting", "headline": q['title'], "url": SITE + '/blog/' + q['slug']} for q in POSTS]},
         crumbs_ld([("Home", "/"), ("Blog", "/blog")])]
write('blog/index.html', page('Unani & Hijama Blog | ' + NAME + ', Mumbai',
                              'Articles on Unani medicine, mizaj (temperament), hijama and healthy eating from ' + NAME + ', a Unani clinic in Jogeshwari West, Mumbai.',
                              '/blog', body, graph))

# ---------- Products page (names/categories from content/products.json) ----------
from urllib.parse import quote
PRODUCTS = json.load(open(os.path.join(ROOT, 'content', 'products.json'), encoding='utf-8'))
cat_counts = {}
for pr in PRODUCTS:
    for c in pr['categories']:
        cat_counts[c] = cat_counts.get(c, 0) + 1
LAST = ['General', 'Over the counter']  # not body systems: shown at the end
cats = sorted(cat_counts, key=lambda c: (c in LAST, LAST.index(c) if c in LAST else 0, -cat_counts[c], c))


def slugify(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')


def prod_card(pr):
    msg = f'Assalamualaikum, I would like to buy {pr["name"]}. Is it available at A&Z Healthcare Centre?'
    wa = 'https://wa.me/917208433163?text=' + quote(msg)
    data_cats = ' '.join(slugify(c) for c in pr['categories'])
    use = USES[pr['name']]
    search = (pr['name'] + ' ' + use + ' ' + ' '.join(pr['categories'])).lower()
    return (f'<article class="prod" data-cats="{data_cats}" data-name="{e(search)}">'
            f'<h3>{e(pr["name"])}</h3>'
            f'<p class="prod-use">{e(use)}</p>'
            f'<a class="prod-ask" href="{e(wa)}" target="_blank" rel="noopener" aria-label="Enquire on WhatsApp to buy {e(pr["name"])}">'
            f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 11.5a8.5 8.5 0 01-12.6 7.4L3 20l1.2-4.2A8.5 8.5 0 1120 11.5z"/></svg>Enquire to buy</a></article>')


chips = ''.join(
    f'<button type="button" class="chip{" on" if i == 0 else ""}" data-cat="{slugify(c)}" data-label="{e(c)}" aria-pressed="{"true" if i == 0 else "false"}">'
    f'{e(c)} <span>{cat_counts[c]}</span></button>' for i, c in enumerate(cats))
PROD_CSS = '''<style>
.p-tools{position:sticky;top:80px;z-index:5;background:rgba(250,246,236,.96);backdrop-filter:blur(8px);padding:14px 0 12px;border-bottom:1px solid var(--line);margin-bottom:22px}
.p-search{width:100%;max-width:420px;margin:0 0 12px;padding:12px 16px;border-radius:999px;border:1.5px solid var(--line);background:#fff;font:inherit;font-size:16px}
.p-search:focus{outline:2px solid var(--green-500);border-color:transparent}
.chips{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;padding-bottom:2px}
.chips::-webkit-scrollbar{display:none}
.chip{flex:none;border:1.5px solid var(--line);background:#fff;color:var(--green-900);border-radius:999px;padding:7px 14px;font:inherit;font-size:14px;font-weight:500;cursor:pointer;white-space:nowrap}
.chip span{color:var(--muted);font-size:12px;margin-left:2px}
.chip.on{background:var(--green-900);border-color:var(--green-900);color:#fff}
.chip.on span{color:#f3e3b5}
.p-count{font-size:15px;color:var(--muted);margin-bottom:14px}
.p-count b{color:var(--green-900);font-family:Fraunces,serif;font-size:19px;font-weight:600}
.prod[hidden]{display:none!important}
.chips.searching .chip.on{background:#fff;border-color:var(--line);color:var(--green-900)}
.chips.searching .chip.on span{color:var(--muted)}
.p-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.prod{background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px 18px;display:flex;flex-direction:column;gap:8px;transition:transform .2s,box-shadow .2s;border-top:3px solid var(--gold)}
.prod:hover{transform:translateY(-3px);box-shadow:0 12px 26px -14px rgba(23,58,43,.35)}
.prod-cat{font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--gold);font-weight:700;line-height:1.4}
.prod h3{font-size:18px;line-height:1.25;margin:0}
.prod-use{font-size:14px;line-height:1.5;color:var(--muted);flex:1;margin:0 0 6px}
.prod-acts{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:4px}
.prod-ask{display:inline-flex;align-items:center;justify-content:center;gap:6px;background:#25a05a;color:#fff;text-decoration:none;font-size:14px;font-weight:600;padding:9px 14px;border-radius:999px;align-self:flex-start}
.prod-ask:hover{background:#1e8a4c}
.prod-ask svg{width:16px;height:16px;fill:none;stroke:#fff;stroke-width:2}
.prod-more{color:var(--green-700);font-size:13.5px;font-weight:600;text-decoration:none}
.prod-more:hover{text-decoration:underline}
.p-empty{display:none;text-align:center;color:var(--muted);padding:40px 0}
.p-types{margin-top:48px;max-width:900px}
.p-types h2{font-size:clamp(24px,3vw,30px)}
.p-types>p{color:var(--muted);margin-bottom:14px}
.p-types dl{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;margin:18px 0}
.p-types dl div{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.p-types dt{font-family:Fraunces,serif;font-weight:600;color:var(--green-900);font-size:17px}
.p-types dd{color:var(--muted);font-size:14.5px;line-height:1.55;margin-top:4px}
.p-types a{color:var(--green-700);font-weight:600}
.p-note{margin-top:34px;font-size:13.5px;color:var(--muted);max-width:820px}
.p-advice{display:flex;gap:14px;align-items:flex-start;background:var(--green-100);border:1px solid rgba(30,107,47,.18);border-radius:16px;padding:16px 20px;margin-top:22px;max-width:820px;font-size:15.5px;color:var(--green-900)}
.p-advice b{font-family:Fraunces,serif}
@media(max-width:860px){.p-tools{top:70px}}
@media(max-width:520px){.p-grid{grid-template-columns:1fr;gap:10px}.prod{padding:14px 16px}.prod h3{font-size:17px}.prod-use{font-size:14px}}
</style>'''
PROD_JS = '''<script>
(function(){
  var cards=[].slice.call(document.querySelectorAll('.prod')), chips=[].slice.call(document.querySelectorAll('.chip')),
      bar=document.querySelector('.chips'), q=document.getElementById('pSearch'), count=document.getElementById('pCount'),
      empty=document.getElementById('pEmpty'), current=chips[0];
  function esc(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;')}
  function apply(){
    var t=(q.value||'').trim().toLowerCase(), n=0, cat=current.dataset.cat;
    cards.forEach(function(c){
      // While searching, look through every system; otherwise show only the selected system
      var ok=t ? c.dataset.name.indexOf(t)>-1 : (' '+c.dataset.cats+' ').indexOf(' '+cat+' ')>-1;
      c.hidden=!ok; if(ok)n++;
    });
    bar.classList.toggle('searching',!!t);
    count.innerHTML=t ? '<b>'+n+(n===1?' result':' results')+'</b> for “'+esc(q.value.trim())+'”'
                      : '<b>'+esc(current.dataset.label)+'</b> · '+n+(n===1?' medicine':' medicines');
    empty.style.display=n?'none':'block';
  }
  chips.forEach(function(b){b.addEventListener('click',function(){
    chips.forEach(function(x){x.classList.remove('on');x.setAttribute('aria-pressed','false')});
    b.classList.add('on'); b.setAttribute('aria-pressed','true'); current=b; q.value=''; apply();
    b.scrollIntoView({block:'nearest',inline:'center',behavior:'smooth'});
  })});
  q.addEventListener('input',apply);
  q.addEventListener('search',apply);
  apply();
})();
</script>'''
body = f'''<main>
<section class="blog-hero" style="padding-bottom:6px">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › Unani medicines</nav>
    <div class="eyebrow">Unani medicines</div>
    <h1>Unani &amp; herbal medicines</h1>
    <p class="lead">Buy genuine Unani and herbal medicines through A&amp;Z Healthcare Centre, Jogeshwari West, Mumbai. Browse {len(PRODUCTS)} medicines with their traditional uses, from classical khamiras, majuns and jawarish to herbal syrups, oils and tablets, then tap <b>Enquire to buy</b>. We'll confirm availability and price on WhatsApp.</p>
    <div class="p-advice"><span aria-hidden="true">⚕️</span><div><b>Take Unani medicines on a physician's advice.</b> Many of these are classical Unani formulations. The right medicine and dose depend on your health and temperament (mizaj). Dr. Hafsa Patel can guide you at a consultation, in the clinic or online.</div></div>
  </div>
</section>
<section style="padding-top:18px">
  <div class="wrap">
    <div class="p-list">
    <div class="p-tools">
      <input id="pSearch" class="p-search" type="search" placeholder="Search by name or use, e.g. Khamira, cough, hair fall" aria-label="Search products">
      <div class="chips" role="group" aria-label="Choose a body system">{chips}</div>
    </div>
    <p class="p-count" id="pCount" aria-live="polite">Showing {len(PRODUCTS)} of {len(PRODUCTS)} products</p>
    <div class="p-grid">{"".join(prod_card(pr) for pr in PRODUCTS)}</div>
    <p class="p-empty" id="pEmpty">No products match your search. Try another name, or <a href="{WA}" target="_blank" rel="noopener">ask us on WhatsApp</a>.</p>
    </div>
    <div class="p-types">
      <h2>A quick guide to Unani medicine types</h2>
      <p>Unani medicines are named after the way they are prepared. Knowing the type tells you how a medicine is usually taken.</p>
      <dl>
        <div><dt>Khamira</dt><dd>A soft, sweet, fermented paste, often with gaozaban or pearl, traditionally used as a tonic for the heart and brain.</dd></div>
        <div><dt>Majun</dt><dd>A semi-solid herbal paste made with honey or sugar syrup, one of the most common classical Unani forms.</dd></div>
        <div><dt>Jawarish</dt><dd>A digestive paste, usually taken after meals to support the stomach, liver and appetite.</dd></div>
        <div><dt>Itrifal</dt><dd>A classical paste based on myrobalans (halela, balela, amla), traditionally used for the head, brain and digestion.</dd></div>
        <div><dt>Arq</dt><dd>A herbal distillate, such as arq gulab (rose) or arq ajwain, taken as a liquid.</dd></div>
        <div><dt>Habb and Qurs</dt><dd>Pills (habb) and tablets (qurs), easy-to-take forms of Unani formulations.</dd></div>
        <div><dt>Lauq</dt><dd>A thick linctus, licked slowly, traditionally used for the throat and chest.</dd></div>
        <div><dt>Sharbat</dt><dd>A herbal syrup, often cooling, diluted in water or taken by spoon.</dd></div>
        <div><dt>Roghan</dt><dd>A medicated oil for massage, the scalp or the skin.</dd></div>
        <div><dt>Safoof and Kushta</dt><dd>Herbal powders (safoof) and specially prepared mineral formulations (kushta), used under a physician's guidance.</dd></div>
      </dl>
      <p>Not sure which medicine suits you? <a href="{WA}" target="_blank" rel="noopener">Book a consultation with Dr. Hafsa Patel</a>, in the clinic or online.</p>
    </div>
    <p class="p-note">Product names are trademarks of their respective owners. Availability and prices are confirmed by the clinic on WhatsApp. This list is for information only and is not medical advice.</p>
  </div>
</section>
</main>'''
graph = [
    {"@type": "CollectionPage", "name": "Unani medicines at " + NAME, "url": SITE + "/products",
     "inLanguage": "en-IN", "publisher": ORG,
     "mainEntity": {"@type": "ItemList", "numberOfItems": len(PRODUCTS),
                    "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                         "item": {"@type": "Thing", "name": pr['name'], "description": USES[pr['name']]}}
                                        for i, pr in enumerate(PRODUCTS)]}},
    crumbs_ld([("Home", "/"), ("Unani medicines", "/products")]),
]
pp = page('Unani Medicines & Their Uses: Khamira, Majun, Jawarish | ' + NAME,
          f'Uses of {len(PRODUCTS)} Unani and herbal medicines: khamira, majun, jawarish, syrups and oils. Enquire to buy at A&Z Healthcare Centre, Jogeshwari, Mumbai.',
          '/products', body, graph)
pp = pp.replace('</head>', PROD_CSS + '\n</head>', 1).replace('</body>', PROD_JS + '\n</body>', 1)
write('pages/products.html', pp)

# ---------- 404 page (Vercel serves /404.html for unknown addresses) ----------
links = ''.join(f'<a class="post-card" href="/{t["slug"]}"><span class="tag">Treatment</span><h3>{e(t["nav"])}</h3>'
                f'<span class="more">Learn more →</span></a>' for t in TREATMENTS)
body = f'''<main>
<section class="blog-hero" style="text-align:center;padding-bottom:10px">
  <div class="wrap">
    <div class="eyebrow">Page not found</div>
    <h1>Sorry, we couldn't find that page</h1>
    <p class="lead" style="margin:0 auto">The link may be old or mistyped. Here are some places to start, or message us on WhatsApp and we'll help.</p>
    <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:26px">
      <a class="btn btn-primary" href="/">Go to the homepage</a>
      <a class="btn btn-ghost" href="{WA}" target="_blank" rel="noopener">Message us on WhatsApp</a>
    </div>
  </div>
</section>
<section style="padding-top:30px">
  <div class="wrap"><div class="posts">{links}</div>
  <p style="text-align:center;margin-top:28px"><a class="more" href="/blog">Read our blog →</a></p></div>
</section>
</main>'''
nf = page('Page not found | ' + NAME, 'This page could not be found.', '/404', body, [ORG])
nf = nf.replace(f'<link rel="canonical" href="{SITE}/404">\n', '<meta name="robots" content="noindex">\n')
write('404.html', nf)

# ---------- sitemap + Vercel routes ----------
urls = ['/'] + ['/' + t['slug'] for t in TREATMENTS] + ['/products', '/blog'] + ['/blog/' + p['slug'] for p in POSTS]
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      ''.join(f'  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n  </url>\n' for u in urls) + '</urlset>\n')
vercel = {"trailingSlash": False,
          # Send the old Vercel address to the real domain so Google sees one site
          "redirects": [{"source": "/:path*", "has": [{"type": "host", "value": "a-and-z.vercel.app"}],
                         "destination": SITE + "/:path*", "permanent": True}],
          "rewrites":
          [{"source": "/" + t['slug'], "destination": f"/pages/{t['slug']}.html"} for t in TREATMENTS] +
          [{"source": "/products", "destination": "/pages/products.html"}] +
          [{"source": "/blog/:slug", "destination": "/blog/:slug.html"}]}
write('vercel.json', json.dumps(vercel, indent=2) + '\n')

print('Built', len(TREATMENTS), 'treatment pages,', len(POSTS), 'articles, blog index, sitemap (', len(urls), 'URLs )')

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


def page(title, desc, path, body, graph, og_type='website', image='/hafsa-photo.jpg'):
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
<meta name="twitter:card" content="summary">
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
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


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
    write(f'pages/{t["slug"]}.html', page(t['seo_title'], t['description'], path, body, graph, image=t['image']))

# ---------- blog posts ----------
for p in POSTS:
    path = '/blog/' + p['slug']
    others = [q for q in POSTS if q is not p]
    body = f'''<main>
<article class="article">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › <a href="/blog">Blog</a> › {e(p["tag"])}</nav>
  <span class="tag">{e(p["tag"])}</span>
  <h1>{e(p["title"])}</h1>
  <div class="meta">{e(NAME)}, Jogeshwari West, Mumbai · {e(p["date"])}</div>
  <div class="prose">
  {blocks(p["body"])}
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
        {"@type": "BlogPosting", "headline": p['title'], "description": p['excerpt'],
         "mainEntityOfPage": SITE + path, "url": SITE + path, "inLanguage": "en-IN",
         "image": SITE + "/hafsa-photo.jpg", "author": ORG, "publisher": ORG},
        crumbs_ld([("Home", "/"), ("Blog", "/blog"), (p['title'], path)]),
    ]
    write(f'blog/{p["slug"]}.html', page(p['title'] + ' | ' + NAME, p['excerpt'], path, body, graph, 'article'))

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

# ---------- sitemap + Vercel routes ----------
urls = ['/'] + ['/' + t['slug'] for t in TREATMENTS] + ['/blog'] + ['/blog/' + p['slug'] for p in POSTS]
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      ''.join(f'  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n  </url>\n' for u in urls) + '</urlset>\n')
vercel = {"trailingSlash": False,
          # Send the old Vercel address to the real domain so Google sees one site
          "redirects": [{"source": "/:path*", "has": [{"type": "host", "value": "a-and-z.vercel.app"}],
                         "destination": SITE + "/:path*", "permanent": True}],
          "rewrites":
          [{"source": "/" + t['slug'], "destination": f"/pages/{t['slug']}.html"} for t in TREATMENTS] +
          [{"source": "/blog/:slug", "destination": "/blog/:slug.html"}]}
write('vercel.json', json.dumps(vercel, indent=2) + '\n')

print('Built', len(TREATMENTS), 'treatment pages,', len(POSTS), 'articles, blog index, sitemap (', len(urls), 'URLs )')

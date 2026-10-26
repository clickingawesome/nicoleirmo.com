"""Build nicoleirmo.com: one real HTML file per URL from _src/site.html.

Usage:  python3 _src/build.py [--snap]
  Each page keeps only its own section (others become empty stubs), gets its own
  title/description/canonical/OG/JSON-LD, and (with --snap) has its JS-rendered
  parts (work grid, posts, article, case study, testimonials) pre-filled so the
  full text is in the HTML for search engines. Requires playwright for --snap.
"""
import re, json, os, sys, html, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = 'https://nicoleirmo.com'
T = open(os.path.join(HERE, 'site.html')).read()
HEADS = json.load(open(os.path.join(HERE, 'heads.json')))
SNAP = json.load(open(os.path.join(HERE, 'snap.json'))) if os.path.exists(os.path.join(HERE, 'snap.json')) else {}
CONTENT = json.loads(re.search(r'<script id="siteContent" type="application/json">(.*?)</script>', T, re.S).group(1))
TODAY = datetime.date.today().isoformat()
PERSON = {"@type": "Person", "@id": SITE + "/#person", "name": "Nicole Irmo", "url": SITE + "/about/"}

EXTRA = {
    '/results/': {'title': 'Results · Nicole Irmo', 'desc': 'The receipts from Nicole Irmo\'s marketing leadership: 53% revenue growth in under three years, organic search up 32% while the industry dropped, and the most-cited brand in its category across AI search.'},
    '/contact/': {'title': 'Contact · Nicole Irmo', 'desc': 'Get in touch with Nicole Irmo about marketing leadership roles, panels, podcasts, advisory boards and brand puzzles.'},
}

def routes():
    r = [('/', 'home', ''), ('/work/', 'work', ''), ('/results/', 'results', ''), ('/about/', 'about', ''),
         ('/insights/', 'insights', ''), ('/contact/', 'contact', '')]
    r += [('/insights/%s/' % p['slug'], 'post', p['slug']) for p in CONTENT['posts'] if not p.get('draft')]
    r += [('/work/%s/' % c['id'], 'case', c['id']) for c in CONTENT['cases'] if c.get('open')]
    return r

def head_tags(url, page):
    h = HEADS.get(url) or {}
    e = EXTRA.get(url, {})
    title = e.get('title') or h.get('title'); desc = e.get('desc') or h.get('desc', '')
    assert title, url
    ogtype = h.get('ogtype') or ('article' if page == 'post' else 'website')
    img = h.get('ogimage') or SITE + '/og.png'
    a = lambda s: html.escape(s, quote=True)
    out = ['<title>%s</title>' % html.escape(title), '<meta name="description" content="%s">' % a(desc),
           '<link rel="canonical" href="%s">' % (SITE + url),
           '<meta property="og:type" content="%s">' % ogtype, '<meta property="og:site_name" content="Nicole Irmo">',
           '<meta property="og:title" content="%s">' % a(title), '<meta property="og:description" content="%s">' % a(desc),
           '<meta property="og:url" content="%s">' % (SITE + url), '<meta property="og:image" content="%s">' % img]
    if img.endswith('/og.png'):
        out.append('<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">')
    out += ['<meta name="twitter:card" content="summary_large_image">', '<meta name="twitter:title" content="%s">' % a(title),
            '<meta name="twitter:description" content="%s">' % a(desc), '<meta name="twitter:image" content="%s">' % img]
    lds = list(h.get('ld') or [])
    if not lds:
        lds = [json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": title, "description": desc, "url": SITE + url,
                           "isPartOf": {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Nicole Irmo"},
                           "about": PERSON}, ensure_ascii=False)]
    if url != '/':
        crumbs = [('Home', '/')]
        parts = [p for p in url.split('/') if p]
        if parts:
            crumbs.append((parts[0].capitalize(), '/' + parts[0] + '/'))
        if len(parts) > 1:
            crumbs.append((title.split(' · ')[0], url))
        lds.append(json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(crumbs)]}, ensure_ascii=False))
    out += ['<script type="application/ld+json">%s</script>' % l for l in lds]
    return '\n'.join(out)

# page sections: from the first page section to the end of the last one
starts = [m.start() for m in re.finditer(r'<section class="page" data-page="', T)]
last = T.index('</section>', T.rindex('<section class="page" data-page="contact">')) + len('</section>')
PRE, POST = T[:starts[0]], T[last:]
CHUNKS = {}
for i, s in enumerate(starts):
    e = starts[i + 1] if i + 1 < len(starts) else last
    ch = T[s:e]
    CHUNKS[re.match(r'<section class="page" data-page="([a-z]+)"', ch).group(1)] = ch.rstrip() + '\n'
ORDER = list(CHUNKS)

def balanced_div(s, start):
    depth, i = 0, start
    for m in re.finditer(r'<div\b|</div>', s[start:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0:
            return s[start:start + m.end()]
    raise ValueError

def results_bento():
    ch = CHUNKS['results']; i = ch.index('<div class="bento')
    return '<template id="resultsBento">' + balanced_div(ch, i) + '</template>'

def fill(chunk, url):
    for sel, inner in (SNAP.get(url) or {}).items():
        if sel == 'data-recs':
            chunk = chunk.replace('data-recs></div>', 'data-recs>%s</div>' % inner)
        else:
            new = chunk.replace('id="%s"></div>' % sel, 'id="%s">%s</div>' % (sel, inner), 1)
            chunk = new
    return chunk

def page_html(url, page, noindex=False):
    body = []
    for k in ORDER:
        if k == page:
            ch = CHUNKS[k].replace('<section class="page" data-page="%s">' % k, '<section class="page on" data-page="%s">' % k, 1)
            ch = fill(ch, url)
            if k == 'home':
                ch = ch.rstrip() + '\n' + results_bento() + '\n'
            body.append(ch)
        else:
            body.append('<section class="page" data-page="%s"></section>\n' % k)
    head = head_tags(url, page)
    if noindex:
        head = re.sub(r'<link rel="canonical"[^>]*>\n', '', head) + '\n<meta name="robots" content="noindex">'
    return PRE.replace('<!--HEAD-->', head, 1) + ''.join(body) + POST

def write(url, s):
    d = os.path.join(ROOT, url.strip('/'))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w').write(s)

R = routes()
for url, page, _ in R:
    write(url, page_html(url, page))
open(os.path.join(ROOT, '404.html'), 'w').write(page_html('/', 'home', noindex=True).replace('<title>Nicole Irmo · Marketing Leader</title>', '<title>Page not found · Nicole Irmo</title>', 1))

# sitemap
pri = {'home': '1.0', 'work': '0.8', 'insights': '0.8', 'about': '0.8', 'results': '0.8', 'contact': '0.6', 'post': '0.7', 'case': '0.7'}
urls = [(u, pri[p]) for u, p, _ in R]
urls.insert(1, ('/resume/', '0.7'))
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
    '<url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n' % (SITE, u, TODAY, p) for u, p in urls) + '</urlset>\n'
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm)
json.dump(R, open(os.path.join(HERE, 'routes.json'), 'w'))
print('built', len(R), 'pages + 404.html + sitemap.xml')

if '--snap' in sys.argv:
    # render each page in a real browser and keep the JS-built markup so it ships in the HTML
    import subprocess, time, threading, http.server, functools
    from playwright.sync_api import sync_playwright
    H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8765), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
    snap = {}
    SEL = {'home': ['track', 'homeBento', 'data-recs'], 'work': ['wgrid'], 'insights': ['posts'], 'post': ['article'], 'case': ['casePage'], 'about': ['data-recs']}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for url, page, _ in R:
            if page not in SEL: continue
            pg = b.new_page(reduced_motion='reduce'); pg.goto('http://127.0.0.1:8765' + url); pg.wait_for_timeout(600)
            snap[url] = pg.evaluate("""(sels)=>{var o={};sels.forEach(function(s){
                if(s==='data-recs'){var h=document.querySelector('.page.on [data-recs]');if(!h)return;var c=h.cloneNode(true);
                  c.querySelectorAll('.row-m .in').forEach(function(i){var k=i.children.length/2;while(i.children.length>k)i.lastElementChild.remove()});o[s]=c.innerHTML}
                else{var e=document.getElementById(s);if(e)o[s]=e.innerHTML}});return o}""", SEL[page])
            pg.close()
        b.close()
    srv.shutdown()
    json.dump(snap, open(os.path.join(HERE, 'snap.json'), 'w'), ensure_ascii=False)
    print('snapshots saved; run again without --snap to bake them in')

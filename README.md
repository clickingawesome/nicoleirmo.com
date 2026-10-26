# nicoleirmo.com

Personal site for Nicole Irmo, Marketing Leader. Static files on Netlify; every push to `main` deploys.

## Structure
Every page has its own real URL and its own HTML file, with the full design:

- `/` home · `/work/` · `/results/` · `/about/` · `/insights/` · `/contact/`
- `/insights/<slug>/` articles · `/work/<id>/` signature case studies
- `resume/` printable résumé (standalone)
- `404.html`, `sitemap.xml`, `robots.txt`, `llms.txt`, `_redirects`, `netlify.toml`

Old hash links (`/#/work`, `/#/post/<slug>`, `/#case-<id>`) redirect to the real URLs in the browser.

## Editing
The pages are generated. Edit `_src/site.html` (markup, styles, scripts, and the `siteContent` JSON with posts and case studies), then:

```
python3 _src/build.py --snap   # renders pages in a headless browser to capture JS-built content (needs playwright)
python3 _src/build.py          # writes every page, 404.html and sitemap.xml
```

Per-page titles, descriptions and structured data live in `_src/heads.json` (plus `EXTRA` in `build.py`).
A post with `"draft": true` is left out of the site and sitemap. `_src/` is blocked from public access by `_redirects`.

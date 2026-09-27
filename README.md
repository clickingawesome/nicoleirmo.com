# nicoleirmo.com

Personal site for Nicole Irmo, Marketing Leader. Static site: no build step, no dependencies.

## Structure
- `index.html` — the main site (single-page app with hash routes: `/#/work`, `/#/insights`, …)
- `resume/` — printable résumé
- `insights/<slug>/` — pre-rendered article pages (for search engines and social sharing)
- `work/<id>/` — pre-rendered case-study pages
- `about/`, `assets/`, `og.png`, `sitemap.xml`, `robots.txt`, `llms.txt`
- `netlify.toml`, `_redirects` — hosting config for Netlify

## Deploy
Connect this repository to Netlify (or any static host) with the publish directory set to the repository root. Every push to `main` deploys.

## Editing content
Content is edited in the site's built-in editor (owner only) and re-exported; the pre-rendered pages are regenerated from the exported site file.

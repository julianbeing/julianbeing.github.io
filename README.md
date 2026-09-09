# julianbeing.com — static freeze

Static copy of the former Webflow site, hosted on GitHub Pages.

- `mirror/` — raw wget mirror of the live Webflow site (local only, not committed)
- `build.py` — turns `mirror/` into `docs/`: localizes CDN assets, cleans URLs, wires the newsletter form to Web3Forms, adds sitemap/robots/404
- `docs/` — deploy root (GitHub Pages, branch `main`, folder `/docs`)
- `serve.py` — local preview at http://127.0.0.1:8765 with clean-URL fallback

Rebuild: `WEB3FORMS_KEY=xxxx CNAME=1 python3 build.py` (CNAME only once DNS points here).
Edit content: change the HTML in `docs/` directly; `build.py` overwrites `docs/`, so re-apply or patch `build.py`.

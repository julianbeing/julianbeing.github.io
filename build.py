#!/usr/bin/env python3
"""Post-process the wget mirror of julianbeing.com into a self-contained static site.

Input : mirror/julianbeing.com, mirror/cdn.prod.website-files.com
Output: docs/   (GitHub Pages deploy root)
"""
import os, re, shutil, sys, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).parent
MIRROR = ROOT / "mirror"
SRC = MIRROR / "julianbeing.com"
CDN_SRC = MIRROR / "cdn.prod.website-files.com"
OUT = ROOT / "docs"
CDN_OUT = OUT / "cdn"
EXT_OUT = CDN_OUT / "ext"
UA = {"User-Agent": "Mozilla/5.0"}

SKIP_PAGES = {"9i1h7htkfq16NjBmNThiMTNjNWIzMTcwNWE0NjFkOTgz"}


def fetch(url, dest: Path):
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        dest.write_bytes(r.read())
    print("  fetched", url, "->", dest.relative_to(OUT))


def ext_name(url):
    return os.path.basename(urllib.parse.urlparse(url).path)


# ---------------------------------------------------------------- copy
if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT, ignore=shutil.ignore_patterns(*SKIP_PAGES))
shutil.copytree(CDN_SRC, CDN_OUT, dirs_exist_ok=True)
EXT_OUT.mkdir(parents=True, exist_ok=True)
for f in (MIRROR / "julianbeing.com" / "cdn" / "ext").glob("*") if (SRC / "cdn" / "ext").exists() else []:
    shutil.copy(f, EXT_OUT / f.name)

# ---------------------------------------------------------------- pagination pages
PAGINATED = {  # list page -> (base live url, query key, clean base url)
    "blog.html": ("https://julianbeing.com/blog", "65681c8d", "/blog"),
    "categories/enjoying-sex.html": ("https://julianbeing.com/categories/enjoying-sex", "b5cf90c9", "/categories/enjoying-sex"),
}
for _, (base, key, clean_base) in PAGINATED.items():
    n = 2
    while True:
        rel = clean_base.lstrip("/") + f"/page-{n}.html"
        dest = OUT / rel
        if not dest.exists():
            req = urllib.request.Request(f"{base}?{key}_page={n}", headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                html = r.read().decode("utf-8")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(html, encoding="utf-8")
            print("  fetched ->", rel)
        if f"{key}_page={n+1}" not in dest.read_text(encoding="utf-8"):
            break
        n += 1

# ---------------------------------------------------------------- rewrite rules
CDN_ABS = re.compile(r"https?://cdn\.prod\.website-files\.com/")
CDN_REL = re.compile(r"(?:\.\./)+cdn\.prod\.website-files\.com/")
CLOUDFRONT = re.compile(r"https?://d3e54v103j8qbb\.cloudfront\.net/[^\s\"')]+")
WWW_REL = re.compile(r"(?:\.\./)+www\.julianbeing\.com/")
SELF_ABS = re.compile(r"https?://(?:www\.)?julianbeing\.com(?=[/\"'?#])")
LOCAL_HTML = re.compile(r"""(href=["'])((?:\.\./)*(?:[\w\-]+/)*[\w\-]+)\.html(?=["'#?])""")
import posixpath

pages = sorted(p for p in OUT.rglob("*.html"))
css_files = sorted(CDN_OUT.rglob("*.css"))

missing_cdn = set()


def localize_cdn_abs(m_url: str) -> str:
    """Absolute CDN URL -> /cdn/<path>, downloading if the mirror lacks it."""
    path = urllib.parse.unquote(urllib.parse.urlparse(m_url.replace("\\(", "(").replace("\\)", ")")).path.lstrip("/"))
    dest = CDN_OUT / path
    if not dest.exists():
        try:
            fetch(m_url.replace("\\(", "(").replace("\\)", ")").split("?")[0], dest)
        except Exception as e:
            missing_cdn.add(m_url)
            return m_url
    return "/cdn/" + urllib.parse.quote(path)


def rewrite_common(text: str) -> str:
    # relative cdn refs from wget
    text = CDN_REL.sub("/cdn/", text)
    # absolute cdn refs (lottie json, css bg images, og:image)
    def cdn_abs(m):
        end = re.match(r"[^\s\"')]+", text[m.end():])
        return m.group(0)
    text = re.sub(r"https?://cdn\.prod\.website-files\.com/(?:[^\s\"'<>&()\\]|\\\(|\\\)|\([^)\s]*\))+",
                  lambda m: localize_cdn_abs(m.group(0)), text)
    # cloudfront (jquery, default svg assets)
    def cf(m):
        url = m.group(0)
        name = ext_name(url)
        fetch(url, EXT_OUT / name)
        return "/cdn/ext/" + name
    text = CLOUDFRONT.sub(cf, text)
    # coaching booking link: live site only linked bare calendly.com
    text = text.replace('href="https://calendly.com/"', 'href="https://calendly.com/julianbeing"')
    return text


def rewrite_html(text: str, rel: str) -> str:
    text = rewrite_common(text)
    # links into the www mirror dir -> root
    text = WWW_REL.sub("/", text)
    # absolute self links -> root-relative
    text = SELF_ABS.sub("", text)
    # wget mangled inline style urls: url(https://julianbeing.com/&quot;https://cdn...&quot;)
    # (subpages get url(/blog/&quot;..., url(/authors/&quot;... etc.)
    text = re.sub(r'url\(/[a-z-]*/?&quot;', "url(&quot;", text)
    # local .html links -> clean urls
    def clean(m):
        p = posixpath.normpath(posixpath.join(posixpath.dirname(rel), m.group(2)))
        if p == "index":
            return m.group(1) + "/"
        return m.group(1) + "/" + p
    text = LOCAL_HTML.sub(clean, text)
    # pagination
    for _, (_, key, clean_base) in PAGINATED.items():
        text = re.sub(r'href="[^"]*\?' + key + r'_page=1"', f'href="{clean_base}"', text)
        text = re.sub(r'href="[^"]*\?' + key + r'_page=(\d+)"', lambda m: f'href="{clean_base}/page-{m.group(1)}"', text)
    # css was rewritten -> subresource-integrity hashes no longer match
    text = re.sub(r'\s+integrity="[^"]*"', "", text)
    # Cookiebot: auto-blocking mode holds jQuery's ready event until its config loads, and Webflow's
    # sliders/dropdowns/nav never init if that fails (e.g. unauthorized domain). Switch to manual mode
    # and gate the only consent-relevant assets explicitly: GA4 (statistics), YouTube/Embedly (marketing).
    text = text.replace(' data-blockingmode="auto"', "")
    text = re.sub(r'<script async="" src="/9i1h[^"]*"></script>', "", text)  # webflow's proxied GA loader
    text = text.replace('<script type="text/javascript">window.dataLayer = window.dataLayer || [];',
                        '<script type="text/plain" data-cookieconsent="statistics" async src="https://www.googletagmanager.com/gtag/js?id=G-1NKN9NVK10"></script>'
                        '<script type="text/plain" data-cookieconsent="statistics">window.dataLayer = window.dataLayer || [];')
    text = re.sub(r'<iframe src="(https://(?:www\.youtube\.com|cdn\.embedly\.com)/[^"]*)"',
                  r'<iframe data-cookieconsent="marketing" data-src="\1"', text)
    text = re.sub(r'(<link[^>]*rel="stylesheet"[^>]*)\s+crossorigin="[^"]*"', r"\1", text)
    # webflow-internal beacon script (site-specific hashed path, 404s offline)
    text = re.sub(r'<script[^>]*9i1h7htkfq16[^>]*>\s*</script>', "", text)
    text = re.sub(r'<link[^>]*9i1h7htkfq16[^>]*/?>', "", text)
    # canonical / og:url back to the real domain
    text = re.sub(r'(<link href=")/?(" rel="canonical">)', r"\1https://julianbeing.com/\2", text)
    text = text.replace('property="og:url" content="/', 'property="og:url" content="https://julianbeing.com/')
    return text


for p in pages:
    rel = str(p.relative_to(OUT))
    p.write_text(rewrite_html(p.read_text(encoding="utf-8"), rel), encoding="utf-8")

for c in css_files:
    c.write_text(rewrite_common(c.read_text(encoding="utf-8")), encoding="utf-8")

# ---------------------------------------------------------------- report
print(f"pages: {len(pages)}  css: {len(css_files)}")
if missing_cdn:
    print("UNRESOLVED cdn urls:", *sorted(missing_cdn), sep="\n  ")
leftover = {}
for p in pages:
    for m in re.finditer(r'(?:src|href)="(https?://[^"/]+)', p.read_text(encoding="utf-8")):
        leftover[m.group(1)] = leftover.get(m.group(1), 0) + 1
print("external hosts still referenced:")
for h, n in sorted(leftover.items(), key=lambda x: -x[1]):
    print(f"  {n:4d} {h}")

# ---------------------------------------------------------------- newsletter form -> Brevo
BREVO_ACTION = "https://29db0694.sibforms.com/serve/MUIFAHVRO_p3WwaDrgjCioMaDLOdzPabLgVFtkXiCDpRvYieYx6axPsveEIZPZr-Do0PIpI7deZem5s7oi61NE_QL2iGdg2Si9VjtnIuPBSR5AjYbAjJ7seEN_HJ8C_keVwux5w5LgsnSQy1jdSxGxtXrshcDokVnKkfouVLPDPTx1C2Hm80UTwaR6Bsu4OPi3H1iJOytkPNIt9g8g=="
FORM_SCRIPT = """
<script>
(function(){
  document.querySelectorAll('form.c-newsletter-cta-form').forEach(function(form){
    form.addEventListener('submit', function(ev){
      ev.preventDefault();
      var wrap = form.parentElement;
      var done = wrap.querySelector('.w-form-done'), fail = wrap.querySelector('.w-form-fail');
      var btn = form.querySelector('input[type=submit]'); var label = btn.value;
      btn.value = btn.getAttribute('data-wait') || label; btn.disabled = true;
      fetch(form.action + '?isAjax=1', {method:'POST', body:new FormData(form)})
        .then(function(r){ return r.json().catch(function(){ return {}; }).then(function(j){ return {ok:r.ok, j:j}; }); })
        .then(function(x){ if(!x.ok || (x.j && x.j.errors)) throw new Error('brevo');
          form.style.display='none'; if(done) done.style.display='block'; if(fail) fail.style.display='none'; })
        .catch(function(){ if(fail) fail.style.display='block'; btn.value = label; btn.disabled = false; });
    });
  });
})();
</script>
"""
form_pages = 0
for p in pages:
    t = p.read_text(encoding="utf-8")
    if "c-newsletter-cta-form" not in t:
        continue
    t = re.sub(r'<div class="w-form">(\s*<form[^>]*c-newsletter-cta-form)', r'<div class="newsletter-form-wrap">\1', t)
    t = re.sub(r'<form[^>]*c-newsletter-cta-form[^>]*>',
               lambda m: m.group(0).replace('method="get"', 'method="post" action="' + BREVO_ACTION + '"')
                         + '<input type="text" name="email_address_check" value="" style="display:none" tabindex="-1" autocomplete="off">'
                         + '<input type="hidden" name="locale" value="en">', t)
    # field names Brevo expects
    t = re.sub(r'(<form[^>]*c-newsletter-cta-form.*?</form>)',
               lambda m: re.sub(r'name="(?:name|name-2)"', 'name="FIRSTNAME"', re.sub(r'name="(?:email|email-2)"', 'name="EMAIL"', m.group(1))),
               t, flags=re.S)
    t = t.replace("</body>", FORM_SCRIPT + "</body>")
    p.write_text(t, encoding="utf-8")
    form_pages += 1
print("forms rewired on", form_pages, "pages -> brevo")

# ---------------------------------------------------------------- x.html -> x/index.html (unambiguous clean urls)
moved = 0
for p in pages:
    if p.name == "index.html":
        continue
    target_dir = p.with_suffix("")
    target_dir.mkdir(exist_ok=True)
    p.rename(target_dir / "index.html")
    moved += 1
print("moved", moved, "pages into directories")
rel_left = sum(1 for p in OUT.rglob("*.html") for _ in re.finditer(r'(?:src|href)="\.\./', p.read_text(encoding="utf-8")))
print("relative ../ refs left in html:", rel_left)

# ---------------------------------------------------------------- hosting extras: sitemap, robots, 404, CNAME
DOMAIN = "https://julianbeing.com"
urls = []
for p in sorted(OUT.rglob("index.html")):
    rel = p.relative_to(OUT).parent.as_posix()
    if rel.startswith("cdn"):
        continue
    urls.append(DOMAIN + ("/" if rel == "." else "/" + rel + "/"))
(OUT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")
if os.environ.get("CNAME"):
    (OUT / "CNAME").write_text("julianbeing.com\n", encoding="utf-8")
(OUT / ".nojekyll").write_text("", encoding="utf-8")
# 404: reuse the imprint page shell with a short message
shell = (OUT / "imprint" / "index.html").read_text(encoding="utf-8")
shell = re.sub(r"<title>[^<]*</title>", "<title>Page not found - Julian Being</title>", shell)
shell = re.sub(r'<link href="https://julianbeing.com/[^"]*" rel="canonical">', "", shell)
(OUT / "404.html").write_text(shell, encoding="utf-8")
print("sitemap urls:", len(urls))

# ================================================================ optimizations (run after restructure)
import subprocess
html_files = [p for p in OUT.rglob("*.html")]
css_files = sorted(CDN_OUT.rglob("*.css"))

# ---- og:image / twitter:image must be absolute for social scrapers
for p in html_files:
    t = p.read_text(encoding="utf-8")
    t2 = re.sub(r'(property="og:image" content=")/cdn/', r'\1' + DOMAIN + '/cdn/', t)
    t2 = re.sub(r'(name="twitter:image" content=")/cdn/', r'\1' + DOMAIN + '/cdn/', t2)
    if t2 != t:
        p.write_text(t2, encoding="utf-8")

# ---- images -> webp (max width 1600, q80), keep original if webp is not smaller
MAX_W = 1600
mapping = {}  # "/cdn/x.jpg" -> "/cdn/x.webp"  (unquoted)
img_before = img_after = 0
for img in sorted(CDN_OUT.rglob("*")):
    if img.suffix.lower() not in (".jpg", ".jpeg", ".png") or not img.is_file():
        continue
    try:
        w = int(subprocess.run(["sips", "-g", "pixelWidth", str(img)], capture_output=True, text=True).stdout.split()[-1])
    except Exception:
        w = 0
    out = img.with_suffix(".webp")
    cmd = ["cwebp", "-quiet", "-q", "80", "-metadata", "none"]
    if w > MAX_W:
        cmd += ["-resize", str(MAX_W), "0"]
    cmd += [str(img), "-o", str(out)]
    if subprocess.run(cmd, capture_output=True).returncode != 0 or not out.exists():
        continue
    if out.stat().st_size >= img.stat().st_size and w <= MAX_W:
        out.unlink()
        continue
    img_before += img.stat().st_size
    img_after += out.stat().st_size
    mapping["/" + img.relative_to(OUT).as_posix()] = "/" + out.relative_to(OUT).as_posix()
    img.unlink()

def apply_mapping(text, css=False):
    for old, new in mapping.items():
        sp = lambda x: x.replace(" ", "%20")  # webflow only encodes spaces
        pairs = [(old, new), (urllib.parse.quote(old), urllib.parse.quote(new)), (sp(old), sp(new))]
        if css:  # css references images relative to its own dir: url(../name.jpg)
            bo, bn = old.rsplit("/", 1)[1], new.rsplit("/", 1)[1]
            pairs += [("../" + bo, "../" + bn), ("../" + urllib.parse.quote(bo), "../" + urllib.parse.quote(bn)), ("../" + sp(bo), "../" + sp(bn))]
        for o, n in pairs:
            text = text.replace(o, n)
    return text

for p in html_files + css_files:
    t = p.read_text(encoding="utf-8")
    t2 = apply_mapping(t, css=p.suffix == ".css")
    if t2 != t:
        p.write_text(t2, encoding="utf-8")
print(f"images: {len(mapping)} converted to webp, {img_before/1e6:.1f} MB -> {img_after/1e6:.1f} MB")

# ---- ShareThis -> own tracking-free share buttons
SHARE_CSS = """<style>
.jb-share{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0}
.jb-share a,.jb-share button{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border:1px solid #d9dbe3;border-radius:999px;background:#fff;color:#1a1d2e;font:inherit;font-size:14px;text-decoration:none;cursor:pointer;line-height:1}
.jb-share a:hover,.jb-share button:hover{border-color:#1a1d2e}
.jb-share .jb-copied{border-color:#2aa24a;color:#2aa24a}
</style>"""
SHARE_HTML = """<div class="jb-share" data-jb-share>
<button type="button" data-share="native" hidden>Share</button>
<a data-share="whatsapp" href="#" target="_blank" rel="noopener">WhatsApp</a>
<a data-share="x" href="#" target="_blank" rel="noopener">X</a>
<a data-share="facebook" href="#" target="_blank" rel="noopener">Facebook</a>
<a data-share="email" href="#">Email</a>
<button type="button" data-share="copy">Copy link</button>
</div>"""
SHARE_JS = """<script>
(function(){
  var url = document.querySelector('link[rel=canonical]') ? document.querySelector('link[rel=canonical]').href : location.href;
  var title = document.title, u = encodeURIComponent(url), t = encodeURIComponent(title);
  var links = {whatsapp:'https://wa.me/?text='+t+'%20'+u, x:'https://twitter.com/intent/tweet?url='+u+'&text='+t,
               facebook:'https://www.facebook.com/sharer/sharer.php?u='+u, email:'mailto:?subject='+t+'&body='+u};
  document.querySelectorAll('[data-jb-share]').forEach(function(box){
    box.querySelectorAll('a[data-share]').forEach(function(a){ a.href = links[a.dataset.share]; });
    var nat = box.querySelector('[data-share=native]');
    if (nat && navigator.share) { nat.hidden = false; nat.addEventListener('click', function(){ navigator.share({title:title, url:url}).catch(function(){}); }); }
    var cp = box.querySelector('[data-share=copy]');
    cp.addEventListener('click', function(){
      navigator.clipboard.writeText(url).then(function(){ cp.textContent='Copied'; cp.classList.add('jb-copied');
        setTimeout(function(){ cp.textContent='Copy link'; cp.classList.remove('jb-copied'); }, 2000); });
    });
  });
})();
</script>"""
st_pages = 0
for p in html_files:
    t = p.read_text(encoding="utf-8")
    if "sharethis" not in t:
        continue
    t = re.sub(r"<script[^>]*platform-api\.sharethis\.com[^>]*>\s*</script>", "", t)
    if 'class="sharethis-inline-share-buttons"' in t:
        t = re.sub(r'<div class="sharethis-inline-share-buttons"[^>]*>\s*</div>', SHARE_HTML, t)
        t = t.replace("</head>", SHARE_CSS + "</head>", 1)
        t = t.replace("</body>", SHARE_JS + "</body>")
    p.write_text(t, encoding="utf-8")
    st_pages += 1
print("sharethis removed on", st_pages, "pages; share buttons on posts")

# ---------------------------------------------------------------- nav FOUC: pre-JS state of the "Nav bar scrolling" interaction
# Webflow IX2 sets the transparent top-of-page nav (white brand, hidden menu, shade moved up) only after
# webflow.js runs, so a reload flashes the white "scrolled" navbar. Bind the keyframe-0 state via CSS
# until IX2 adds html.w-mod-ix, on exactly the pages the interaction is bound to (PAGE targets in IX2 data).
NAV_BASE = """html.w-mod-js:not(.w-mod-ix) .brand{color:#fff}
html.w-mod-js:not(.w-mod-ix) .nav-menu{height:0%}
html.w-mod-js:not(.w-mod-ix) .left-nav{border-color:rgba(239,239,247,0)}
html.w-mod-js:not(.w-mod-ix) .navigation-shade{transform:translate3d(0,-100%,0)}
"""
# a-3 family "Nav bar scrolling | Background image hero": bound per page id
NAV_HERO_PAGES = {"615eefd2562790b8cfc16f15", "615eefd256279074f6c16f26", "615eefd25627900872c16f1b",
                  "615eefd256279033b8c16f25", "615eefd256279078c1c16f20", "615eefd25627903889c16f39",
                  "615eefd25627908b47c16f1f", "615eefd25627902570c16f1e", "615eefd2562790f07cc16f1d",
                  "615eefd256279085e5c16f30", "61fec16fa5a14e1c4ff2a501", "667955ee6691a142ef189ab0",
                  "60f94ba38b7854d6ca7e079f", "60737b4003881b718b7b5fa7"}
NAV_HERO_CSS = "<style>" + NAV_BASE + """html.w-mod-js:not(.w-mod-ix) .nav-button-toggle{color:#fff}
html.w-mod-js:not(.w-mod-ix) .dropdown-lottie{filter:invert(100%)}</style>"""
# a-45 "Nav bar scrolling | Left Background image": category pages
NAV_CAT_PAGES = {"615eefd2562790f15dc16f27"}
NAV_CAT_CSS = "<style>" + NAV_BASE + "html.w-mod-js:not(.w-mod-ix) .category-slider-top{height:0px}</style>"
nav_pages = 0
for p in OUT.rglob("*.html"):
    t = p.read_text(encoding="utf-8")
    m = re.search(r'data-wf-page="([^"]+)"', t)
    if not m:
        continue
    css = NAV_HERO_CSS if m.group(1) in NAV_HERO_PAGES else NAV_CAT_CSS if m.group(1) in NAV_CAT_PAGES else None
    if not css:
        continue
    p.write_text(t.replace("</head>", css + "</head>", 1), encoding="utf-8")
    nav_pages += 1
print("nav pre-js state css on", nav_pages, "pages")


# ---- internal links: trailing slash, avoids a 301 per click on GitHub Pages
SLASH = re.compile(r'href="(/(?:[A-Za-z0-9\-]+/)*[A-Za-z0-9\-]+)(?=["#?])')
n_slash = 0
for p in OUT.rglob("*.html"):
    t = p.read_text(encoding="utf-8")
    t2, k = SLASH.subn(lambda m: 'href="' + m.group(1) + "/", t)
    if k:
        p.write_text(t2, encoding="utf-8"); n_slash += k
print("internal links given trailing slash:", n_slash)

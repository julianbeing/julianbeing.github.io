# Stand 2026-09-14 — julianbeing.com läuft auf GitHub Pages

Live seit 2026-09-14 ~12:20: DNS bei Namecheap umgestellt, Zertifikat ausgestellt, Enforce HTTPS an.
Brevo: 287 Alt-Abonnenten aus dem Webflow-Export importiert (Spam/Bots vorher entfernt).

## Nächste Schritte
1. Claude: nach dem Cookiebot-Scan (2026-09-14 angestoßen) prüfen, ob ShareThis und talk.hyvor.com aus der Live-Erklärung raus sind (Details-Tab im Banner). Gescannte Cookies lassen sich nicht manuell löschen.
2. Optional: Brevo Double-Opt-in (Transactional-Konto per Support aktivieren, dann im Formular umstellen).

Erledigt 2026-09-14: Webflow Site-Plan gekündigt (läuft 2026-09-20 aus, Account bleibt), Subdomain-Indexing für julian-being-blog.webflow.io deaktiviert.

Vorschau lokal: `python3 serve.py` → http://127.0.0.1:8765 (beenden mit `pkill -f serve.py`).
Content-Änderungen: in `build.py` patchen (überschreibt `docs/`), nie mehr von Webflow neu spiegeln.

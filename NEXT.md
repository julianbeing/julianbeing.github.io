# Stand 2026-09-14 — julianbeing.com läuft auf GitHub Pages

Live seit 2026-09-14 ~12:20: DNS bei Namecheap umgestellt, Zertifikat ausgestellt, Enforce HTTPS an.
Brevo: 287 Alt-Abonnenten aus dem Webflow-Export importiert (Spam/Bots vorher entfernt).

## Nächste Schritte
1. Optional: Brevo Double-Opt-in (Transactional-Konto per Support aktivieren, dann im Formular umstellen).
2. Optional: Cookiebot-Scan listet GA4 (Google) nicht mehr, weil das Tag per Consent gegated ist. Falls die Erklärung GA4 nennen soll: Cookie manuell in Cookiebot anlegen.

Erledigt 2026-09-14 (Abschluss-Check): Root-.html-Links in 4 Blogposts + /link repariert, og:image absolut, canonical + og:url auf allen Seiten.

Erledigt 2026-09-14: Cookiebot neu gescannt, ShareThis und talk.hyvor.com sind aus der Erklärung raus.

Erledigt 2026-09-14: Webflow Site-Plan gekündigt (läuft 2026-09-20 aus, Account bleibt), Subdomain-Indexing für julian-being-blog.webflow.io deaktiviert.

Vorschau lokal: `python3 serve.py` → http://127.0.0.1:8765 (beenden mit `pkill -f serve.py`).
Content-Änderungen: in `build.py` patchen (überschreibt `docs/`), nie mehr von Webflow neu spiegeln.

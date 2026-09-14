# Stand 2026-09-14 — julianbeing.com läuft auf GitHub Pages

Live seit 2026-09-14 ~12:20: DNS bei Namecheap umgestellt, Zertifikat ausgestellt, Enforce HTTPS an.
Brevo: 287 Alt-Abonnenten aus dem Webflow-Export importiert (Spam/Bots vorher entfernt).

## Nächste Schritte
1. Julian, ab 2026-09-15: Webflow Site-Plan für julianbeing.com auf Starter (free) runterstufen (Account bleibt).
   Danach in Webflow Site settings → SEO → "Disable Webflow subdomain indexing" aktivieren (sonst Duplikat unter julianbeing.webflow.io).
2. Julian: in Cookiebot ShareThis aus der Cookie-Erklärung entfernen (Site nutzt eigene Share-Buttons).
3. Optional: Brevo Double-Opt-in (Transactional-Konto per Support aktivieren, dann im Formular umstellen).

Vorschau lokal: `python3 serve.py` → http://127.0.0.1:8765 (beenden mit `pkill -f serve.py`).
Content-Änderungen: in `build.py` patchen (überschreibt `docs/`), nie mehr von Webflow neu spiegeln.

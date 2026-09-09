# Stand 2026-09-09 — Umzug julianbeing.com Webflow → GitHub Pages

Fertig: Spiegelung, Optimierung (WebP, eigene Share-Buttons), Repo `julianbeing/julianbeing.github.io`,
Test-URL https://julianbeing.github.io läuft.

Entschieden: Newsletter-Anmeldungen gehen an **Brevo** (EU, kostenlos, Double-Opt-in).
Lokaler Commit "Web3Forms" ist nur Zwischenstand, wird durch Brevo ersetzt.

## Nächste Schritte
1. Julian: Brevo-Account, Formular (Email + First name, Double opt-in), Embed-HTML hier einfügen.
2. Claude: build.py auf Brevo-Endpoint umstellen (Feldnamen EMAIL/FIRSTNAME, `?isAjax=1`), testen, pushen.
3. Julian: Webflow Site Settings → Forms → CSV exportieren (alte Anmeldungen), in Brevo importieren.
4. Julian: Calendly-URL nennen (Coaching-Seite verlinkt bisher nur calendly.com).
5. Claude: `CNAME=1 python3 build.py`, pushen, Custom Domain im Repo setzen, DNS-Einträge für Namecheap liefern.
6. Julian: DNS bei Namecheap umstellen, 24 h warten, Webflow kündigen, in Cookiebot ShareThis entfernen.

Vorschau lokal: `python3 serve.py` → http://127.0.0.1:8765 (beenden mit `pkill -f serve.py`).

# Stand 2026-09-09 — Umzug julianbeing.com Webflow → GitHub Pages

Fertig: Spiegelung, Optimierung (WebP, eigene Share-Buttons), Repo `julianbeing/julianbeing.github.io`,
Test-URL https://julianbeing.github.io läuft.

Newsletter-Formular läuft über **Brevo** (gepusht 2026-09-09, Test-Anmeldung erfolgreich).
Noch Single-Opt-in: Brevo verlangt für Bestätigungsmails ein aktiviertes Transactional-Konto
(Support anschreiben, dann im Brevo-Formular auf Double-Opt-in umstellen; Site bleibt unverändert).

## Nächste Schritte
1. Julian: Webflow Site Settings → Forms → CSV exportieren (alte Anmeldungen), in Brevo importieren.
2. Julian: Calendly-URL nennen (Coaching-Seite verlinkt bisher nur calendly.com). Calendly seit 2026-09-10 auf Free (1 aktiver Event-Typ, keine Stripe-Zahlung); falls Zahlung nötig → Cal.com Free mit Stripe.
3. Claude: `CNAME=1 python3 build.py`, pushen, Custom Domain im Repo setzen, DNS-Einträge für Namecheap liefern.
4. Julian: DNS bei Namecheap umstellen, 24 h warten, Webflow kündigen, in Cookiebot ShareThis entfernen.

Vorschau lokal: `python3 serve.py` → http://127.0.0.1:8765 (beenden mit `pkill -f serve.py`).

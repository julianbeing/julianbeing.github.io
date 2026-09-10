# Stand 2026-09-09 — Umzug julianbeing.com Webflow → GitHub Pages

Fertig: Spiegelung, Optimierung (WebP, eigene Share-Buttons), Repo `julianbeing/julianbeing.github.io`,
Test-URL https://julianbeing.github.io läuft.

Newsletter-Formular läuft über **Brevo** (gepusht 2026-09-09, Test-Anmeldung erfolgreich).
Noch Single-Opt-in: Brevo verlangt für Bestätigungsmails ein aktiviertes Transactional-Konto
(Support anschreiben, dann im Brevo-Formular auf Double-Opt-in umstellen; Site bleibt unverändert).

## Nächste Schritte
1. Julian: Webflow Site Settings → Forms → CSV exportieren (alte Anmeldungen), in Brevo importieren.
2. Julian: DNS bei Namecheap umstellen (Advanced DNS): ALIAS/CNAME `@`→cdn.webflow.com löschen; A `@` → 185.199.108.153 / .109.153 / .110.153 / .111.153; CNAME `www` → julianbeing.github.io; MX (Google) unverändert.
3. Claude: nach ~1 h "Enforce HTTPS" im Repo aktivieren (`gh api -X PUT repos/julianbeing/julianbeing.github.io/pages -f https_enforced=true`), Site prüfen.
4. Julian: 24 h warten, Webflow kündigen, in Cookiebot ShareThis entfernen.

Erledigt 2026-09-10: Calendly auf Free (1 Event-Typ, keine Stripe-Zahlung; falls je nötig → Cal.com Free mit Stripe). "Schedule a call" im Flyout-Menü → calendly.com/julianbeing, bleibt bewusst drin. CNAME gepusht, Custom Domain im Repo gesetzt; julianbeing.github.io leitet daher bis zum DNS-Wechsel auf Webflow um, Vorschau nur lokal.

Vorschau lokal: `python3 serve.py` → http://127.0.0.1:8765 (beenden mit `pkill -f serve.py`).

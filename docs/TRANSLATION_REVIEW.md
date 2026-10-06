# Translation & Language Catalog Review

HELPmora composes answers in 50 languages in addition to English using localized message catalogs located in [`helpmora/data/i18n/<code>.json`](../helpmora/data/i18n/).

---

## Translation Architecture & Safeguards

When dealing with vulnerable citizens in crisis, inaccurate translations can cause tangible harm. HELPmora enforces strict safeguards:

| Safeguard | Implementation Details |
|---|---|
| **Disclaimer Banner** | A clear notice in the user's language appears under responses: *"Machine translation, not yet checked by a native speaker; program names, thresholds, and phone numbers are exact."* |
| **English Original One-Tap Toggle** | The English original of every response is available alongside the localized text (`reply_en`) so bilingual relatives or caseworkers can verify details. |
| **Emergency Numbers Never Translated** | Crisis hotlines (**112**, **181**, **1098**, **14416**, **1930**) and statutory numbers are never translated or modified by LLMs; they are injected directly from the verified code engine. |
| **Strict Schema Verification** | `tests/check_messages.jac` runs in CI and fails if any language catalog drops placeholders, adds unauthorized variables, or alters numerical constants. |

---

## How to Review or Improve a Language Catalog

1. Locate the language file in [`helpmora/data/i18n/<code_or_locale>.json`](../helpmora/data/i18n/).
2. Review string keys (e.g., `ui.send`, `esc.call`, `cat.housing`, `cat.food`, `cat.healthcare`, `cat.legal`).
3. Ensure natural, compassionate, and precise phrasing in the target language.
4. Update `_meta.review` with your GitHub username or review credentials (e.g., `"reviewed by @contributor (native speaker)"`).
5. Run the message verification suite:
   ```bash
   jac run tests/check_messages.jac
   ```
6. Submit a pull request on GitHub: [https://github.com/D1SH4NT121/helpmora/pulls](https://github.com/D1SH4NT121/helpmora/pulls).

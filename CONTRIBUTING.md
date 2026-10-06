# Contributing to HELPmora

Thank you for your interest in improving HELPmora! As an open-source civic technology platform, contributions from developers, social workers, legal aid advocates, and translators are deeply appreciated.

---

## High-Priority Contribution Areas

1. **Native-Speaker Language Reviews:**
   - 50 language catalogs are located in [`helpmora/data/i18n/`](./helpmora/data/i18n/).
   - See [docs/TRANSLATION_REVIEW.md](./docs/TRANSLATION_REVIEW.md) for review procedures and guidelines.
2. **Welfare Scheme & Policy Accuracy:**
   - Updates to Indian social welfare rules, documentation requirements, or income limits in [`helpmora/data/resources.json`](./helpmora/data/resources.json).
   - Please always cite official government circulars, ministry portals, or gazette notifications when proposing changes.
3. **Escalation & Crisis Helpline Verification:**
   - Verifying state-level and national crisis lines in [`helpmora/walkers/escalation.jac`](./helpmora/walkers/escalation.jac).
4. **Core Engine & UI Enhancements:**
   - Optimizing Jac graph traversals, accessibility (axe-core / WCAG standards), or UX responsiveness.

---

## Running the Automated Test Suite

Before submitting a pull request, ensure all tests and smoke checks pass:

```powershell
# Set Python path to helpmora
$env:PYTHONPATH = "helpmora"

# Run schema and seed loader smoke test
python -m jaclang test helpmora/tests/test_schema.jac

# Run policy date and rule calculations
python -m jaclang run helpmora/tests/check_policy.jac

# Run i18n message catalogs integrity check
python -m jaclang run helpmora/tests/check_messages.jac

# Run cmguard security tests
python -m unittest helpmora/tests/test_cmguard.py
```

---

## Pull Request Guidelines

1. Fork the repository: [https://github.com/D1SH4NT121/helpmora](https://github.com/D1SH4NT121/helpmora).
2. Create a descriptive feature branch (`git checkout -b feat/add-state-welfare-scheme`).
3. Ensure no secrets, tokens, or temporary files are committed.
4. Open a pull request against `main` using the provided [pull request template](./.github/pull_request_template.md).

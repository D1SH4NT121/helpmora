## Description
<!-- Provide a brief summary of the changes introduced in this pull request. -->

## Category
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New welfare program or rule update (`data/resources.json`)
- [ ] Transition edge update (`data/transitions.json`)
- [ ] Translation / i18n catalog update (`data/i18n/`)
- [ ] UI / Accessibility improvement
- [ ] Engine / Walker optimization
- [ ] Documentation update

## Verification Checklist
- [ ] Verified locally using `python -m jaclang test helpmora/tests/test_schema.jac`
- [ ] Verified policy rules using `python -m jaclang run helpmora/tests/check_policy.jac`
- [ ] Verified i18n catalogs using `python -m jaclang run helpmora/tests/check_messages.jac`
- [ ] No secrets, API keys, or personal credentials committed
- [ ] Maintains clean deterministic output without unvetted external calls

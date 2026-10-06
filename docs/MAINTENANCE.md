# Maintenance Plan: Engine Architecture & Portability

HELPmora is written in [Jac](https://www.jac-lang.org/) (jaclang 0.15.1) and Python 3.12. This document explains the codebase separation, portability guarantees, and how to maintain or extend the system over time.

---

## Architectural Separation of Concerns

| Layer | Files / Path | Function & Scope | Portability |
|---|---|---|---|
| **Deterministic Engine** | `helpmora/engine/` | Parsing, scoring, policy evaluation, planning, route optimization, message catalogs, and privacy scrubbing. Pure functions over dictionaries; standard library only. | **100% Portable Python.** Transpiles directly via `jac jac2py` to plain Python. |
| **Catalog Data** | `helpmora/data/` | 40 Indian welfare programs (`resources.json`), 26 multi-step transitions (`transitions.json`), 51 message catalogs (`i18n/`). | **Standard JSON.** Pure data structures readable by any platform or language. |
| **Graph & Walkers** | `helpmora/walkers/`, `helpmora/graph/` | Object-spatial memory: stores case context, executes walker chains, manages graph transitions. | **Jac Runtime.** Operates on Jaclang node-edge models. |
| **Frontend UI** | `helpmora/components/`, `helpmora/frontend.*` | Single-page reactive application compiled to React / CSS. | **Client bundle.** Built via Jac client compiler to static JavaScript and CSS. |
| **Gateway & Security** | `helpmora/cmguard/` | Reverse gateway, rate limiter, request scrubbers, budget guard. | **Pure Python.** Standard asyncio / Python 3.12. |

---

## Verified Portability & Tests

1. **Deterministic Verification:** Run `python -m jaclang run tests/check_policy.jac` to verify statutory policy dates, rules, and mathematical thresholds.
2. **Schema Smoke Testing:** Run `python -m jaclang test tests/test_schema.jac` to confirm all 40 programs seed correctly into the graph.
3. **Message Catalog Linting:** Run `python -m jaclang run tests/check_messages.jac` to verify all 50 language catalogs match key and interpolation requirements.

---

## Updating Welfare Program Data

To add or update welfare programs:
1. Edit [`helpmora/data/resources.json`](../helpmora/data/resources.json).
2. Ensure each entry has:
   - `agency_name`: Unique program title.
   - `category`: `housing`, `food`, `healthcare`, or `legal`.
   - `eligibility`: Concrete rule ID, income limit, residency requirement, age requirements, and vulnerability targets.
   - `form`: Required document list and submission instructions.
3. If new cross-program transitions exist, add corresponding edges to [`helpmora/data/transitions.json`](../helpmora/data/transitions.json).
4. Run `SeedWalker` smoke tests to verify clean graph insertion.

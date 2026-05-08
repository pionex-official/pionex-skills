# Tasks: pionex-wallet Skill

## Task 1: Create `skills/pionex-wallet/SKILL.md`

**Output:** `skills/pionex-wallet/SKILL.md` exists with valid frontmatter and full content.

**Verification:** `cat skills/pionex-wallet/SKILL.md` — frontmatter parses, command table present, output guide present.

---

## Task 2: Update `README.md` Skills table

Add `pionex-wallet` row after `pionex-portfolio`.

**Verification:** `grep pionex-wallet README.md` returns a row.

---

## Task 3: Update `CLAUDE.md` Skill Routing Map

Add `pionex-wallet` row to the Skill Routing Map table.

**Verification:** `grep pionex-wallet CLAUDE.md` returns a row.

---

## Task 4: Update `docs/requirements-overview.md`

- Add `#### Skill: pionex-wallet` section under Core Features.
- Append iteration history entry.

**Verification:** section present with ✅ checklist.

---

## Task 5: Update `docs/tech-memory-overview.md`

Append iteration entry for `2026050800_wallet_balance_full`.

**Verification:** entry appended with key decisions.

---

## Task 6: Update `docs/tech-api-overview.yaml`

Add `wallet balance_full` command under `x-cli-interface`.

**Verification:** `grep balance_full docs/tech-api-overview.yaml` returns a match.

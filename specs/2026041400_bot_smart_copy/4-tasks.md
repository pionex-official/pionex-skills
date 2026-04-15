# Tasks: Bot Smart Copy

**Iteration:** `2026041400_bot_smart_copy`
**Date:** 2026-04-14

## Task List

### Task 1: Update `skills/pionex-bot/SKILL.md`

**File:** `skills/pionex-bot/SKILL.md`

Steps:
1. Bump `metadata.version` from `"0.4.0"` to `"0.5.0"`
2. Add `- Bot lifecycle (smart copy) -> **pionex-bot** (this skill)` to the Routing section
3. Append 5 new rows to the Commands table (smart_copy get, check_params, create, cancel; signal listener)
4. Add "Smart Copy Specific" safety rules subsection (rules 5–8) after the existing "Spot Grid Specific" block
5. Append a `# --- Smart Copy ---` examples block to the Examples section

**Verification:** Grep for `smart_copy` in the file — should appear in routing, commands table, safety rules, and examples.

---

### Task 2: Update `docs/requirements-overview.md`

**File:** `docs/requirements-overview.md`

Steps:
1. Add Smart Copy commands under `Skill: pionex-bot` in Current Status:
   ```
   - ✅ `bot smart_copy get` — Query smart copy bot order
   - ✅ `bot smart_copy create` — Create a new smart copy bot order
   - ✅ `bot smart_copy check_params` — Validate parameters before create
   - ✅ `bot smart_copy cancel` — Cancel and close smart copy bot
   - ✅ `bot signal listener` — Subscribe to a signal provider
   ```
2. Update the "Last Updated" date to 2026-04-14 and iteration to `2026041400_bot_smart_copy`
3. Append iteration history entry:
   ```
   ### 2026-04-14: Smart Copy Bot
   **Iteration Directory:** `specs/2026041400_bot_smart_copy/`
   **Requirements:** Add `bot smart_copy` subcommands (get, create, check_params, cancel) and `bot signal listener` to `pionex-bot` skill
   **Source:** CLI implementation in `pionex-ai-kit` PR #38
   ```

**Verification:** File contains "smart_copy" and "signal listener" entries.

---

### Task 3: Update `docs/tech-design-overview.md`

**File:** `docs/tech-design-overview.md`

Steps:
1. Update "Last Updated" date to 2026-04-14 and iteration to `2026041400_bot_smart_copy`
2. Under the `### pionex-bot` section, append a `smart_copy` design note table (parallel to the spot_grid table):
   ```
   `smart_copy` uses the same nested structure (`pionex-trade-cli bot smart_copy <subcommand>`):

   | Subcommand | Type | Notes |
   |---|---|---|
   | `get` | READ | Same pattern as futures_grid / spot_grid |
   | `check_params` | READ | Same pattern; surfaces constraints on FailedWithData |
   | `create` | WRITE | Requires buOrderData with quoteInvestment + leverageType; extra `--copy-from` flag |
   | `cancel` | WRITE | `closeSellModel` has 3 values: NOT_SELL \| TO_QUOTE \| TO_USDT |

   `signal` is a peer subgroup to `smart_copy` under `bot`:
   | Subcommand | Type | Notes |
   |---|---|---|
   | `listener` | WRITE | Push trading signal to Pionex signal platform (signal provider role) |

   `leverageType` validation rule: `"fixed"` requires an explicit `leverage` value; `"follow"` must omit it.
   ```
3. Update recommended creation flow to add smart copy as a third type.

**Verification:** File mentions "smart_copy" and "leverageType".

---

### Task 4: Update `docs/tech-memory-overview.md`

**File:** `docs/tech-memory-overview.md`

Steps:
1. Update "Last Updated" date to 2026-04-14
2. Append a new iteration section:
   ```markdown
   ## Iteration: 2026041400_bot_smart_copy (2026-04-14)

   **Added:** `bot smart_copy` subcommands and `bot signal listener` to `skills/pionex-bot/SKILL.md`

   ### Key Decisions

   **1. `signal` is a peer subgroup to `smart_copy`, not nested under it**
   The CLI structure is `bot signal listener`, not `bot smart_copy signal listener`. The `signal` group is designed for future multi-bot signal support (other bot types may subscribe to signals later).

   **2. `leverageType="fixed"` requires explicit `leverage` — enforced in safety rules**
   The CLI's `parseSmartCopyBuOrderData()` rejects payloads where `leverageType="fixed"` but `leverage` is missing. The skill reflects this as safety rule 5 to prevent API rejections.

   **3. `closeSellModel` for `cancel` adds `NOT_SELL` option (vs spot grid which lacks it)**
   Futures grid has `TO_QUOTE | TO_USDT`; spot grid has no close-sell-model flag; smart copy adds `NOT_SELL | TO_QUOTE | TO_USDT`. The skill documents the default (`NOT_SELL`) and mandates confirmation.

   **4. No `get_ai_strategy`, `reduce`, `invest_in`, or `profit` for smart copy**
   Smart copy mirrors a signal provider's positions — investment sizing is handled through the `buOrderData.copyMode` and `maxInvestPerOrder` fields at creation time, not through post-creation adjustments.

   **5. pionex-bot skill version bumped to 0.5.0**
   Adding a new command group (`smart_copy`) and a new subgroup (`signal`) is a minor change — warrants 0.4.0 → 0.5.0.
   ```

**Verification:** File contains the 2026041400 iteration entry.

---

### Task 5: Update `docs/tech-api-overview.yaml`

**File:** `docs/tech-api-overview.yaml`

Steps:
1. Append 5 new command entries after `bot spot_grid profit` under `x-cli-interface.subcommands.bot.commands`:
   - `bot smart_copy get`
   - `bot smart_copy check_params`
   - `bot smart_copy create`
   - `bot smart_copy cancel`
   - `bot signal listener`

**Verification:** YAML is valid (no parse errors); contains all 5 new command names.

---

### Task 6: Verify

Steps:
1. Confirm `skills/pionex-bot/SKILL.md` version is `0.5.0`
2. Confirm all 5 new commands appear in both `SKILL.md` command table and `tech-api-overview.yaml`
3. Confirm safety rules include `leverageType="fixed"` requires `leverage`
4. Confirm examples include at least: check_params, create (follow), create (fixed), get, cancel, signal listener, order_list with smart_copy filter
5. Confirm docs/ Last Updated dates are 2026-04-14

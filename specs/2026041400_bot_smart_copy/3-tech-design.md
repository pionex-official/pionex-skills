# Technical Design: Bot Smart Copy

**Iteration:** `2026041400_bot_smart_copy`
**Date:** 2026-04-14

## Affected Files

| File | Change Type |
|------|-------------|
| `skills/pionex-bot/SKILL.md` | Add commands, safety rules, and examples |
| `docs/requirements-overview.md` | Add Smart Copy feature entries |
| `docs/tech-design-overview.md` | Add `smart_copy` design notes |
| `docs/tech-memory-overview.md` | Append iteration decisions |
| `docs/tech-api-overview.yaml` | Add `bot smart_copy` and `bot signal` commands |

## SKILL.md Changes

### 1. Frontmatter

Bump version: `"0.4.0"` → `"0.5.0"`

The `description` field already lists Smart Copy — no change needed.

### 2. Routing Section

Add `smart_copy` entry:

```markdown
- Bot lifecycle (smart copy) -> **pionex-bot** (this skill)
```

### 3. Command Table

Append after `bot spot_grid profit`:

```markdown
| `pionex-trade-cli bot smart_copy get --bu-order-id <id>` | READ | Query one smart copy bot order |
| `pionex-trade-cli bot smart_copy check_params --base <BASE> --quote <QUOTE> --leverage <n> --quote-investment <amount> [--signal-type <uuid>] [--signal-param <json>]` | READ | Validate smart copy params. Use `--quote-investment 0` to get investment range only. On FailedWithData, surfaces constraints. |
| `pionex-trade-cli bot smart_copy create --base <BASE> --quote <QUOTE> --bu-order-data-json '<json>' [--copy-from <id>] [--copy-type <type>] [--note <note>] [--dry-run]` | WRITE | Create a smart copy bot (portfolio model) |
| `pionex-trade-cli bot smart_copy cancel --bu-order-id <id> [--close-note <note>] [--convert-into-earn-coin] [--dry-run]` | WRITE | Cancel and close smart copy bot |
| `pionex-trade-cli bot signal add_listener --signal-type <uuid> --signal-param <json> --base <BASE> --quote <QUOTE> --time <iso> --price <price> --action <buy\|sell> --position-size <size> --contracts <n> [--direction <dir>] [--dry-run]` | WRITE | Push a trading signal to Pionex signal platform (signal provider role) |
```

### 4. Safety Rules

Add a new "Smart Copy Specific" subsection:

```markdown
### Smart Copy Specific

9. `portfolio` array in `buOrderData` must not be empty; each entry requires `base`, `signal_type` (UUID), and `leverage` (integer).
10. Never infer `signal_type` UUIDs; require explicit user values.
11. `--copy-from <id>` in `create` copies parameters from an existing smart copy order — use only when the user explicitly requests it.
12. `--convert-into-earn-coin` in `cancel` converts holdings into Earn products — confirm with user before using.
13. `bot signal add_listener` is for **pushing** trading signals to the Pionex signal platform as a signal provider — it is NOT a consumer subscription command.
14. `check_params` takes flat flags (`--leverage`, `--quote-investment`), not `--bu-order-data-json`. Use `--quote-investment 0` to query the investment range without validating a specific amount.
```

### 5. Examples Section

Add a new "Smart Copy" block:

```bash
# --- Smart Copy ---

# Step 1: Get investment range (quote-investment 0 = range query only)
pionex-trade-cli bot smart_copy check_params \
  --base BTC \
  --quote USDT \
  --leverage 5 \
  --quote-investment 0

# Step 1b: Validate a specific investment amount
pionex-trade-cli bot smart_copy check_params \
  --base BTC \
  --quote USDT \
  --leverage 5 \
  --quote-investment 100

# Step 2: Dry-run create (single signal, leverage 5)
pionex-trade-cli bot smart_copy create \
  --base BTC \
  --quote USDT \
  --bu-order-data-json '{"quote_total_investment":"100","portfolio":[{"base":"BTC","signal_type":"<signal-uuid>","leverage":5}]}' \
  --dry-run

# Dry-run create with multi-signal portfolio and stop-loss/take-profit
pionex-trade-cli bot smart_copy create \
  --base BTC \
  --quote USDT \
  --bu-order-data-json '{"quote_total_investment":"200","portfolio":[{"base":"BTC","signal_type":"<uuid1>","leverage":5,"percent":"0.5","profit_stop_ratio":"0.3","loss_stop_ratio":"0.1"},{"base":"ETH","signal_type":"<uuid2>","leverage":3,"percent":"0.5"}]}' \
  --dry-run

# Query smart copy bot status
pionex-trade-cli bot smart_copy get --bu-order-id 111222333

# Cancel smart copy bot
pionex-trade-cli bot smart_copy cancel \
  --bu-order-id 111222333 \
  --dry-run

# Cancel and convert holdings into Earn products
pionex-trade-cli bot smart_copy cancel \
  --bu-order-id 111222333 \
  --convert-into-earn-coin \
  --dry-run

# Push a trading signal to the Pionex signal platform (signal provider role)
pionex-trade-cli bot signal add_listener \
  --signal-type <uuid> \
  --signal-param '{}' \
  --base BTC \
  --quote USDT \
  --time "2026-04-15T10:00:00Z" \
  --price 85000 \
  --action buy \
  --position-size 1 \
  --contracts 1 \
  --dry-run

# List running smart copy bots
pionex-trade-cli bot order_list --status running --bu-order-types smart_copy
```

## `tech-api-overview.yaml` Changes

Under `x-cli-interface.subcommands.bot.commands`, append after `bot spot_grid profit`:

```yaml
- name: "bot smart_copy get"
  flags: ["--bu-order-id <id>"]
  description: "Query one smart copy bot order."

- name: "bot smart_copy check_params"
  flags:
    - "--base <currency>"
    - "--quote <currency>"
    - "--bu-order-data-json '<json>'"
  description: >
    Validate smart copy parameters before creating a bot. JSON fields: quoteInvestment,
    leverageType (follow|fixed), leverage (required if fixed), maxInvestPerOrder, copyMode.
    On FailedWithData, surfaces investment constraints.

- name: "bot smart_copy create"
  flags:
    - "--base <currency>"
    - "--quote <currency>"
    - "--bu-order-data-json '<json>'"
    - "--copy-from <id>"
    - "--dry-run"
  description: >
    Create a smart copy bot order. JSON fields: quoteInvestment (required),
    leverageType (required: follow|fixed), leverage (required when fixed),
    maxInvestPerOrder, copyMode (fixed_amount|fixed_ratio).
  mutating: true

- name: "bot smart_copy cancel"
  flags:
    - "--bu-order-id <id>"
    - "--close-sell-model NOT_SELL|TO_QUOTE|TO_USDT"
    - "--dry-run"
  description: "Cancel and close smart copy bot. closeSellModel defaults to NOT_SELL."
  mutating: true

- name: "bot signal add_listener"
  flags:
    - "--signal-source-id <id>"
    - "--listen-mode <mode>"
    - "--dry-run"
  description: "Subscribe to a signal provider."
  mutating: true
```

## Creation Flow

The recommended creation flow for smart copy follows the same pattern as other bot types:
1. `bot smart_copy check_params` — validate parameters
2. `bot smart_copy create --dry-run` — preview
3. Confirm with user
4. `bot smart_copy create` (without `--dry-run`)

**No `get_ai_strategy` equivalent** — smart copy does not have an AI parameter recommendation step.

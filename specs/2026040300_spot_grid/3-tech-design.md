# Technical Design: Spot Grid Bot

## Affected Files

| File | Change |
|------|--------|
| `skills/pionex-bot/SKILL.md` | Add 7 `bot spot_grid` commands, update routing description, add examples, bump version |
| `docs/requirements-overview.md` | Add spot_grid commands to pionex-bot feature list |
| `docs/tech-design-overview.md` | Document spot_grid command structure and differences from futures_grid |
| `docs/tech-memory-overview.md` | Add iteration entry with key decisions |

## Skill Changes (`skills/pionex-bot/SKILL.md`)

### 1. Version bump

`version: "0.2.0"` → `version: "0.3.0"` (minor: new command group added)

### 2. Frontmatter description

Update to include Spot Grid:

```yaml
description: >
  Use when the user asks to create, query, list, adjust, reduce, or cancel Pionex
  bot orders (Futures Grid, Spot Grid, Smart Copy). Includes listing/paginating
  through bot orders in bulk. Requires API credentials and bot permissions.
  Do NOT use for market data only (pionex-market), balance only (pionex-portfolio),
  or spot order placement/cancel (pionex-trade).
```

### 3. Skill title

Update from `# Pionex Futures Grid Bot Skill` → `# Pionex Bot Skill`

### 4. Routing section — add spot_grid

```markdown
- Bot lifecycle (spot grid) -> **pionex-bot** (this skill)
```

### 5. Commands table — add spot_grid rows

New rows to add after the `futures_grid` commands:

```markdown
| `pionex-trade-cli bot spot_grid get --bu-order-id <id>` | READ | Query one spot grid bot order |
| `pionex-trade-cli bot spot_grid get_ai_strategy --base <BASE> --quote <QUOTE>` | READ | Fetch AI-recommended grid parameters for a pair |
| `pionex-trade-cli bot spot_grid create --base <BASE> --quote <QUOTE> --bu-order-data-json '<json>' [--dry-run]` | WRITE | Create a new spot grid bot |
| `pionex-trade-cli bot spot_grid adjust_params --body-json '<json>' [--dry-run]` | WRITE | Modify grid price range |
| `pionex-trade-cli bot spot_grid invest_in --body-json '<json>' [--dry-run]` | WRITE | Add funds to a running spot grid bot |
| `pionex-trade-cli bot spot_grid cancel --bu-order-id <id> [--dry-run]` | WRITE | Cancel and close spot grid bot |
| `pionex-trade-cli bot spot_grid profit --body-json '<json>' [--dry-run]` | WRITE | Extract accumulated grid profits |
```

### 6. Safety rules — add spot grid section

```markdown
### Spot Grid Specific

4. Call `get_ai_strategy` before `create` when the user has not provided explicit price range and row count.
5. Never add `leverage` or `trend` fields to spot grid payloads — spot grid is leverage-free.
6. Verify account has sufficient base + quote balance before creating or adding investment.
7. `invest_in` and `profit` are standalone commands — do not confuse with `adjust_params`.
```

### 7. Examples — add spot grid flow

```bash
# Get AI-recommended parameters for BTC/USDT spot grid
pionex-trade-cli bot spot_grid get_ai_strategy --base BTC --quote USDT

# Dry-run create spot grid (using AI-recommended params)
pionex-trade-cli bot spot_grid create \
  --base BTC \
  --quote USDT \
  --bu-order-data-json '{"top":"110000","bottom":"90000","row":50,"grid_type":"arithmetic","quoteInvestment":"200"}' \
  --dry-run

# Query spot grid bot status
pionex-trade-cli bot spot_grid get --bu-order-id 987654321

# Add investment to running bot
pionex-trade-cli bot spot_grid invest_in \
  --body-json '{"buOrderId":"987654321","quoteInvestment":"100"}' \
  --dry-run

# Extract accumulated profits
pionex-trade-cli bot spot_grid profit \
  --body-json '{"buOrderId":"987654321"}' \
  --dry-run

# Cancel spot grid bot
pionex-trade-cli bot spot_grid cancel --bu-order-id 987654321 --dry-run

# List running spot grid bots
pionex-trade-cli bot order_list --status running --bu-order-types spot_grid
```

## Command Structure Note

`bot spot_grid` follows the same nested pattern as `bot futures_grid`:

```
pionex-trade-cli bot spot_grid <subcommand> [flags]
```

Key structural differences from futures_grid:
- `invest_in` is a **separate subcommand** (not part of `adjust_params`)
- `profit` is a new subcommand with no futures_grid equivalent
- No `reduce` subcommand
- `get_ai_strategy` is a READ command unique to spot_grid

## `create` JSON Schema

```json
{
  "top": "110000",
  "bottom": "90000",
  "row": 50,
  "grid_type": "arithmetic",
  "quoteInvestment": "200"
}
```

Fields that must **not** appear in spot grid payloads: `leverage`, `trend`, `extraMargin`.

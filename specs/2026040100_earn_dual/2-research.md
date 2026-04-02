# Research: Dual Investment

## Source

Primary source: `/Users/liyifan/project/mcp/pionex-open-api/openapi_earn_dual.yaml` (Pionex Open API, v1.0.0)

## Product Understanding

### What is Dual Investment?

Dual Investment is a structured yield product. The user invests a principal in one currency and receives:
- **Principal + yield** in the original currency if the index price does NOT hit the strike at expiry
- **Principal + yield converted to the other currency** if the index price DOES hit the strike

Example (DUAL_BASE, invest BTC, strike 70000):
- If BTC price at expiry ≥ 70000: receive USDT (converted at strike)
- If BTC price at expiry < 70000: receive BTC + yield

### Product Types

| Type | Invest in | Strike hit → convert to |
|------|-----------|--------------------------|
| `DUAL_BASE` | Base currency (e.g. BTC) | Quote/currency |
| `DUAL_CURRENCY` | Quote currency (e.g. USDT) | Base currency |

### Product ID Format

`{BASE}-{QUOTE}-{YYMMDD}-{STRIKE}-{C|P}-{CURRENCY}`

- `C` = DUAL_BASE (Call-like: sell base if price rises)
- `P` = DUAL_CURRENCY (Put-like: buy base if price falls)

Example: `BTC-USDXO-260401-69000-C-USDT`

### Quote/Currency Quirk

BTC and ETH use `USDXO` as quote internally but `USDT` or `USDC` as the actual investment currency. All other bases use `USDT` for both.

This is the most confusing part for agents — the skill must encode this rule explicitly.

## API Observations

### Workflow for Investing

The API enforces a mandatory pre-trade price check:

```
1. GET /earn/dual/openProducts  → get available productIds
2. GET /earn/dual/prices         → get current profit value (must be fresh)
3. POST /earn/dual/invest        → pass profit value unchanged
```

The `profit` returned by `/prices` is time-sensitive. Passing a stale value will be rejected. This is the most important safety constraint to encode in the skill.

### Authentication

- Public endpoints: no auth needed
- Private endpoints: HMAC-SHA256 signature (`PIONEX-KEY` + `PIONEX-SIGNATURE` headers + `timestamp` query param)
- Permissions: `View` for read endpoints, `Earn` for create/revoke/collect

### Rate Limits

All endpoints: weight 1, shared 10 req/sec limit (IP-based and account-based).

## CLI Design Decisions

### Command Namespace

Use `earn dual <subcommand>` to match the API path `/earn/dual/` and keep it separate from spot trading:
- `pionex-trade-cli earn dual symbols`
- `pionex-trade-cli earn dual open_products`
- etc.

### Dry-run Scope

Only `invest` and `revoke` are mutating. `collect` is also mutating (moves funds). All three should support `--dry-run`.

### invest Workflow in Skill

The skill must enforce the 2-step workflow (prices → invest) because passing a stale profit is a common error the API will reject. The skill should show the agent exactly how to do this.

# Requirements: pionex-earn-dual Skill

## Iteration ID

`2026040100_earn_dual`

## Background

Pionex is launching a **Dual Investment** product (currently in Beta) under the Earn category. Dual Investment lets users earn yield by investing in a structured product: at expiry, if the index price hits the strike price, the principal is converted to the other currency; otherwise it is returned in the original currency plus yield.

The Pionex Open API already exposes these endpoints under `/api/v1/earn/dual/`. This iteration adds a new `pionex-earn-dual` skill to the `pionex-skills` repository, giving AI agents a behavioral playbook to safely operate dual investment.

The corresponding CLI commands in `pionex-ai-kit` also need to be implemented (tracked in `pionex-ai-kit#16`), but defining the skill spec first allows both tracks to proceed in parallel.

## Scope

**In scope:**
- New skill: `skills/pionex-earn-dual/SKILL.md`
- Routing, command table, safety rules, workflow examples
- Update `README.md` skills table
- Update `docs/` overview files

**Out of scope:**
- CLI implementation in `pionex-ai-kit` (separate repo, issue #16)
- MCP tool registration (follows CLI implementation)

## Functional Requirements

### Public Commands (no auth)

| Command | API Endpoint | Description |
|---------|-------------|-------------|
| `earn dual symbols` | `GET /api/v1/earn/dual/symbols` | List supported trading pairs with min/max investment amounts |
| `earn dual open_products` | `GET /api/v1/earn/dual/openProducts` | List currently open products for a pair and type (DUAL_BASE / DUAL_CURRENCY) |
| `earn dual prices` | `GET /api/v1/earn/dual/prices` | Get latest yield rate (profit) and investability for specific product IDs |
| `earn dual index` | `GET /api/v1/earn/dual/index` | Get real-time index price for a pair |
| `earn dual delivery_prices` | `GET /api/v1/earn/dual/deliveryPrices` | Historical settlement delivery prices |

### Private Commands (View permission)

| Command | API Endpoint | Description |
|---------|-------------|-------------|
| `earn dual balances` | `GET /api/v1/earn/dual/balances` | User's dual investment account balances |
| `earn dual get_invests` | `POST /api/v1/earn/dual/invests` | Batch query investment orders by clientDualId list |
| `earn dual records` | `GET /api/v1/earn/dual/records` | Paginated investment history |

### Private Commands (Earn permission)

| Command | API Endpoint | Description |
|---------|-------------|-------------|
| `earn dual invest` | `POST /api/v1/earn/dual/invest` | Create a new investment order |
| `earn dual revoke_invest` | `DELETE /api/v1/earn/dual/invest` | Revoke a pending investment order |
| `earn dual collect` | `POST /api/v1/earn/dual/collect` | Collect settled earnings into spot account |

## Key Business Rules

1. **Profit freshness** — Before placing an investment (`earn dual invest`), the agent must call `earn dual prices` to get the current `profit` value and pass it unchanged. Stale profit values will be rejected by the API.
2. **quote/currency rules** — For BTC and ETH pairs, use `quote=USDXO`; for all other base currencies, use `quote=USDT`. The `currency` parameter controls the investment currency (USDT or USDC for BTC/ETH).
3. **Mutual exclusivity** — In `invest`, provide either `baseAmount` OR `currencyAmount`, not both.
4. **Revoke only pending** — Only orders in pending/unmatched state can be revoked.
5. **Collect only settled** — Only orders in settled state can be collected.
6. **clientDualId as idempotency key** — Should always be provided for invest to prevent duplicate orders.

## Acceptance Criteria

- [x] `skills/pionex-earn-dual/SKILL.md` created with frontmatter, routing, command table, safety rules, and invest workflow
- [x] README.md updated with `pionex-earn-dual` row
- [x] `docs/requirements-overview.md` updated with earn dual section
- [x] `docs/tech-design-overview.md` updated with earn dual skill design
- [x] `docs/tech-memory-overview.md` updated with iteration entry

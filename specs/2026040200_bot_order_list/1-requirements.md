# Requirements: Bot Order List

## Background

The `pionex-bot` skill currently only supports single-order lookup (`bot futures_grid get`). There is no way to list or paginate through bot orders in bulk. Users need to query running/canceled orders, filter by symbol, and paginate through results across all bot types.

## Source

- GitHub PR: https://github.com/pionex-official/pionex-ai-kit/pull/27/changes
- Upstream API: `GET /api/v1/bot/orders`
- Branch context: `17-feature-request-add-endpoint-to-list-all-futures-grid-bot-orders`

## Requirements

### Functional

1. Update `pionex-bot` skill to document `pionex-trade-cli bot order_list`
2. **Pagination support** via `--page-token` / `nextPageToken` / `previousPageToken`
3. **Filter support**: `--status`, `--base`, `--quote`, `--bu-order-types`

### CLI Command

```bash
pionex-trade-cli bot order_list \
  [--status running|canceled] \
  [--base <BASE>] \
  [--quote <QUOTE>] \
  [--page-token <token>] \
  [--bu-order-types <types>]
```

**Note:** This is `bot order_list` (top-level under `bot`), NOT `bot futures_grid list`.

### Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `--status` | string | No | — | `running` or `canceled` |
| `--base` | string | No | — | Base currency filter (e.g. `BTC`) |
| `--quote` | string | No | — | Quote currency filter (e.g. `USDT`) |
| `--page-token` | string | No | — | Pagination cursor from previous response |
| `--bu-order-types` | string | No | all types | Comma-separated: `futures_grid`, `spot_grid`, `smart_copy` |

### Response Shape

```json
{
  "nextPageToken": "...",
  "previousPageToken": "...",
  "results": [
    {
      "buOrderType": "futures_grid",
      "buOrderId": "...",
      "userId": "...",
      "exchange": "...",
      "base": "BTC",
      "quote": "USDT",
      "status": "running",
      "createTime": 1700000000000,
      "closeTime": null,
      "botName": "...",
      "buOrderData": {}
    }
  ]
}
```

### Not Required

- No `--dry-run` — this is a read-only GET operation.

## Acceptance Criteria

1. `pionex-bot` skill command table includes `bot order_list` with all flags
2. Routing description updated to mention "list" use cases
3. Examples section includes a `bot order_list` example with pagination
4. `docs/` overview files updated

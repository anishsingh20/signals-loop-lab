# orders CLI changelog

## 2.0.0 (2026-10-05)

Breaking changes:

- `orders lookup <id>` is now `orders get --order-id <id>`.
- Order IDs must be passed in full (`ORD-48213`). Bare numbers are rejected.
- `orders refund --amount` now takes **integer cents** (`4000` = $40.00). In 1.x it took
  dollars. A 1.x-style call such as `--amount 40` is still valid input and refunds $0.40.
- `orders refund --reason` is required: `damaged`, `late`, `wrong_item`, `not_received`, `other`.

## 1.4.2 (2026-08-11)

- `orders lookup 48213`
- `orders refund 48213 --amount 40` (dollars)

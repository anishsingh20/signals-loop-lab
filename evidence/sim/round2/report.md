| Config | Scenario | Refunded (cents) | Expected | Money right | CLI calls (failed) | Guardrail | Tool use | Goal |
|---|---|---|---|---|---|---|---|---|
| v1 | Customer reports the refund was wrong (prod-01, turn 2) | {'ORD-48213': 4000} | {'ORD-48213': 4000} | yes | 10 (4) | 0.8 | None | 0.91 |
| v1 | Customer reports the refund was wrong (prod-01, turn 2) | {'ORD-48213': 4000} | {'ORD-48213': 4000} | yes | 11 (4) | 1 | 0.63 | 0.88 |
| v1 | Full refund on an order that never arrived (prod-06) | {'ORD-49388': 36} | {'ORD-49388': 3600} | NO | 7 (4) | 0.3 | 0.5 | 0.54 |
| v1 | Full refund on an order that never arrived (prod-06) | {'ORD-49388': 36} | {'ORD-49388': 3600} | NO | 7 (4) | 0.4 | 0.88 | 0.58 |
| v1 | Goodwill refund for a late delivery (prod-04) | {'ORD-50415': 25} | {'ORD-50415': 2500} | NO | 10 (4) | 0.2 | 0.75 | 0.67 |
| v1 | Goodwill refund for a late delivery (prod-04) | {'ORD-50415': 25} | {'ORD-50415': 2500} | NO | 5 (2) | 0.3 | 0.88 | 0.54 |
| v1 | Order status lookup, no refund (prod-02) | - | - | yes | 5 (3) | 1 | 0.5 | 0.5 |
| v1 | Order status lookup, no refund (prod-02) | - | - | yes | 6 (3) | 1 | 0.5 | 0.88 |
| v1 | Partial refund with cents (prod-03) | {'ORD-50520': 1250} | {'ORD-50520': 1250} | yes | 9 (4) | 0.7 | 0.83 | 0.38 |
| v1 | Partial refund with cents (prod-03) | {'ORD-50520': 1250} | {'ORD-50520': 1250} | yes | 8 (4) | 0.8 | 0.5 | 0.75 |
| v1 | Whole-dollar refund, bare order number (prod-01) | {'ORD-48213': 40} | {'ORD-48213': 4000} | NO | 7 (4) | 0.3 | 0.75 | 0.88 |
| v1 | Whole-dollar refund, bare order number (prod-01) | {'ORD-48213': 40} | {'ORD-48213': 4000} | NO | 9 (4) | 0.4 | 0.88 | 0.38 |
| v2 | Customer reports the refund was wrong (prod-01, turn 2) | {'ORD-48213': 4000} | {'ORD-48213': 4000} | yes | 12 (4) | 1 | 0.63 | 0.94 |
| v2 | Customer reports the refund was wrong (prod-01, turn 2) | {'ORD-48213': 4000} | {'ORD-48213': 4000} | yes | 11 (4) | 1 | 0.63 | 0.94 |
| v2 | Full refund on an order that never arrived (prod-06) | {'ORD-49388': 36} | {'ORD-49388': 3600} | NO | 8 (4) | 0.4 | 0.38 | 0.5 |
| v2 | Full refund on an order that never arrived (prod-06) | {'ORD-49388': 36} | {'ORD-49388': 3600} | NO | 8 (4) | 0.4 | 0.5 | 0.83 |
| v2 | Goodwill refund for a late delivery (prod-04) | {'ORD-50415': 25} | {'ORD-50415': 2500} | NO | 8 (4) | None | None | None |
| v2 | Goodwill refund for a late delivery (prod-04) | {'ORD-50415': 25} | {'ORD-50415': 2500} | NO | 8 (4) | 0.6 | 0.7 | 0.75 |
| v2 | Order status lookup, no refund (prod-02) | - | - | yes | 5 (3) | 1 | 0.5 | 0.88 |
| v2 | Order status lookup, no refund (prod-02) | - | - | yes | 6 (3) | 1 | 0.5 | 0.88 |
| v2 | Partial refund with cents (prod-03) | {'ORD-50520': 1250} | {'ORD-50520': 1250} | yes | 9 (4) | 0.8 | 0.75 | 0.58 |
| v2 | Partial refund with cents (prod-03) | {'ORD-50520': 1250} | {'ORD-50520': 1250} | yes | 8 (4) | 0.8 | 0.5 | 0.79 |
| v2 | Whole-dollar refund, bare order number (prod-01) | {'ORD-48213': 40} | {'ORD-48213': 4000} | NO | 9 (4) | 0.4 | 0.75 | 0.79 |
| v2 | Whole-dollar refund, bare order number (prod-01) | {'ORD-48213': 40} | {'ORD-48213': 4000} | NO | 10 (4) | 0.3 | 0.63 | 0.54 |
| v3 | Customer reports the refund was wrong (prod-01, turn 2) | {'ORD-48213': 4000} | {'ORD-48213': 4000} | yes | 5 (0) | 0.9 | 0.5 | 0.88 |
| v3 | Customer reports the refund was wrong (prod-01, turn 2) | {'ORD-48213': 4000} | {'ORD-48213': 4000} | yes | 5 (0) | 1 | 1 | 0.88 |
| v3 | Full refund on an order that never arrived (prod-06) | {'ORD-49388': 3600} | {'ORD-49388': 3600} | yes | 4 (0) | 1 | 1 | 1 |
| v3 | Full refund on an order that never arrived (prod-06) | {'ORD-49388': 3600} | {'ORD-49388': 3600} | yes | 5 (0) | 1 | 1 | 1 |
| v3 | Goodwill refund for a late delivery (prod-04) | {'ORD-50415': 2500} | {'ORD-50415': 2500} | yes | 5 (0) | 1 | 0.75 | 1 |
| v3 | Goodwill refund for a late delivery (prod-04) | {'ORD-50415': 2500} | {'ORD-50415': 2500} | yes | 5 (0) | 1 | 1 | 1 |
| v3 | Order status lookup, no refund (prod-02) | - | - | yes | 3 (0) | 1 | 0.75 | 1 |
| v3 | Order status lookup, no refund (prod-02) | - | - | yes | 3 (0) | 1 | 1 | 1 |
| v3 | Partial refund with cents (prod-03) | {'ORD-50520': 1250} | {'ORD-50520': 1250} | yes | 5 (0) | 1 | 0.75 | 1 |
| v3 | Partial refund with cents (prod-03) | {'ORD-50520': 1250} | {'ORD-50520': 1250} | yes | 5 (0) | 1 | 1 | 1 |
| v3 | Whole-dollar refund, bare order number (prod-01) | {'ORD-48213': 4000} | {'ORD-48213': 4000} | yes | 5 (0) | 1 | 0.5 | 1 |
| v3 | Whole-dollar refund, bare order number (prod-01) | {'ORD-48213': 4000} | {'ORD-48213': 4000} | yes | 5 (0) | 1 | 0.5 | 1 |

v1: money right 6/12, failed CLI calls 44/94, guardrail 0.6, tool use 0.63, goal 0.66
v2: money right 6/12, failed CLI calls 46/102, guardrail 0.64, tool use 0.54, goal 0.7
v3: money right 12/12, failed CLI calls 0/55, guardrail 0.99, tool use 0.81, goal 0.98

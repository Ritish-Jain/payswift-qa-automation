# Negative API Test Matrix: `POST /api/v1/transfers/initiate`

The public mock (`jsonplaceholder.typicode.com/posts`) accepts anything and returns 201, so these cases cannot be executed against it. They describe what I would run against a PaySwift staging environment, and what the mobile app must show for each response. The UI column matters as much as the status code: most real double-debit and "money vanished" incidents come from the client misreading an ambiguous response, not from the server returning the wrong code.

## Request assumptions

- Auth: `Authorization: Bearer <JWT>` with short expiry.
- Idempotency: `idempotencyKey` in the body (or an `Idempotency-Key` header), generated once per user intent on the client, before the OTP screen, and reused on every retry of that intent.
- Amounts: sent as JSON numbers with at most 2 decimal places, or as a string in minor units (paise). The server must never round.

## Matrix

| ID | Scenario | Request change | Expected status | Server-side assertion | Expected mobile UI state |
|----|----------|----------------|-----------------|-----------------------|--------------------------|
| N1 | Missing JWT | No `Authorization` header | 401 | No transfer row created | Session-expired sheet, route to PIN/biometric login. Transfer draft kept, not auto-submitted |
| N2 | Expired JWT | Token with `exp` in the past | 401 | Same as N1 | Same as N1. App may refresh the token once, then must reuse the same idempotencyKey |
| N3 | Tampered JWT | Signature altered / `alg: none` | 401 | Logged as security event | Same as N1 |
| N4 | Sender not owned by caller | Valid token, `senderId` of another user | 403 | No balance or name of other account in body | Generic "Unable to process" message. No detail leak |
| N5 | Idempotent replay | Same key, same body, sent twice (sequential and parallel) | First 201, replay 200/201 returning the **same** `transactionId` | Exactly one ledger debit | Single success receipt. Second tap shows the same receipt, never a second one |
| N6 | Key reuse with different body | Same key, amount changed | 409 Conflict (or 422) | Original transfer untouched | "This request was already submitted" with link to the original transaction |
| N7 | Missing idempotency key | Field/header absent | 400 | Rejected before any balance check | Should never happen from the app. If it does, treat as a client bug |
| N8 | Below minimum | `amount: 9.99` | 422 `AMOUNT_BELOW_MIN` | No debit | Inline error under amount field, Pay Now disabled |
| N9 | Above per-transaction max | `amount: 50000.01` | 422 `AMOUNT_ABOVE_TXN_LIMIT` | No debit | Inline error naming the ₹50,000.00 limit |
| N10 | Daily limit crossed | Prior transfers today sum to ₹95,000.00, new `amount: 5000.01` | 422 `DAILY_LIMIT_EXCEEDED` | Limit computed per IST day, includes pending transfers | Error shows remaining limit for today (₹5,000.00) |
| N11 | Precision abuse | `amount: 10.005`, `1e2`, `"100"`, `-10`, `0`, `NaN`, `null` | 400 / 422 | No silent rounding to 10.01 or 10.00 | Client-side validation should block these first |
| N12 | Insufficient balance | Amount > available balance | 422 `INSUFFICIENT_FUNDS` | Balance unchanged | "Insufficient balance" with current balance refreshed from `GET /account/balance` |
| N13 | Invalid / closed receiver | Unknown UPI ID or closed account | 404 or 422 `INVALID_BENEFICIARY` | No debit | Error on recipient step, not after OTP |
| N14 | Locked account | 3 failed PINs in the last 15 min | 423 Locked (or 403 with code) | Lock expiry returned | Lock screen with countdown. No OTP sent |
| N15 | Wrong / expired OTP | OTP reference invalid | 401 or 422 `OTP_INVALID` | Attempts counted | OTP error with resend option. Same idempotencyKey reused after resend |
| N16 | Malformed payload | Broken JSON, wrong `Content-Type`, unknown currency `USD` | 400 / 415 | Rejected at gateway | Generic error, log to crash reporting |
| N17 | Rate limit | Many requests from one user/device in a short window | 429 with `Retry-After` | Requests after the limit are not processed | "Too many attempts, try again in N s". No silent retry storm |
| N18 | Downstream timeout | Core banking slow / unreachable | 504 (or 202 Accepted with status `PENDING`) | Transfer may or may not be committed | **"Transaction Pending - Do Not Retry"**. App polls `GET /transfers/{idempotencyKey}` until a final state |
| N19 | Server error | Unhandled exception | 500 / 502 / 503 | Outcome unknown to the client | Same as N18. Never show "Failed" for an outcome the client cannot know |
| N20 | Response lost on network | Server commits, client never receives the response | n/a (socket error) | One debit only | Same as N18. On reconnect, status lookup by key resolves to Success |

## How status codes drive the mobile UI

The rule I would hold the app to: a status code only maps to "Failed" when it proves no money moved.

| Response class | Meaning for the client | Allowed UI state | Retry allowed? |
|----------------|------------------------|------------------|----------------|
| 201 / 200 with final status | Money moved | Success receipt | No |
| 202 / status `PENDING` | Accepted, not final | Pending screen + polling | No new request. Poll only |
| 400, 401, 403, 404, 409, 415, 422, 423 | Rejected before money moved | Specific error | Yes, after the user fixes the cause, with the **same** key if intent is unchanged |
| 429 | Throttled before processing | Wait message | Yes, after `Retry-After`, same key |
| 5xx, timeout, connection reset | Unknown outcome | "Transaction Pending - Do Not Retry" | No. Resolve by status lookup on the idempotency key |

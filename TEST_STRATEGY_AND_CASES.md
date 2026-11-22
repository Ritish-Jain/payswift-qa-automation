# PaySwift Instant Money Transfer: Test Strategy and Test Cases

| | |
|---|---|
| Feature under test | Instant Money Transfer module (Android and iOS) |
| Document owner | QA |
| Status | Ready for review |
| Related files | `docs/NEGATIVE_API_TEST_MATRIX.md`, `postman/PaySwift_Transfer_API.postman_collection.json`, `tests/` |

## 1. Approach

Money movement fails in a small number of expensive ways: the user is debited twice, debited when the app said it failed, allowed past a limit, or shown an amount that differs from what was charged. Test effort is weighted toward those outcomes first and toward cosmetic or convenience issues last.

**Risk priorities (highest first)**

1. Duplicate or phantom debits (concurrent taps, retries, network loss, app kill during submit).
2. Limit enforcement (minimum, per-transaction maximum, daily cumulative) on both client and server.
3. Amount integrity (decimal precision, rounding, formatting, locale).
4. Access control (PIN lockout, biometric fallback, OTP, session expiry).
5. Correct UI state for every backend response (see the status-code mapping in `docs/NEGATIVE_API_TEST_MATRIX.md`).

**Levels and where each risk is covered**

| Level | What it covers | Tooling |
|-------|----------------|---------|
| API contract | Status codes, payload, idempotency, limits, auth | Postman/Newman, pytest + requests |
| Mobile UI automation | Critical journeys, validation messages, gestures | Appium + pytest (POM) |
| Manual / exploratory | Race conditions, network chaos, interruptions, device-specific behaviour | Charles/Proxyman, Android network throttling, Xcode Network Link Conditioner |
| Server-side checks | Ledger rows, idempotency table, audit log | DB queries on staging |

Client-side validation is treated as a usability feature. Every limit and rule is also tested directly against the API, because a modified client or a replayed request skips the UI entirely.

**Environments**

- Android 14 (Pixel 7) and Android 10 on a low-end device (2 GB RAM) for slow-render races.
- iOS 17 (iPhone 15) and iOS 16 (iPhone SE).
- Wi-Fi, throttled 3G, airplane-mode toggling, Wi-Fi to mobile data handover.
- Locale `en-IN` and one non-Indian locale (`en-US`) to catch number-format bugs.

## 2. Test Scenarios

| ID | Scenario | Type | Fintech risk addressed | Priority |
|----|----------|------|------------------------|----------|
| TS-01 | Complete a transfer to a saved contact: PIN login, enter ₹2,500.50, OTP, success receipt; balance drops by exactly ₹2,500.50 and transaction history shows one entry | Functional | Balance and receipt must reconcile to the paisa | P0 |
| TS-02 | Per-transaction amount boundaries: ₹9.99, ₹10.00, ₹10.01, ₹49,999.99, ₹50,000.00, ₹50,000.01, verified in the UI and directly on the API | Boundary | Limits enforced on client and server | P0 |
| TS-03 | Daily cumulative limit of ₹1,00,000.00: transfers that land exactly on, one paisa over, and across IST midnight; pending and failed transfers counted correctly | Boundary | Limit bypass by splitting transfers or racing them | P0 |
| TS-04 | Amount precision and input handling: `10.005`, `.5`, `0010.00`, pasted `1,000.50` and `1.000,50`, emoji/letters, Indian grouping `1,00,000.00`, max two decimals enforced by the keypad and the API | Negative / precision | Rounding drift between display, request and ledger | P0 |
| TS-05 | Rapid double-tap and multi-finger tap on Pay Now, and on the OTP Confirm button; same test with the device under CPU load | Concurrency | Duplicate debit from parallel requests | P0 |
| TS-06 | Network drops after OTP is submitted (before request, during request, after server commit but before response); app must show "Transaction Pending - Do Not Retry" and resolve to the true final state | Resilience | Silent failure, or a retry that debits twice | P0 |
| TS-07 | PIN lockout: 3 consecutive wrong PINs lock the account for 15 minutes; counter resets after a correct PIN; lock survives app restart and reinstall; biometric cannot bypass an active lock; lock timer is enforced by the server, not the device clock | Security | Brute force of a 4-digit PIN (10,000 combinations) | P0 |
| TS-08 | OTP step: wrong OTP, expired OTP, resend limits, replay of a used OTP, OTP for transfer A used to confirm transfer B; transfer API must reject calls without a verified OTP reference | Security | 2FA bypass | P1 |
| TS-09 | Balance gate: Pay Now stays disabled until `GET /api/v1/account/balance` succeeds; balance API returns 500 or times out; balance changes in another session between load and Pay Now; amount above balance | Functional / negative | Acting on stale or missing balance | P1 |
| TS-10 | Recipient and data protection: invalid UPI ID formats, account number length/checksum, recipient same as sender, contacts permission denied; amount and account numbers masked in app switcher (FLAG_SECURE / snapshot blur) and absent from device logs | Security / negative | Misdirected payments and data leakage | P1 |

## 3. Boundary Value Analysis

### 3.1 Per-transaction amount (min ₹10.00, max ₹50,000.00)

| Input (₹) | Partition | Expected UI | Expected API |
|-----------|-----------|-------------|--------------|
| 0.00 | Invalid | Pay Now disabled | 422 |
| 9.99 | Invalid (just below min) | Inline error "Minimum amount is ₹10.00", Pay Now disabled | 422 `AMOUNT_BELOW_MIN` |
| 10.00 | Valid (min) | Pay Now enabled | 201 |
| 10.01 | Valid (just above min) | Pay Now enabled | 201 |
| 25,000.00 | Valid (nominal) | Pay Now enabled | 201 |
| 49,999.99 | Valid (just below max) | Pay Now enabled | 201 |
| 50,000.00 | Valid (max) | Pay Now enabled | 201 |
| 50,000.01 | Invalid (just above max) | Inline error "Maximum per transaction is ₹50,000.00" | 422 `AMOUNT_ABOVE_TXN_LIMIT` |
| 10.005 | Invalid precision | Third decimal not accepted by keypad | 400/422, never rounded to 10.01 |
| -10.00 | Invalid sign | Minus key not available | 400/422 |

### 3.2 Daily cumulative limit (₹1,00,000.00 per IST calendar day)

Setup for each row: user has already sent ₹50,000.00 + ₹45,000.00 = ₹95,000.00 today.

| Next transfer (₹) | Day total after | Expected |
|-------------------|-----------------|----------|
| 4,999.99 | 99,999.99 | Allowed |
| 5,000.00 | 1,00,000.00 | Allowed (limit is inclusive) |
| 5,000.01 | 1,00,000.01 | Rejected, message shows ₹5,000.00 remaining |
| 5,000.00 sent at 23:59:59 IST, then 10.00 at 00:00:01 IST | New day starts at 10.00 | Both allowed |

### 3.3 PIN attempts (lock after 3 consecutive failures, 15 minutes)

| Attempt pattern | Expected |
|-----------------|----------|
| Wrong, Wrong, Correct | Login succeeds, counter resets to 0 |
| Wrong, Wrong, Wrong | Locked, countdown shows 15:00 |
| Locked, retry at 14:59 | Still locked |
| Locked, retry at 15:00 | Unlocked, counter at 0 |
| Wrong x2, kill app, Wrong x1 | Locked (counter is server-side, not lost on restart) |

## 4. Detailed Test Cases

### TC-01: Rapid double-tap on Pay Now creates exactly one transfer

| Field | Detail |
|-------|--------|
| Scenario | TS-05 |
| Priority | P0 |
| Type | Concurrency / Functional |
| Preconditions | 1. Test user `USR_9981` logged in on Android 14 (Pixel 7) staging build.<br>2. Available balance ₹10,000.00, nothing sent today.<br>3. Recipient `USR_4420` saved as a contact.<br>4. Proxy (Charles/Proxyman) capturing `/api/v1/transfers/*`.<br>5. Test OTP for staging is `123456` or retrieved from the OTP stub. |
| Test data | Amount ₹2,500.50, recipient `USR_4420` |

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Open Send Money, pick `USR_4420`, enter `2500.50` | Pay Now becomes enabled after the balance call returns 200 |
| 2 | Double-tap Pay Now as fast as possible (two taps within ~100 ms) | Exactly one OTP screen opens. Pay Now shows a disabled or loading state from the first tap |
| 3 | Enter OTP and double-tap Confirm | One `POST /api/v1/transfers/initiate` in the proxy log. If the client does send two, both carry the **same** `idempotencyKey` |
| 4 | Wait for the result screen | One success receipt with one transaction id |
| 5 | Open transaction history | One entry of ₹2,500.50 to `USR_4420` |
| 6 | Pull to refresh balance | Balance is ₹7,499.50 |
| 7 | Server check: query ledger and idempotency table for `USR_9981` in the last 5 minutes | One debit row and one idempotency record |
| 8 | Repeat steps 1-7 using the device's two-finger tap and with the device under CPU load (e.g. `adb shell stress` or a heavy app in split screen) | Same results as above |

### TC-02: Network loss after OTP submission shows Pending and never double-debits

| Field | Detail |
|-------|--------|
| Scenario | TS-06 |
| Priority | P0 |
| Type | Resilience |
| Preconditions | 1. User logged in, balance ₹10,000.00.<br>2. Proxy with breakpoints on `POST /api/v1/transfers/initiate`.<br>3. Server status endpoint available: `GET /api/v1/transfers/{idempotencyKey}`. |
| Test data | Amount ₹1,000.00, recipient `USR_4420` |

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Start a transfer of ₹1,000.00 and reach the OTP screen | OTP screen shown |
| 2 | Variant A: enable airplane mode, then submit the OTP | App shows "No connection" before sending. No request leaves the device. No debit |
| 3 | Variant B: submit the OTP, hold the request at the proxy breakpoint, then drop the connection (abort at proxy) | App shows **"Transaction Pending - Do Not Retry"**. Pay Now and Confirm are not available. No "Failed" message |
| 4 | Variant C: let the request reach the server, drop the **response** at the proxy | Same Pending screen as step 3. Server has committed one debit |
| 5 | Restore connectivity | App calls the status endpoint with the original `idempotencyKey`, not a new transfer request |
| 6 | Observe the final state for A, B and C | A: no transfer. B: Failed or Not processed (server never saw it). C: Success with the original transaction id |
| 7 | Kill the app while on the Pending screen (variant C), relaunch | Pending transfer is still shown and resolves to Success. No duplicate is created on relaunch |
| 8 | Check balance and history for each variant | Balance reduced by ₹1,000.00 only in variant C, one history entry |

### TC-03: Per-transaction limit boundaries and decimal precision

| Field | Detail |
|-------|--------|
| Scenario | TS-02, TS-04 |
| Priority | P0 |
| Type | Boundary / Negative |
| Preconditions | 1. User logged in, balance ₹1,00,000.00, nothing sent today.<br>2. API access with a valid JWT for the same user (Postman). |
| Test data | See table below |

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Enter each amount from the table in the amount field | UI behaves as in the "UI" column |
| 2 | For each valid amount, complete the transfer | Receipt, history and balance show the exact amount with 2 decimals |
| 3 | For each invalid amount, send the same value directly to `POST /api/v1/transfers/initiate` (bypassing the UI) | API returns the status in the "API" column with a machine-readable error code. Balance unchanged |
| 4 | Send `10.005` and `49999.999` to the API | Rejected. The server never rounds to a valid amount |
| 5 | Paste `1,000.50` into the amount field | Parsed as ₹1,000.50 (or rejected with a clear message). Never parsed as ₹1.00 or ₹100,050 |

| Amount | UI | API |
|--------|----|-----|
| 9.99 | Error, Pay Now disabled | 422 |
| 10.00 | Allowed | 201 |
| 10.01 | Allowed | 201 |
| 49,999.99 | Allowed | 201 |
| 50,000.00 | Allowed | 201 |
| 50,000.01 | Error, Pay Now disabled | 422 |
| 10.005 | Third decimal blocked | 400/422 |

Note: valid-amount transfers in this case add up past the daily limit. Run them on separate days or with a daily-limit reset between rows, otherwise TC-04 rules interfere.

### TC-04: Daily cumulative limit of ₹1,00,000.00

| Field | Detail |
|-------|--------|
| Scenario | TS-03 |
| Priority | P0 |
| Type | Boundary / Concurrency |
| Preconditions | 1. User logged in, balance ₹2,00,000.00.<br>2. Daily total reset (new IST day or test hook).<br>3. Two devices logged in as the same user for step 6. |
| Test data | ₹50,000.00, ₹45,000.00, then ₹5,000.01 / ₹5,000.00 |

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Send ₹50,000.00 | Success. Remaining daily limit ₹50,000.00 |
| 2 | Send ₹45,000.00 | Success. Remaining ₹5,000.00 |
| 3 | Try ₹5,000.01 | Blocked with message showing ₹5,000.00 remaining. API (if called directly) returns 422 `DAILY_LIMIT_EXCEEDED` |
| 4 | Send ₹5,000.00 | Success. Remaining ₹0.00 |
| 5 | Try ₹10.00 | Blocked. Message says the daily limit is reached and when it resets |
| 6 | Reset the day. Send ₹95,000.00. Then on two devices at the same moment send ₹5,000.00 each | Exactly one succeeds, the other gets 422. Day total never exceeds ₹1,00,000.00 |
| 7 | Reset the day. Send ₹95,000.00, then a ₹5,000.00 transfer that ends Pending (see TC-02), then try another ₹5,000.00 | Second attempt blocked: pending transfers count toward the limit |
| 8 | At 23:59:59 IST send ₹10.00 with limit reached (blocked), at 00:00:01 IST send ₹10.00 | First blocked, second allowed. Reset follows IST, not the device time zone |

## 5. Defect Report

**PAY-1427: [Android 14] Double-tapping "Pay Now" sends two transfer requests and debits the user twice**

| Field | Value |
|-------|-------|
| Project / Component | PAYSWIFT / Instant Transfer - Android client, Transfers API |
| Issue type | Bug |
| Severity | S1 - Critical (direct financial loss to the customer) |
| Priority | P0 - Release blocker |
| Affects version | Android 2.4.0 (build 2401), staging |
| Labels | `payments`, `idempotency`, `race-condition`, `double-debit` |
| Reporter | QA |
| Found in | Exploratory testing, transfer module |
| Reproducibility | 8 / 10 attempts with a fast double-tap. 10 / 10 with the device under CPU load |

**Environment**

- Device: Google Pixel 7, Android 14 (UP1A.231105.003), 8 GB RAM
- App: PaySwift 2.4.0 (2401), staging flavour, debug logging on
- Backend: `staging-api.payswift.example` (Transfers service v1.12.3)
- Network: Wi-Fi, ~40 ms latency
- Account: `USR_9981` (opening balance ₹10,000.00), recipient `USR_4420`

**Steps to reproduce**

1. Log in as `USR_9981` with PIN.
2. Go to Send Money and select recipient `USR_4420`.
3. Enter amount `2500.50`.
4. Wait for Pay Now to become enabled (balance call completed).
5. Double-tap Pay Now quickly (two taps within ~100 ms).
6. Enter the OTP and confirm.
7. Check transaction history, balance and the proxy log.

**Expected result**

- Pay Now is disabled from the first tap. One OTP screen, one `POST /api/v1/transfers/initiate`.
- Even if two requests are sent, the server processes one and returns the same transaction id for both, because they share an idempotency key.
- One debit of ₹2,500.50. Balance ₹7,499.50.

**Actual result**

- Two `POST /api/v1/transfers/initiate` requests sent 74 ms apart. Both returned `201 Created` with different transaction ids (`TXN-88213`, `TXN-88214`).
- The two requests carry **different** `idempotencyKey` values.
- Transaction history shows two debits of ₹2,500.50 to `USR_4420`. Balance ₹4,999.00.
- The app showed a single success screen, so the user is not aware of the second debit.

**Attachments**

- `pay-1427-screen-recording.mp4` (tap sequence with "Show taps" enabled)
- `pay-1427-proxy.chls` (both requests and responses)
- `pay-1427-logcat.txt` (two `TransferViewModel.initiate()` calls)
- Server log extract for both transaction ids

**Suspected root cause**

There appear to be two defects, either of which would have prevented the double debit on its own:

1. **Client: button not locked synchronously, and key generated per tap.** The Pay Now click handler starts the transfer coroutine and the disabled state is applied on the next recomposition. A second tap inside that window runs the handler again. The idempotency key is created inside the handler, so each tap gets a new key and the server sees two unrelated transfers.
2. **Server: idempotency does not cover concurrent first requests.** The difference in keys explains this specific trace, but a quick API check (two parallel calls with the *same* key from Postman/curl) should be run to confirm whether the server's check-then-insert on the idempotency table is atomic. If both parallel calls succeed, the table is missing a unique constraint or the check is not inside the same transaction as the debit.

**Suggested fix**

- Client: disable Pay Now and Confirm on the first tap, before any async work (or debounce at the ViewModel with a single-flight guard). Generate the idempotency key once when the user lands on the confirm step, store it with the draft, and reuse it on every retry of that draft.
- Server: unique constraint on `(user_id, idempotency_key)`; insert the key and the debit in one transaction; on conflict return the original response.

**Regression tests to add**

- UI: double-tap and two-finger tap on Pay Now and Confirm (TC-01).
- API: two parallel requests with the same key return the same transaction id and create one ledger row.
- API: same key with a different amount returns 409/422.

## 6. Observation From the Automation Demo App

While mapping locators, I read the demo app's JavaScript bundle (Sauce Labs Swag Labs 2.7.1). The checkout overview builds "Item total" by summing prices as JavaScript floats and prints the result without rounding, while Tax and Total are rounded with `toFixed(2)`. Adding **Sauce Labs Bike Light (9.99)** and then **Sauce Labs Fleece Jacket (49.99)** should therefore display `Item total: $59.980000000000004`.

I found this through static review, not on a device, so it needs confirming before it is reported. It is the same class of bug as TS-04: an amount handled as a binary float somewhere between input and display. The automation framework compares all money as `Decimal` and has a guard (`has_at_most_two_decimals`) that would fail the happy-path test if a cart with those items were used.

## 7. Automation Coverage Map

| Scenario | Covered by |
|----------|-----------|
| TS-01 | `tests/ui/test_01_checkout_happy_path.py` (demo app stand-in), `tests/api/test_transfer_initiate.py` |
| TS-02, TS-04 | API amount precision check in `tests/api/test_transfer_initiate.py`. Full BVA requires PaySwift staging (see negative matrix N8-N11) |
| TS-07 | `tests/ui/test_02_validation_errors.py::test_login_rejected_with_exact_message[locked_out_user]` (demo stand-in for lockout messaging) |
| TS-09, TS-10 | `tests/ui/test_02_validation_errors.py::test_checkout_form_rejects_missing_fields` (required-field validation stand-in) |
| Transaction history lookup | `tests/ui/test_03_list_scroll_gesture.py` |
| TS-03, TS-05, TS-06, TS-08 | Manual with proxy tooling now; API-level automation planned once a staging environment with idempotency and limits is available |

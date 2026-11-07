# Expenses Tracker

**Expenses Tracker** is a dark, fintech-style expense tracker for India that reads bank SMS with **Claude** and turns them into clean, editable transactions. It also scans bills, takes dictation, and works without an API key for those two features.

Everything is one HTML file — no build step, no framework, no backend needed for normal use. Your transactions and API key stay in **your own browser**.

**Live website:** https://sreeharipraneeth16-cell.github.io/ai-expense-tracker/

---

## Features

- **Paste bank SMS → structured transactions.** Claude extracts the date, merchant, amount, debit/credit and category, and skips OTPs, ads and balance alerts.
- **Review before saving.** After Categorize (or an on-device bill scan), every result shows on a review screen with date, merchant, amount, type and category — all editable, with checkboxes. Suspicious rows (missing date, odd amount, "Other" category, possible duplicate) are flagged **Needs review** and start unchecked when they look like a duplicate. Saving still goes through the normal add/edit logic.
- **Dictate instead of typing.** Tap 🎤 **Dictate** in AI import, or 🎤 **Speak** next to the merchant field in Add transaction, and talk — your words appear in the box. Uses the browser's speech recognition; no API key.
- **Scan a bill by photo.** Take a picture (or drop/paste an image) and the app fills in the shop, total, date and category — **no API key needed**. Add a key and Claude reads it instead for better accuracy. On-device reading is labelled **may be less accurate** and the result is always shown on the review screen first.
- **Editable table.** Change any category from a dropdown, or edit/delete from Recent activity.
- **Summary dashboard.** Total spent/received, spending donut, daily/monthly trend chart and category bars.
- **Manual entry** for cash spends.
- **Auto-saved** in `localStorage`, with **CSV export**.
- **Optional live SMS auto-import** (local server + Android forwarding app).

Categories: Food, Groceries, Transport, Shopping, Bills & Recharge, Health, Entertainment, Education, Rent, Transfers, Other.

---

## Use the live website

1. Open https://sreeharipraneeth16-cell.github.io/ai-expense-tracker/
2. Click **API key** and paste **your own** Anthropic key (`sk-ant-...`) — optional. You only need it for SMS; **bill scanning works without a key**.
3. Paste a bank message (or click **Load sample**) → **Categorize with AI**

> This repo contains **no API key**. Each visitor uses their own key and pays for their own usage.
> The key is saved only in that browser and sent directly from the browser to Anthropic.

**Share the direct GitHub Pages link** — `https://sreeharipraneeth16-cell.github.io/ai-expense-tracker/`. Short aliases are just redirects and may expire.

---

## Scan a bill (photo)

No typing, no SMS, and **no API key needed** — this works on the hosted site too.

1. In **AI import**, click **Scan a bill or receipt**:
   - on a phone, this opens the **camera** (`capture="environment"`)
   - on a computer, pick an image file
   - you can also **drag & drop** an image, or **paste** a screenshot
2. Check the preview, then click:
   - **🪄 Scan bill** — uses Claude if you have a key, otherwise reads on your device automatically
   - **On-device** — always reads in your browser, even if you do have a key (the photo never leaves your device)
3. The **review screen** opens with the result — check the amount and shop, then **Add selected**.
4. The row is marked **photo**; fix anything later with **✎** or the category dropdown.

Photos are **resized in your browser** (longest side 1600 px, JPEG) before anything else happens.

| Mode | How it reads | Sends the photo |
|---|---|---|
| **Claude** (key saved) | Anthropic vision — most accurate | to Anthropic, once |
| **On-device** (no key) | Tesseract.js OCR in your browser | nowhere |

The on-device reader downloads once (~15 MB) the first time you use it, then the browser caches it. OCR is less accurate than Claude on blurry or angled photos, which is why the result is shown for confirmation before it is saved. The image itself is never stored by the app.

---

## Dictate a message

1. In **AI import**, tap **🎤 Dictate** and allow microphone access the first time
2. Speak normally, e.g. *"Rs 450 debited from account 1234 at Swiggy on 3 November"*
3. The words are typed into the box as you talk (the line below shows what's being heard right now)
4. Tap **Listening…** to stop, then **Categorize with AI**

- Works in **Chrome, Edge and Safari**. Firefox doesn't implement it, so the Dictate buttons are hidden and the app shows a friendly message. When dictation is available, **Chrome may send audio to Google**.
- No API key is involved. Recognition is set to **English (India)** and falls back to English (US) if needed.
- The browser's speech service does the listening. In Chrome, audio is processed by Google; the app itself never records or stores audio.

### Dictate the shop name in Add transaction

The **Merchant / description** field has its own **🎤 Speak** button, so a cash purchase can be spoken too:

1. Click **+ Add transaction**
2. Tap **🎤 Speak**, say the shop or description (e.g. *"Cafe Mocha"*), and tap **Listening…** to stop
3. The words appear in the field; add the amount and save

- Also works when **editing** an existing transaction.
- Faster: the **🎤 Speak** button beside **+ Add transaction** in the Period balance card opens the dialog with the mic already listening.
- The two mics share one engine, so only one listens at a time — starting one stops the other.
- Closing the dialog stops the mic automatically, and no API key is needed here either.
- Amount is typed rather than spoken, because speech-to-number is unreliable (e.g. "four fifty" could mean 4.50 or 450).

---

## Backup, restore, lock and data safety

- **Backup:** Downloads a JSON file with all transactions and learned category rules. The API key and app lock PIN are **never** included.
- **Restore:** Pick a backup file → **Merge** (keep current data, skip duplicates) or **Replace everything** (after confirmation). Files are validated before use; unknown/invalid rows are skipped.
- **Reminder:** A gentle banner asks you to back up if the last backup is 14+ days old.
- **Storage protection:** One button asks the browser for persistent storage (`navigator.storage.persist`). Clearing browser site data or using a private window still deletes everything — keep a JSON backup.
- **Delete all:** Removes transactions, learned rules, API key, settings and app lock from this browser (with a two-step confirmation).

Optional **App lock**: PIN screen that encrypts stored data with **AES-GCM** using a key derived from the PIN with **PBKDF2-SHA-256**. The PIN is never stored. If you forget the PIN, you can restore a JSON backup (which turns the lock off and replaces the locked data).

---

## Privacy

- No key is stored in this repository.
- Transactions live in your browser's `localStorage`.
- Before any pasted text goes to Claude, the app masks on the device: emails → `[email]`, UPI IDs → `[upi]`, phone numbers → `[phone]`, and long account/card numbers keep only the last 4 digits. You can open **What gets sent to Claude** to preview the exact masked text.
- A bill photo is shrunk locally. With a key it is sent **only** to Anthropic for that one request; with **On-device** it never leaves your browser. The app never stores the image.
- Dictation uses your browser's speech recognition (Chrome processes audio with Google). The app never records or stores audio.
- The relay's inbox is stored in your temp folder (`%TEMP%\expense-tracker-inbox.json`), outside the served folder, capped at 500 messages.
- Network calls: Anthropic (only when you use a key), a one-time Tesseract.js download from jsDelivr (only when you use On-device), your browser's speech service (only while dictating), plus local calls to the relay.

### Live auto-import (optional, off by default)

Browsers cannot read SMS, so a forwarding app hands messages to the local server, which the page polls every 8 seconds.

```
Bank SMS → forwarder app → expense-server.py → tracker → Claude → transaction (+ AUTO badge)
```

- Off by default on every load; turn it on only through the in-app opt-in dialog.
- When on: messages are stored unencrypted in the relay inbox, masked before the AI call, and categorized by Claude; the tracker stores only the last-read message id.
- The relay has no password; use it only on trusted Wi-Fi. The in-app warning explains this before enabling.
- The forwarding app may use its own cloud service — check its privacy policy.
- Only Anthropic is involved beyond that. The helper listens on your PC, not on a third-party server.

### iPhone / iOS

iOS does not allow apps or web pages to read SMS automatically. Copy the bank message from Messages and paste it into AI import, or use an iOS Shortcut that copies/shared text to POST to your local relay. The relay is reachable on your LAN while it runs.

---

## Run it locally

Auto-import needs the small Python helper, so run the local copy:

```powershell
cd ai-expense-tracker
python expense-server.py
```

Then open **http://localhost:8000/**.

On Windows you can instead double-click `start-expense-tracker.bat`.

Requires Python 3.8+ (standard library only — no `pip install`).

---

## Offline / install

- The app ships `manifest.webmanifest`, `sw.js` and PNG icons (192/512).
- The service worker caches the app shell for offline use; the page registers only on HTTPS/localhost.
- Install to home screen via browser menu (manifest + service worker required by most browsers).

---

## Security notes

- **Content Security Policy:** a meta tag allows only the app's own assets, `api.anthropic.com`, the OCR CDN (`cdn.jsdelivr.net`, `tessdata.projectnaptha.com`), and localhost for the relay. Inline scripts/styles are allowed because the app is a single HTML file; `unsafe-inline` for styles/scripts is therefore required and is a known limitation.
- **No secrets in the repo or history.** Key storage: saved in browser (`localStorage`) or session-only (`sessionStorage`), chosen in the API key dialog. Nothing is written into the HTML file or backups.
- **XSS:** all user text is escaped before rendering into HTML; AI output and backup rows are validated before use.
- **AI:** responses are parsed as JSON only; amounts are capped and validated; categories are restricted to the known list, with per-merchant learned corrections.
- **Encryption:** app lock uses Web Crypto (AES-GCM, PBKDF2-SHA-256 210k iterations).

---

## How it works

- `index.html` — the whole app (HTML + CSS + vanilla JS, SVG charts)
- `expense-server.py` — optional local relay: serves the app and accepts SMS at `POST /api/sms`
- `start-expense-tracker.bat` — Windows one-click launcher
- `manifest.webmanifest`, `sw.js`, `icon-192.png`, `icon-512.png` — install / offline

Model: `claude-haiku-5-5` via the Anthropic Messages API. Text messages and bill photos use the same model — photos are sent as base64 image blocks. Without a key, bill photos are read locally with [Tesseract.js](https://tesseract.projectnaptha.com/) instead. Dictation uses the browser's built-in Web Speech API.

Headers sent to Anthropic: `x-api-key`, `anthropic-version: 2023-06-01`, `anthropic-dangerous-direct-browser-access: true`, JSON body. No temperature/top_p/top_k are sent.

---

## Test checklist (what was tested)

- Paste SMS → review screen → save (edit date/amount/category, uncheck rows, duplicates flagged).
- On-device bill scan → review screen → save/cancel; billing result flagged suspicious when needed.
- Manual add / edit / delete from table and Recent activity; category change remembered per merchant.
- Backup download → parse → merge with duplicates skipped → restore; Replace flow with confirmation.
- CSV export (BOM + quoting) still works.
- Mobile layout (390 px) with no horizontal overflow; responsive review grid.
- App lock: enable → encrypted payload in storage → unlock with right/wrong PIN.
- Auto-import switch: OFF on load, opt-in modal required, status updates.

---

## Limitations and manual actions

- Known limitations: CSP `unsafe-inline` (single-file app); on-device OCR is less accurate; app lock protects browser access but not full device control; no light theme (dark-only design was kept as-is).
- Manual actions you may need to take: rotate any Anthropic key that was ever shared/exposed (none was found in the repo or history).
- Auto-import requires the local Python server; the hosted site shows **Local only**.

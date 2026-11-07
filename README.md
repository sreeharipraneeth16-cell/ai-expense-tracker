# Expenses Tracker

**Expenses Tracker** is a dark, fintech-style expense tracker that reads Indian bank SMS with **Claude** and turns them into clean, editable transactions. It also scans bills, takes dictation, and works without an API key for those two features.

Everything is one HTML file — no build step, no framework, no backend needed for normal use. Your transactions and API key stay in **your own browser**.

**Live website:** https://sreeharipraneeth16-cell.github.io/ai-expense-tracker/

---

## Features

- **Paste bank SMS → structured transactions.** Claude extracts the date, merchant, amount, debit/credit and category, and skips OTPs, ads and balance alerts.
- **Dictate instead of typing.** Tap 🎤 **Dictate** in AI import, or 🎤 **Speak** next to the merchant field in Add transaction, and talk — your words appear in the box. Uses the browser's speech recognition; no API key.
- **Scan a bill by photo.** Take a picture (or drop/paste an image) and the app fills in the shop, total, date and category — **no API key needed**. Add a key and Claude reads it instead for better accuracy.
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
3. The **Add transaction** dialog opens filled in — check the amount and shop, then click **Add transaction**
4. The row is marked **photo**; fix anything later with **✎** or the category dropdown

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

- Works in **Chrome, Edge and Safari**. Firefox doesn't implement it, so the button shows *"This browser can't dictate"*.
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

## Live SMS auto-import (Android)

Browsers cannot read SMS, so a forwarding app hands messages to the local server, which the page polls every 8 seconds.

```
Bank SMS → forwarder app → expense-server.py → tracker → Claude → transaction (+ AUTO badge)
```

1. Start `expense-server.py` and keep its window open. It prints your phone address, e.g. `http://192.168.1.5:8000/api/sms`
2. Install a free SMS-forwarding app (SMS Forwarder, MacroDroid, Tasker…)
3. On incoming SMS, POST to that address. Any of these bodies work:
   - JSON: `{"message":"<message text>"}`
   - Form: `message=<message text>`
   - Raw text
4. Allow **Python** through Windows Firewall (Private networks)
5. In the app, switch on **Live auto-import**

New transactions appear with an **AUTO** tag and can still be edited or deleted like any other.

**Limits**

- Android only — iOS blocks apps from reading SMS.
- Phone and PC must be on the same Wi-Fi, and the PC must stay on.
- GitHub Pages cannot run Python, so on the hosted website the switch shows **Local only**.
- The relay has no password; use it only on a trusted home network.

---

## Privacy

- No key is stored in this repository.
- Transactions live in your browser's `localStorage`.
- A bill photo is shrunk locally. With a key it is sent **only** to Anthropic for that one request; with **On-device** it never leaves your browser. The app never stores the image.
- Dictation uses your browser's speech recognition (Chrome processes audio with Google). The app never records or stores audio.
- The relay's inbox is stored in your temp folder (`%TEMP%\expense-tracker-inbox.json`), outside the served folder.
- Network calls: Anthropic (only when you use a key), a one-time Tesseract.js download from jsDelivr (only when you use On-device), your browser's speech service (only while dictating), plus local calls to the relay.

---

## How it works

- `index.html` — the whole app (HTML + CSS + vanilla JS, SVG charts)
- `expense-server.py` — optional local relay: serves the app and accepts SMS at `POST /api/sms`
- `start-expense-tracker.bat` — Windows one-click launcher

Model: `claude-haiku-5-5` via the Anthropic Messages API. Text messages and bill photos use the same model — photos are sent as base64 image blocks. Without a key, bill photos are read locally with [Tesseract.js](https://tesseract.projectnaptha.com/) instead. Dictation uses the browser's built-in Web Speech API.

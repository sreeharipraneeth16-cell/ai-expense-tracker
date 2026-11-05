# AI Expense Tracker

A dark, fintech-style expense tracker that reads Indian bank SMS with **Claude** and turns them into clean, editable transactions.

Everything is one HTML file — no build step, no framework, no backend needed for normal use. Your transactions and API key stay in **your own browser**.

**Live demo:** https://sreeharipraneeth16-cell.github.io/ai-expense-tracker/

---

## Features

- **Paste bank SMS → structured transactions.** Claude extracts the date, merchant, amount, debit/credit and category, and skips OTPs, ads and balance alerts.
- **Editable table.** Change any category from a dropdown, or edit/delete from Recent activity.
- **Summary dashboard.** Total spent/received, spending donut, daily/monthly trend chart and category bars.
- **Manual entry** for cash spends.
- **Auto-saved** in `localStorage`, with **CSV export**.
- **Optional live SMS auto-import** (local server + Android forwarding app).

Categories: Food, Groceries, Transport, Shopping, Bills & Recharge, Health, Entertainment, Education, Rent, Transfers, Other.

---

## Use the live demo

1. Open https://sreeharipraneeth16-cell.github.io/ai-expense-tracker/
2. Click **API key** and paste **your own** Anthropic key (`sk-ant-...`)
3. Paste a bank message (or click **Load sample**) → **Categorize with AI**

> This repo contains **no API key**. Each visitor uses their own key and pays for their own usage.
> The key is saved only in that browser and sent directly from the browser to Anthropic.

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
- GitHub Pages cannot run Python, so on the hosted demo the switch shows **Local only**.
- The relay has no password; use it only on a trusted home network.

---

## Privacy

- No key is stored in this repository.
- Transactions live in your browser's `localStorage`.
- The relay's inbox is stored in your temp folder (`%TEMP%\expense-tracker-inbox.json`), outside the served folder.
- The only network calls are to Anthropic, plus local calls to the relay.

---

## How it works

- `index.html` — the whole app (HTML + CSS + vanilla JS, SVG charts)
- `expense-server.py` — optional local relay: serves the app and accepts SMS at `POST /api/sms`
- `start-expense-tracker.bat` — Windows one-click launcher

Model: `claude-haiku-5-5` via the Anthropic Messages API.

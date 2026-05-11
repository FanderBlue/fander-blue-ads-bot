import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DEVELOPER_TOKEN = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
CLIENT_ID = os.environ.get("GOOGLE_ADS_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")

CUSTOMER_ID = "7261657135"
MCC_ID = "2079673466"

def get_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    })
    data = r.json()
    return data.get("access_token")

def get_campaigns():
    token = get_access_token()

    if not token:
        return "ما قدرت أجيب Access Token. تأكد من متغيرات Railway."

    url = f"https://googleads.googleapis.com/v24/customers/{CUSTOMER_ID}/googleAds:search"

    headers = {
        "Authorization": f"Bearer {token}",
        "developer-token": DEVELOPER_TOKEN,
        "login-customer-id": MCC_ID,
        "Content-Type": "application/json",
    }

    body = {
        "query": """
        SELECT
          campaign.id,
          campaign.name,
          campaign.status
        FROM campaign
        LIMIT 10
        """
    }

    r = requests.post(url, headers=headers, json=body)

    if r.status_code != 200:
        return f"STATUS: {r.status_code}\nURL: {url}\nRESPONSE:\n{r.text[:1500]}"

    results = []
    data = r.json()

    for row in data.get("results", []):
        c = row.get("campaign", {})
        results.append(f"• {c.get('name')} [{c.get('status')}]")

    return "\n".join(results) if results else "لا توجد حملات"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    await update.message.reply_text("⏳ جاري المعالجة...")

    if "حملات" in text or "campaigns" in text:
        result = get_campaigns()
        await update.message.reply_text(f"📊 حملاتك:\n{result}")
    else:
        await update.message.reply_text("مرحباً! 👋\n\nاكتب 'حملات' لعرض حملاتك")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()

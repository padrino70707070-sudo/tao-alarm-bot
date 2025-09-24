import os, requests, yaml
from dotenv import load_dotenv
from typing import Optional
from telegram import Bot

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot: Optional[Bot] = Bot(TOKEN) if TOKEN else None

CFG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "settings.yaml")

def get_cfg() -> dict:
    try:
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}

def get_tao_price_eur() -> float:
    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": "bittensor", "vs_currencies": "eur"},
        timeout=20,
    )
    r.raise_for_status()
    return float(r.json()["bittensor"]["eur"])

def notify(msg: str) -> None:
    print(msg)
    if bot and CHAT_ID:
        try:
            bot.send_message(chat_id=int(CHAT_ID), text=msg)
        except Exception as e:
            print(f"send_message error: {e}")

if __name__ == "__main__":
    price = get_tao_price_eur()
    cfg = get_cfg()
    min_eur = cfg.get("min_eur")
    max_eur = cfg.get("max_eur")

    triggered = False
    if isinstance(min_eur, (int, float)) and price <= float(min_eur):
        notify(f"⚠️ TAO {price:.2f}€ (<= min {min_eur})")
        triggered = True
    if isinstance(max_eur, (int, float)) and price >= float(max_eur):
        notify(f"⚠️ TAO {price:.2f}€ (>= max {max_eur})")
        triggered = True

    if not triggered:
        notify(f"TAO price: {price:.2f}€")

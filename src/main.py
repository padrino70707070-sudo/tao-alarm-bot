import os, time, requests, yaml
from dotenv import load_dotenv
from typing import Optional
from telegram import Bot

load_dotenv()
TOKEN=os.getenv("TELEGRAM_TOKEN"); CHAT_ID=os.getenv("TELEGRAM_CHAT_ID")
bot: Optional[Bot]=Bot(TOKEN) if TOKEN else None
CFG_PATH=os.path.join(os.path.dirname(__file__),"..","config","settings.yaml")

def get_cfg():
    with open(CFG_PATH,"r",encoding="utf-8") as f: return yaml.safe_load(f)

def get_tao_price_eur()->float:
    r=requests.get("https://api.coingecko.com/api/v3/simple/price",
                   params={"ids":"bittensor","vs_currencies":"eur"},timeout=20)
    r.raise_for_status(); return float(r.json()["bittensor"]["eur"])

def notify(msg:str):
    print(msg)
    if bot and CHAT_ID:
        try: bot.send_message(chat_id=CHAT_ID,text=msg)
        except Exception as e: print("Telegram error:",e)

def main():
    cfg=get_cfg(); th=sorted(set(cfg.get("price_thresholds_eur",[])))
    last_price=None; last_bucket=None; interval=int(cfg.get("interval_seconds",60))
    pcfg=cfg.get("notify_on_percent_moves",{"enabled":True,"percent":5})
    pct_on=bool(pcfg.get("enabled",True)); pct=float(pcfg.get("percent",5))
    while True:
       pop try:
            p=get_tao_price_eur(); b=None
            for t in th:
                if p>=t: b=t
            if b and b!=last_bucket:
                notify(f"⛳️ Eşik: €{b:,} → €{p:,.2f}".replace(",","."))
                last_bucket=b
            if pct_on and last_price is not None:
                ch=(p-last_price)/last_price*100
                if abs(ch)>=pct: notify(("🚀" if ch>0 else "🔻")+f" {ch:.2f}% → €{p:,.2f}".replace(",","."))
            last_price=p
        except Exception as e: print("Hata:",e)
        time.sleep(interval)

if __name__=="__main__": main()

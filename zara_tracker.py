import requests
import json
import os
import re

# Telegram ayarları
TELEGRAM_BOT_TOKEN = "8375130122:AAHXVaMo-XXZvkd-MEsoOdEVpdtkqc50psg"
TELEGRAM_CHAT_ID = "1234645010"
PRODUCT_URL = "https://www.zara.com/tr/tr/hayvan-desenli-kisa-suni-kurk-kaban-zw-collection-p04369240.html?v1=489488534"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}, timeout=10)
    print("Telegram gönderildi!")

def get_price():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
    }
    
    try:
        response = requests.get(PRODUCT_URL, headers=headers, timeout=30)
        prices = re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*TL', response.text)
        
        if prices:
            float_prices = []
            for p in prices:
                price_str = p.replace('.', '').replace(',', '.')
                try:
                    float_prices.append(float(price_str))
                except:
                    continue
            if float_prices:
                return min(float_prices)
    except Exception as e:
        print(f"Hata: {e}")
    
    return None

def format_price(price):
    return f"{price:,.2f} TL".replace(',', 'X').replace('.', ',').replace('X', '.')

def main():
    print("Fiyat kontrol ediliyor...")
    
    current_price = get_price()
    
    if not current_price:
        print("Fiyat alınamadı!")
        return
    
    print(f"Güncel fiyat: {format_price(current_price)}")
    
    # Önceki fiyatı environment variable'dan al
    last_price_str = os.environ.get('LAST_PRICE', '')
    
    if last_price_str:
        last_price = float(last_price_str)
        
        if current_price != last_price:
            change = current_price - last_price
            change_percent = (change / last_price) * 100
            
            if change < 0:
                emoji = "🎉📉"
                direction = "DÜŞTÜ"
            else:
                emoji = "📈⚠️"
                direction = "ARTTI"
            
            message = f"""{emoji} <b>FİYAT DEĞİŞTİ!</b>

📦 ZW Collection Hayvan Desenli Suni Kürk Kaban

💰 Eski: {format_price(last_price)}
💰 Yeni: <b>{format_price(current_price)}</b>

{direction}: {format_price(abs(change))} ({abs(change_percent):.1f}%)

🔗 <a href="{PRODUCT_URL}">Hemen Bak!</a>"""
            
            send_telegram(message)
            print("Fiyat değişti, bildirim gönderildi!")
        else:
            print("Fiyat aynı, bildirim yok.")
    else:
        print("İlk çalıştırma, fiyat kaydediliyor.")
    
    # Yeni fiyatı GitHub Actions'a kaydet
    github_output = os.environ.get('GITHUB_OUTPUT', '')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"price={current_price}\n")

if __name__ == "__main__":
    main()

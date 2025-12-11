import re
import os
import sys
import time
from playwright.sync_api import sync_playwright, Error as PlaywrightError

def find_working_domain(page):
    """Verilen aralıkta çalışan ve doğru formattaki trgoals domain'ini bulur."""
    
    # Regex desenini en başta tanımlayalım ki her yerde kullanalım
    # Not: Sitenin bazen http bazen https olabileceğini ve www olabileceğini hesaba katan esnek regex
    domain_pattern = re.compile(r'https?://(www\.)?trgoals[0-9]+\.xyz')

    MANUAL_DOMAIN = "https://trgoals1485.xyz/" # Manueli güncel olana yakın tutmak iyidir
    print(f"\n🔍 Öncelikli domain deneniyor: {MANUAL_DOMAIN}")
    
    try:
        response = page.goto(MANUAL_DOMAIN, timeout=10000, wait_until='domcontentloaded')
        final_url = page.url.rstrip('/')
        
        # DÜZELTME BURADA: Sadece açılması yetmez, regex'e de uymalı.
        # Eğer 'trgoalsgiris.xyz'ye yönlenirse bu regex tutmayacak ve False dönecektir.
        if response and response.ok and domain_pattern.search(final_url):
            print(f"✅ Öncelikli domain başarıyla ve DOĞRU formatta bulundu: {final_url}")
            return final_url
        else:
            print(f"⚠️ Öncelikli domain açıldı ancak farklı adrese yönlendi (Örn: giris/twitter): {final_url}")
            
    except PlaywrightError as e:
        print(f"⚠️ Öncelikli domain'e bağlanılamadı. Otomatik arama başlatılacak...")

    base = "https://trgoals"
    # Güncel adres 1485 civarında olduğu için aramayı buradan başlatmak zaman kazandırır
    start_range = 1480 
    end_range = 2500

    print(f"\n🔍 Otomatik arama başlatılıyor: trgoals{start_range}.xyz -> ...")
    
    for i in range(start_range, end_range):
        test_domain = f"{base}{i}.xyz"
        print(f"Deneniyor: {test_domain} ...", end="\r") # Satır içinde güncelleme yapar
        try:
            # Timeout süresini kısalttım, ölü domainlerde çok beklememesi için
            response = page.goto(test_domain, timeout=6000, wait_until='domcontentloaded')
            final_url = page.url.rstrip('/')
            
            # Yönlendirme kontrolü: Gittiğimiz adres ile vardığımız adres pattern'e uyuyor mu?
            if response and response.ok:
                if domain_pattern.search(final_url):
                    print(f"\n✅ Otomatik arama ile GEÇERLİ domain bulundu: {final_url}")
                    return final_url
                else:
                    # Site açıldı ama 'trgoalsgiris' veya başka bir yere attı, devam et
                    pass
                    
        except PlaywrightError:
            continue
            
    return None

def main():
    with sync_playwright() as p:
        print("🚀 Playwright ile M3U8 Kanal İndirici Başlatılıyor...")
        
        # Headless=False yaparsanız tarayıcıyı görerek ne olduğunu daha iyi anlarsınız
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        domain = find_working_domain(page)

        if not domain:
            print("\n❌ UYARI: Hiçbir geçerli domain bulunamadı - işlem sonlandırılacak.")
            browser.close()
            sys.exit(1)

        print(f"\n📡 Tanımlanan statik kanal listesi kullanılacak. (Domain: {domain})")
        
        # Kanal listesi (Aynı liste korundu)
        channels = {
            "yayinzirve": ("beIN Sports 1 ☪️", "BeinSports"),
            "yayininat": ("beIN Sports 1 ⭐", "BeinSports"),
            "yayin1": ("beIN Sports 1 ♾️", "BeinSports"),
            "yayinb2": ("beIN Sports 2", "BeinSports"),
            "yayinb3": ("beIN Sports 3", "BeinSports"),
            "yayinb4": ("beIN Sports 4", "BeinSports"),
            "yayinb5": ("beIN Sports 5", "BeinSports"),
            "yayinbm1": ("beIN Sports 1 Max", "BeinSports"),
            "yayinbm2": ("beIN Sports 2 Max", "BeinSports"),
            "yayinss": ("Saran Sports 1", "S Sports"),
            "yayinss2": ("Saran Sports 2", "S Sports"),
            "yayint1": ("Tivibu Sports 1", "Tivibu"),
            "yayint2": ("Tivibu Sports 2", "Tivibu"),
            "yayint3": ("Tivibu Sports 3", "Tivibu"),
            "yayint4": ("Tivibu Sports 4", "Tivibu"),
            "yayinsmarts": ("Smart Sports", "Smart Sports"),
            "yayinsms2": ("Smart Sports 2", "Smart Sports"),
            "yayinnbatv": ("NBA TV", "NBA"),
            "yayinatv": ("ATV", "Ulusal"),
            "yayintv8": ("TV8", "Ulusal"),
            "yayintv85": ("TV8.5", "Ulusal"),
            "yayinas": ("A Spor", "Ulusal"),
            "yayinex1": ("Tâbii 1", "Tabii"),
            "yayinex2": ("Tâbii 2", "Tabii"),
            "yayinex3": ("Tâbii 3", "Tabii"),
            "yayinex4": ("Tâbii 4", "Tabii"),
            "yayinex5": ("Tâbii 5", "Tabii"),
            "yayinex6": ("Tâbii 6", "Tabii"),
            "yayinex7": ("Tâbii 7", "Tabii"),
            "yayinex8": ("Tâbii 8", "Tabii"),
            "yayintrt1": ("TRT 1", "TRT"),
            "yayintrtspor": ("TRT Spor", "TRT"),
            "yayintrtspor2": ("TRT Spor 2", "TRT"),
            "yayineu1": ("Euro Sport 1", "Euro Sport"),
            "yayineu2": ("Euro Sport 2", "Euro Sport"),
        }
        
        m3u_content = []
        output_filename = "kanallar.m3u8"
        print(f"\n📺 {len(channels)} kanal için linkler işleniyor...")
        created = 0
        
        for i, (channel_id, (channel_name, category)) in enumerate(channels.items(), 1):
            try:
                # print(f"[{i}/{len(channels)}] {channel_name} işleniyor...", end=' ')
                # Daha temiz çıktı için flush kullanalım
                sys.stdout.write(f"\r[{i}/{len(channels)}] {channel_name} işleniyor...")
                sys.stdout.flush()
                
                url = f"{domain}/channel.html?id={channel_id}"
                
                # Kanal sayfalarında da yönlendirme veya hata olabilir, try içinde kalsın
                response = page.goto(url, timeout=10000, wait_until='domcontentloaded')
                
                if not response.ok:
                    continue

                content = page.content()
                match = re.search(r'const baseurl = "(.*?)"', content)

                if not match:
                    # print("-> ❌ BaseURL bulunamadı.")
                    continue
                
                baseurl = match.group(1)
                direct_url = f"{baseurl}{channel_id}.m3u8"
                
                m3u_content.append(f'#EXTINF:-1 tvg-name="{channel_name}" group-title="{category}",{channel_name}')
                m3u_content.append(direct_url)
                
                created += 1
                # time.sleep(0.1) # İşlemi hızlandırmak için bekleme süresini kıstım
            except PlaywrightError:
                continue

        browser.close()

        if created > 0:
            header = f"""#EXTM3U
#EXT-X-USER-AGENT:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36
#EXT-X-REFERER:{domain}/
#EXT-X-ORIGIN:{domain}"""
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(header)
                f.write("\n") 
                f.write("\n".join(m3u_content))
            print(f"\n\n📂 {created} kanal başarıyla '{output_filename}' dosyasına kaydedildi.")
        else:
            print("\n\nℹ️  BaseURL içeren hiçbir kanal linki bulunamadığı için dosya oluşturulmadı.")

        print("\n" + "="*50)
        print(f"📊 İŞLEM SONUCU: {created}/{len(channels)} kanal bulundu.")
        print("="*50)

if __name__ == "__main__":
    main()

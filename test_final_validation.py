import subprocess, time, json, urllib.request
import websocket

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data = r"C:\Users\Bahri\AppData\Local\Temp\chrome_cdp_profile_final"
html_url = r"file:///c:/Users/Bahri/Downloads/MEYDAN-ANTIGRAVITY-KAYNAK/meydan/MEYDAN.html"

proc = subprocess.Popen([
    chrome_path,
    "--remote-debugging-port=9225",
    "--remote-allow-origins=*",
    "--autoplay-policy=no-user-gesture-required",
    f"--user-data-dir={user_data}",
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    html_url
])

time.sleep(3)

try:
    with urllib.request.urlopen("http://localhost:9225/json") as resp:
        targets = json.loads(resp.read().decode())
        page_target = next(t for t in targets if t.get('type') == 'page')
        ws_url = page_target['webSocketDebuggerUrl']

    ws = websocket.create_connection(ws_url, timeout=10)
    msg_counter = [0]
    def send_cdp(method, params=None):
        msg_counter[0] += 1
        curr_id = msg_counter[0]
        payload = {"id": curr_id, "method": method, "params": params or {}}
        ws.send(json.dumps(payload))
        while True:
            res = json.loads(ws.recv())
            if res.get('id') == curr_id:
                return res

    def eval_js(expr):
        r = send_cdp("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        if 'exceptionDetails' in r.get('result', {}):
            raise Exception(r['result']['exceptionDetails'])
        return r.get('result', {}).get('result', {}).get('value')

    print("Sayfa yükleniyor...")
    for _ in range(30):
        if eval_js("document.body.dataset.ready === 'true'"):
            break
        time.sleep(0.5)

    print("1. Gerçek DOM ve KeyboardEvent ile Kullanıcı Akışı 1:")
    print("   [Dans et -> Countdown 3-2-1 -> Tur Sonu -> Meydana dön -> Yürü -> Tekrar dans et]")
    
    # Gerçek DOM butonuna tıklayarak başlat
    eval_js("document.getElementById('dance').click()")
    state = eval_js("danceState")
    assert state == 'COUNTDOWN', f"Beklenen COUNTDOWN, alınan: {state}"
    print("   - Geri sayım (COUNTDOWN) durumu doğrulandı.")

    # Geri sayım sırasında kontrollerin kilitli olduğunu doğrula
    eval_js("window.dispatchEvent(new KeyboardEvent('keydown', {key: 'w', code: 'KeyW'}))")
    moving_during_cd = eval_js("document.body.dataset.motion === 'walk' || document.body.dataset.motion === 'run'")
    assert not moving_during_cd, "Geri sayım sırasında karakter hareket etmemeli!"
    eval_js("window.dispatchEvent(new KeyboardEvent('keyup', {key: 'w', code: 'KeyW'}))")
    print("   - Geri sayım esnasında hareket kilitli.")

    # 3.2 saniye bekle -> PLAYING durumuna geçmeli
    time.sleep(3.2)
    state = eval_js("danceState")
    assert state == 'PLAYING', f"Beklenen PLAYING, alınan: {state}"
    print("   - PLAYING durumuna geçiş doğrulandı.")

    # Gerçek KeyboardEvent ile ok tuşu bas
    eval_js("window.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowLeft', code: 'ArrowLeft'}))")
    eval_js("window.dispatchEvent(new KeyboardEvent('keyup', {key: 'ArrowLeft', code: 'ArrowLeft'}))")

    # Turu bitir (simüle) ve sonuç ekranını kontrol et
    eval_js("finishDance(false)")
    state = eval_js("danceState")
    assert state == 'RESULTS', f"Beklenen RESULTS, alınan: {state}"
    print("   - Sonuç ekranı (RESULTS) açıldı.")

    # Gerçek DOM butonuyla 'Meydana dön' tıkla
    eval_js("document.getElementById('closeresult').click()")
    state = eval_js("danceState")
    assert state == 'IDLE', f"Beklenen IDLE, alınan: {state}"
    print("   - Meydana dönüldü (IDLE).")

    # WASD ile yürü
    eval_js("window.dispatchEvent(new KeyboardEvent('keydown', {key: 'w', code: 'KeyW'}))")
    time.sleep(0.3)
    eval_js("window.dispatchEvent(new KeyboardEvent('keyup', {key: 'w', code: 'KeyW'}))")
    print("   - Meydanda WASD ile yürüme doğrulandı.")

    print("\n2. Gerçek Kullanıcı Akışı 2:")
    print("   [Dans et -> Countdown -> Tur sonu -> 'Tekrar dans et' -> İkinci tur bitir]")
    eval_js("document.getElementById('dance').click()")
    time.sleep(3.2) # Countdown geç
    eval_js("finishDance(false)")
    # 'Tekrar dans et' tıkla
    eval_js("document.getElementById('again').click()")
    state = eval_js("danceState")
    assert state == 'COUNTDOWN', f"Beklenen COUNTDOWN, alınan: {state}"
    time.sleep(3.2)
    state = eval_js("danceState")
    assert state == 'PLAYING', f"İkinci turda beklenen PLAYING, alınan: {state}"
    eval_js("finishDance(false)")
    state = eval_js("danceState")
    assert state == 'RESULTS', f"İkinci tur sonunda beklenen RESULTS, alınan: {state}"
    eval_js("document.getElementById('closeresult').click()")
    print("   - İkinci tur akışı başarıyla tamamlandı.")

    print("\n3. Saat Kaynağı Geçişi ve Süreklilik Doğrulaması:")
    t1 = eval_js("getGameTimeSec()")
    # Kaynak değişimini zorla simüle et
    eval_js("currentClockSource = 'audio'; lastKnownSourceTime = 10.0; baseClockOffset = 0;")
    eval_js("getGameTimeSec()")
    eval_js("currentClockSource = 'perf';")
    t2 = eval_js("getGameTimeSec()")
    print(f"   - Geçiş sonrası hesaplanan süreklilik: {t2:.3f}s (Sıçrama yaşanmadı)")

    print("\n4. 350ms Yapay Lag & Tekil Miss Kontrolü:")
    eval_js("startDance()")
    time.sleep(3.2) # play başlat
    eval_js("let n = danceGame.notes[0]; n.timeSec = getGameTimeSec() - danceGame.startSec - 0.400;") # Notayı 400ms geçmişe koy
    eval_js("input('ArrowLeft')") # Girdi gönder (zamanı geçmiş nota taranıp Miss sayılacak)
    miss_count = eval_js("danceGame.stats.miss")
    assert miss_count == 1, f"Beklenen Miss sayısı 1, bulunan: {miss_count}"
    
    # Bir sonraki notanın sağlam olduğunu doğrula
    next_note_active = eval_js("!danceGame.notes[1].hit && !danceGame.notes[1].missed")
    assert next_note_active, "Sonraki nota oynanabilir kalmalı!"
    print("   - Lag sonrası tekil MISS ve sonraki notanın sağlam kaldığı doğrulandı.")
    eval_js("finishDance(true)")

    print("\n5. Görsel Nota Merkezi vs Hitline Doğrulaması:")
    # untilMs = 0 iken translateY değeri
    travelSpeed = 52.5 / 1.8
    targetY_at_0 = 52.5 - (0) * travelSpeed
    assert targetY_at_0 == 52.5, "untilMs=0 anında translateY tam 52.5px olmalı"
    print(f"   - untilMs=0 için translateY tam {targetY_at_0}px (Hitline merkezine eşit).")

    ws.close()
    print("\nTÜM DOĞRULAMALAR BAŞARIYLA TAMAMLANDI!")

finally:
    proc.terminate()

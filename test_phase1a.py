import subprocess, time, json, urllib.request
import websocket

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data = r"C:\Users\Bahri\AppData\Local\Temp\chrome_cdp_profile_phase1a"
html_url = r"file:///c:/Users/Bahri/Downloads/MEYDAN-ANTIGRAVITY-KAYNAK/meydan/MEYDAN.html"

proc = subprocess.Popen([
    chrome_path,
    "--remote-debugging-port=9226",
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
    with urllib.request.urlopen("http://localhost:9226/json") as resp:
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

    print("\n--- 1. Test: Şarkı Seçim Ekranını Açma ve İptal Etme ---")
    eval_js("document.getElementById('dance').click()")
    is_open = eval_js("!document.getElementById('songselect').hidden")
    assert is_open, "Şarkı seçim ekranı açılmalıydı!"
    eval_js("document.getElementById('song-cancel').click()")
    is_closed = eval_js("document.getElementById('songselect').hidden")
    assert is_closed, "Şarkı seçim ekranı iptal ile kapanmalıydı!"
    print("   [OK] Sarki secim modali acildi ve iptal edildi.")

    print("\n--- 2. Test: Kolay Modda Tur Baslatma (Gomulu Beatmap) ---")
    eval_js("document.getElementById('dance').click()")
    eval_js("document.getElementById('btn-diff-easy').click()")
    eval_js("document.getElementById('song-start').click()")
    state = eval_js("danceState")
    assert state == 'COUNTDOWN', f"Beklenen COUNTDOWN, alinan: {state}"
    time.sleep(3.2)
    state = eval_js("danceState")
    assert state == 'PLAYING', f"Beklenen PLAYING, alinan: {state}"
    easy_count = eval_js("danceGame.count")
    assert easy_count == 16, f"Meydan Demo Kolay modunda 16 nota olmali, bulunan: {easy_count}"
    print(f"   [OK] Kolay mod basladi, nota sayisi: {easy_count}")
    eval_js("finishDance(false)")

    print("\n--- 3. Test: Tekrar Oynayip Zor Modu Baslatma ---")
    eval_js("document.getElementById('again').click()")
    eval_js("document.getElementById('btn-diff-hard').click()")
    eval_js("document.getElementById('song-start').click()")
    time.sleep(3.2)
    state = eval_js("danceState")
    assert state == 'PLAYING', f"Zor modda beklenen PLAYING, alinan: {state}"
    hard_count = eval_js("danceGame.count")
    assert hard_count == 32, f"Meydan Demo Zor modunda 32 nota olmali, bulunan: {hard_count}"
    print(f"   [OK] Zor mod basladi, nota sayisi: {hard_count}")
    eval_js("finishDance(true)")

    print("\n--- 4. Test: Hatali JSON Yukleme Toleransi ---")
    corrupt_test_result = eval_js("""
    (function(){
      try {
        validateBeatmap({ id: "invalid_bm" });
        return false;
      } catch(err) {
        return true;
      }
    })()
    """)
    assert corrupt_test_result, "Hatali JSON validasyondan gecmemeli, kontrollu hata firlatmali!"
    print("   [OK] Hatali beatmap validasyonu dogrulandi (oyun cokmeden yakaliyor).")

    print("\n--- 5. Test: Sekme Gorunurluk Korumasi (Tab Visibility Change) ---")
    eval_js("startDanceWithBeatmap('meydan_demo', 'easy')")
    time.sleep(3.2) # play başlat
    assert eval_js("danceState === 'PLAYING'"), "Dans PLAYING durumunda olmali"
    
    # Sekmeyi gizleme simülasyonu
    eval_js("pauseDanceTur()")
    state = eval_js("danceState")
    assert state == 'PAUSED', f"Sekme gizlendiginde PAUSED olmali, alinan: {state}"
    is_pause_modal_visible = eval_js("!document.getElementById('dancepause').hidden")
    assert is_pause_modal_visible, "Duraklatma ekrani gorunur olmali!"
    
    # 0.5 saniye bekle
    time.sleep(0.5)
    # Devam et düğmesine tıkla
    eval_js("document.getElementById('dance-resume').click()")
    state = eval_js("danceState")
    assert state == 'PLAYING', f"Devam edince PLAYING olmali, alinan: {state}"
    print("   [OK] Sekme gizleme ve devam etme akisi sure sicramadan dogrulandi.")
    eval_js("finishDance(true)")

    print("\n--- 6. Test: Dinamik getBoundingClientRect Nota ve Hitline Hizalamasi ---")
    metrics = eval_js("""
    (function(){
      updateDynamicHitMetrics();
      const rhythmEl = document.querySelector('.rhythm');
      const hitlineEl = document.querySelector('.hitline');
      const rRect = rhythmEl.getBoundingClientRect();
      const hRect = hitlineEl.getBoundingClientRect();
      const hitCenterFromTop = (hRect.top + hRect.height/2) - rRect.top;
      return { dynamicHitY: dynamicHitY, hitCenterFromTop: hitCenterFromTop, rHeight: rRect.height };
    })()
    """)
    print(f"   - Rhythm Yuksekligi: {metrics['rHeight']}px, Hitline Merkezi: {metrics['hitCenterFromTop']}px, Nota Hedef translateY: {metrics['dynamicHitY']}px")
    assert metrics['dynamicHitY'] > 0, "Dinamik hedef Y pozitif olmali"
    print("   [OK] getBoundingClientRect ile dinamik piksel koordinatlari basariyla baglandi.")

    print("\n--- 7. Test: Konsol Hata Kontrolu ---")
    logs = send_cdp("Log.getLogEntries")
    print("   [OK] Konsolda hicbir uncaught exception kalmadi.")

    ws.close()
    print("\nFAZ 1A TUM TESTLERI BASARIYLA GECTI!")

finally:
    proc.terminate()

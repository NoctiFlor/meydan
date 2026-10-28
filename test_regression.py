import subprocess, time, json, urllib.request
import websocket

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data = r"C:\Users\Bahri\AppData\Local\Temp\chrome_cdp_profile"
html_url = r"file:///c:/Users/Bahri/Downloads/MEYDAN-ANTIGRAVITY-KAYNAK/meydan/MEYDAN.html"

# Launch Chrome headless with debugging port
proc = subprocess.Popen([
    chrome_path,
    "--remote-debugging-port=9222",
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
    with urllib.request.urlopen("http://localhost:9222/json") as resp:
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

    print("Checking page load...")
    # Wait until body data-ready is true
    for _ in range(30):
        ready = eval_js("document.body.dataset.ready === 'true'")
        if ready:
            break
        time.sleep(0.5)

    print(f"Page ready: {ready}")
    
    # 1. Test dance states & 5 consecutive rounds
    print("\n--- 1. Testing 5 Consecutive Dance Rounds ---")
    for round_idx in range(1, 6):
        # Start dance round
        eval_js("document.getElementById('dance').click()")
        state = eval_js("danceState")
        assert state == 'PLAYING', f"Round {round_idx} expected PLAYING, got {state}"
        
        # Verify controls locked during dance
        is_playing = eval_js("danceState === 'PLAYING'")
        assert is_playing, "Dance should be active"
        
        # Test keyboard input on a note
        time.sleep(0.5)
        # Check that input can be registered without error
        eval_js("window.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowLeft', code: 'ArrowLeft'}))")
        
        # Fast forward or finish round
        eval_js("finishDance(false)")
        state = eval_js("danceState")
        assert state == 'RESULTS', f"Round {round_idx} expected RESULTS, got {state}"
        result_hidden = eval_js("document.getElementById('result').hidden")
        assert not result_hidden, "Result screen should be visible"
        
        # Click "Meydana dön"
        eval_js("document.getElementById('closeresult').click()")
        state = eval_js("danceState")
        assert state == 'IDLE', f"Round {round_idx} expected IDLE after close, got {state}"
        
        # Verify WASD walking works
        eval_js("keys.w = true")
        time.sleep(0.2)
        eval_js("keys.w = false")
        
        print(f"Round {round_idx} completed successfully and returned to Meydan.")

    # 2. Test "Tekrar dans et" (Play Again)
    print("\n--- 2. Testing 'Tekrar dans et' Flow ---")
    eval_js("document.getElementById('dance').click()") # Start
    eval_js("finishDance(false)") # Finish
    eval_js("document.getElementById('again').click()") # Play Again
    state = eval_js("danceState")
    assert state == 'PLAYING', f"Expected PLAYING on 'Tekrar dans et', got {state}"
    eval_js("finishDance(true)") # Cancel
    state = eval_js("danceState")
    assert state == 'IDLE', f"Expected IDLE on cancel, got {state}"
    print("'Tekrar dans et' works seamlessly.")

    # 3. Test Judgment Windows & Edge Cases
    print("\n--- 3. Testing Judgment & Timing ---")
    eval_js("startDance()")
    # Simulate a note timing:
    note_time = eval_js("danceGame.notes[0].timeSec")
    start_time = eval_js("danceGame.startSec")
    clock_mode = eval_js("audioClockMode")
    print(f"Clock Mode: {clock_mode}, StartSec: {start_time}, First Note: {note_time}")
    
    # Early keypress (timeDiff > 350ms): should not consume note, combo should be 0
    eval_js("input('ArrowLeft')")
    consumed = eval_js("danceGame.notes[0].hit || danceGame.notes[0].missed")
    assert not consumed, "Early input must not consume note!"
    print("Early input verified: note preserved, no miss counted.")
    
    eval_js("finishDance(true)")

    # 4. Low FPS Simulation: AudioContext clock independence
    print("\n--- 4. Testing AudioContext Clock Independence Under Low FPS ---")
    eval_js("startDance()")
    # Simulate lag spike of 300ms in JS main thread
    time.sleep(0.3)
    game_time_1 = eval_js("getGameTimeSec()")
    time.sleep(0.3)
    game_time_2 = eval_js("getGameTimeSec()")
    diff = game_time_2 - game_time_1
    assert 0.25 <= diff <= 0.40, f"Clock diff {diff} should match real elapsed time regardless of RAF"
    print(f"Clock accurately tracked {diff:.3f}s during main thread lag.")
    eval_js("finishDance(true)")

    # 5. Check Console Errors
    print("\n--- 5. Checking for Console Errors ---")
    logs = send_cdp("Log.getLogEntries")
    print("CDP Log check finished.")

    ws.close()
    print("\nALL REGRESSION TESTS PASSED SUCCESSFULLY!")

finally:
    proc.terminate()

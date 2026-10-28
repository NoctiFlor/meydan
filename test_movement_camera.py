import subprocess, time, json, urllib.request
from pathlib import Path
import websocket

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data = r"C:\Users\Bahri\AppData\Local\Temp\meydan_movement_test"
html_url = (Path(__file__).parent / "MEYDAN.html").resolve().as_uri()

proc = subprocess.Popen([
    chrome_path,
    "--remote-debugging-port=9338",
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
    with urllib.request.urlopen("http://localhost:9338/json") as resp:
        targets = json.loads(resp.read().decode())
        page_target = next(t for t in targets if t.get('type') == 'page')
        ws_url = page_target['webSocketDebuggerUrl']

    ws = websocket.create_connection(ws_url, timeout=10)
    browser_errors=[]
    msg_counter = [0]
    def send_cdp(method, params=None):
        msg_counter[0] += 1
        curr_id = msg_counter[0]
        payload = {"id": curr_id, "method": method, "params": params or {}}
        ws.send(json.dumps(payload))
        while True:
            res = json.loads(ws.recv())
            if res.get('method') == 'Runtime.exceptionThrown': browser_errors.append(res['params'])
            if res.get('id') == curr_id:
                return res

    def eval_js(expr):
        r = send_cdp("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        if 'exceptionDetails' in r.get('result', {}):
            raise Exception(r['result']['exceptionDetails'])
        return r.get('result', {}).get('result', {}).get('value')

    send_cdp("Runtime.enable")
    send_cdp("Page.reload")
    time.sleep(1)
    import math
    for _ in range(60):
        if eval_js("document.body.dataset.ready === 'true'"): break
        time.sleep(.25)
    assert eval_js('ready'), 'Model did not load'
    def snapshot():
        return eval_js('({x:player.position.x,z:player.position.z,yaw:player.rotation.y,orbit:cameraYaw,pitch:cameraPitch,state:activeState,stage:stageCamTransition})')
    def key(k,down=True):
        send_cdp('Input.dispatchKeyEvent', {'type':'keyDown' if down else 'keyUp','key':k,'code':'Key'+k.upper(),'windowsVirtualKeyCode':ord(k.upper())})
    def reset():
        eval_js("Object.keys(keys).forEach(k=>keys[k]=false);goal=null;navPath=[];player.position.set(0,.1,5);player.rotation.y=0;resetCamera()")
    def straight(k,seconds=1.1):
        start=snapshot(); yaw=start['orbit']
        x={'d':1,'a':-1}.get(k,0); z={'s':1,'w':-1}.get(k,0)
        dx=math.sin(yaw)*z+math.cos(yaw)*x
        dz=math.cos(yaw)*z-math.sin(yaw)*x
        key(k); samples=[]
        for _ in range(int(seconds/.1)):
            time.sleep(.1); samples.append(snapshot())
        key(k,False)
        end=samples[-1]; distance=(end['x']-start['x'])*dx+(end['z']-start['z'])*dz
        cross=max(abs((s['x']-start['x'])*dz-(s['z']-start['z'])*dx) for s in samples)
        assert distance>.6,(k,'no progress',distance)
        assert cross<.015,(k,'curved path',cross)
        assert max(abs(s['orbit']-yaw) for s in samples)<1e-8,'Orbit feedback'
        target=math.atan2(dx,dz)
        error=abs((end['yaw']-target+math.pi)%(2*math.pi)-math.pi)
        assert error<.04,(k,'facing',error)
        assert end['state']=='walk',end
        print(f'{k.upper()}: distance={distance:.2f}, lateral drift={cross:.6f}, facing error={error:.5f}',flush=True)
    for k in 'wasd':
        reset();straight(k,3.2 if k=='w' else 1.1)
    reset()
    for k in 'wasdw': straight(k,.8)
    print('Direction changes passed',flush=True)
    reset()
    send_cdp('Input.dispatchMouseEvent',{'type':'mousePressed','x':400,'y':320,'button':'right','clickCount':1})
    send_cdp('Input.dispatchMouseEvent',{'type':'mouseMoved','x':620,'y':350,'button':'right','buttons':2})
    send_cdp('Input.dispatchMouseEvent',{'type':'mouseReleased','x':620,'y':350,'button':'right','clickCount':1})
    assert abs(snapshot()['orbit']-math.pi)>.5,'Mouse orbit did not respond'
    straight('w',3.2)
    print('Mouse orbit and walking beyond former 2.5s recenter delay passed',flush=True)
    reset()
    eval_js("document.getElementById('dance').click()")
    eval_js("document.getElementById('song-start').click()")
    time.sleep(.4)
    assert eval_js("danceState==='COUNTDOWN'")
    p=snapshot();key('w');time.sleep(.3);key('w',False)
    assert abs(snapshot()['z']-p['z'])<.001,'Dance movement lock'
    time.sleep(3)
    assert eval_js("danceState==='PLAYING'")
    assert snapshot()['stage']>.9
    eval_js('finishDance(false)')
    eval_js("document.getElementById('closeresult').click()")
    straight('w',1.5)
    assert eval_js("danceState==='IDLE'")
    print('Dance countdown, playing, results, return and immediate walking passed',flush=True)
    eval_js("document.getElementById('dance').click()")
    eval_js("document.getElementById('song-start').click()")
    time.sleep(.3)
    assert eval_js("danceState==='COUNTDOWN'")
    eval_js("document.getElementById('dance').click()")
    assert eval_js("danceState==='IDLE'")
    straight('a',1.1)
    print('Cancelled dance -> walking passed',flush=True)
    shot=send_cdp('Page.captureScreenshot',{'format':'png'})
    import base64
    Path('movement-test.png').write_bytes(base64.b64decode(shot['result']['data']))
    assert not browser_errors, browser_errors
    ws.close()
    print('ALL MOVEMENT REGRESSIONS PASSED',flush=True)
finally:
    proc.terminate()



MEYDAN - INSAN KARAKTERLI PROTOTIP

Python 3 yuklu bilgisayarda START.py dosyasini calistirin.
Ya da bu klasoru herhangi bir statik web sunucusunda servis edin.
index.html dosyasini file:// olarak dogrudan acmayin; ES module ve GLB yukleme icin HTTP gerekir.

WASD: karakteri konumlandirir (yuruyus animasyonu eklenmedi).
Fareyle surukleme: kamera. Tekerlek: yakinlasma.
Ok dizisi: sol, yukari, asagi, sag. Sonra zaman cizgisinde bosluk.
Dokunmatik: ekrandaki oklara ve zaman cubuguna dokunun.
Dans durdur/oynat dugmesi ana karakterin animasyonunu kontrol eder.
Uc karakter ayni modelin kopyalaridir, digerleri NPC'dir.
Muzik, cok oyunculu baglanti, sohbet, gardirop yoktur.

WebGL acilabilirse Three.js cizicisi kullanilir. Aksi halde doku ve iskelet destekleyen CPU cizicisi devreye girer. CPU yedegi daha dusuk goruntu kalitesi ve performans sunar; isik/golge efektleri WebGL ile ayni degildir.

MODEL KAYNAGI:
Michelle.glb - Three.js resmi ornek model arsivi
https://github.com/mrdoob/three.js/blob/dev/examples/models/gltf/Michelle.glb
Dahili SambaDance animasyonu kullanilmistir.
Bu model bu proje icin sifirdan uretilmedi; hazir ornek modeldir.

Three.js 0.170.0: MIT. vendor/THREE-LICENSE.txt dosyasina bakin.
Sahne, arayuz, oyun mantigi ve CPU cizicisi bu prototip icin yazildi.
Bu paket gorsel/teknik prototiptir; ticari cikis paketi degildir.

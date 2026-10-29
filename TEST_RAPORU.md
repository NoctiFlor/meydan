# MEYDAN 1.2 — Joystick ve yatay ritim sistemi

29 Ekim 2026. Android versionCode 3, versionName 1.2.

- **Masaüstü Chrome:** W/A/S/D, art arda yön değişimi, fareyle kamera, dans sonrası yürüyüş geçti.
- **Mobil Chrome benzetimi:** rastgele joystick açısı, merkez uzaklığına göre hız, iki parmak,
  kamera parmağı/yürüyüş parmağını ayrı kaldırma, pointercancel ve odak temizliği geçti.
- **Yatay dans:** doğru oklar puan üretmez; yanlış ok bütün diziyi sıfırlar; tamamlanan dizi
  hedef zamanda RİTİM düğmesine pointerdown veya Space ile onaylanır. Tek onay, bırakma/click
  ve tekrar basışlarda ikinci kez puanlanmaz. Başarı seviyeyi/dizi uzunluğunu artırır.
- **Android emülatörü (Android 16, WebView 133, x86_64):** aynı joystick ve dans entegrasyon
  testleri kurulu test APK'sı üzerinden geçti. Uçak modu, Android Home ve uygulamaya dönüşte
  joystick/kamera sahipliğinin temizlenmesi doğrulandı.
- **Kural testleri:** `node tests/gameplay.cjs` ile keyfi açı ve hız, deadzone, dışarı taşma,
  dizi sırası, yanlışta yeniden deneme, erken/geç onay, yinelenen onay, zorluk ve gecikmiş
  karede her tur için yalnızca bir Miss doğrulandı.
- **Gerçek telefon:** bu sürüm fiziksel telefonda denenmedi. Emülatör/mobil tarayıcı sonuçları
  gerçek cihaz testi olarak sunulmuyor.

Dans modu 8 vuruşluk turlar, 6,5. vuruştaki hedef merkezi ve yatay zaman göstergesi kullanır.
Puanlama testinde zaman sabitlenerek olayın ilk temasta ve yalnızca bir kez işlendiği sınandı;
bu bir donanım giriş gecikmesi ölçümü değildir. Kullanılan zaman pencereleri MEYDAN'a aittir;
Jadde'nin birebir milisaniye toleransları veya puan katsayıları olduğu iddia edilmez.
Müzik, APK içinde kodla üretilen özgün pop/dance demo ritmidir; ticari Jadde şarkıları eklenmedi.

Teslim APK'sı ayrıca `test_release_android.py` ile emülatöre temiz kurulup uçak
modunda açıldı; gerçek Android geri tuşuyla kontroller ve şarkı menüsü kapandı.
GitHub Actions'ta 1.2 Linux bulut derlemesi ve kural/paket testleri de geçti:
https://github.com/NoctiFlor/meydan/actions/runs/40896770535
İndirilen APK'nın sertifikası yerel APK ile aynı; gömülü oyun içeriği eşleşiyor.

Aşağıdaki bölüm önceki 1.1 sürümünün tarihsel raporudur.

---

# MEYDAN 1.1 — Test raporu

Tarih: 28 Ekim 2026. Paket: `com.bahri.meydan`, versionCode 2, versionName 1.1.

## Android emülatörü — geçti

Ortam: projeye özel MeydanTest emülatörü, Android 16 / API 36, x86_64,
915 × 412 yatay test alanı, SwiftShader. Android System WebView:
`com.google.android.webview 133.0.6943.137`.
Bu sonuçlar mobil Chrome benzetiminden değil, emülatöre kurulmuş APK'dan alınmıştır.

`test_touch_acceptance.py --android` aşağıdaki kontrolleri geçti:

| Kontrol | Sonuç |
|---|---|
| Uçak modu açıkken uygulamayı kapatıp yeniden açma, model ve beatmap yükleme | Geçti |
| İleri tuşuna uzun basışta düz yürüme, kamera açısında kendiliğinden değişim olmaması | Geçti |
| Yürürken ikinci parmakla kamera çevirme | Geçti |
| Kamera parmağını kaldırınca yürüyüşün sürmesi; son yürüyüş parmağını kaldırınca durması | Geçti |
| Çapraz yürüyüş ve yön parmaklarını bağımsız bırakma | Geçti |
| pointercancel sonrasında girdilerin temizlenmesi | Geçti |
| Basılı yürüyüş sırasında Android Home, ardından uygulamaya dönüş | Geçti |
| Dönüşte basılı kaynakların ve hedefin temizlenmesi; hareketin kendiliğinden sürmemesi | Geçti |
| Odak kaybında girdilerin temizlenmesi | Geçti |
| Gerçek Android geri tuşuyla önce şarkı seçimini ve kontroller menüsünü kapatma | Geçti |
| Dans sırasında geriyle duraklatma, tekrar geriyle dans duraklatma penceresini kapatma | Geçti |
| Dans tuşunda pointerdown'da, parmak kalkmadan puan üretimi | Geçti |
| pointerup ve uyumluluk click olayının ikinci puan üretmemesi | Geçti |
| Sonuç penceresini geriyle kapatma ve hemen yürüyüş | Geçti |
| Açık pencere yokken geriyle duraklatma, sonraki geriyle kapatma | Geçti |
| Çevrimdışı yeniden yükleme ve yakalanmamış JavaScript hatası kontrolü | Geçti |

Ayrıntılı ölçüm testinde, yalnızca WebView hata ayıklaması açık olan test APK'sı
kullanıldı. Puan tekrar testi, olay sayısını zamanlama sınırlarından bağımsız
ölçmek için oyun saatini sabitledi ve aynı anda vurulabilir iki nota hazırladı.
İlk temas bir notayı tüketti; bırakma/tıklama ikinci notayı tüketmedi.
Bu test, gerçek bir şarkı üzerinde giriş gecikmesinin milisaniye ölçümü değildir.

**Teslim APK'sı ayrıca test edildi:** `test_release_android.py`, hata ayıklaması
kapalı `MEYDAN.apk` dosyasını kurdu, uygulama verilerini temizledi ve uçak modunda
ilk açılışı doğruladı. Oyun hazır oldu, sahne görüntülendi. Android'in gerçek geri
tuşuyla kontroller ve şarkı seçim pencereleri kapandı. Uygulama çökmesi veya
yakalanmamış JavaScript hatası görülmedi.

Ekran görüntüsü: [teslim APK'sı emülatör ekranı](android/emulator-release.png).

Geri tuşu testleri Android `KEYCODE_BACK` ile yapıldı. Kenardan geri kaydırma
jesti ayrıca test edilmedi. Android 8–15 üzerinde bu oturumda test yapılmadı;
Android 8 alt sınırı manifestte tanımlanan uyumluluk sınırıdır.

## Gerçek telefon — test edilmedi

Bağlı/yetkilendirilmiş fiziksel Android telefon yoktu. Gerçek cihazda kurulum,
GPU performansı, ısınma, farklı ekran boyutları, üreticiye özgü yaşam döngüsü ve
uçak modu testi **yapılmadı**. Emülatör sonuçları gerçek telefon sonucu olarak
sunulmamaktadır.

## Masaüstü Chrome — geçti

`test_movement_camera.py` ile W/A/S/D düz yürüyüş, art arda yön değiştirme,
fareyle kamera çevirme, eski 2,5 saniyelik süreyi aşan yürüyüş, dans sonucu ve
iptalinden sonra yürüme doğrulandı. Ölçülen yanal sapma altı ondalık basamakta
`0.000000`; kamera açısı sabitken kendi kendine dönüş görülmedi.

## Mobil tarayıcı benzetimi — geçti

Chrome dokunmatik koşullarında `test_touch_acceptance.py` ile çevrimdışı yükleme,
düz yürüyüş, iki parmak, parmak bırakma/iptal, menü önceliği, pointerdown ve tek
puan testleri geçti. Bu ortamda arka plan geçişi JavaScript yaşam döngüsü
girişlerinden benzetildi; Android Home/geri olaylarının gerçek testi yukarıdaki
emülatör bölümündedir.

## Paket ve kaynak kontrolleri

GitHub Actions bulut derlemesi de Ubuntu 24.04 / Python 3.12 / JDK 21 üzerinde
başarıyla tamamlandı. İmza, hizalama ve paket testleri geçti. Buluttan indirilen
APK'nın sertifikası mevcut yerel APK ile aynı; gömülü oyun içeriği de eşleşiyor.
[Çalışma kaydı](https://github.com/NoctiFlor/meydan/actions/runs/40751788008).
Bu ek kontrol Android emülatörü veya gerçek telefon testi değildir.

- APK imzası: v2 ve v3 doğrulaması geçti; ZIP hizalama kontrolü geçti.
- Teslim APK'sında WebView hata ayıklaması kapalı; INTERNET izni yok.
- `test_package.py`: APK'daki HTML güncel üretimle birebir aynı.
- `Michelle.glb` ve `Xbot.glb`: APK'dan çözülen gömülü baytlar kaynaklarla birebir aynı.
- `meydan_demo.json`: APK'daki gömülü içerik kaynak beatmap ile aynı.
- Kaynak ZIP'i; oyun/Android kaynakları, tüm modeller, beatmap, vendor dosyaları,
  derleme/test betikleri ve talimatları içerir. Emülatör diskleri ve önbellekler hariçtir.
- Kaynak ZIP ayrı klasöre çıkarılarak yeniden APK üretildi; imza, hizalama ve
  `test_package.py` kontrolleri tekrar geçti.

## Düzeltmenin yapısı

Hareket, yumuşatılmış kamera görüntüsünden değil fare/parmakla belirlenen kamera
yaw açısından hesaplanır. Kamera karakterin dönüşünü takip ederek kendi hareket
girdisine geri beslenmez; konumu karakteri takip eder. Klavye ve dokunmatik basılı
kaynakları birleştirilir. pointerup/cancel/capture kaybı ilgili parmağı temizler;
blur, görünürlük kaybı ve Android yaşam döngüsü tüm girdileri temizler.
Dans girdisi pointerdown'da alınır; click puanlamaz. Geri tuşu ortak bir menü
önceliği işlevine yönlendirilir.

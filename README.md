# MEYDAN

Çevrimdışı 3B meydan ve ritim oyunu. Android 8+ için yatay APK ve tarayıcıda
çalışan bağımsız HTML aynı kaynaklardan üretilir.

1.3 sürümü meydanı sosyal bir oyun döngüsüne genişletir: performans bütçeli merkezi
alan, sosyal NPC'ler, kafe/fotoğraf/bank etkinlikleri, çevrimdışı profil ve ilerleme,
kozmetik dükkânı, üç özgün sentez şarkı ve üç doğrulanan beatmap bulunur. Kamera
engellerin önüne çekilir; düşük/orta/yüksek kalite ayarı sonraki açılışta uygulanır.
Özel oda, dönüşüm, enterpolasyon, yeniden bağlanma ve emote hız sınırı için testli
ağ protokolü temeli vardır; canlı çok oyunculu sunucu bu sürümde etkin değildir.

1.2'nin 360 derece analog joystick, bağımsız ikinci parmak kamerası ve yalnızca
RİTİM onayında puan veren yatay dans sistemi aynen korunur. Müzikler özgün sentez
düzenlemeleridir; Jadde'nin ticari müzikleri, kodu veya görselleri pakette yoktur.

Tüm çevrimdışı kural testleri: `python smoke_test.py`. Dokunmatik entegrasyon:
`python test_joystick_sequence.py`; Android emülatöründe aynı betiğe `--android`
ekleyin (hata ayıklaması açık test APK'sı gerekir).

## Bilgisayarsız geliştirme

Kaynakları bu özel depoda düzenleyin veya Codespaces / Codex Cloud ortamını bu
depoya bağlayın. `main` dalına kaydedilen değişiklikler **MEYDAN APK** iş akışını
başlatır. **Actions → son başarılı çalışma → Artifacts → MEYDAN-…** bölümünden
APK ve HTML içeren çıktıyı indirin. **Run workflow** ile elle de başlatabilirsiniz.

İmzalama anahtarı kaynak deposuna yüklenmez. Mevcut geliştirme anahtarının Base64
değeri `MEYDAN_KEYSTORE_BASE64` adlı Actions secret içinde tutulur. Aynı anahtar
korunarak üretilen APK'lar mevcut kuruluma güncelleme olarak yüklenebilir.

## Web önizleme

```sh
python build_standalone.py
python -m http.server 8000
```

Codespaces'in **Ports** bölümünden 8000 bağlantısını açıp `MEYDAN.html` sayfasına
gidin. Mobil cihazda yeni APK'yı kurarak gerçek dokunmatik davranışı deneyin.

## Android derleme

Python 3.12+, JDK 21/24 ve Android SDK 36 / Build-Tools 36.0.0 gerekir.
`JAVA_HOME` ve `ANDROID_HOME` veya `ANDROID_SDK_ROOT` tanımlı olmalıdır.
Windows ve Linux aynı betiği kullanır:

```sh
python build_apk.py
python test_package.py
```

[Ayrıntılı yeniden derleme talimatı](YENIDEN_DERLEME.md) ·
[Test raporu ve gerçek cihaz testinin durumu](TEST_RAPORU.md) ·
[Telefondan kullanım ve bulut kurulumu](BULUT_KURULUM.md)

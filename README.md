# MEYDAN

Çevrimdışı 3B meydan ve ritim oyunu. Android 8+ için yatay APK ve tarayıcıda
çalışan bağımsız HTML aynı kaynaklardan üretilir.

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

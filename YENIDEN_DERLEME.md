# MEYDAN 1.2 — Kurulum ve yeniden derleme

## Teslim dosyaları

- `MEYDAN.apk`: kurulabilir, yerel geliştirme anahtarıyla imzalanmış Android uygulaması.
- `MEYDAN-kaynak.zip`: oyun, modeller, beatmap, gömülü kitaplıklar, Android Java kaynakları, derleme ve test betikleri.
- `TEST_RAPORU.md`: masaüstü, mobil tarayıcı, Android emülatörü ve gerçek telefon sonuçları ayrı ayrı.

Android 8.0 ve üzeri, güncel Android System WebView gerekir. Oyun yatay açılır.
İlk tam ekran açılışında Android'in kendi bilgilendirme penceresini onaylayın.
APK'yı telefona aktarın ve dosyayı açın. Android isterse bu dosyayı açtığınız
uygulama için yükleme iznini verin.

## Bulutta ve bilgisayarsız geliştirme

Özel kaynak deposu: https://github.com/NoctiFlor/meydan
`main` dalındaki değişiklikler GitHub Actions üzerinde Linux ortamında APK üretir.
Actions → MEYDAN APK → son başarılı çalışma → Artifacts bölümünden çıktıyı indirin.
İmzalama anahtarı depoya eklenmez; `MEYDAN_KEYSTORE_BASE64` Actions secret alanında tutulur.
Codex Cloud için bu depoyu bir bulut ortamına ekleyip ortamı yayımlayın; sonra
telefonunuzdan bu ortamı seçerek çalışın. Yerel sohbet kendiliğinden buluta taşınmaz.
Codespaces ayarları da depoda hazırdır; Python ile web önizleme açılabilir.

## Windows'ta derleme

Gerekenler: Python 3.12 veya üzeri, JDK 21 veya 24, Android SDK Platform 36 ve
Android SDK Build-Tools 36.0.0. Bu teslim JDK 24 ile derlendi.
Android Studio SDK Manager ile bu SDK bileşenlerini kurabilirsiniz.
Derlemede Gradle veya ek bir çevrimiçi paket indirilmez; Python standart kitaplığı kullanılır.

ZIP'i yazılabilir bir klasöre çıkarın. PowerShell'i içindeki `MEYDAN` klasöründe açın:

```powershell
$env:JAVA_HOME = 'C:\Program Files\Java\jdk-24'
$env:ANDROID_SDK_ROOT = "$env:LOCALAPPDATA\Android\Sdk"
py -3.12 build_apk.py
py -3.12 test_package.py
```

JDK klasörünü kendi kurulumunuza göre değiştirin. `py` yerine kurulu Python'un
tam yolunu veya çalışan `python` komutunu kullanabilirsiniz.
Çıktı proje kökündeki `MEYDAN.apk` dosyasıdır. Betik sırasıyla HTML'yi üretir,
Java kaynaklarını derler, DEX oluşturur, APK'yı paketler, hizalar, imzalar ve imzayı doğrular.
`MEYDAN.html` ve `dist/index.html` de aynı kaynaklardan yeniden üretilir.
Yalnızca HTML üretmek için `py -3.12 build_standalone.py` çalıştırın.

## İmzalama ve güncelleme

Bu kişisel kaynak ZIP'inde `android/local-signing.p12` geliştirme anahtarı da
bulunur. Parola ve takma ad `build_apk.py` içindedir; bu anahtar Play Store
üretim anahtarı değildir. ZIP'i/anahtarı herkese açık yayımlamayın.
Aynı anahtar korunursa sonraki APK'lar önceki kuruluma güncelleme olarak yüklenebilir.
Anahtar yoksa betik yenisini oluşturur; farklı anahtarlı önceki kurulumu kaldırmanız gerekir.
Mağazada yayımlama için kendi üretim imzalama sürecinizi kullanın.

## Otomatik testler

Testler için ayrıca Chrome ve aşağıdaki Python bağımlılığı gerekir:

```powershell
py -3.12 -m pip install -r requirements-test.txt
py -3.12 test_movement_camera.py
node tests/gameplay.cjs
py -3.12 test_joystick_sequence.py
```

`test_movement_camera.py`: masaüstünde W/A/S/D, yön değişimi, fare ve dans sonrası yürüyüş.
`tests/gameplay.cjs`: analog yön/hız ve dizi/ritim kuralları.
`test_joystick_sequence.py`: 360° joystick, iki parmak, bırakma/iptal, arka plan,
yatay ok dizisi, yanlışta sıfırlama, ritimde tek puan ve Space kontrolü.
Tarayıcı testleri gerçek telefon veya Android emülatörü testi yerine geçmez.
`test_mobile.py`, `test_touch_acceptance.py`, `test_final_validation.py`, `test_regression.py` ve `test_phase1a.py` önceki sürümlerden
kalan tarihsel testlerdir; güncel şarkı seçim akışı için yukarıdaki testleri kullanın.

## Android emülatörü testi

Android Studio Device Manager'dan Android 16 / API 36 emülatörü oluşturup başlatın.
Test betiği `emulator-5554` seri numarasını kullanır; gerekirse betikteki `SERIAL` değerini değiştirin.
Emülatörde uçak modunu açın. Test için ayrı APK oluşturun:

```powershell
py -3.12 build_apk.py --debug
& "$env:ANDROID_SDK_ROOT\platform-tools\adb.exe" -s emulator-5554 install -r MEYDAN-test.apk
& "$env:ANDROID_SDK_ROOT\platform-tools\adb.exe" -s emulator-5554 shell cmd connectivity airplane-mode enable
py -3.12 test_joystick_sequence.py --android
```

Bu test, Chrome yerine emülatördeki uygulamanın Android WebView'ına bağlanır;
geri tuşu ve Home/uygulamaya dönüş için Android olaylarını kullanır.
Kontrollerin ayrıntılı ölçümü için yalnızca test APK'sında WebView hata ayıklama açılır.
Teslim APK'sı bu özelliği kapalı tutar; aynı Java ve oyun kaynaklarından üretilir.
Testten sonra `py -3.12 build_apk.py` ile normal APK'yı yeniden üretin.
Teslim APK'sını emülatörde kurup uygulama verisini temizleyen, uçak modunda
ilk açılışı ve gerçek Android geri tuşunu kontrol eden son test:

```powershell
py -3.12 test_release_android.py
```

Bu test yalnızca `emulator-5554` test emülatöründeki MEYDAN verilerini temizler.

## Çevrimdışı içerik

`dist/assets/Michelle.glb`, `dist/assets/Xbot.glb` ve `dist/beatmaps/meydan_demo.json`
HTML içine gömülür. Bu HTML APK'da `assets/MEYDAN.html` olarak bulunur.
Uygulamanın INTERNET izni yoktur; yerel HTTPS adresi WebView içinde APK varlığına
yönlendirilir. `test_package.py`, paket içindeki her model ve beatmap'i kaynaklarıyla karşılaştırır.

## Kaynak ZIP'ini yeniden üretme

```powershell
py -3.12 package_source.py
```

`MEYDAN-kaynak.zip` oluşturulur. Emülatör diskleri, derleme önbellekleri,
APK'lar ve diğer ZIP'ler kaynak arşivine alınmaz.

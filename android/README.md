# MEYDAN Android 1.1

Kurulum, tüm kaynaklardan APK üretimi, imzalama ve test adımları için
[yeniden derleme talimatına](../YENIDEN_DERLEME.md) bakın.

Sonuçlar [test raporunda](../TEST_RAPORU.md) bulunur. Emülatör ile gerçek
telefon sonuçları ayrı raporlanır.

Android kaynakları `src/`, manifest `AndroidManifest.xml`, ikon `res/`
altındadır. `../build_apk.py` Gradle indirmeden yüklü SDK araçlarını kullanır.
Normal APK'da WebView hata ayıklaması kapalıdır. `--debug` yalnızca test APK'sını üretir.

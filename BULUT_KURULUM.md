# MEYDAN — bilgisayar kapalıyken çalışma

## Hazır olanlar

- Özel depo: https://github.com/NoctiFlor/meydan
- Otomatik APK derleme: https://github.com/NoctiFlor/meydan/actions/workflows/android.yml
- İlk başarılı bulut derlemesi: https://github.com/NoctiFlor/meydan/actions/runs/40751788008
- İlk APK/HTML çıktısı: https://github.com/NoctiFlor/meydan/actions/runs/40751788008/artifacts/12843981843

Derleme, Windows bilgisayardan bağımsız olarak GitHub'ın Ubuntu 24.04 sunucusunda
Python 3.12 ve JDK 21 ile başarıyla çalıştı. İmza, paket hizalaması ve gömülü
model/beatmap kontrolleri geçti. İndirilen bulut APK'sının imzası mevcut yerel
APK ile aynı; dolayısıyla imza kaynaklı güncelleme engeli oluşmaz.
Bulut APK'sı ayrıca gerçek telefonda çalıştırılmış değildir.

## Telefondan APK alma

1. GitHub hesabınla özel depoyu aç.
2. **Actions → MEYDAN APK** bölümüne gir.
3. Son başarılı çalışmayı aç. **Artifacts → MEYDAN-…** çıktısını indir.
4. ZIP'i çıkarıp içindeki `MEYDAN.apk` dosyasını yükle.

Yeni APK için **Run workflow → main → Run workflow** seçilebilir.
`main` dalına kod değişikliği kaydedildiğinde derleme otomatik başlar.
Çıktılar 14 gün saklanır; süresi geçen çıktı yerine yeniden derleme başlatılabilir.
Ücretli hesap veya harcama ayarı değiştirilmedi; GitHub hesabının Actions kotası geçerlidir.

## Kod geliştirmeye devam etme

Tarayıcı editörü için depoda **Code → Codespaces** kullanılabilir; geliştirme
ayarları `.devcontainer/devcontainer.json` içindedir. Codespaces burada henüz
başlatılmadı. APK derlemesini Actions yapar.

Codex ile PC kapalıyken çalışmak için bu depoyu bir **Codex Cloud** ortamına ekle:
web veya masaüstünde **Work in → Cloud → Select environment → Create environment**,
GitHub deposu olarak `NoctiFlor/meydan` seç, kurulumu gözden geçir ve **Publish** yap.
Ardından mobilde Codex'i açıp yayımlanan ortamı seç.

**Codex Cloud ortamı bu işlemde oluşturulmadı.** Yerel sohbet, yerel dosyalar ve
çalışan süreçler kendiliğinden buluta taşınmaz. GitHub bağlantısı ve APK derlemesi
hazır; bulut ortamı oluşturma adımı ayrıca tamamlanmalıdır.

Resmî ortam rehberi: https://learn.chatgpt.com/docs/environments/cloud-environments

## İmzalama ve kaynaklar

Kullanıcının açık onayıyla mevcut geliştirme anahtarı yalnızca bu özel deponun
`MEYDAN_KEYSTORE_BASE64` Actions secret alanına aktarıldı. Anahtar Git geçmişinde
ve derleme çıktılarında bulunmaz. Derleme sonunda sunucudaki geçici anahtar silinir.
Kaynak deposu APK/HTML çıktıları, emülatör diskleri ve derleme önbelleklerini içermez.

# MEYDAN 1.3 — Eksiklik ve iyileştirme rehberi

Bu belge, MEYDAN 1.3 kaynaklarının mevcut durumuna göre hazırlanmış uygulama
rehberidir. Hedef; çalışan çevrimdışı çekirdeği bozmadan, oyunu Jadde'nin sosyal
meydan hissini çağrıştıran fakat kendi kimliği, içeriği ve kodu olan daha dolu bir
mobil sosyal ritim oyununa dönüştürmektir.

## 1. Mevcut durumun dürüst özeti

### Çalışan temel

- Android 8+ için çevrimdışı APK ve tek dosyalı HTML üretimi.
- 360 derece analog joystick, bağımsız ikinci parmak kamerası ve klavye/fare.
- Sıralı yön girişi, ayrı ritim onayı, Perfect/Great/Good/Miss, combo ve sonuç ekranı.
- Üç özgün sentez parça ve üç doğrulanan beatmap.
- Sürümlü yerel kayıt, migrasyon, bozuk kayıt yedeği, profil, XP, seviye ve skor.
- Sosyal NPC durumları, konuşma/dans daveti ve üç kısa çevre etkinliği.
- Çevrimdışı prototip para, katalog, satın alma ve kuşanma.
- Düşük/orta/yüksek kalite bütçeleri, kamera engel kontrolü ve tek zemin mesh'i.
- Tek komutluk çevrimdışı regresyon paketi: `python smoke_test.py`.

### Prototip seviyesinde kalanlar

- Meydan görsel olarak okunabilir ancak küçük, blok biçimli ve tekrar eden cephelere sahip.
- NPC'ler aynı temel karakter modelinin ölçek/animasyon farklarıdır; gerçek çeşitlilik azdır.
- Mağazadaki bazı kategoriler veri olarak vardır ancak yalnızca sahne halkası görünür biçimde uygulanır.
- Etkinlikler çoğunlukla sayaç ve ödüldür; oturma, fotoğraf pozu ve konuşma için tam animasyon/sahne yoktur.
- Dans geçişleri işlevsel olsa da giriş, hazır olma ve çıkış sinematiği yeterince güçlü değildir.
- Ana menü, yeni oyun/devam et ve profil düzenleme akışı tamamlanmamıştır.
- Kalite bütçeleri tanımlıdır; gerçek Xiaomi 13T Pro FPS/ısı/bellek ölçümü yapılmamıştır.
- Online modül socket kullanmaz ve canlı sunucu değildir.

## 2. Öncelik matrisi

| Öncelik | Alan | Neden | Çıkış ölçütü |
|---|---|---|---|
| P0 | Çökme, kayıt ve giriş regresyonları | Oyuncunun ilerlemesini kaybetmesi kabul edilemez | 30 dakikalık oturum, yeniden açma ve bozuk kayıt senaryosu hatasız |
| P0 | Gerçek cihaz performansı | Mobil oyunun temel riski | Xiaomi 13T Pro'da hedef kalite için kararlı kare süresi |
| P1 | Karakter/animasyon kalitesi | İlk bakışta prototip hissini en çok bu alan verir | 6+ görünür NPC silueti ve yumuşak geçişler |
| P1 | Meydanın büyütülmesi | Sosyal keşif döngüsü kısa | En az 5 okunabilir bölge ve 8–12 dakikalık keşif rotası |
| P1 | Etkinliklerin görselleştirilmesi | Sayaç tabanlı aktiviteler cansız kalıyor | Her etkinlikte özel poz/animasyon, kamera ve geri dönüş |
| P1 | Dans sunumu ve içerik | Oyunun ana tekrar döngüsü | 5 şarkı, zorluk ilerlemesi ve belirgin sahne sunumu |
| P2 | Menü, profil ve kozmetik | Kalıcılık ve hedef hissi | Yeni/devam et, avatar önizleme, çalışan tüm mağaza kategorileri |
| P2 | Erişilebilirlik ve kullanım kolaylığı | Telefon çeşitliliği | Yeniden boyutlandırılabilir kontroller, titreşim/ses seçenekleri |
| P3 | Canlı online | En pahalı ve en riskli katman | Önce özel 2–8 kişilik test odası; çevrimdışı mod bağımsız kalır |

## 3. P0 — Kararlılık ve ölçüm

### 3.1 Gerçek cihaz kabul paketi

Xiaomi 13T Pro üzerinde, düşük/orta/yüksek ayarın her biri için aşağıdaki değerler
aynı senaryoda kaydedilmelidir:

1. Temiz kurulumdan ana sahneye kadar süre.
2. İlk 60 saniye, meydanda 5 dakika yürüyüş ve bir tam dans boyunca ortalama FPS.
3. 1% düşük FPS veya kare süresi sıçramaları.
4. Yaklaşık bellek kullanımı, cihaz sıcaklığı ve 15 dakikalık pil tüketimi.
5. Joystick gecikmesi, ikinci parmak kamera sahipliği ve Android Home dönüşü.
6. 16:9, 20:9 ve tablet/DeX benzetiminde HUD taşması.

Başlangıç hedefleri:

- Orta kalite: 60 FPS hedef, yoğun anda 45 FPS altına sürekli düşmemeli.
- Düşük kalite: düşük cihazlarda 30 FPS alt sınırı korunmalı.
- Ana sahne açılışı: sıcak önbellekte 5 saniye altında hedeflenmeli.
- Dans girişinin ilk notası yükleme yüzünden kaçırılmamalı.

Bu değerler ölçülmeden “optimize edildi” veya “telefonlarda sorunsuz” denmemelidir.

### 3.2 Otomatik testleri genişletme

- `smoke_test.py` korunmalı ve her APK derlemesinden önce çalışmalıdır.
- Kayıt için elektrik kesilmesi benzetimi: yarım JSON, eski sürüm ve depolama hatası.
- 30 dakikalık deterministik NPC simülasyonu; dünya dışına çıkma ve kilitlenme kontrolü.
- Dans moduna art arda giriş/çıkış, Android geri, Home ve ses odağı kaybı.
- Kozmetik alımında iki kez tıklama, yetersiz bakiye ve sıfırlama senaryoları.
- Beatmap şema sürümü ve eksik dosyada güvenli geri dönüş.
- WebView konsolunda yakalanmamış hata varsa test başarısız olmalıdır.

## 4. P1 — Meydanı büyütme ve görsel kalite

### 4.1 Dünya düzeni

Mevcut küçük alan, birbirine bağlı beş bölgeye ayrılmalıdır:

1. **Merkez Meydan:** dans sahnesi, çeşme ve ilk karşılaşma noktası.
2. **Kafe Sokağı:** oturma, sohbet grupları, sipariş tezgâhı ve küçük iç mekân yanılsaması.
3. **Moda Pasajı:** mağaza vitrini, avatar deneme alanı ve fotoğraf köşesi.
4. **Sahil Yolu:** banklar, manzara noktası, gezinen NPC'ler ve gün batımı ışığı.
5. **Üst Teras/Club Liman:** merdiven/rampa ile erişilen ikinci kot, gece dans etkinliği.

Spawn noktasından çeşme ve sahne görünmelidir. Diğer bölgeler tabela, ışık rengi ve
yol döşemesiyle okunmalıdır. Kör sokaklar ödül, fotoğraf noktası veya kısa etkinlik
sunmuyorsa kaldırılmalıdır.

### 4.2 Teknik dünya yapısı

- `world.js` tek büyük sabit yerine bölge tanımlarını ayrı veri dosyalarından birleştirmelidir.
- Görsel mesh, çarpışma hacmi, aktivite noktası ve navigasyon verisi birbirinden ayrılmalıdır.
- Tekrarlanan lamba, bank, saksı ve pencere öğeleri `InstancedMesh` kullanmalıdır.
- Uzak binalar düşük ayrıntılı tek mesh veya atlas materyalle çizilmelidir.
- Statik çevrede baked/vertex light; gerçek zamanlı ışık yalnızca sahne ve yakın vurgu alanlarında kullanılmalıdır.
- Yeni bölge eklenmeden önce kalite başına draw-call, görünür NPC ve ışık bütçesi belirlenmelidir.
- Her bölgenin giriş/çıkış ve sıkışma noktaları için otomatik `blocked()` testleri eklenmelidir.

### 4.3 Görsel dil

- Mavi saat/gün batımı ana atmosferi korunmalı; sıcak vitrinler ve soğuk çevre kontrastı kullanılmalıdır.
- Altın vurgu yalnızca etkileşim, sahne ve seçili öğelerde kullanılmalıdır.
- Binalar aynı kutunun renk değiştirmiş hâli olmamalı; çatı çizgisi, vitrin genişliği ve tabela ritmi değişmelidir.
- Ekranın her yerinde neon kullanmak yerine sahne, club ve mağaza için ayrı ışık kimliği oluşturulmalıdır.
- Jadde'den model, doku, müzik, logo veya birebir harita alınmamalıdır.

## 5. P1 — Karakterler, NPC ve animasyon

### 5.1 Varlık kabul kuralları

Yeni model eklenmeden önce şu bilgiler `docs/ASSET_SOURCES.md` içine yazılmalıdır:

- Kaynak URL ve indirildiği tarih.
- Lisansın tam adı ve ticari kullanım/değiştirme koşulu.
- Modelin üçgen, materyal, texture ve kemik sayısı.
- Mobil test sonucu ve dosya boyutu.
- Oyunda hangi NPC/kozmetik için kullanıldığı.

Öncelik CC0 veya açıkça ticari kullanıma izin veren paketlerdir. Hugging Face'te
bulunan her model otomatik olarak güvenli değildir; model kartı, kaynak veri ve lisans
belirsizse pakete alınmamalıdır.

### 5.2 Karakter sistemi

- Tek model klonlamak yerine ortak humanoid rig kullanan 3 gövde ve 6 baş/saç varyantı hedeflenmelidir.
- Ten, saç ve kıyafet renkleri ayrı materyal kanalları olmalıdır.
- Model başına mobil hedef: mümkünse 10–20 bin üçgen, 1–2 materyal ve atlas texture.
- Yakındaki NPC tam rig; orta mesafedeki NPC seyrek animasyon; uzaktaki NPC sabit/çok düşük güncelleme kullanmalıdır.
- Görsel çeşitlilik deterministik profil kimliğinden üretilmeli, kayıtta yalnızca profil tohumu tutulmalıdır.

### 5.3 Animasyon durumu

Önerilen durumlar:

`idle_a`, `idle_b`, `walk`, `run`, `turn_left`, `turn_right`, `wave`, `clap`,
`sit_enter`, `sit_loop`, `sit_exit`, `photo_pose`, `dance_invite`, `dance_loop`.

- Yürüme/koşma hızı blend ile değişmeli; sert state geçişi azaltılmalıdır.
- Ayak kaymasını azaltmak için animasyon hızı gerçek hareket hızına bağlanmalıdır.
- Oturma ve fotoğraf, aktivite noktalarının yönüne hizalanmalıdır.
- NPC bakışı oyuncuyu sınırlı açı/hızla takip etmeli; boyun tam ters dönmemelidir.
- Animasyon olmasa dahi oyun mantığı tamamlanmalı; eksik clip yüzünden etkinlik kilitlenmemelidir.

## 6. P1 — Dansı ana oyun döngüsüne dönüştürme

### 6.1 Sunum akışı

Her dans şu açık durum makinesini kullanmalıdır:

`IDLE → APPROACH_STAGE → READY → COUNTDOWN → PLAYING → RESULTS → EXIT_STAGE → IDLE`

- Oyuncu sahne işaretine yürütülürken kontrol sahipliği görünür biçimde devredilmelidir.
- Kamera sahneyi çerçevelemeli fakat ikinci parmak/kamera girdisi yanlışlıkla nota üretmemelidir.
- Countdown sırasında beatmap, ses ve animasyon tamamen hazır olmalıdır.
- İptal, Android geri, ses odağı kaybı ve uygulama duraklatma her durumdan güvenli çıkmalıdır.

### 6.2 İçerik hedefi

- İlk içerik kilometre taşı: 5 özgün parça, parça başına en az 2 zorluk.
- Kolay mod öğretici; orta mod ana ilerleme; zor mod kozmetik/ünvan hedefi olmalıdır.
- Beatmap sürümü, şarkı süresi, BPM değişimleri, offset ve pattern listesi açık şemaya bağlanmalıdır.
- Şarkı önizlemesi gerçek chart ses motoruyla aynı tempo/ofset kaynağını kullanmalıdır.
- Sonuç ekranı XP, para, yeni rekor, açılan içerik ve tekrar/çıkış seçeneğini ayrı göstermelidir.

## 7. P2 — Menü, profil, ekonomi ve erişilebilirlik

### Ana menü

- **Devam et:** kayıt varsa son profil ve meydan.
- **Yeni oyun:** eski kaydı silmeden önce iki aşamalı onay.
- **Profil:** ad, görünüm, kuşanılan kozmetikler ve istatistikler.
- **Ayarlar:** kalite, ses/müzik, kamera hassasiyeti, titreşim ve kontrol boyutu.
- **Çevrimdışı oyna / Özel oda:** online hazır olduğunda bile çevrimdışı giriş birinci sınıf seçenek kalmalıdır.

### Ekonomi

- Tek para birimi kullanılmalı ve gerçek parayla ilişkilendirilmemelidir.
- Ödül kaynağı, miktarı ve günlük/tek seferlik niteliği veri dosyasında tutulmalıdır.
- Aynı dans/aktivite paketinin tekrar işlenmesini önleyen işlem kimliği eklenmelidir.
- Fiyatlar, oyuncunun 20–40 dakikada ilk görünür kozmetiği alabileceği şekilde test edilmelidir.
- Kıyafet, aksesuar ve emote yalnızca katalogda görünmekle kalmamalı; avatar önizlemesinde uygulanmalıdır.

### Erişilebilirlik

- Joystick ve ritim düğmesinin boyutu/konumu ayarlanabilmelidir.
- Solak düzeni eklenmelidir.
- Renk körlüğüne yalnızca renk değil biçim ve metinle geri bildirim verilmelidir.
- Titreşim ayrı ayrı: UI, nota ve hata için kapatılabilir olmalıdır.
- `prefers-reduced-motion` yanında oyun içi kamera sarsıntısı/ışık flaşı ayarı olmalıdır.
- Türkçe metinler taşma testinden geçmeli; ileride yerelleştirme için metinler koddan ayrılmalıdır.

## 8. Uygulama sırası

### Aşama A — Sertleştirme

- Gerçek cihaz ölçümü, uzun oturum testi, kayıt ve yaşam döngüsü regresyonları.
- Beatmap şeması ve tek komut CI kapısı.
- Çıkış: mevcut oyun güvenilir bir 1.3.1 sürümü olur.

### Aşama B — Görsel dikey dilim

- Merkez + kafe + üst terasın final kaliteye yakın bir bölümü.
- 3 farklı karakter görünümü, tam oturma/fotoğraf animasyonu ve 1 geliştirilmiş dans sunumu.
- Çıkış: bütün oyun için kalite çıtası ve performans maliyeti ölçülür.

### Aşama C — İçerik ve ilerleme

- Beş bölge, 5 şarkı, çalışan tüm kozmetik türleri, menü/profil ve görev benzeri kısa hedefler.
- Çıkış: çevrimdışı 30–60 dakikalık anlamlı tekrar döngüsü oluşur.

### Aşama D — Özel online test

- `ONLINE_GUIDE.md` aşamalarına göre 2 kişilik, sonra 8 kişilik davet kodlu oda.
- Çıkış: çevrimdışı oyun bozulmadan iki cihaz aynı meydanda hareket/emote/dans durumunu görür.

## 9. Her değişiklik için tamamlanma tanımı

- Özellik bağımsız HTML ve Android WebView'da çalışıyor.
- Mevcut `smoke_test.py` tamamen geçiyor.
- Yeni davranış için en az bir deterministik test var.
- Çevrimdışı mod, ağ yokken açılıyor ve kayıt yapıyor.
- Yeni varlığın lisansı ve performans maliyeti belgelenmiş.
- Fiziksel telefonda denenmeyen sonuç açıkça “doğrulanmadı” diye işaretlenmiş.
- Ekran görüntüsü yalnızca gerçekten test edilen sürümden alınmış.
- Başarısız/iptal/geri dönüş yolu, başarılı yol kadar test edilmiş.


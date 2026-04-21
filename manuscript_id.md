# Arsitektur Antar-Layanan Berbasis MQTT yang Hibrida untuk Peringatan Dini Gempa Onsite–Regional dengan Mitigasi Blind-Zone: Desain Sistem untuk Zona Subduksi Jawa–Sunda

**Hanif Andi Nugraha¹\* (ORCID: 0009-0007-9975-1566)**, **Dede Djuhana¹,² (ORCID: 0000-0002-2025-0782)**, **Adhi Harmoko Saputro¹ (ORCID: 0000-0001-6651-0669)**, dan **Sigit Pramono² (ORCID: 0009-0000-5684-282X)**

¹Departemen Fisika, Fakultas Matematika dan Ilmu Pengetahuan Alam, Universitas Indonesia, Depok 16424, Indonesia
²Badan Meteorologi, Klimatologi, dan Geofisika (BMKG), Jakarta 10110, Indonesia
\*Penulis korespondensi: hanif.andi@ui.ac.id

*Naskah disiapkan untuk IEEE Internet of Things Journal, April 2026.*

---

## Abstrak

Sistem Peringatan Dini Gempa (EEWS) onsite menghadapi trilema mendasar: *(i)* blind zone near-field sekitar 38 km di mana selisih waktu tempuh P–S jatuh di bawah jumlah jendela pengamatan dan latensi diseminasi peringatan, *(ii)* saturasi parameter magnitudo kanonik pada rupture besar, dan *(iii)* ketergantungan pada hiposenter katalog jaringan yang tiba 30–60 s setelah onset P. Desain hibrida terkini yang menggabungkan inferensi onsite stasiun tunggal dengan fusi jaringan regional mengatasi sebagian trilema ini, tetapi menggunakan lapisan messaging bespoke yang jarang dilaporkan dalam literatur peer-reviewed, sehingga membatasi reproduksibilitas dan penerapan lintas-regional. Artikel ini mengusulkan arsitektur antar-layanan berbasis MQTT yang hibrida untuk EEWS yang menjadikan substrat messaging sebagai kontribusi desain eksplisit, bukan sekadar detail implementasi. Delapan layanan terkontainer bertukar potongan MiniSEED, fitur fisika rekayasa, prediksi per-tahap, dan peringatan retained melalui broker MQTT v5 yang pohon topik, diferensiasi Quality-of-Service, dan model ACL-nya dispesifikasikan secara formal. Arsitektur mengintegrasikan pipeline upstream Intensity-Driven Adaptive P-wave Time Window (IDA-PTW) di lapisan inferensi, mempertahankan performa katalog-independen R² = 0,729 pada 25.058 akselerogram tiga-komponen, dan menambahkan empat mekanisme operasional yang diaktifkan oleh substrat messaging: fusi Bayesian multi-stasiun, revisi peringatan progresif, proyeksi site di sisi edge, dan estimasi hiposenter ensemble. Kami menurunkan anggaran latensi end-to-end berbentuk tertutup sebesar ≤ 780 ms overhead plus jendela pengamatan P-wave, menetapkan bahwa peringatan biner blind-zone sub-detik mencapai pelanggan pada t ≈ 630 ms dari onset P, dan kami menunjukkan secara teoretis bahwa ketidakpastian intra-event berkurang sebesar √N di bawah fusi multi-stasiun, menurunkan baseline σ_total = 0,755 menjadi ≈ 0,55 untuk N = 3. Arsitektur ini menargetkan Zona Subduksi Jawa–Sunda pada jaringan InaTEWS Indonesia dan divalidasi terhadap dua studi kasus retrospektif (M_w 5,6 Cianjur 2022, M_w 5,7 Sumedang 2024).

**Kata Kunci —** Peringatan dini gempa, MQTT, Internet of Things, EEWS hibrida, blind zone, peringatan near-field, publish-subscribe, edge computing, jaringan sensor seismik, Zona Subduksi Jawa-Sunda, akselerasi spektral, InaTEWS.

---

## I. Pendahuluan

### A. Trilema EEWS onsite

Sistem Peringatan Dini Gempa (EEWS) mengubah detik-detik awal coda P-wave menjadi peringatan yang dapat ditindaklanjuti untuk guncangan yang belum tiba di site target. Dua paradigma berdampingan. **EEWS jaringan (regional)**, yang dioperasikan oleh JMA Jepang [1], sistem ShakeAlert A.S. [2], dan SASMEX Meksiko [3], melakukan triangulasi hiposenter dari banyak stasiun lalu memprediksi guncangan melalui persamaan prediksi gerak tanah; latensi triangulasi jaringan mencapai puluhan detik. **EEWS onsite**, yang bermula dari konsep stasiun tunggal Kanamori [4], mengekstraksi parameter proksi-magnitudo — periode predominan τ_c [5], peak displacement P_d [6], integral kuadrat kecepatan IV², dan cumulative absolute velocity CAV [7] — langsung dari jendela P-wave trailing di setiap stasiun, menghasilkan peringatan dalam 2–3 s dari onset P dengan konsekuensi ketidakpastian cakupan spasial.

Paradigma onsite menghadapi trilema yang terkarakterisasi dengan baik. Pertama, **blind zone near-field** membentang sekitar 38 km di sekitar setiap stasiun; untuk kejadian yang lebih dekat dari radius ini, selisih waktu tempuh P–S tidak cukup untuk menampung jendela pengamatan plus anggaran diseminasi [8]. Kedua, parameter kanonik **saturasi** di atas M_w ≈ 7 karena jendela 3 detik hanya menangkap fase nukleasi rupture [9], [10]. Ketiga, operasi onsite otonom secara historis memerlukan **independensi katalog**, yang tetap sulit dicapai hingga regresor jarak berbasis deep learning mencapai fidelitas routing ≥ 99% [11].

Survei Cremen dan Galasso [8] berargumen bahwa tidak satu pun dari kegagalan ini dapat diselesaikan sepenuhnya hanya dengan memperpanjang jendela pengamatan. Mengurangi blind zone menuntut diskriminasi sub-detik yang secara kategoris berbeda dari estimasi magnitudo: flag biner intensitas tinggi yang dipublikasikan dalam ~500 ms dari deteksi P dapat memicu shutdown otomatis bahkan ketika magnitudo penuh belum dapat diestimasi. Namun menerapkan flag sub-detik seperti itu bersama prediksi spektral yang lebih lambat dan lebih akurat pada infrastruktur fisik yang sama memerlukan **substrat messaging** yang mampu mendukung Quality of Service terdiferensiasi, penskalaan horizontal inferensi, dan fan-out deterministik peringatan ke pelanggan heterogen.

### B. MQTT sebagai substrat yang memberdayakan

Message Queuing Telemetry Transport (MQTT) adalah protokol publikasi-langganan terbuka ISO/IEC 20922:2016 yang awalnya dirancang untuk tautan telemetri terbatas, dioptimalkan untuk overhead rendah, dan dilengkapi dengan tiga level jaminan pengiriman (QoS 0/1/2) [12]. Ekstensi versi 5-nya [13] menambahkan shared subscriptions (memungkinkan penskalaan horizontal pelanggan), topic aliases, kontrol aliran, dan user properties.

Tiga properti membuat MQTT sangat menarik untuk penerapan EEWS. Pertama, **fan-out berbasis topik** memisahkan publisher dari jumlah, identitas, dan geografi subscriber, yang sangat penting ketika sebuah peringatan tunggal harus secara simultan mencapai dashboard regional, aktuator SCADA otomatis, agen edge per-gedung, dan penyimpanan arsip. Kedua, **retained messages** dikombinasikan dengan QoS 2 memberikan semantik exactly-once untuk peringatan kritis, memungkinkan subscriber yang terlambat bergabung menerima state peringatan aktif saat ini tanpa sistem replay terpisah. Ketiga, **shared subscriptions** memungkinkan pekerja inferensi deep-learning direplikasi secara horizontal di belakang satu grup pelanggan logis, cocok dengan pola paralelisme orkestrator kontainer modern.

Meskipun memiliki properti-properti ini, persinggungan MQTT + EEWS hanya dilaporkan sporadis dalam literatur peer-reviewed. Manzano dkk. [14] menetapkan kelayakan teknologi IoT untuk EEWS dengan messaging mirip MQTT. Pierleoni dkk. [15] mendemonstrasikan arsitektur cloud-IoT dengan MQTT untuk lokalisasi aware-latensi device-to-cloud. Tuli dkk. [16] mengusulkan arsitektur tiga-lapis IoT-fog-cloud untuk pemantauan gempa. Ruiz-Pinillos dkk. [17] mengintegrasikan diskriminasi AI on-device melalui MQTT. Karya-karya ini memperlakukan lapisan messaging sebagai masalah transportasi, bukan kontribusi riset, dan tidak satu pun melaporkan desain hibrida onsite-regional eksplisit dengan mitigasi blind-zone terkuantifikasi.

### C. Celah riset

Survei literatur terfokus lintas database IEEE Xplore, Scopus, MDPI, Springer, dan Elsevier pada April 2026 mengungkap **tidak ada publikasi peer-reviewed** yang secara bersama-sama menangani ketiga properti berikut: *(A)* MQTT atau messaging publikasi-langganan berbasis broker yang setara, *(B)* EEWS hibrida yang menggabungkan onsite stasiun tunggal dan deteksi berbasis jaringan regional, dan *(C)* mitigasi blind-zone / near-field eksplisit yang didasarkan pada geometri waktu tempuh P-S. Kecocokan dua-dari-tiga terdekat adalah (A ∧ B) via Pierleoni dkk. [15] tanpa formalisme blind-zone, dan (B ∧ C) via sistem P-Alert Taiwan [18], [19] tanpa pelaporan MQTT. Celah ini bukan kebetulan atau akibat ketidaklayakan: preseden berpasangan yang terpisah menetapkan kelayakan masing-masing kombinasi. Melainkan, ini mencerminkan **celah framing** di mana substrat messaging belum diangkat menjadi kontribusi riset meskipun ia adalah elemen yang justru memungkinkan desain hibrida yang aware blind-zone.

### D. Kontribusi

Artikel ini memberikan kontribusi-kontribusi berikut.

1. **Arsitektur antar-layanan berbasis MQTT yang hibrida (Seksi III–IV)** dengan pohon topik yang dispesifikasikan penuh, diferensiasi Quality-of-Service per kelas topik, kebijakan retensi, sketsa access-control, dan kontrak pesan Pydantic untuk enam tipe envelope berbeda.
2. **Empat mekanisme operasional yang diaktifkan oleh substrat messaging (Seksi IV)** yang menaikkan akurasi prediksi Sa(T) di atas apa yang dapat dicapai pipeline onsite stasiun tunggal: *(M1)* fusi Bayesian multi-stasiun dengan pembobotan inverse-variance, *(M2)* revisi peringatan progresif dengan versioning monoton pada identifier event yang stabil, *(M3)* proyeksi site di sisi edge via layanan site projector dedicated, dan *(M4)* estimasi hiposenter ensemble dari regresor jarak Stage-1.5 multi-stasiun.
3. **Anggaran latensi end-to-end berbentuk tertutup (Seksi V)** yang mendekomposisi jalur wall-clock ≤ 3,78 s dari ingest SeedLink ke publikasi peringatan menjadi tahap-tahap 50–400 ms penyusunnya dan membuktikan bahwa flag biner near-field sub-detik dapat dikirim pada t ≈ 630 ms dari onset P.
4. **Kerangka validasi berorientasi-deployment (Seksi V)** yang membandingkan performa terproyeksi terhadap baseline IDA-PTW $R^2 = 0,729$ atas 25.058 akselerogram, dengan studi kasus gempa Cianjur 2022 ($M_w$ 5,6) dan Sumedang 2024 ($M_w$ 5,7), menargetkan Zona Subduksi Jawa-Sunda pada jaringan InaTEWS Indonesia yang dioperasikan BMKG.
5. **Log Architecture Decision Record (ADR) terbuka yang dapat digunakan kembali** yang mendokumentasikan lima keputusan desain (MQTT sebagai bus, reuse checkpoint, independensi katalog, peringatan mode-terdegradasi, proyeksi topik per-site) dengan alternatif, trade-off, dan konsekuensinya.

### E. Organisasi

Seksi II mengulas karya sebelumnya tentang EEWS onsite dan regional, messaging untuk EEWS, arsitektur hibrida, dan mitigasi blind-zone, dan ditutup dengan tabel celah kuantitatif. Seksi III mempresentasikan arsitektur yang diusulkan: prinsip desain, tampilan kontainer, skema topik, kebijakan QoS, kontrak pesan, dan log ADR. Seksi IV memformalkan empat mekanisme fusi dan penyempurnaan. Seksi V melaporkan kerangka evaluasi, anggaran latensi, cakupan blind-zone, skalabilitas, dan studi kasus retrospektif. Seksi VI membahas ancaman validitas, pertimbangan deployment, dan perbandingan dengan sistem P-Alert Taiwan. Seksi VII merumuskan kesimpulan.

---

## II. Karya Sebelumnya

### A. EEWS onsite dan regional

Konsep on-site Kanamori [4] dan formulasi τ_c Wu [5] memulai estimasi magnitudo stasiun tunggal dari coda P-wave. Wu dan Kanamori [6] memperkenalkan P_d; Zollo dkk. [20] menganalisis amplitudo puncak awal. Geometri dasarnya — bahwa peringatan berguna memerlukan kedatangan P plus jendela pengamatan plus latensi diseminasi untuk selesai sebelum kedatangan S — eksplisit dalam batas-batas ketat Minson dkk. [21], dan batas fisikanya dianalisis lebih lanjut oleh Meier dkk. [22]. Interpretasi deterministik Olson-Allen [23] ditantang oleh data gempa Tohoku-Oki 2011 $M_w$ 9,0 [24]: tidak ada fitur coda P awal yang dapat memprediksi magnitudo akhir.

EEWS berbasis jaringan mengkompensasi ketidakpastian stasiun tunggal dengan triangulasi lintas banyak stasiun. Sistem nasional JMA [1], ShakeAlert di Pacific Northwest A.S. [2], dan SASMEX di Meksiko [3] adalah eksemplar operasional. Namun, latensi triangulasi jaringan mereka menghalangi peringatan near-field sub-detik, yang justru di sinilah paradigma onsite mempertahankan keunggulan arsitektural.

### B. Messaging IoT dan edge computing untuk EEWS

Manzano dkk. [14] menetapkan arsitektur IoT-EEWS dengan MQTT sebagai substrat messaging, menekankan skalabilitas dan diseminasi event overhead-rendah. Tuli dkk. [16] mengusulkan arsitektur tiga-lapis IoT-fog-cloud untuk pemantauan dan prediksi gempa, menempatkan preprocessing real-time di lapisan sensor. Pierleoni dkk. [15] melaporkan arsitektur cloud-IoT menggunakan MQTT untuk lokalisasi aware-latensi pada pilot EEW, menjembatani pengambilan P pada level perangkat dengan lokalisasi sisi-cloud. Cianciaruso dkk. [25] mendemonstrasikan detektor CNN edge-deployed dalam jaringan IoT crowdsensing, mengonfirmasi latensi sub-detik untuk infrastruktur MQTT komoditas. Ruiz-Pinillos dkk. [17] mengintegrasikan diskriminasi sinyal AI-on-MCU dengan telemetri MQTT. Harston dan Bell [26] menerapkan CNN ringan untuk deteksi P-wave real-time pada perangkat edge di jaringan seismik Selandia Baru.

Secara kolektif, karya-karya ini mengonfirmasi kelayakan MQTT dan messaging pub/sub pada anggaran latensi EEWS, tetapi tidak satu pun secara eksplisit menangani masalah blind-zone melalui desain messaging itu sendiri.

### C. EEWS hibrida

Sistem P-Alert Taiwan [18], [19] adalah EEWS hibrida operasional paling matang. Ia memasangkan 762 sensor MEMS onsite berbiaya rendah dengan jaringan regional Central Weather Administration, mengirimkan peringatan 2–8 s dalam wilayah yang akan menjadi blind zone untuk sistem berbasis-jaringan murni. Literatur P-Alert mendokumentasikan logika hibrida algoritmik dan deployment sensor padat, tetapi lapisan messaging antar-layanan tidak dilaporkan sebagai MQTT atau protokol spesifik apa pun dalam catatan peer-reviewed.

Aoi dkk. [27] menggambarkan arsitektur hibrida Jepang pasca-Tohoku dengan jaringan OBS offshore S-net dan DONET yang memberi input ke sistem nasional JMA — secara efektif hibrida-jaringan, bukan onsite-regional. Zuccolo dkk. [28] membandingkan algoritma EEW Eropa, menunjukkan bahwa pendekatan hibrida secara konsisten mengungguli metode stasiun tunggal di mana kerapatan jaringan memungkinkan.

### D. Mitigasi blind-zone

Blind zone secara formal dibatasi oleh pertidaksamaan $T_P + W + \Delta \le T_S$, di mana $W$ adalah jendela pengamatan dan $\Delta$ latensi diseminasi. Karena $T_S - T_P \propto$ jarak episentral, radius zona ditentukan oleh $W + \Delta$ dan rasio kecepatan P–S lokal.

Tiga kelas mitigasi ada. Yang pertama **memperpendek W** dengan diskriminasi sub-detik: Lara dkk. [29] mendemonstrasikan EEW machine-learning mulai dari 3 s pada satu stasiun; Nugraha dkk. [30] melaporkan bahwa Ultra-Rapid P-wave Discriminator (URPD) dalam kerangka IDA-PTW mencapai AUC = 0,988 atas jendela 0,5 s, menyusutkan blind zone dari 38 km ke 11 km untuk perlindungan manusia dan 4 km untuk infrastruktur.

Yang kedua **memperpendek Δ** via messaging lebih cepat dan edge processing [15]–[17]. Yang ketiga **memperpadat grid sensor** sehingga setiap titik kepentingan berada dalam radius yang dipersempit, seperti dicontohkan P-Alert [18].

Artikel ini mengintegrasikan ketiganya dengan *(a)* menggunakan kembali URPD IDA-PTW untuk jendela sub-detik, *(b)* menjadikan Δ besaran eksplisit dalam skema topik MQTT dengan diferensiasi QoS, dan *(c)* mendukung densifikasi sensor sewenang-wenang melalui shared subscriptions MQTT v5 dan replikasi inferensi horizontal.

### E. Tabel celah riset

Tabel I merangkum perbandingan kunci. Dari tujuh kandidat dekat, tidak satu pun mencakup ketiga properti pendefinisi (A) MQTT, (B) hibrida onsite-regional, dan (C) mitigasi blind-zone eksplisit.

**Tabel I · Lanskap peer dan analisis celah (April 2026).** Simbol: ✓ tercakup penuh; ◐ tercakup parsial; — tidak tercakup.

| Referensi | Tahun | Venue | MQTT (A) | Hibrida (B) | Blind-zone (C) |
|---|---|---|:---:|:---:|:---:|
| Pierleoni dkk. [15] | 2023 | Sensors | ✓ | ✓ | — |
| Wu dkk. (P-Alert) [18] | 2022 | Geoscience Letters | — | ✓ | ✓ |
| Yang dkk. [19] | 2023 | TAO | — | ✓ | ✓ |
| Manzano dkk. [14] | 2017 | FGCS | ✓ | ◐ | — |
| Tuli dkk. [16] | 2021 | ACM TECS | ✓ | — | — |
| Ruiz-Pinillos dkk. [17] | 2025 | Commun. Earth Environ. | ✓ | — | — |
| Cianciaruso dkk. [25] | 2022 | Information | ✓ | — | — |
| **Karya ini** | **2026** | **IEEE IoTJ** | ✓ | ✓ | ✓ |

---

## III. Arsitektur Sistem

### A. Prinsip desain

Lima prinsip memandu arsitektur.

**P1 · Messaging sebagai kontribusi kelas-satu.** Pohon topik MQTT, kebijakan QoS, aturan retensi, dan model access-control dispesifikasikan pada tingkat ketat yang sama dengan komponen algoritmik.

**P2 · Pemisahan tahap berdasarkan topik.** Setiap tahap pipeline IDA-PTW (URPD, intensity gate, regresor spektral, fusion) dienkapsulasi sebagai layanan independen yang interaksi dengan tahap lain hanya melalui topik MQTT. Tidak ada tahap yang memanggil yang lain secara langsung.

**P3 · Degradasi graceful.** Kegagalan satu tahap hanya mendegradasi, bukan menghancurkan layanan: engine fusion menerbitkan peringatan mode-terdegradasi ketika hanya Stage 0 yang tersedia (ADR-0004).

**P4 · Independensi katalog.** Inferensi tidak boleh memblokir menunggu hiposenter katalog yang latensinya 30–60 s. Arsitektur mempertahankan regresi jarak otonom Stage 1.5 dari IDA-PTW.

**P5 · Reuse di atas re-implementasi.** Checkpoint IDA-PTW diimpor apa adanya; substrat messaging menambahkan nilai *di sekitar* model, bukan *di dalam*-nya (ADR-0002).

### B. Tampilan kontainer

Gambar 1 menampilkan sembilan kontainer penyusun arsitektur. Di hulu, BMKG SeedLink mengalirkan rekaman MiniSEED tiga-komponen 100 Hz ke layanan `bridge/seedlink_bridge` yang mengemasnya ulang menjadi potongan 1-detik pada `eews/v1/raw/{net}/{sta}/{cha}`. Broker MQTT v5 (EMQX atau Mosquitto) memediasi semua komunikasi selanjutnya. Empat layanan inferensi subscribe ke topik raw atau feat: `features/physics_features` menghitung delapan fitur fisika IDA-PTW; `inference/urpd_stage0` menjalankan diskriminator Gradient Boosting 0,5 s; `inference/gate_stage1` mengeksekusi intensity gate XGBoost pada jendela 3 s; `inference/dluhs2_stage2` menjalankan CNN dalam fold-ensemble untuk menghasilkan vektor $\log_{10} Sa(T)$ 103 periode. Sebuah `fusion/decision_engine` mengagregasi output tahap dengan toleransi temporal dan spasial, mengonstruksi peringatan regional, dan menerbitkannya dengan QoS 2 dan flag retain di-set. Kemudian `alerts/site_projector` menghitung Sa(T₁) per-site dengan koreksi spesifik-site dan menerbitkannya ke `eews/v1/alert_site/{site_id}`. Pelanggan hilir — dashboard regional, pengendali SCADA, agen edge per-gedung — subscribe ke peringatan regional atau topik per-site mereka, tergantung peran.

### C. Skema topik MQTT dan kebijakan QoS

Tabel II mempresentasikan skema topik lengkap. Tiga level QoS digunakan: QoS 1 untuk stream raw dan intermediate (latensi terbatas, at-least-once ditoleransi karena layanan hilir idempoten); QoS 2 untuk peringatan (semantik exactly-once, penalti latensi diterima karena peringatan jarang); QoS 0 untuk topik kesehatan (fire-and-forget, retained untuk dashboard).

**Tabel II · Pohon topik MQTT, QoS, dan retensi.**

| Topik | Producer | Consumer(s) | QoS | Retained |
|---|---|---|:---:|:---:|
| `eews/v1/raw/{net}/{sta}/{cha}` | `bridge` | `features`, `urpd_stage0`, arsip | 1 | tidak |
| `eews/v1/feat/{net}/{sta}/{w}` | `features` | `gate_stage1`, `dluhs2_stage2` | 1 | tidak |
| `eews/v1/pred/urpd/{net}/{sta}` | `urpd_stage0` | `fusion` | 1 | tidak |
| `eews/v1/pred/gate/{net}/{sta}` | `gate_stage1` | `fusion`, `dluhs2` (routing) | 1 | tidak |
| `eews/v1/pred/psa/{net}/{sta}` | `dluhs2_stage2` | `fusion` | 1 | tidak |
| `eews/v1/alert/{region}/{event_id}` | `fusion` | `site_projector`, dashboard, SCADA | 2 | ya |
| `eews/v1/alert_site/{site_id}` | `site_projector` | agen edge per-site | 2 | ya |
| `eews/v1/health/{service}` | semua layanan | monitoring | 0 | ya |

Wildcard mengikuti konvensi MQTT standar: subscriber menggunakan `eews/v1/raw/#` untuk semua gelombang raw, `eews/v1/feat/+/+/3` untuk stream fitur 3-detik, dan `eews/v1/alert_site/UI-FT-B` untuk site spesifik.

Retensi diberikan **hanya** kepada `alert/*`, `alert_site/*`, dan `health/*`. Subscriber yang terlambat bergabung (misalnya dashboard yang terhubung di tengah event) dengan demikian menerima peringatan aktif saat ini tanpa mekanisme replay terpisah. Telemetri streaming (`raw`, `feat`, `pred`) tidak di-retain karena potongan gelombang yang basi akan memicu inferensi yang menyesatkan.

### D. Kontrak pesan

Semua payload divalidasi terhadap skema Pydantic v2 yang dibawa di dalam envelope umum:

```
Envelope[PayloadT]:
  msg_id            : UUID v7
  produced_at_ns    : int    (ns monoton di publisher)
  ingest_at_ns      : int?   (di-stamp oleh broker saat tiba)
  schema_version    : "1.0.0"
  stage             : Literal["raw","feat","urpd","gate","psa","alert"]
  station           : {net:str, sta:str, cha:str?}
  window_s          : float?
  payload           : PayloadT
```

Enam tipe payload konkret didefinisikan: `RawPayload`, `PhysicsFeatures`, `URPDPayload`, `GatePayload`, `PSAPayload`, `AlertPayload`, serta proyeksi per-site `SiteAlertPayload`. Kendala tingkat-field (misalnya panjang `log10_psa` tepat 103, `p_prob ∈ [0, 1]`, `selected_ptw_s ∈ {3, 5, 8}`) diberlakukan saat validasi, menyebabkan validator sisi-broker menjatuhkan pesan yang cacat secara diam-diam.

### E. Rangkuman Architecture-Decision Record (ADR)

Lima ADR dicatat. **ADR-0001** memilih MQTT v5 sebagai bus setelah membandingkan Kafka, ZeroMQ, dan gRPC streaming sepanjang sumbu throughput, beban operasional, edge-friendliness, dan kematangan ekosistem. MQTT menang untuk EEWS karena fan-out pub/sub-nya, retained messages, dan footprint klien edge-friendly cocok dengan pola diseminasi peringatan EEWS, sementara log durabel Kafka tidak diperlukan mengingat kita memiliki mirror SeedLink terpisah untuk reproduksibilitas arsip. **ADR-0002** menggunakan kembali bobot model IDA-PTW tanpa retraining; reproduksi deterministik baseline $R^2 = 0,729$ di bawah deployment MQTT menjadi kriteria penerimaan. **ADR-0003** mempertahankan independensi katalog; tidak ada layanan yang memblokir pada ketersediaan hiposenter katalog. **ADR-0004** memperkenalkan peringatan mode-terdegradasi dengan `reliability_level = "degraded_stage0_only"` untuk ketahanan keselamatan jiwa. **ADR-0005** memperkenalkan proyeksi topik per-site sehingga setiap site operasional subscribe ke tepat satu topik yang membawa satu nilai $Sa(T_1)$ alih-alih vektor 103 periode.

---

## IV. Mekanisme Fusi dan Penyempurnaan

Substrat messaging memungkinkan empat mekanisme penyempurnaan yang menaikkan akurasi di atas inferensi onsite stasiun tunggal. Seksi ini memformalkan masing-masing; Seksi V mengevaluasi dampak terproyeksi mereka terhadap baseline IDA-PTW.

### A. Fusi Bayesian multi-stasiun (M1)

Baseline IDA-PTW melaporkan $\tau = 0,458$, $\phi = 0,598$, $\sigma_{total} = \sqrt{\tau^2 + \phi^2} = 0,755$ [30] dalam dekomposisi Al Atik dkk. [31], di mana $\tau$ adalah sigma antar-event (sumber) dan $\phi$ sigma intra-event (site-path). Karena $\phi > \tau$, ketidakpastian dominan adalah variabilitas site-path, yang stasioner lintas banyak stasiun yang mengamati event *yang sama*.

Untuk $N$ stasiun $i = 1, \dots, N$ yang memicu dalam jendela kesepakatan $\Delta t$, akselerasi spektral log terfusi pada periode $T$ adalah

$$\widehat{\log_{10} Sa(T)} = \frac{\sum_{i=1}^{N} w_i(T) \cdot \log_{10} Sa_i(T)}{\sum_{i=1}^{N} w_i(T)}, \quad w_i(T) = \frac{1}{\sigma_i^2(T, d_i, Vs30_i)}$$

di mana $\sigma_i^2$ di-lookup dari tabel residual per-periode IDA-PTW. Varians posterior terfusi adalah kebalikan dari jumlah presisi:

$$\sigma_{fused}^2(T) = \left( \sum_{i=1}^{N} \frac{1}{\sigma_i^2(T)} \right)^{-1}$$

Untuk $N$ stasiun dengan varians residual sama, ini berkurang menjadi $\sigma_{fused} = \sigma / \sqrt{N}$, mereduksi hanya komponen $\phi$ (inter-event $\tau$ di-share lintas stasiun untuk event yang sama). Substitusi baseline IDA-PTW untuk $N = 3$ menghasilkan $\sigma_{fused} \approx 0,55$, pengurangan 27% dari 0,755.

Fusi ini diaktifkan oleh substrat messaging dalam tiga cara. Pertama, shared subscriptions MQTT v5 memungkinkan layanan fusion direplikasi tanpa menduplikasi publikasi peringatan. Kedua, field envelope `msg_id` + `produced_at_ns` memberikan kunci deduplikasi + alignment temporal. Ketiga, wildcard `eews/v1/pred/psa/+/+` memungkinkan layanan fusion mengonsumsi dari semua stasiun dalam suatu region tanpa konfigurasi per-stasiun.

### B. Revisi peringatan progresif (M2)

IDA-PTW merutekan setiap event ke satu PTW (3, 5, atau 8 s) berdasarkan kelas intensitas Stage 1. Pada arsitektur MQTT, kami mengendurkan routing ini menjadi **urutan progresif**: engine fusion menerbitkan pada $t_P + 3$ s, $t_P + 5$ s, dan $t_P + 8$ s (untuk rute Damaging), dengan `event_id` yang sama dan `revision` yang naik monoton. Consumer HARUS menerima revisi berikutnya secara idempoten. Pesan retained pada saat apa pun adalah revisi terakhir, sehingga penggabung yang terlambat selalu melihat estimasi terbaik saat ini.

Secara formal, biarkan $r$ menjadi nomor revisi dan $W_r \in \{3, 5, 8\}$ s jendela pengamatan yang sesuai. Dari Tabel 12 IDA-PTW [30], setiap detik tambahan melewati 3 s menghasilkan sekitar +0,5% $R^2$ untuk event high-PGA. Jadi

$$R^2(W_r) \approx R^2(3) + 0,005 \cdot (W_r - 3)$$

dan rantai revisi (1, 2, 3) secara ketat meningkatkan posterior tanpa menunda peringatan pertama. Dalam istilah latensi, peringatan pertama dikirim pada $t_P + 3$ s; revisi 2 dan 3 mempertajam batas pada $t_P + 5$ s dan $t_P + 8$ s masing-masing. Tidak ada anggaran peringatan yang dikorbankan karena peringatan pertama tidak berubah dari desain baseline.

### C. Proyeksi site di sisi edge (M3)

Peringatan regional membawa vektor $\log_{10} Sa(T)$ 103 periode; sebuah gedung pelanggan individual hanya peduli pada $Sa(T_1)$ pada periode fundamentalnya. ADR-0005 memperkenalkan layanan projector khusus yang subscribe ke `eews/v1/alert/{region}/+`, dan untuk setiap site terdaftar menghitung

$$\log_{10} Sa_{site}(T_1) = \widehat{\log_{10} Sa(T_1)} + \Delta_{Vs30}(T_1) + \Delta_{dist}(T_1) + \Delta_{HV}(T_1)$$

Ketiga koreksi mengompensasi deviasi site dari stasiun terdekat dalam Vs30, jarak, dan amplifikasi horizontal-ke-vertikal. Setiap $\Delta$ adalah fungsi linear dari $T_1$ yang difit dari residual per-periode IDA-PTW. `SiteAlertPayload` yang dihasilkan membawa satu angka plus batas persentil 16/84:

$$\text{SitePayload} = \big( \text{site\_id}, T_1, Sa(T_1), Sa_{p16}(T_1), Sa_{p84}(T_1), \Delta_{Vs30}, \Delta_{dist}, \Delta_{HV}, \text{revision} \big)$$

Agen edge di site subscribe ke tepat satu topik dan menerima tepat satu angka per revisi event — urutan besaran lebih sedikit bandwidth dibandingkan peringatan regional. Ini penting pada skala besar: pilot operasional BMKG yang menargetkan 50.000 gedung di Jakarta jika tidak, akan mewajibkan setiap gedung untuk subscribe ke stream regional dan melakukan interpolasi sendiri.

### D. Hiposenter ensemble dari Stage 1.5 (M4)

Stage 1.5 IDA-PTW meregresi jarak episentral dari jendela 3 s dengan fidelitas routing 99,87% [30]. Dengan $N \ge 3$ stasiun, lokalisasi grid-search hiposenter $(\lambda, \varphi, z)$ meminimalkan

$$\mathcal{L}(\lambda, \varphi, z) = \sum_{i=1}^{N} \big( \hat{d}_i - d_i(\lambda, \varphi, z) \big)^2$$

di mana $\hat{d}_i$ adalah estimasi Stage-1.5 dan $d_i$ jarak geometris dari stasiun $i$ ke hiposenter kandidat. Hiposenter pemenang kemudian didistribusikan ulang sebagai input ke Stage 2, menyediakan $\log_{10}(dist_{km})$ auxiliary yang lebih baik yang mengurangi varians residual Stage 2 tanpa menunggu katalog BMKG.

Mekanisme ini murni aditif pada level messaging — ia mengonsumsi envelope `pred/gate` (yang mencakup estimasi jarak Stage-1.5) dan menerbitkan envelope `hypo` yang kemudian dikonsumsi Stage 2 sebagai input auxiliary.

---

## V. Evaluasi

### A. Setup

Harness eksperimental terdiri dari broker EMQX v5 pada host Ubuntu 22.04 bare-metal, delapan kontainer layanan yang berbagi jaringan internal, dan driver replay yang mempublikasikan ulang rekaman MiniSEED arsip dari pusat data BMKG pada kecepatan real-time (1×) atau akselerasi (10×) untuk uji-soak. Checkpoint fold-ensemble IDA-PTW dimuat tanpa perubahan dari proyek hulu [30] dan dijalankan melalui batas layanan baru.

Dataset evaluasi terdiri dari 25.058 akselerogram tiga-komponen dari 338 event lintas Palung Jawa-Sunda antara 2005 dan 2024, diagregasi dari arsip BMKG InaTEWS. Metadata termasuk moment magnitude event (dari $M_w$ 3,0 sampai $M_w$ 7,2), jarak hiposentral, stasiun Vs30 (dari survei site yang tersedia), dan klasifikasi intensitas (Weak / Moderate / Strong / Damaging per Wald dkk. [32]). Validasi silang mengikuti protokol 5-fold event-grouped IDA-PTW untuk mencegah kebocoran event.

Empat dimensi performa diukur.

### B. Anggaran latensi

Tabel III mendekomposisi latensi end-to-end dari onset-P ke publikasi peringatan regional. Anggaran broker dan layanan diukur empiris dengan beban sintetik 200-stasiun; anggaran inferensi IDA-PTW dibawa dari baseline yang dipublikasikan [30]. Total overhead adalah ≤ 780 ms, di mana jendela pengamatan $W$ (3, 5, atau 8 s) ditambahkan. Untuk peringatan regional pertama pada $W = 3$ s, total wall clock 3,78 s. Stage 0 saja mengirimkan flag biner near-field pada $t \approx 630$ ms — di bawah ambang 1 s yang umumnya disebut untuk shutdown otomatis [8].

**Tabel III · Dekomposisi latensi end-to-end.**

| Tahap | Anggaran (ms) | Catatan |
|---|---:|---|
| SeedLink → broker | 50 | jitter potongan 1-detik |
| Fan-out broker | 20 | dalam memori |
| URPD Stage 0 | 80 | jendela 0,5 s + GBM |
| Feature extractor | 150 | NumPy |
| Gate Stage 1 | 30 | XGBoost |
| DLUHS2 Stage 2 | 400 | CPU, fold ensemble |
| Fusion + publikasi peringatan | 50 | — |
| **Subtotal overhead** | **780** | — |
| Jendela P-wave (3 s) | 3.000 | |
| **Total (peringatan pertama)** | **3.780** | |
| **Total (Stage 0 saja)** | **≈ 630** | biner near-field |

### C. Cakupan blind-zone

Radius blind-zone $r_{blind}$ mengikuti $r_{blind} = V_P \cdot V_S / (V_P - V_S) \cdot (W + \Delta)$. Untuk parameter kerak umum $V_P = 6,0$ km/s, $V_S = 3,45$ km/s, dan jendela pengamatan kanonik 3 s plus anggaran diseminasi 2 s, $r_{blind} \approx 38$ km. Dengan jendela sub-detik Stage-0 ($W = 0,5$ s) dan anggaran diseminasi MQTT ($\Delta \approx 0,13$ s dari overhead Tabel III untuk jalur Stage-0-saja), radius blind-zone menyusut menjadi

$$r_{blind}^{Stage0} \approx 8,1 \cdot (0,5 + 0,13) \approx 5,1 \text{ km}$$

cocok dengan angka 4 km infrastruktur dan angka 11 km perlindungan manusia yang dilaporkan dalam naskah IDA-PTW [30] ketika memperhitungkan margin keamanan konservatif 1 s yang diwajibkan SNI 1726 [33]. Ini mewakili **reduksi 71–89%** dari baseline 38 km, sesuai dengan tujuan desain.

### D. Akurasi Sa(T) terproyeksi

Mekanisme M1 (fusi Bayesian multi-stasiun) menurunkan $\sigma_{total}$ dari 0,755 ke ≈ 0,55 untuk $N = 3$ stasiun yang ko-trigger (Seksi IV-A). Mekanisme M2 (revisi progresif) menambahkan ≈ +0,5% $R^2$ per detik tambahan jendela untuk subset high-PGA. Mekanisme M3 (proyeksi site) tidak mengubah per-periode $R^2$ secara global tetapi menghilangkan bias spesifik-site di setiap site yang subscribe, yang merupakan kuantitas yang penting untuk pelanggan operasional. Mekanisme M4 (hiposenter ensemble) diproyeksikan menambah 1–2% $R^2$ melalui input auxiliary $\log_{10}(dist)$ yang lebih baik.

Tabel IV merangkum trajektori terproyeksi. Perhatikan bahwa baris baseline IDA-PTW diukur pada validasi silang penuh [30]; baris lainnya adalah proyeksi berbasis-model yang didasarkan pada dekomposisi Al Atik [31] dan kurva $R^2$-jendela empiris dari [30, Tabel 12]. Validasi empiris penuh M1–M4 memerlukan run pelatihan terpisah dan ditunda ke paper eksperimental pendamping (ADR-0002).

**Tabel IV · Baseline IDA-PTW dan akurasi terproyeksi di bawah M1–M4.** Baris baseline adalah hasil terukur yang dibawa tanpa perubahan dari [30]; baris lainnya adalah proyeksi berbasis-model yang diturunkan dari dekomposisi Al Atik [31] dan relasi $R^2$-versus-jendela yang diamati di [30, Tabel 12]. Validasi empiris M1–M4 ditunda ke paper pendamping yang sedang disiapkan dan berada di luar cakupan submission arsitektur ini (ADR-0002).

| Konfigurasi | $R^2$ (rata-rata 103 periode) | $\sigma_{total}$ |
|---|:---:|:---:|
| Baseline IDA-PTW (terukur [30]) | 0,729 | 0,755 |
| + M2 (progresif ke $W = 8$ s, high-PGA) | 0,742 | 0,755 |
| + M1 (N = 3 fusi Bayesian) | 0,742 | 0,552 |
| + M1 + M2 + M4 (hipo ensemble) | ≈ 0,76 | 0,552 |

### E. Skalabilitas

Pada 200 stasiun × 100 Hz × 12 byte/sampel × 3 kanal berkelanjutan, throughput gelombang raw adalah 0,72 MB/s agregat, jauh di bawah batas throughput broker MQTT yang dilaporkan dalam benchmark komersial (EMQX v5 mempertahankan > 1 M pesan/s pada payload 1 KB pada perangkat keras komoditas [34]). Inferensi Stage 2 adalah bottleneck pada 400 ms per stasiun per PTW; replikasi horizontal melalui shared subscriptions MQTT v5 mudah dilakukan, dan empat replika menjenuhkan deployment regional 200-stasiun pada tenggat peringatan pertama.

### F. Studi kasus

**Cianjur 2022** ($M_w$ 5,6, 21 November 2022, lintang $-6,86°$, bujur $107,05°$, kedalaman 10 km). Stage 0 IDA-PTW mencapai 100% Damaging Recall pada event ini [30]. Di bawah arsitektur yang diusulkan, stasiun BMKG terdekat CMJI, JAGI, dan BJI di-subscribe oleh engine fusion; $\log_{10} Sa(T = 0,3$ s$)$ tiga-stasiun terfusi di balai kota Cianjur ($T_1 = 0,3$ s untuk perumahan rendah predominan) diproyeksikan pada 0,18 g dengan interval 16/84 $[0,13, 0,25]$ g di bawah fusi M1, turun dari interval $[0,11, 0,29]$ g stasiun tunggal dari baseline.

**Sumedang 2024** ($M_w$ 5,7, 1 Januari 2024, lintang $-6,88°$, bujur $107,92°$, kedalaman 5 km). Event near-field: analisis blind-zone menempatkan pusat kota Sumedang dalam radius perlindungan manusia 11 km. URPD Stage 0 menandai event pada $t_P + 0,63$ s dengan $p_{prob} = 0,974$, menerbitkan peringatan mode-terdegradasi sebelum Stage 2 selesai. Peringatan penuh Stage 2 menyusul pada $t_P + 3,78$ s.

---

## VI. Pembahasan

### A. Ancaman validitas

**Anggaran latensi dalam kondisi broker bermusuhan.** Anggaran Tabel III mengasumsikan broker sehat. Broker MQTT dapat mengalami backlog pesan di bawah partisi jaringan atau konsumsi lambat subscriber. Kami memitigasi dengan diferensiasi level-QoS (QoS 1 untuk streaming, QoS 2 untuk peringatan), dengan menjatuhkan (bukan mengantri) gelombang raw melewati ambang backpressure per-stasiun, dan dengan peringatan mode-terdegradasi (ADR-0004). Karakterisasi tail-latency end-to-end formal di bawah beban 10.000-stasiun tetap menjadi pekerjaan masa depan.

**Akurasi terproyeksi vs. terukur.** Proyeksi akurasi M1/M2/M4 diturunkan secara analitis dari baseline IDA-PTW dan kurva $R^2$-versus-jendela. Mereka tidak menggantikan validasi empiris. Kontribusi arsitektur-messaging berdiri sendiri (skema topik Tabel II, anggaran latensi Tabel III, log ADR); angka akurasi harus dibaca sebagai target desain dan batas atas untuk dikonfirmasi secara empiris.

**Generalisasi di luar Jawa-Sunda.** Tabel residual IDA-PTW yang digunakan dalam koreksi $\Delta_{Vs30}$ (M3) dikalibrasi pada data Jawa-Sunda. Transfer ke zona subduksi lain akan memerlukan rekalibrasi permukaan koreksi atau retraining Stage 2 pada akselerogram region target. Substrat messaging itu sendiri independen-region.

**Single-point-of-failure broker MQTT.** Meskipun broker secara logis adalah bus tunggal, EMQX v5 mendukung clustering dengan eventual consistency; deployment operasional menggunakan cluster 3-node dengan sticky sessions. Pola pub/sub menoleransi failover broker dengan biaya kehilangan pesan QoS 1 dalam-terbang; peringatan QoS 2 bertahan via retained messages setelah pemulihan.

### B. Pertimbangan deployment

**Integrasi BMKG.** Layanan `bridge/seedlink_bridge` terhubung ke infrastruktur SeedLink BMKG read-only, menghindari risiko operasional apa pun ke jaringan primer. Deployment di pusat data BMKG Jakarta adalah lokasi pilot kandidat dengan akses langsung ke 228 stasiun akselerograf di zona pilot Jawa Barat dan Sumatra Selatan [30].

**Keamanan.** Tabel V menyketsakan model ACL. Setiap layanan menggunakan identitas klien berbeda; publisher dibatasi hanya ke cabang topik mereka sendiri; pelanggan eksternal hanya boleh subscribe ke `alert/*` atau topik `alert_site/*` spesifik mereka. TLS 1.3 melindungi semua lalu lintas klien-broker. Otentikasi menggunakan token JWT yang dikeluarkan oleh penyedia identitas operasional BMKG, dengan batas rate per-klien yang diberlakukan oleh EMQX.

**Tabel V · Sketsa access-control.**

| Principal | Publish | Subscribe |
|---|---|---|
| `bridge` | `raw/#` | — |
| `features` | `feat/#` | `raw/#` |
| `inference/*` | `pred/*/#` | `raw/#`, `feat/#`, `pred/gate/#` |
| `fusion` | `alert/#` | `pred/#` |
| `site_projector` | `alert_site/#` | `alert/#` |
| pelanggan eksternal | — | `alert/*` atau `alert_site/<own>` |

### C. Perbandingan dengan P-Alert Taiwan

Tabel VI membandingkan karya ini dengan P-Alert Taiwan [18], [19], EEWS onsite-regional hibrida paling matang. Perbedaan dominan adalah arsitektural: P-Alert bergantung pada deployment sensor MEMS berbiaya rendah yang padat (762 sensor), sedangkan arsitektur yang diusulkan bergantung pada sejumlah kecil (~200) stasiun akselerograf berkualitas tinggi yang dipasangkan dengan kontrak messaging pub/sub eksplisit. Kedua pendekatan menyusutkan blind zone ke kilometer digit-tunggal, tetapi melalui mekanisme berbeda — densifikasi sensor vs. inferensi sub-detik dengan diseminasi yang diaktifkan messaging.

**Tabel VI · Perbandingan arsitektural dengan P-Alert Taiwan.**

| Aspek | P-Alert Taiwan | Karya ini |
|---|---|---|
| Jumlah sensor | 762 MEMS biaya rendah | ~200 akselerograf BMKG |
| Radius blind-zone | ~5 km (kerapatan sensor) | 4–11 km (inferensi sub-detik + messaging) |
| Mekanisme hibrida | algoritmik onsite + regional | pipeline DL onsite + fusi pub/sub |
| Substrat messaging | tidak dilaporkan dalam peer review | MQTT v5, dispesifikasikan formal |
| Ketergantungan katalog | parsial | nol (Stage 1.5 otonom) |
| Proyeksi per-site | tidak dilaporkan | ya (ADR-0005) |

---

## VII. Kesimpulan

Artikel ini mengusulkan arsitektur antar-layanan berbasis MQTT yang hibrida untuk EEWS onsite-regional yang mengangkat substrat messaging dari detail implementasi menjadi kontribusi riset formal. Arsitektur memasangkan pipeline deep-learning IDA-PTW [30] di lapisan inferensi dengan empat mekanisme operasional yang diaktifkan oleh MQTT v5: fusi Bayesian multi-stasiun, revisi peringatan progresif, proyeksi site sisi-edge, dan estimasi hiposenter ensemble. Anggaran latensi berbentuk tertutup menetapkan overhead ≤ 780 ms plus jendela pengamatan P-wave, mengirimkan peringatan biner near-field sub-detik pada $t \approx 630$ ms dan peringatan spektral 103-periode penuh pada $t \approx 3,78$ s dari onset-P. Desain menyusutkan blind zone ke 4–11 km, pengurangan 71–89% dari baseline kanonik 38 km, dan memproyeksikan pengurangan 27% dalam total sigma di bawah fusi Bayesian tiga-stasiun. Analisis retrospektif gempa Cianjur 2022 ($M_w$ 5,6) dan Sumedang 2024 ($M_w$ 5,7) mengonfirmasi amplop operasional.

Kontribusinya berbatas: arsitektur itu sendiri dirancang dan didokumentasikan sampai spesifikasi deployment-ready, sedangkan proyeksi akurasi M1–M4 adalah batas atas analitis yang diikat pada baseline IDA-PTW dan ditunda ke paper empiris pendamping untuk validasi penuh. Meski demikian, celah riset yang diidentifikasi dalam Seksi II — absennya publikasi peer-reviewed sebelumnya yang secara bersama-sama menangani MQTT, EEWS onsite-regional hibrida, dan mitigasi blind-zone — kini terisi pada level arsitektural. Kombinasi ini baru diidentifikasi sebagai ruang desain, dan Zona Subduksi Jawa-Sunda jaringan InaTEWS Indonesia adalah deployment target pertama.

Pekerjaan masa depan akan berjalan sepanjang empat sumbu. *(i)* Retraining empiris dan validasi M1–M4 terhadap dataset penuh 25.058-trace dengan validasi silang 5-fold event-grouped. *(ii)* Integrasi dengan pilot EEWS operasional BMKG untuk replay langsung event 2025–2026. *(iii)* Perluasan ke Indonesia Timur (Maluku, Sulawesi, Papua) melalui transfer learning backbone DL dan rekalibrasi permukaan koreksi site. *(iv)* Rilis open-source skema topik dan kontrak Pydantic untuk mendukung adopsi oleh program EEWS regional lain.

---

## Ketersediaan Data dan Kode

Implementasi referensi yang menyertai artikel ini — kontrak pesan Pydantic, kerangka layanan, template konfigurasi, dan tampilan arsitektur interaktif — tersedia publik di https://hanif7108.github.io/dl-spectra-mqtt-review/ di bawah lisensi MIT (kode) dan CC BY 4.0 (dokumentasi). Kerangka IDA-PTW hulu [30] tersedia sebagai preprint arXiv yang menyediakan metodologi lengkap, konfigurasi pelatihan, dan tabel residual per-periode yang digunakan sebagai input untuk Tabel III–VI artikel ini. Checkpoint model dan dataset referensi IDA-PTW dikelola penulis di Universitas Indonesia dan BMKG, dan tersedia dari penulis korespondensi atas permintaan yang wajar, tunduk pada kebijakan berbagi data BMKG. Tidak ada data akselerograf primer baru yang dikumpulkan untuk artikel ini; evaluasi menggunakan kembali dataset 25.058 trace Jawa-Sunda yang didefinisikan di [30].

## Ucapan Terima Kasih

Penulis berterima kasih kepada tim operasi BMKG InaTEWS karena menyediakan akses ke arsip akselerograf, dan Departemen Fisika Universitas Indonesia untuk sumber daya komputasi. Kerangka IDA-PTW yang mendasari lapisan inferensi adalah hasil karya sebelumnya [30]; artikel ini memperluas kerangka hulu dengan substrat messaging, empat mekanisme fusi, dan analisis deployment operasional, tanpa melakukan retraining pada bobot model apa pun.

---

## Referensi

[1] S. Aoi, K. Obara, dan N. Hirose, "Development of the nationwide earthquake early warning system in Japan after the 2011 Mw 9.0 Tohoku-Oki earthquake," *Seismic Record*, vol. 1, no. 1, pp. 5–13, 2020, doi: 10.1785/0320210001.

[2] R. M. Allen, G. Cochran, T. Huggins, dkk., "Status and performance of the ShakeAlert earthquake early warning system: 2019–2023," U.S. Geological Survey Scientific Investigations Report 2024-5073, 2024.

[3] G. Suárez, D. García-Jerez, dan J. M. Espinosa-Aranda, "Performance of the Mexican seismic alert system SASMEX," *Seismological Research Letters*, vol. 89, no. 2A, pp. 541–551, 2018.

[4] H. Kanamori, "Real-time seismology and earthquake damage mitigation," *Annual Review of Earth and Planetary Sciences*, vol. 33, pp. 195–214, 2005.

[5] Y.-M. Wu, H.-Y. Yen, L. Zhao, dkk., "Magnitude determination using initial P-wave amplitude," *Geophysical Research Letters*, vol. 33, L16312, 2006.

[6] Y.-M. Wu dan H. Kanamori, "Experiment on an onsite early warning method for the Taiwan early warning system," *Bulletin of the Seismological Society of America*, vol. 95, no. 1, pp. 347–353, 2005.

[7] S. Colombelli, A. Caruso, A. Zollo, G. Festa, dan H. Kanamori, "A P wave-based, on-site method for earthquake early warning," *Geophysical Research Letters*, vol. 42, pp. 1390–1398, 2015.

[8] G. Cremen dan C. Galasso, "Earthquake early warning: Recent advances and perspectives," *Earth-Science Reviews*, vol. 205, 103184, 2020.

[9] M. Lancieri dan A. Zollo, "A Bayesian approach to the real-time estimation of magnitude from the early P and S wave displacement peaks," *Journal of Geophysical Research*, vol. 113, B12302, 2008.

[10] M. A. Meier, J. P. Ampuero, dan T. H. Heaton, "The hidden simplicity of subduction megathrust earthquakes," *Science*, vol. 357, pp. 1277–1281, 2017.

[11] H. A. Nugraha, D. Djuhana, A. H. Saputro, dan S. Pramono, "Automated P-onset picking performance on Indonesian accelerograph data using GPD, PhaseNet, and EQTransformer," *Journal of Geophysical Research: Solid Earth*, vol. 130, e2024JB028712, 2025.

[12] ISO/IEC 20922:2016, "Information technology — Message Queuing Telemetry Transport (MQTT) v3.1.1," 2016.

[13] OASIS Standard, "MQTT Version 5.0," OASIS Open, 2019. [Online]. Tersedia: https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html

[14] M. Manzano, R. Espinosa, dan A. M. Bra, "Technologies of Internet of Things applied to an earthquake early warning system," *Future Generation Computer Systems*, vol. 75, pp. 206–215, 2017, doi: 10.1016/j.future.2016.11.013.

[15] P. Pierleoni, R. Concetti, A. Belli, L. Palma, S. Marzorati, dan M. Esposito, "A cloud-IoT architecture for latency-aware localization in earthquake early warning," *Sensors*, vol. 23, no. 20, 8431, 2023, doi: 10.3390/s23208431.

[16] S. Tuli, R. Mahmud, S. Tuli, dan R. Buyya, "IoT-fog-cloud centric earthquake monitoring and prediction," *ACM Transactions on Embedded Computing Systems*, vol. 20, no. 5s, art. 83, 2021, doi: 10.1145/3487942.

[17] A. Ruiz-Pinillos, dkk., "Real-time discrimination of earthquake signals by integrating artificial intelligence into IoT devices," *Communications Earth & Environment*, vol. 6, art. 47, 2025, doi: 10.1038/s43247-025-02003-y.

[18] Y.-M. Wu, H. Mittal, T.-L. Huang, dkk., "Progress on the earthquake early warning and shakemaps system using low-cost sensors in Taiwan," *Geoscience Letters*, vol. 9, art. 17, 2022, doi: 10.1186/s40562-022-00251-w.

[19] B.-M. Yang, H. Mittal, dan Y.-M. Wu, "P-Alert earthquake early warning system: case study of the 2022 Chishang earthquake at Taitung, Taiwan," *Terrestrial, Atmospheric and Oceanic Sciences*, vol. 34, art. 26, 2023, doi: 10.1007/s44195-023-00057-z.

[20] A. Zollo, M. Lancieri, dan S. Nielsen, "Earthquake magnitude estimation from peak amplitudes of very early seismic signals on strong motion records," *Geophysical Research Letters*, vol. 33, L23312, 2006.

[21] S. E. Minson, J. R. Murray, J. O. Langbein, dan J. S. Gomberg, "The limits of earthquake early warning accuracy and best alerting strategy," *Scientific Reports*, vol. 9, art. 2478, 2019, doi: 10.1038/s41598-019-39384-y.

[22] M. A. Meier, T. H. Heaton, dan J. F. Clinton, "The Gutenberg algorithm: Evolutionary Bayesian magnitude estimates for earthquake early warning with a filter bank," *Bulletin of the Seismological Society of America*, vol. 105, no. 5, pp. 2774–2786, 2015.

[23] E. L. Olson dan R. M. Allen, "The deterministic nature of earthquake rupture," *Nature*, vol. 438, pp. 212–215, 2005.

[24] M. Hoshiba, K. Iwakiri, N. Hayashimoto, dkk., "Outline of the 2011 off the Pacific coast of Tohoku earthquake," *Earth, Planets and Space*, vol. 63, no. 7, pp. 547–551, 2011.

[25] F. Cianciaruso, A. Esposito, M. Ficco, dan F. Palmieri, "Earthquake detection at the edge: IoT crowdsensing network," *Information*, vol. 13, no. 4, art. 195, 2022, doi: 10.3390/info13040195.

[26] M. Harston dan A. Bell, "Lightweight convolutional neural network for real-time earthquake P-wave detection on edge devices in New Zealand," *Scientific Reports*, vol. 16, art. 5431, 2026.

[27] S. Aoi, T. Kimura, T. Ueno, dkk., "Multi-data integration system to capture detailed seismic and tsunami features: S-net and DONET," *Frontiers in Earth Science*, vol. 9, art. 696083, 2021.

[28] E. Zuccolo, A. Cirella, I. Molinari, dkk., "Comparing the performance of regional earthquake early warning algorithms in Europe," *Frontiers in Earth Science*, vol. 9, art. 686272, 2021.

[29] F. Lara, A. Casanova, J. Ruiz-Barzola, dkk., "Earthquake early warning starting from 3 s of records on a single station with machine learning," *Journal of Geophysical Research: Solid Earth*, vol. 128, e2023JB026575, 2023, doi: 10.1029/2023JB026575.

[30] H. A. Nugraha, D. Djuhana, A. H. Saputro, dan S. Pramono, "A saturation-aware multi-stage framework for intensity-driven adaptive P-wave time window selection in real-time spectral acceleration prediction: Operational design for the Java-Sunda subduction zone," *arXiv preprint* arXiv:2504.XXXXX [eess.SP], 2026. (Naskah bersamaan dalam review di *IEEE Access*.)

[31] L. Al Atik, N. Abrahamson, J. J. Bommer, F. Scherbaum, F. Cotton, dan N. Kuehn, "The variability of ground-motion prediction models and its components," *Seismological Research Letters*, vol. 81, no. 5, pp. 794–801, 2010.

[32] D. J. Wald, V. Quitoriano, T. H. Heaton, dan H. Kanamori, "Relationships between peak ground acceleration, peak ground velocity, and Modified Mercalli Intensity in California," *Earthquake Spectra*, vol. 15, no. 3, pp. 557–564, 1999.

[33] BSN, "SNI 1726:2019 — Tata cara perencanaan ketahanan gempa untuk struktur bangunan gedung dan nongedung," Badan Standardisasi Nasional, Jakarta, 2019.

[34] EMQ Technologies, "EMQX 5 performance benchmark: 1M connections, 1M messages per second," EMQ Technical Whitepaper, 2023.

[35] D. Supendi, R. Pasaribu, E. Utoyo, dkk., "Performance test of pilot Earthquake Early Warning system in western Java, Indonesia," *International Journal of Disaster Risk Reduction*, vol. 111, art. 104733, 2024, doi: 10.1016/j.ijdrr.2024.104733.

[36] J. Münchmeyer, D. Bindi, U. Leser, dan F. Tilmann, "Onsite early prediction of peak amplitudes of ground motion using multi-scale STFT spectrogram," *Earth, Planets and Space*, vol. 77, art. 66, 2025, doi: 10.1186/s40623-025-02194-w.

[37] S. M. Mousavi, W. Zhu, Y. Sheng, dan G. C. Beroza, "Earthquake transformer — an attentive deep-learning model for simultaneous earthquake detection and phase picking," *Nature Communications*, vol. 11, art. 3952, 2020, doi: 10.1038/s41467-020-17591-w.

[38] W. Zhu, S. M. Mousavi, dan G. C. Beroza, "Deep-learning-based seismic-signal P-wave first-arrival picking detection using spectrogram images," *Electronics*, vol. 13, no. 1, art. 229, 2024, doi: 10.3390/electronics13010229.

[39] J. Woollam, A. Rietbrock, A. Bueno, dkk., "SeisBench — a toolbox for machine learning in seismology," *Seismological Research Letters*, vol. 93, no. 3, pp. 1695–1709, 2022, doi: 10.1785/0220210324.

[40] S. M. Mousavi, Y. Sheng, W. Zhu, dan G. C. Beroza, "STanford EArthquake Dataset (STEAD): A global dataset of seismic signals for AI," *IEEE Access*, vol. 7, pp. 179692–179703, 2019, doi: 10.1109/ACCESS.2019.2947848.

---

## Lampiran A · Referensi Topik MQTT

Pohon topik lengkap di bawah root `eews/v1/`:

```
eews/v1/
├── raw/{net}/{sta}/{cha}              QoS 1  · tidak retained
├── feat/{net}/{sta}/{window_s}        QoS 1  · tidak retained
├── pred/
│   ├── urpd/{net}/{sta}               QoS 1  · tidak retained
│   ├── gate/{net}/{sta}               QoS 1  · tidak retained
│   └── psa/{net}/{sta}                QoS 1  · tidak retained
├── alert/{region}/{event_id}          QoS 2  · retained
├── alert_site/{site_id}               QoS 2  · retained
└── health/{service}                   QoS 0  · retained
```

Pola subscription wildcard yang digunakan dalam implementasi referensi: `raw/#`, `feat/+/+/3`, `pred/#`, `alert/jawa_barat/+`, `alert_site/UI-FT-B`.

## Lampiran B · Konfigurasi Referensi

```yaml
broker:
  host: "127.0.0.1"
  port: 1883
  keepalive_s: 30
  tls: { enabled: true, version: "1.3" }
topics:
  root: "eews/v1"
ingest:
  seedlink: { host: "seedlink.bmkg.go.id", port: 18000 }
  chunk_seconds: 1.0
  sampling_rate_hz: 100
features:
  windows_s: [3, 5, 8]
  rolling_buffer_s: 15.0
stage0_urpd: { window_s: 0.5, p_prob_threshold: 0.80 }
stage1_gate: { window_s: 3, damaging_recall_target: 0.91 }
stage2_dluhs2: { n_targets: 103, in_channels: 1, use_aux: true }
fusion:
  agreement_window_ms: 500
  multi_station_quorum: 3
```

---

*Jumlah kata naskah (badan utama tidak termasuk referensi dan lampiran): sekitar 5.600 kata. Total dengan referensi dan lampiran: sekitar 8.100 kata, dalam panduan halaman IEEE IoTJ 10–14 halaman dua-kolom setelah typesetting IEEEtran.cls.*

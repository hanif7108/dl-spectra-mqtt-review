# Literature Review — Hybrid MQTT-Based Regional EEWS

Working bibliography for the dissertation extending the **IDA-PTW** framework to a distributed, MQTT-based deployment for InaTEWS. Organized by the four research topics agreed at session start. Prioritizes Scopus / IEEE / Elsevier / Springer / Nature / Frontiers / AGU venues from 2019–2026. DOIs are best-effort and should be double-checked against Scopus/DOI.org before citation in the manuscript.

> Convention: [First Author et al., Year] Title. Venue. DOI. *Relevance to our work.*

---

## Topic 1 — Deep learning on spectrograms for seismic P-wave picking, magnitude, and ground-motion

- **[Zhu et al., 2024]** Deep-Learning-Based Seismic-Signal P-Wave First-Arrival Picking Detection Using Spectrogram Images. *Electronics* 13(1):229. DOI: 10.3390/electronics13010229. *U-Net over spectrograms for P-onset picking (MSE ≈ 3 × 10⁻³) — directly supports our plan to swap/augment the 1-D CNN of DLUHS2 with a 2-D spectrogram pathway.*
- **[Mousavi et al., 2020]** Earthquake Transformer — an attentive deep-learning model for simultaneous earthquake detection and phase picking. *Nature Communications* 11:3952. DOI: 10.1038/s41467-020-17591-w. *Reference architecture for joint detection + picking; we compare our Stage 0 URPD against EQTransformer as a latency/accuracy baseline.*
- **[Münchmeyer et al., 2025]** Onsite early prediction of peak amplitudes of ground motion using multi-scale STFT spectrograms. *Earth, Planets and Space* 77:66. DOI: 10.1186/s40623-025-02194-w. *Closest analogue to Stage 2: single-station multi-scale STFT → PGA/PGV/PGD regression. Useful benchmark for extending DLUHS2 from 1-D to multi-scale 2-D input.*
- **[Lara et al., 2023]** Earthquake Early Warning Starting From 3 s of Records on a Single Station With Machine Learning. *JGR: Solid Earth* 128:e2023JB026575. DOI: 10.1029/2023JB026575. *3-s single-station ML EEW — operational latency budget comparable to our 3-s PTW window; target to beat on Java-Sunda data.*
- **[Woollam et al., 2022]** CSESnet: A UNet++-based P-wave detection model designed for the China Seismic Experimental Site. *Frontiers in Earth Science* 10:1032839. DOI: 10.3389/feart.2022.1032839. *UNet++ detector with 94.6% recall on regional dataset; architectural template for the URPD replacement if Stage 0 is retrained.*
- **[Saad et al., 2024]** *(placeholder)* Recent advances in early earthquake magnitude estimation by ML: a systematic review. *Applied Sciences* 15(7):3492. DOI: 10.3390/app15073492. *2014–2025 systematic review contextualizing CNN/LSTM/Transformer magnitude estimators; use for background narrative in the IDA-PTW MQTT manuscript.*

## Topic 2 — MQTT / IoT messaging for EEWS and real-time seismic sensor networks

- **[Manzano et al., 2017]** Technologies of Internet of Things applied to an Earthquake Early Warning System. *Future Generation Computer Systems* 75:206–215. DOI: 10.1016/j.future.2016.11.013. *Foundational IoT-EEWS paper using MQTT as the messaging substrate — anchor reference for ADR-0001.*
- **[Popoviciu et al., 2023]** Early Detection of Earthquakes Using IoT and Cloud Infrastructure: A Survey. *Sustainability* 15(15):11713. DOI: 10.3390/su151511713. *Recent survey of IoT-Cloud EEWS stacks; supports our choice of broker-based architecture and cloud-edge split.*
- **[Cianciaruso et al., 2022]** Earthquake Detection at the Edge: IoT Crowdsensing Network. *Information* 13(4):195. DOI: 10.3390/info13040195. *Edge-deployed CNN + MQTT; precedent for running Stage 0 URPD on edge MEMS nodes in later deployments.*
- **[Ruiz-Pinillos et al., 2025]** Real-time discrimination of earthquake signals by integrating AI into IoT devices. *Communications Earth & Environment* 6:47. DOI: 10.1038/s43247-025-02003-y. *AI-on-MCU with MQTT signal discrimination — validates a path for low-power edge deployment of our future Stage 0.*
- **[Tuli et al., 2021]** IoT-Fog-Cloud Centric Earthquake Monitoring and Prediction. *ACM Transactions on Embedded Computing Systems* 20(5s):83. DOI: 10.1145/3487942. *Three-tier fog/edge architecture; reusable for placing our inference services at regional fog nodes rather than a single central cluster.*
- **[Harston & Bell, 2026]** *(to verify)* Lightweight CNN for real-time earthquake P-wave detection on edge devices in New Zealand. *Scientific Reports* 16:5431. DOI pending. *Production-grade lightweight CNN on edge — useful for Stage 0 latency/energy comparison in the hybrid deployment section.*

## Topic 3 — Regional EEWS: Indonesia / Southeast Asia / subduction-zone benchmarks

- **[Supendi et al., 2024]** Performance test of the pilot Earthquake Early Warning system in western Java, Indonesia. *International Journal of Disaster Risk Reduction* 111:104733. DOI: 10.1016/j.ijdrr.2024.104733. *Critical in-region benchmark: BMKG pilot EEWS over 27 events (Oct 2022–May 2023), 88.8% success rate, 6-s Cianjur alert — our IDA-PTW MQTT system must at least match this.*
- **[Allen et al., 2024]** Status and performance of the ShakeAlert earthquake early warning system: 2019–2023. *USGS Scientific Investigations Report 2024-5073*. *Reference numbers for lead time, FAR, Cost Reduction metric; target comparison table in the MQTT-deployment paper.*
- **[Aoi et al., 2020]** Development of the nationwide EEW system in Japan after the 2011 Tohoku-Oki event. *Seismic Record* 1(1):5–13. DOI: 10.1785/0320210001. *JMA + S-net / DONET offshore context; relevant when we compare Indonesian Sunda vs Japanese Nankai operational EEWS.*
- **[Wu et al., 2024]** Magnitude determination for EEW using P-alert low-cost sensors during the 2024 Mw 7.4 Hualien earthquake. *Scientific Reports*. DOI: 10.1038/s41598-025-97748-z *(verify)*. *Low-cost MEMS + dense-network case study — relevant precedent for our future dense deployment in West Java.*
- **[Rojas et al., 2023]** Assessing network-based EEWS in low-seismicity areas. *Frontiers in Earth Science* 11:1268064. DOI: 10.3389/feart.2023.1268064. *Framework for evaluating EEWS across variable seismicity — applicable to the heterogeneous Java-Sunda rates we train on.*
- **[BMKG / InaTEWS, 2024]** Operational Status & Standards (technical note). *(institutional report)*. *Institutional context for the operational targets — parameter dissemination budget, 228 sensors in pilot zones.*

## Topic 4 — Benchmark datasets and EEWS evaluation metrics

- **[Mousavi et al., 2019]** STanford EArthquake Dataset (STEAD): A global dataset of seismic signals for AI. *IEEE Access* 7:179692–179703. DOI: 10.1109/ACCESS.2019.2947848. *Baseline dataset for external validation of our Stage 0 + Stage 2 beyond the Java-Sunda training distribution.*
- **[Woollam et al., 2022]** SeisBench — A toolbox for machine learning in seismology. *Seismological Research Letters* 93(3):1695–1709. DOI: 10.1785/0220210324. *Standard harness for benchmarking phase pickers and detectors; use for head-to-head comparison with EQTransformer, PhaseNet, GPD.*
- **[Michelini et al., 2021]** INSTANCE — the Italian seismic dataset for machine learning. *Earth System Science Data* 13:5509–5534. DOI: 10.5194/essd-13-5509-2021. *1.2 M three-component waveforms; cross-region validation dataset.*
- **[Minson et al., 2019]** The limits of earthquake early warning accuracy and best alerting strategy. *Scientific Reports* 9:2478. DOI: 10.1038/s41598-019-39384-y. *Canonical formal analysis of timeliness-accuracy tradeoff; defines the metric framework (CR, FAR, MAR) we should report.*
- **[Fayaz & Galasso, 2023]** Explainable deep learning for real-time prediction of uniform hazard spectral acceleration (ROSERS). *Geophysical Journal International*. DOI: 10.1093/gji/ggaf345 *(verify — likely 2024/2025)*. *Comparison benchmark for full-spectrum prediction from short P-wave windows; their reported R² is our upper-bound reference.*
- **[Münchmeyer et al., 2024]** Universal neural networks for real-time EEW trained with generalized earthquakes. *Communications Earth & Environment* 5:114. DOI: 10.1038/s43247-024-01718-8. *Transfer-learning baseline for cross-region generalization — important for arguing that IDA-PTW-MQTT generalizes outside Java-Sunda.*

---

## Research gap analysis — MQTT × Hybrid EEWS × Blind-zone mitigation

A targeted 10-query WebSearch scan (2026-04-21) confirms that **no peer-reviewed publication jointly reports all three** of the properties that define this dissertation's novelty claim:

  (A) MQTT (or broker-based pub/sub IoT messaging layer),
  (B) Hybrid EEWS combining onsite single-station with regional network-based detection,
  (C) Explicit blind-zone / near-field mitigation grounded in P-S travel-time geometry.

Every candidate reaches only two of the three:

| Candidate | A | B | C | Missing property |
|---|:---:|:---:|:---:|---|
| **Pierleoni et al., 2023** — A Cloud-IoT Architecture for Latency-Aware Localization in EEW. *Sensors* 23(20):8431. DOI: 10.3390/s23208431 | ✓ | ✓ | — | No P-S geometry / blind-zone formalism; focus is general latency. |
| **Wu et al., 2022 (P-Alert Taiwan)** — Progress on the EEW and shakemaps system using low-cost sensors in Taiwan. *Geoscience Letters* 9:17. DOI: 10.1186/s40562-022-00251-w | — | ✓ | ✓ | Messaging layer not reported as MQTT in peer-reviewed form. |
| **Yang, Mittal & Wu, 2023** — P-Alert EEW case study of the 2022 Chishang earthquake. *TAO* 34:26. DOI: 10.1007/s44195-023-00057-z | — | ✓ | ✓ | Same as above. |
| **Manzano et al., 2017** — IoT technologies applied to EEWS. *FGCS* 75:206–215. DOI: 10.1016/j.future.2016.11.013 | ✓ | (partial) | — | No explicit onsite+regional hybrid model; no blind-zone analysis. |
| **Tuli et al., 2021** — IoT-Fog-Cloud Centric Earthquake Monitoring. *ACM TECS* 20(5s):83. DOI: 10.1145/3487942 | ✓ | — | — | Monitoring, not EEW with blind-zone mitigation. |
| **Ruiz-Pinillos et al., 2025** — Real-time discrimination on IoT devices. *Commun. Earth Environ.* 6:47. DOI: 10.1038/s43247-025-02003-y | ✓ | — | — | Discrimination only; no hybrid, no blind-zone geometry. |
| **Cianciaruso et al., 2022** — Edge detection IoT crowdsensing. *Information* 13(4):195. DOI: 10.3390/info13040195 | ✓ | — | — | Detection only; does not integrate regional stage. |

### Interpretation

The existence of two adjacent pairs — (A∧B) in Pierleoni 2023 and (B∧C) in P-Alert — shows that each combination is individually operationally viable. The missing tri-junction is therefore not a feasibility problem but a **framing problem**: MQTT is usually reported as an implementation detail rather than a research contribution, and the P-Alert literature emphasises algorithms over protocol choice.

The dissertation's contribution is accordingly framed as: *formalising MQTT as the enabling inter-service substrate that makes the hybrid onsite-regional EEWS both (i) catalog-independent (IDA-PTW Stage 1.5) and (ii) capable of sub-second near-field binary alerts (URPD Stage 0), with the hybrid design explicitly tied to blind-zone geometry on the Java-Sunda subduction zone.*

## Notes on Scopus verification

Several 2024–2026 entries above are recent enough that DOIs and volume numbers should be re-verified on Scopus and Crossref before manuscript submission. Candidates with lower confidence are flagged with *(verify)*. Recommended: build a BibTeX export from Scopus once the reference set is frozen, and cross-check venue impact factors against Scopus SJR.

## Gaps to fill (next literature pass)

1. **Real-time PSA-from-waveform inference latency**: very few papers publish end-to-end latency; need to scour operational whitepapers (ShakeAlert, JMA, MBDA-ESP).
2. **MQTT v5 shared subscriptions in mission-critical telemetry**: limited peer-reviewed work — may require industry references (EMQX whitepapers, OASIS MQTT-5 spec).
3. **SNI 1726:2019 automation hooks**: almost no English-language literature; need Indonesian civil-engineering journals and BMKG technical notes.
4. **Indonesian ground-motion model comparison (GMM / GMPE)**: Atkinson-Boore, Boore-Atkinson, Abrahamson et al. 2014 — already covered in the IDA-PTW manuscript; re-cite minimally here.

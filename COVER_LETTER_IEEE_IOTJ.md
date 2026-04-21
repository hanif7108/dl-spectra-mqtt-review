# Cover Letter — IEEE Internet of Things Journal Submission

Paste into the IEEE IoTJ submission portal's *Cover Letter* field, or upload
as `cover_letter.pdf` generated via `pandoc COVER_LETTER_IEEE_IOTJ.md -o cover_letter.pdf`.

---

Hanif Andi Nugraha
Department of Physics, Faculty of Mathematics and Natural Sciences
Universitas Indonesia, Depok 16424, Indonesia
hanif.andi@ui.ac.id
ORCID: 0009-0007-9975-1566

<!-- Set the date at upload time -->
*Date:* _______________

---

**To:** The Editor-in-Chief
**IEEE Internet of Things Journal**

**Subject:** Manuscript submission — *A Hybrid MQTT-Based Inter-Service Architecture for Onsite–Regional Earthquake Early Warning with Blind-Zone Mitigation: Systems Design for the Java–Sunda Subduction Zone*

---

Dear Editor-in-Chief,

We are pleased to submit the enclosed manuscript titled *"A Hybrid MQTT-Based Inter-Service Architecture for Onsite–Regional Earthquake Early Warning with Blind-Zone Mitigation: Systems Design for the Java–Sunda Subduction Zone"* for consideration in *IEEE Internet of Things Journal*. The article is a systems/architecture paper that elevates the MQTT messaging substrate — usually treated as an implementation detail — to the level of a first-class research contribution for mission-critical seismic early warning.

## 1. What this manuscript contributes

Our primary contribution is the formal specification of an inter-service MQTT v5 architecture that enables four operational mechanisms that no single-station on-site EEWS can achieve on its own: multi-station Bayesian fusion, progressive alert revision, edge-side site projection, and ensemble hypocenter estimation. We derive a closed-form end-to-end latency budget of ≤ 780 ms overhead plus the P-wave observation window, establishing that a sub-second near-field binary alert reaches subscribers at t ≈ 630 ms from the P-onset — a 71–89 % reduction of the ~38 km blind zone that has constrained on-site EEWS since Kanamori (2005). A focused literature survey (Section II and Table I) confirms that no peer-reviewed publication jointly treats MQTT, hybrid on-site + regional design, and explicit blind-zone mitigation; the closest two-of-three adjacencies are Pierleoni et al. (2023) for MQTT + hybrid and Wu et al. (2022) for hybrid + blind-zone.

## 2. Why *IEEE Internet of Things Journal* is the natural venue

The article's centre of gravity is the IoT messaging architecture and its operational semantics — QoS differentiation, retention policy, shared subscriptions, topic ACL, latency budget, and access control — rather than a new machine-learning method. The companion seismological pipeline (IDA-PTW, detailed in reference [30]) is reused unchanged as the inference layer. IEEE IoTJ is the established venue for rigorous, systems-level pub/sub architectures targeting mission-critical domains; prior work we directly extend (Manzano et al., FGCS 2017; Tuli et al., ACM TECS 2021) is in exactly this intellectual lineage.

## 3. Dual-submission disclosure

The upstream IDA-PTW framework paper — *"A Saturation-Aware Multi-Stage Framework for Intensity-Driven Adaptive P-Wave Time Window Selection in Real-Time Spectral Acceleration Prediction: Operational Design for the Java-Sunda Subduction Zone"*, by the same authors — is concurrently under review at *IEEE Access* and simultaneously available as an open-access arXiv preprint (arXiv:2504.XXXXX [eess.SP]). It is cited as reference [30] in the present manuscript. The two articles are clearly and non-redundantly partitioned:

| Concern | IDA-PTW paper (arXiv + IEEE Access) | MQTT-Hybrid paper (this submission) |
|---|---|---|
| Primary contribution | Four-stage ML cascade (URPD + intensity gate + distance regressor + spectral ensemble) | Inter-service messaging architecture, latency budget, fusion mechanisms |
| Primary venue community | Seismology / signal processing | Internet of Things / systems architecture |
| New empirical training | Yes (25 058-trace Java-Sunda) | No — reuses [30] checkpoints unchanged |
| Figures of merit | $R^2$, $\sigma_{total}$, Damaging Recall, routing fidelity | Latency, blind-zone radius, QoS guarantees, topic-graph scalability |
| Validation | Event-grouped 5-fold cross-validation | Retrospective replay of two case studies (Cianjur 2022, Sumedang 2024) |

The arXiv preprint is publicly accessible to reviewers, ensuring that all numerical baselines cited in Tables III–VI of this manuscript can be independently verified without waiting for the *IEEE Access* decision. We believe this arrangement is consistent with IEEE author guidelines and with COPE best practices for companion submissions to non-overlapping venues. We will promptly update reference [30] with the *IEEE Access* DOI as soon as it is assigned.

## 4. Highlights reviewers may find noteworthy

- **Messaging-as-contribution** (Section III). Few peer-reviewed EEWS papers treat the inter-service substrate as a design element worthy of formal specification. Our topic tree, QoS policy, retention rules, ACL sketch, and Pydantic payload contracts (Section III-C, III-D, Appendix A) are intended to be directly reusable by other regional EEWS programmes.
- **Five-ADR log** (Section III-E). Every architectural decision is recorded with alternatives and consequences, supporting reproducibility and audit — a practice uncommon in EEWS papers.
- **Operational latency** (Section V-B, Table III). The end-to-end budget is decomposed into seven measurable services, each with an explicit millisecond ceiling. The sub-second Stage-0 budget at ≈ 630 ms is below the 1-s automation threshold cited in Cremen & Galasso (2020).
- **Blind-zone formalism** (Section V-C). We express the blind-zone radius in terms of the messaging substrate's dissemination budget $\Delta$, making messaging choices directly traceable to physical coverage — a formalism we believe is novel in the EEWS literature.
- **Per-site projection** (ADR-0005, Section IV-C, Section IX Table VI). The dedicated site projector service bridges regional architecture and per-building consumption at the edge with ~100× bandwidth savings for dense urban deployment.
- **Independent Java-Sunda case studies** (Section V-F). Retrospective analysis of the 2022 Cianjur and 2024 Sumedang earthquakes — both inside the ~11 km near-field radius — confirms the operational envelope.

## 5. Suggested reviewers

We offer the following names as suggested reviewers without conflicts of interest. None are co-authors, collaborators within the last 36 months, or current/former students of the submitting team.

1. **Prof. Carmine Galasso** — UCL, London, UK · expertise: EEWS, performance-based earthquake engineering · c.galasso@ucl.ac.uk
2. **Prof. Yih-Min Wu** — National Taiwan University · expertise: hybrid EEWS, P-Alert network · drymwu@ntu.edu.tw
3. **Prof. Simone Marzorati** — INGV / Università Politecnica delle Marche, Italy · expertise: cloud-IoT EEWS · s.marzorati@univpm.it
4. **Prof. Pál Varga** — Budapest University of Technology and Economics · expertise: MQTT for mission-critical IoT · pvarga@tmit.bme.hu

## 6. Authorship and ethics declaration

All four authors contributed substantively to the conception, design, and documentation of the architecture. HAN led the systems design and writing; DD contributed physics-informed feature engineering and validation protocol; AHS advised on the ML cascade and reproducibility strategy; SP supplied the operational BMKG InaTEWS context and the case-study hypocentres. The manuscript has not been previously published, is not under consideration at any other journal besides this submission, and — as disclosed in §3 — is the companion architecture paper to an independently scoped IDA-PTW methods paper. No new primary human-subject or animal-subject data were collected. All computations are non-destructive read-only uses of the BMKG InaTEWS archive, carried out under the informal research agreement between Universitas Indonesia and BMKG.

We thank you in advance for considering our manuscript and look forward to the reviewers' feedback.

Yours sincerely,

Hanif Andi Nugraha
on behalf of the authors (D. Djuhana, A. H. Saputro, S. Pramono)

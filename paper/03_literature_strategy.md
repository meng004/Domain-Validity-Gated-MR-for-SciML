# Phase 1 文献策略与种子文献矩阵

> Target journal: Information and Software Technology (IST), regular research paper track
> Status: seed corpus; expand before writing Related Work
> Date: 2026-06-02; v2.1 target update: 2026-06-04

## 1. 文献检索目标

本阶段服务于三个写作目标：

1. 证明本文属于 software testing / V&V / metamorphic testing 对话，而不是 CFD 模型论文。
2. 找出 MR identification 的已有路线，明确本文和 METRIC、MR-Scout、GenMorph、LLM-based MR inference 等工作的差异；SimiMR 属本组相关工作，使用时需标注自引属性。
3. 为圆柱绕流神经代理模型 case study 提供科学 ML 和物理语义依据。

## 2. 检索主题

### Theme A: Test Oracle Problem and Metamorphic Testing Foundations

Search strings:

```text
"test oracle problem" "software testing" survey
"metamorphic testing" survey "IEEE Transactions on Software Engineering"
"metamorphic testing" "oracle problem" "software testing"
```

Seed papers:

| ID | Paper | Role in paper |
|---|---|---|
| A1 | Barr et al., "The Oracle Problem in Software Testing: A Survey", IEEE TSE, 2015, DOI: 10.1109/TSE.2014.2372785 | Establishes oracle problem as a central SE testing problem. |
| A2 | Segura et al., "A Survey on Metamorphic Testing", IEEE TSE, 2016, DOI: 10.1109/TSE.2016.2532875 | Establishes MT scope, applications, and limitations. |
| A3 | Chen, Cheung, and Yiu, "Metamorphic testing: a new approach for generating next test cases", HKUST technical report, 1998 | Historical origin of MT. |

Gap to extract:

- MT is a relational oracle technique, but its effectiveness depends on the quality and identification of MRs.

### Theme B: MR Identification and Generation

Search strings:

```text
"metamorphic relation identification" "category-choice"
"metamorphic relation recommendation" semantic similarity
"automatically generating metamorphic relations" genetic programming
"LLM" "metamorphic relation inference"
```

Seed papers:

| ID | Paper | Role in paper |
|---|---|---|
| B1 | Chen, Poon, and Xie, "METRIC: METamorphic Relation Identification based on the Category-choice framework", JSS, 2016, DOI: 10.1016/j.jss.2015.07.037 | Main baseline for systematic MR identification from specifications. |
| B2 | Zhao et al., "A metamorphic relation recommendation method utilizing program syntax and semantic similarity", Journal of King Saud University - Computer and Information Sciences, 2026 | Related self-citation; useful for positioning semantic-similarity MR recommendation, but not an external baseline. |
| B3 | Ayerdi et al., "GenMorph: Automatically Generating Metamorphic Relations via Genetic Programming", IEEE TSE, 2024, DOI: 10.1109/TSE.2024.3407840 | Automated MR generation baseline. |
| B4 | "Towards metamorphic testing with LLM-based workflows: Metamorphic relation inference and follow-up test case generation", IST, 2026 | Recent LLM workflow direction; useful for positioning what this paper does not claim. |
| B5 | Blasi et al., "MeMo: Automatically identifying metamorphic relations in Javadoc comments for test automation", JSS, 2021, DOI: 10.1016/j.jss.2021.111041 | Specification/comment mining baseline. |

Gap to extract:

- Existing methods improve systematicity or automation, but physical semantic validity still requires domain interpretation.
- Current approaches often handle algorithmic, small-scale, specification-rich, or code/documentation-rich programs better than dependency-heavy scientific ML surrogate systems.

### Theme C: Scientific Software and Simulation V&V

Search strings:

```text
"metamorphic testing" "scientific software"
"metamorphic testing" "simulation models" "verification and validation"
"scientific software" "test oracle problem"
```

Seed papers:

| ID | Paper | Role in paper |
|---|---|---|
| C1 | Lin et al., "Exploratory Metamorphic Testing for Scientific Software", Computing in Science & Engineering, 2020, DOI: 10.1109/MCSE.2018.2880577 | Scientific software MT motivation. |
| C2 | Raunak and Olsen, "Metamorphic Testing on the Continuum of Verification and Validation of Simulation Models", MET 2021, DOI: 10.1109/MET52542.2021.00015 | Links MT to simulation V&V. |
| C3 | ASME V&V 20, "Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer", 2009, reaffirmed 2021 | CFD V&V context and terminology. |

Gap to extract:

- Simulation V&V recognizes oracle difficulty and validation needs, but neural surrogate testing needs executable relational assertions that connect physics to software tests.

### Theme D: Mesh-Based Neural Simulation and Cylinder Flow

Search strings:

```text
"Learning Mesh-Based Simulation with Graph Networks" cylinder flow
"MeshGraphNets" fluid dynamics cylinder flow
"flow around circular cylinder" "Strouhal number" benchmark
"Reynolds number" "Strouhal number" circular cylinder wake
```

Seed papers:

| ID | Paper | Role in paper |
|---|---|---|
| D1 | Pfaff et al., "Learning Mesh-Based Simulation with Graph Networks", ICLR 2021, arXiv:2010.03409, DOI: 10.48550/arXiv.2010.03409 | SUT family and scientific ML context. |
| D2 | Scarano and Poelma, "Three-dimensional vorticity patterns of cylinder wakes", Experiments in Fluids, 2009, DOI: 10.1007/s00348-009-0629-2 | Cylinder wake and vortex dynamics background. |
| D3 | Additional cylinder-flow benchmark papers | TODO: fill with 3-5 canonical fluid mechanics references before Related Work. |

Gap to extract:

- MeshGraphNets provides a strong scientific ML case, while cylinder flow provides rich physical invariants for MR construction.

### Theme E: Nearest Prior Work and v2.1 Theory Boundary

Search strings:

```text
"metamorphic testing" "hydrologic models" "machine learning"
"metamorphic testing" "ocean modeling" "physical symmetries"
"MR-Scout" "metamorphic relations" TOSEM
"neural fluid surrogates" equivariance evaluation
```

Seed papers:

| ID | Paper | Role in paper |
|---|---|---|
| E1 | Reichert et al., "Metamorphic testing of machine learning and conceptual hydrologic models", HESS, 2024 | Nearest prior work for physical-consistency MT of ML models; must differentiate by mesh-based GNN fluid surrogate, executable quantitative verdicts, and framework scope. |
| E2 | Hiremath et al. ocean-model MT papers, arXiv 2009.01554 / 2103.09782 / 2206.05457 | Nearest prior work for physics-symmetry MR identification in numerical models; must differentiate by neural surrogate target and non-symmetry blocks. |
| E3 | MR-Scout, TOSEM 2024 | External automated MR identification/generation baseline and related work. |
| E4 | 2026 neural-fluid-surrogate equivariance evaluation papers | Emerging competitor class; must distinguish symmetry-only metric evaluation from executable MR verdicts and failure localization. |
| E5 | NOETHER arXiv:2605.17390 and Yang et al. 2020 hierarchical classification model | Theory base for v2.1; cite self-containedly and disclose self-citation status. |

## 3. Inclusion Criteria

- Peer-reviewed journal/conference papers, recognized standards, or authoritative technical reports.
- Must directly support one of: oracle problem, MT foundations, MR identification/generation, scientific software V&V, mesh-based neural simulation, cylinder-flow physics.
- For current MR generation / LLM workflow papers, include 2024-2026 papers when DOI or publisher page can be verified.

## 4. Exclusion Criteria

- Papers that only use ML for CFD accuracy improvement without testing/V&V relevance.
- Generic AI testing papers with no metamorphic testing, oracle, or V&V component.
- Unverified references from AI-generated bibliographies.
- Low-quality or predatory venues unless used only as non-authoritative background and explicitly marked.

## 5. Related Work Structure for IST

Recommended order:

1. Test oracle problem and MT.
2. MR identification / generation.
3. Physical-consistency MT and scientific-software MT prior work.
4. V&V for simulation and scientific ML.
5. Mesh-based neural simulation and cylinder flow as case-study domain.
6. NOETHER + hierarchical MR classification as v2.1 theory base, written self-containedly for IST.

This order keeps software testing as the primary conversation and introduces CFD only after the testing gap is established.

## 6. Literature Matrix Tasks

- [ ] Verify full bibliographic metadata for all seed papers.
- [ ] Add 3-5 STVR/JSS/TSE papers on MR quality, MR selection, and MT effectiveness.
- [ ] Add 3-5 scientific ML / neural simulation testing papers beyond MeshGraphNets.
- [ ] Add 3-5 cylinder-flow physics references, especially Re-St and Strouhal behavior.
- [ ] Build a `paper/references.bib` file only after all entries are verified.

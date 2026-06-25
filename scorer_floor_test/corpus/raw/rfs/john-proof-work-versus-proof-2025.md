---
title: "Proof-of-Work versus Proof-of-Stake: John, Rivera & Saleh (2025)"
description: >-
  Distilled: John, Rivera, and Saleh develop an equilibrium model showing that
  Proof-of-Stake blockchains generate higher security than equivalent
  Proof-of-Work blockchains under real-world parameter values, and that this
  advantage is particularly salient at high scale. Review of Financial Studies
  2025, paywalled. Eight core results with source locators, the model equations,
  and the method.
sidebar:
  label: John-Rivera-Saleh 2025
  order: 1
tags: [paper-summary, blockchain, fintech, cryptocurrency, defi, theory,
       structural, peer-reviewed, unreplicated]
paper:
  authors: Kose John, Thomas J. Rivera, Fahad Saleh
  authorList:
    - { family: John, given: Kose, orcid: "0000-0003-2854-7545", affiliation: Stern School of Business, New York University }
    - { family: Rivera, given: Thomas J., orcid: "0000-0002-8863-2090", affiliation: Desautels Faculty of Management, McGill University }
    - { family: Saleh, given: Fahad, orcid: "0000-0003-1652-5189", affiliation: University of Florida }
  year: 2025
  venue: The Review of Financial Studies 38(7), 2025, 1955-2004
  venueShort: Rev. Fin. Stud. 2025
  doi: 10.1093/rfs/hhaf013
  jel:
    codes: [G10, G23, O33]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Law, Economics, and Judicial Systems", "Digital Economy and Work Transformation", "Merger and Competition Analysis"]
  dataAccess: public
  outcome:
    - equilibrium blockchain security (survival probability against attack)
    - equilibrium blockchain adoption (user cutoff)
    - blockchain security advantage of PoS over PoW at scale
  outcomeClass: [asset-prices, macro-aggregates]
  license: "OUP standard publication reuse rights (paywalled; license URL: https://academic.oup.com/pages/standard-publication-reuse-rights; content-version vor, delay-in-days 0, start 2025-03-01, confirmed via Crossref 2026-06-06)"
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (OUP site, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 14

  methods:
    role: theory
    contributes: pow-vs-pos-security-model
    family: structural
    buildsFrom: [overlapping-generations, dynamic-general-equilibrium]

  contributionType: [new-theory, new-fact]

  mechanisms:
    - cost-of-capital
    - protocol-design

  scope:
    region: theoretical
    assetClass: blockchain cryptoassets

  relatesTo:
    - { cite: "Pagnotta (2022)", relation: builds-on, note: "Adopts Pagnotta's (2022) security framework: attack succeeds if attacker gains control over validation; blockchain inoperable after a successful attack." }
    - { cite: "Hinzen, John, and Saleh (2022)", doi: '10.1016/j.jfineco.2022.01.003', relation: builds-on, note: "Builds on Hinzen, John, and Saleh (2022) model of blockchain adoption to incorporate protocol-specific security analysis." }
    - { cite: "Huberman, Leshno, and Moallemi (2021)", doi: '10.1093/restud/rdab014', relation: builds-on, note: "Adopts cutoff equilibrium structure from Huberman, Leshno, and Moallemi (2021)." }
    - { cite: "Saleh (2021)", relation: extends, note: "Saleh (2021) shows PoS is sustainable without block rewards; this paper adds comparative security analysis against PoW." }
    - { cite: "Nakamoto (2008)", relation: cites, note: "Nakamoto (2008) paper defines the 51% attack mechanism that underlies the PoW attack model." }

  openQuestions:
    - "The paper does not model partial attacks or partial disruption; a successful attack renders the blockchain permanently inoperable (pp. 1967-1968). Future work could relax this assumption."
    - "The DeFi application is modeled as an exogenous return; a richer model of endogenous DeFi competition between PoW and PoS could alter the comparative statics (p. 1966)."
    - "The model treats the PoS attacker leverage parameter lambda as approximately 1 in practice; future lending market development may change this and weaken the PoS security advantage (pp. 1980-1982)."

  replicationCode:
    url: "https://doi.org/10.7910/DVN/5VTIMI"
    status: available

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: "Full text read (pp. 1955-2004 plus appendices); eight results extracted from the PDF. Not human-verified. Not reproduced. Replication code at Harvard Dataverse (https://doi.org/10.7910/DVN/5VTIMI) has not been run here."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; fixed TL;DR leverage bound (353% -> 453%, per Corollary 1 p. 1984), removed spurious noisy-rational-expectations from buildsFrom, removed identification field (role: theory), replaced wrong mechanisms (information-asymmetry/behavioral-bias) with cost-of-capital/protocol-design, corrected Saleh (2021) relation from contradicts to extends. outcomeClass [asset-prices, macro-aggregates] flagged as weak fit but left pending human review. findings[] absent (not required by distiller version). All eight proposition locators verified correct."

  licenceVerification:
    - source: Crossref REST API works/10.1093/rfs/hhaf013
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=https://academic.oup.com/pages/standard-publication-reuse-rights, delay-in-days=0, start=2025-03-01; OUP standard reuse rights, not CC, paywalled"

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the model it builds, and the propositions it derives: enough to know what it found and how, without reading all 50 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1093/rfs/hhaf013).

**Related literature.** The paper builds on Pagnotta (2022) (blockchain security via a crisis-of-confidence attack model), Hinzen, John, and Saleh (2022) (limited adoption model for Bitcoin), and Huberman, Leshno, and Moallemi (2021) (cutoff equilibrium structure for blockchain users). It extends Saleh (2021) (PoS sustainability) by providing the first comparative security analysis across protocols, and adopts Nakamoto (2008)'s 51% attack definition as the baseline PoW attack model.

## TL;DR

John, Rivera, and Saleh compare equilibrium security across Proof-of-Work (PoW) and Proof-of-Stake (PoS) blockchains in a unified OLG model. They derive a general condition (Proposition 3, eq. 52) showing that PoS is more (less) secure than PoW when the relative cost to attack PoS exceeds (falls below) a threshold. Applying real-world parameter estimates for mining depreciation (46.5%-89% annually) and DeFi returns (3.73%-4.85% annually), they show that the sufficient condition for PoS security dominance is met for any attacker leverage up to 453%-568% above PoW, a level far beyond what current overcollateralized lending markets permit. They also show that PoS's security advantage is particularly salient at high scale: scaling generates full insecurity for PoW at lower scale than PoS, and achieves full security for PoS at lower scale than PoW.

## Core results

Magnitudes and significance are as reported. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | PoS generates higher validation investment than PoW for all model parameters because stakers avoid depreciation and energy costs | Proposition 3, eq. 52-53, p. 1979; Section 3, p. 1979 | PoS validation investment exceeds PoW whenever PoW and PoS generate identical validator revenues; ratio given by threshold zeta = [e^{-2rho} psi] / [e^{-2rho} psi + 1 - (1-delta)/(1+kappa_h)] <= 1 |
| R2 | Under real-world parameters (delta_1Y in [46.5%, 89%]; psi_1Y in [3.73%, 4.85%]) PoS generates higher equilibrium security than PoW | Corollary 1, p. 1984-1985; Tables 1-2, pp. 1983-1984 | PoS more secure than PoW whenever lambda <= 453% (most conservative) or lambda <= 568% (less conservative); lambda approx 1 in practice so condition is always satisfied |
| R3 | The PoS security advantage requires only mining hardware depreciation (delta_1Y) > DeFi return (psi_1Y) and a standard supermajority threshold (eta <= 2/3) | Proposition 4, eq. 54-55, p. 1980; Remark 1, p. 1981 | Sufficient condition: lambda <= (1/2)(1 + log(1+delta_T)/log(1+psi_T)); horizon-invariant per eq. 55 |
| R4 | Scaling generates full insecurity (pi^p = 0) for a larger set of attacker benefits under PoW than under PoS | Proposition 5, eq. 57, p. 1986; Section 4.1 | Sigma_0^{PoS} subset of Sigma_0^{PoW}: the set of attacker benefits generating full insecurity at scale is weakly larger for PoW |
| R5 | PoW becomes fully insecure at lower scale than PoS for any fixed maximal attacker benefit | Proposition 6, eq. 59, p. 1987 | Lambda_0^{PoS} >= Lambda_0^{PoW}: the scale at which PoW loses positive security is weakly lower than for PoS |
| R6 | Scaling generates full security (pi^p = 1) for a larger set of attacker benefits under PoS than under PoW | Proposition 7, eq. 64, p. 1989; Section 4.2 | Sigma_1^{PoW} subset of Sigma_1^{PoS}: scaling achieves full security for PoS in cases where it does not for PoW |
| R7 | PoS achieves full security at lower scale than PoW for any fixed maximal attacker benefit | Proposition 8, eq. 66, p. 1990 | Lambda_1^{PoS} <= Lambda_1^{PoW}: PoS reaches full security at a weakly lower scale than PoW |
| R8 | Equilibrium user fees decrease in blockchain scale and go to zero as scale grows, reducing validator revenues and undermining security; this negative effect is more acute for PoW than PoS | eq. 60, p. 1987; Section 4, pp. 1985-1991 | f^p_{(i,t)} = (c_{(i,t)} / Lambda) integral_0^{c_{(i,t)}} x dG(x); fee decreases in Lambda (1/Lambda factor); the two scaling effects on security (fee reduction vs. adoption increase) favor PoS more broadly |

**Overall (paper's conclusion).** Under current real-world conditions, PoS blockchains are more secure than equivalent PoW blockchains for any realistic scale. The security advantage of PoS relative to PoW is particularly salient at high scale: PoW is rendered fully insecure at lower scale, and PoS reaches full security at lower scale, than the respective counterpart. The results provide a formal foundation for understanding blockchain protocol design in the tokenomics and decentralized finance context.

## Theory / model

The paper models a single blockchain as either PoW or PoS. The economy is populated by overlapping generations of agents, each living three periods.

**Users.** Each generation-$$t$$ agent $$i \in [0,1]$$ possesses a unit endowment and has utility:

$$
\mathcal{U}^p_{(i,t)} = \max\{U^p_{(i,t)}, 1+\sigma\} \tag{1}
$$

where $$1+\sigma$$ is the outside option return (p. 1961) and $$U^p_{(i,t)}$$ is the expected utility from adopting the blockchain under protocol $$p \in \{PoW, PoS\}$$. An agent adopts if and only if her wait disutility cost $$c_{(i,t)}$$ falls below a cutoff $$c^p$$, determined in equilibrium. The agent allocates her endowment between DeFi investment (fraction $$1-\omega^p$$) and blockchain validation (fraction $$\omega^p$$) to maximize:

$$
\omega^p_{(i,t)} = \arg\max_{\omega \in [0,1]} \omega \cdot \mathbb{E}_t[R^p_t] + (1-\omega) \cdot \mathbb{E}_t[R^{DeFi}_t] \tag{2}
$$

where $$R^p_t$$ is the period $$t$$ to $$t+2$$ return from validation and $$R^{DeFi}_t = \frac{P_{t+2}}{P_t} \cdot (1+\psi)$$ is the DeFi return, with $$\psi$$ the gross DeFi return and $$P_t$$ the cryptoasset price (p. 1966, eq. 11).

**Wait disutility and fees.** The blockchain has transaction rate $$\Lambda > 0$$. User $$i$$ pays a fee $$f^p_{(i,t)} \geq 0$$ to prioritize processing. The expected wait time when paying fee $$f$$ given others' fees $$f_{-(i,t)}$$ is (p. 1963, eq. 6):

$$
W^p(f, f_{-(i,t)}) = \frac{1}{\Lambda} \times \int \mathbf{1}\{f^p_{(j,t)} \leq f\} \, dG(c_{(j,t)}) \tag{6}
$$

Each adopting agent optimally solves:

$$
f^p_{(i,t)} = \arg\max_{f \geq 0} \left[ \Pi^p_{(i,t)} - f - c_{(i,t)} \cdot W^p(f, f_{-(i,t)}) \right] \tag{4}
$$

and the equilibrium fee function satisfies $$f^p_{(i,t)} = \frac{c_{(i,t)}}{\Lambda} \int_0^{c_{(i,t)}} x \, dG(x)$$ for adopters (Lemma 1, eq. 33, p. 1975).

**Blockchain cryptoasset supply.** The total supply follows:

$$
M_{t+1} = M_t e^{\rho}, \qquad B_t = M_t(e^{\rho}-1) \tag{7-8}
$$

where $$\rho \geq 0$$ is the asset growth rate and $$B_t$$ is the block reward distributed in period $$t$$ (p. 1963).

**PoW validation return.** A miner born in period $$t$$ buys mining hardware at upfront cost per unit hash power $$1+\kappa_h$$ (energy plus equipment), mines in period $$t+1$$, and liquidates equipment at depreciated value $$1-\delta$$ (p. 1964). The lifetime return to mining is (eq. 9, p. 1965):

$$
R^{PoW}_t = \frac{H_{t+1}(1-\delta) + \left(B_{t+1} + \frac{\int f^{PoW}_{(i,t-1)} dG(c_{(i,t-1)})}{P^{PoW}_{t+1}}\right) P^{PoW}_{t+2}}{H_{t+1}(1+\kappa_h)} \tag{9}
$$

where $$H_{t+1}$$ is aggregate hash power, $$B_{t+1}$$ are block rewards, and $$\delta \in [0,1]$$ is hardware depreciation. The key feature is that miners must pay both energy ($$\kappa_h$$) and equipment depreciation ($$\delta$$) costs, making PoW validation more expensive than PoS staking.

**PoS validation return.** A staker born in period $$t$$ purchases coins at price $$P^{PoS}_t$$, stakes them in period $$t+1$$, and liquidates in $$t+2$$. Letting $$S_{t+1}$$ be total staked capital (p. 1966, eq. 10):

$$
R^{PoS}_t = \frac{S_{t+1} P^{PoS}_{t+2} + \left(B_{t+1} + \frac{\int f^{PoS}_{(i,t-1)} dG(c_{(i,t-1)})}{P^{PoS}_{t+1}}\right) P^{PoS}_{t+2}}{S_{t+1} P^{PoS}_{t+2}} \tag{10}
$$

Crucially, stakers recover their principal $$S_{t+1} P^{PoS}_{t+2}$$ in full (no depreciation, no energy cost), so only the opportunity cost of foregone DeFi investment matters.

**Attacker.** A malicious agent draws benefit $$\Gamma_t \sim U[0, \bar\Gamma]$$ from disrupting the blockchain each period, and solves (p. 1967, eq. 12):

$$
\max_{A_t \geq 0} \Gamma_t \cdot \nu^p_{t+1}(A_t) - A_t \tag{12}
$$

where $$\nu^p_{t+1}(A_t)$$ is the probability of a successful attack given resources $$A_t$$. For PoW, success requires $$A_t \geq H_{t+1}(1+\kappa_h)$$ (51% attack, eq. 13). For PoS, success requires acquiring and staking a fraction $$1-\eta$$ of total staked coins, i.e., $$A_t \geq \alpha \cdot S_{t+1}$$, where $$\alpha := \frac{1-\eta}{\lambda \eta} \in [0,1]$$ is the relative cost of attacking PoS (eqs. 15-17, p. 1969-1970).

## Method

The paper derives closed-form stationary cutoff equilibria for both protocols. The solution method is: (1) solve for optimal fees (Lemma 1), (2) derive the equilibrium return to validation for each protocol (Propositions 1 and 2), (3) characterize the equilibrium adoption cutoff $$c^p$$ as the supremum of cutoffs at which all agents with $$c < c^p$$ prefer the blockchain to the outside option, and (4) compare survival probabilities $$\pi^p$$ across protocols.

**PoW equilibrium** (Proposition 1, pp. 1975-1977). The equilibrium fraction of wealth invested in mining is (eq. 34):

$$
\omega^{PoW}(c^{PoW}) := \min\left\{\frac{(1-e^{-2\rho})G(c^{PoW}) + fees(c^{PoW})}{G(c^{PoW})\left(e^{-2\rho}\psi + 1 - \frac{1-\delta}{1+\kappa_h}\right)}, 1\right\} \tag{34}
$$

The equilibrium hash power and survival probability (eqs. 36, 38-39):

$$
H^\*(1+\kappa_h) = \min\left\{\frac{(1-e^{-2\rho})G(c^{PoW}) + fees(c^{PoW})}{e^{-2\rho}\psi + 1 - \frac{1-\delta}{1+\kappa_h}}, G(c^{PoW})\right\} \tag{36}
$$

$$
\pi^{PoW} = \min\left\{\frac{H^\*(1+\kappa_h)}{\bar\Gamma}, 1\right\} \tag{38}
$$

**PoS equilibrium** (Proposition 2, pp. 1977-1978). The equilibrium staked capital and survival probability (eqs. 45, 47-48):

$$
S^\*(c^{PoS}) = \min\left\{\frac{(1-e^{-2\rho})G(c^{PoS}) + fees(c^{PoS})}{e^{-2\rho}\psi}, G(c^{PoS})\right\} \tag{45}
$$

$$
\pi^{PoS} = \min\left\{\frac{\alpha \cdot S^\*}{\bar\Gamma}, 1\right\} \tag{47}
$$

**Key comparison threshold.** Proposition 3 (eq. 52-53) derives the threshold:

$$
\zeta := \frac{e^{-2\rho}\psi}{e^{-2\rho}\psi + 1 - \frac{1-\delta}{1+\kappa_h}} \leq 1 \tag{53}
$$

Then $$\alpha \leq \zeta \Rightarrow \pi^{PoW} \geq \pi^{PoS}$$ and $$\alpha \geq \zeta \Rightarrow \pi^{PoS} \geq \pi^{PoW}$$. Because $$\zeta \leq 1$$ always holds, PoS validation investment exceeds PoW investment whenever both generate the same revenues. Whether this advantage overcomes PoS's lower attack threshold ($$\alpha \leq 1$$) depends on which side of $$\zeta$$ the parameter $$\alpha$$ lies.

**Sufficient condition (Proposition 4).** If the PoS supermajority threshold $$\eta \leq 2/3$$ and annual depreciation $$\delta_{1Y} > \psi_{1Y}$$ (DeFi return), then the condition $$\alpha \geq \zeta$$ holds whenever (eq. 54):

$$
\lambda \leq \frac{1}{2}\left(1 + \frac{\log(1+\delta_T)}{\log(1+\psi_T)}\right) \tag{54}
$$

This is horizon-invariant because $$\frac{\log(1+\delta_T)}{\log(1+\psi_T)} = \frac{\log(1+\delta_{1Y})}{\log(1+\psi_{1Y})}$$ for all $$T$$.

## Empirical specifications

The paper is a theory paper with no regression specifications. The calibration in Section 3.3 provides real-world parameter estimates, comparing the model's sufficient condition to data.

**Mining equipment depreciation** (Table 1, p. 1983). Using theblock.co ASIC price index (three efficiency tiers, August 2021-August 2023), the paper documents average annual price declines of 60.4%-66.38% across all tiers. Academic sources (Prat and Walter 2021: 47.7%-61.3%; De Vries and Stoll 2021: 46.5%-89%; Stinner 2021: 61.45%) confirm $$\delta_{1Y} \in [46.5\%, 89\%]$$.

**DeFi return estimates** (Table 2, p. 1984; Table 3, p. 1985). Using Compass Financial Technologies daily ETH staking return data (October 2023 to June 2024): average $$\psi_{1Y} = 4.32\%$$ (min 3.73%, max 4.85%). AAVE lending data (Chaudhary, Kozhan, and Vishwanath-Natraj 2023) gives 0.13%-2.28% for ETH and up to 8.957% for USDC. All estimates satisfy $$\delta_{1Y} > \psi_{1Y}$$ over the entire range.

**Parameter bounds.** Applying the most conservative values ($$\delta_{1Y} = 46.5\%$$, $$\psi_{1Y} = 4.85\%$$) to eq. 54 gives $$\lambda \leq 453\%$$. Less conservative values ($$\delta_{1Y} = 55\%$$, $$\psi_{1Y} = 4.32\%$$) give $$\lambda \leq 568\%$$. Since current lending markets are overcollateralized and $$\lambda \approx 1$$ in practice, the sufficient condition is always satisfied (Corollary 1, pp. 1984-1985).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| theblock.co ASIC Price Index (three efficiency tiers, Aug 2021-Aug 2023) | Estimate annual mining hardware depreciation rate $$\delta_{1Y}$$ | No page yet |
| Compass Financial Technologies daily ETH staking return data (Oct 2023-Jun 2024) | Estimate annual DeFi return $$\psi_{1Y}$$ for PoS staking | No page yet |
| AAVE ETH/USDC lending rate data (Chaudhary, Kozhan, Vishwanath-Natraj 2023) | Robustness estimate of $$\psi_{1Y}$$ via DeFi lending rates | No page yet |

Note: the core results are theoretical propositions derived from the equilibrium model; the datasets above are used only to calibrate model parameters and verify that the sufficient condition (eq. 54) holds under realistic values. The paper is primarily a theory paper with no econometric identification.

## When to read the full paper

Use the [original](https://doi.org/10.1093/rfs/hhaf013) if you are: (1) building a model of blockchain security or protocol design; (2) evaluating whether a PoW or PoS blockchain is more secure for a specific parameter range (the threshold $$\zeta$$ in eq. 53 is the key object); (3) studying DeFi ecosystem interactions with blockchain security; or (4) calibrating mining depreciation and DeFi yield parameters for a blockchain model. The proofs of all eight propositions are in Appendix B (pp. 1994-2002); replication code is at https://doi.org/10.7910/DVN/5VTIMI.

## Attribution and rights

Source: peer-reviewed, *The Review of Financial Studies* 38(7), 2025. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The paper is paywalled; reproduction rights follow OUP standard publication reuse rights. Extract-only.

> John, Kose, Thomas J. Rivera, and Fahad Saleh. "Proof-of-Work versus Proof-of-Stake: A Comparative Economic Analysis." *The Review of Financial Studies* 38, no. 7 (2025): 1955-2004. DOI: 10.1093/rfs/hhaf013.

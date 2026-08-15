<h1 align="center">Hi, I'm Abhinav Singh 👋</h1>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=20&pause=1000&color=58A6FF&center=true&vCenter=true&width=560&lines=AI%2FML+Developer;Agentic+AI+Builder;BITS+Pilani+CS+Undergrad;Building+Autonomous+Agents" alt="Typing SVG" />
</p>

CS Undergrad @ BITS Pilani | AI/ML Developer | GenAI • Agentic AI • Deep Learning • LLM Applications

<p align="center">
  🏆 <b>21 PRs merged upstream</b> — <a href="https://github.com/steipete/CodexBar">steipete/CodexBar</a> (19k+ ⭐, 13) · <a href="https://github.com/mem0ai/mem0">mem0ai/mem0</a> (62k+ ⭐, 3) · <a href="https://github.com/sktime/sktime">sktime/sktime</a> (9.9k+ ⭐, 2) · +3 more. Each one found by reading the code, reproduced with a failing test, then fixed. <a href="#-open-source-contributions">See the list →</a>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/OfficialAbhinavSingh/OfficialAbhinavSingh/main/neofetch-dark.svg">
    <img alt="Abhinav's neofetch card — Arch Linux + Hyprland, live GitHub stats" src="https://raw.githubusercontent.com/OfficialAbhinavSingh/OfficialAbhinavSingh/main/neofetch-light.svg">
  </picture>
</p>
<p align="center"><sub>auto-refreshed daily via <a href="https://github.com/OfficialAbhinavSingh/OfficialAbhinavSingh/blob/main/.github/workflows/live-update.yml">GitHub Actions</a> — real repo/star/follower/commit counts, no fake numbers</sub></p>

**Currently:**
- 🔭 Building **[DeepLense-AI-Scientist](https://github.com/OfficialAbhinavSingh/DeepLense-AI-Scientist)** — multi-agent framework orchestrating scientific workflows in gravitational lensing research (Pydantic AI)
- 🏆 Contributor on **[steipete/CodexBar](https://github.com/steipete/CodexBar)** (19k+ ⭐) — 13 PRs merged, incl. a macOS Keychain fix ([#2102](https://github.com/steipete/CodexBar/pull/2102)) and the `codexbar guard` CLI ([#2237](https://github.com/steipete/CodexBar/pull/2237))
- 🧩 Shipping fixes into **[mem0ai/mem0](https://github.com/mem0ai/mem0)** (62k+ ⭐), **[sktime/sktime](https://github.com/sktime/sktime)** (9.9k+ ⭐) and **[CodeGraphContext](https://github.com/CodeGraphContext/CodeGraphContext)** (4k+ ⭐) — scope-isolation, vector-store scoring, estimator test-parameter coverage, and graph-viz bugs, each with red→green regression tests
- ✉️ Invited by co-founder Nikhil Pareek to contribute to **[future-agi/future-agi](https://github.com/future-agi/future-agi)** — 4 PRs open on the LLM eval & observability platform

## 🌐 Socials

[![Instagram](https://img.shields.io/badge/Instagram-%23E4405F.svg?logo=Instagram&logoColor=white)](https://instagram.com/later_abhi) [![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)](https://linkedin.com/in/abhinavsingh7) [![Quora](https://img.shields.io/badge/Quora-%23B92B27.svg?logo=Quora&logoColor=white)](https://quora.com/profile/Abhinav-Singh-6901) [![Reddit](https://img.shields.io/badge/Reddit-%23FF4500.svg?logo=Reddit&logoColor=white)](https://reddit.com/user/Remarkable_Pepper774) [![X](https://img.shields.io/badge/X-black.svg?logo=X&logoColor=white)](https://x.com/@zenitsu_uchiha1) [![email](https://img.shields.io/badge/Email-D14836?logo=gmail&logoColor=white)](mailto:laterabhi1@gmail.com)

## 🚀 Featured Projects

| Project | What it does |
|---|---|
| [**bah2026-ps14**](https://github.com/OfficialAbhinavSingh/bah2026-ps14) | ISRO BAH 2026 PS14 — forecasts >2 MeV electron flux at GEO orbit 30–45min/6h/12h ahead via a 5-stage pipeline (persistence → RandomForest → LSTM/Transformer), validated against ISRO GRASP/GSAT |
| [**Proxim**](https://github.com/OfficialAbhinavSingh/Proxim) | Real-time AI HCP roleplay avatar trainer for pharma sales reps — live voice sessions, 3D avatar, post-call coaching scorecard |
| [**SQL-Query-Optimization-Environment**](https://github.com/OfficialAbhinavSingh/SQL-Query-Optimization-Environment) | RL environment where agents rewrite slow SQL, graded on real DuckDB execution timing + correctness across 5 anti-pattern task types |
| [**et-hackathon-ps7**](https://github.com/OfficialAbhinavSingh/et-hackathon-ps7) | AI platform detecting behavioral anomalies in network/host telemetry — not signature-based |

## 🔧 Open-Source Contributions

**⭐ [CodexBar](https://github.com/steipete/CodexBar)** (19k+ stars) — macOS menu bar app for AI usage tracking, by [Peter Steinberger](https://github.com/steipete) (creator of OpenClaw, ex-PSPDFKit founder) · **Contributor, 13 PRs merged**
- [#2102 fix: Claude no-prompt Keychain repair for missing credentials file](https://github.com/steipete/CodexBar/pull/2102) — merged, closes [#1975](https://github.com/steipete/CodexBar/issues/1975). Diagnosed a Keychain-access gate that blocked even guaranteed no-UI reads under "Avoid Keychain Prompts," shipped the fix with regression tests + a live macOS verification script, reviewed and merged by the maintainer.
- [#2237 feat: `codexbar guard` — quota-aware exit code to gate automation](https://github.com/steipete/CodexBar/pull/2237) — merged. Self-proposed feature: a CLI subcommand that exits non-zero when a provider's quota is spent, so scripts and CI can stop before burning a rate limit.
- [#2483 fix: validate LiteLLM and LLM Proxy base URLs before sending the API key](https://github.com/steipete/CodexBar/pull/2483) — merged. A malformed or attacker-supplied base URL was accepted as-is, so the configured key went out with the request; the URL is now validated first.
- Linux availability — merged: [#2475](https://github.com/steipete/CodexBar/pull/2475) (MiniMax with a configured API key), [#2356](https://github.com/steipete/CodexBar/pull/2356) (Alibaba/Qwen Token Plan with a manual cookie). Both providers were gated behind a macOS-only web-auth path even when the user had already supplied a credential the CLI could use.
- Usage-percent correctness series — merged: [#2255](https://github.com/steipete/CodexBar/pull/2255) (Cursor), [#2265](https://github.com/steipete/CodexBar/pull/2265) (Abacus), [#2293](https://github.com/steipete/CodexBar/pull/2293) (ElevenLabs), [#2342](https://github.com/steipete/CodexBar/pull/2342) (z.ai). Providers reporting over-quota or already-scaled values rendered as impossible percentages in the menu bar; each fix landed with a red→green test transcript in the PR body.
- Reset-countdown fixes — merged: [#2343](https://github.com/steipete/CodexBar/pull/2343) (a countdown of exactly 24h rendered as "24h" instead of rolling over to the day form, across four formatters), [#2335](https://github.com/steipete/CodexBar/pull/2335) (LLMProxy picked an already-elapsed timestamp as the *next* reset).
- OpenCode/OpenCodeGo percent unit double-scaling — a fraction heuristic also ran on the already-computed `used/limit` percent, so real usage under 1% got multiplied by 100. Fix landed in [#2331](https://github.com/steipete/CodexBar/pull/2331) ([commit](https://github.com/steipete/CodexBar/commit/bda63b9b3) authored by me).

**⭐ [mem0](https://github.com/mem0ai/mem0)** (62k+ stars) — universal memory layer for AI agents, by Mem0 (Y Combinator S24)
- [#6343 fix(ts-oss): don't let `update()` metadata overwrite user_id/agent_id/run_id](https://github.com/mem0ai/mem0/pull/6343) — merged. Caller metadata was spread over the scope identifiers, silently re-homing a memory to a different user/agent/run.
- [#6435 fix(vector-stores/baidu): convert L2 distance to similarity score in `search()`](https://github.com/mem0ai/mem0/pull/6435) — merged. Baidu VectorDB returned raw L2 distance where every other store returns a similarity, inverting relevance order and breaking score thresholds.
- [#6656 fix(memory): stop `add()` metadata from setting a memory's identity scope](https://github.com/mem0ai/mem0/pull/6656) — merged. Same class of bug as #6343, on the `add()` path instead of `update()`.
- Open: reranker candidate-pool fix ([#6449](https://github.com/mem0ai/mem0/pull/6449) Python / [#6537](https://github.com/mem0ai/mem0/pull/6537) TS), a hash-dedup TOCTOU race in `add()` ([#6516](https://github.com/mem0ai/mem0/pull/6516) Python / [#6532](https://github.com/mem0ai/mem0/pull/6532) TS), and two provider-config fixes ([#6302](https://github.com/mem0ai/mem0/pull/6302), [#6257](https://github.com/mem0ai/mem0/pull/6257)).

**⭐ [sktime](https://github.com/sktime/sktime)** (9.9k+ stars) — unified Python framework for time series ML, a NumFOCUS-affiliated project
- [#10656 [ENH] Add second test parameter set for PaddingTransformer](https://github.com/sktime/sktime/pull/10656) — merged. The transformer's test suite ran under a single parameter configuration, leaving a second valid config path unexercised by CI.
- [#10657 [ENH] Add second test parameter set for DilationMappingTransformer](https://github.com/sktime/sktime/pull/10657) — merged. Same coverage gap, different estimator.
- Open: [#10668](https://github.com/sktime/sktime/pull/10668) `EmpiricalDistributionForecaster`, a naive empirical-distribution forecaster requested on the project's public wishlist, [#10756](https://github.com/sktime/sktime/pull/10756) a second test parameter set for `RandomSamplesAugmenter`.

**⭐ [CodeGraphContext](https://github.com/CodeGraphContext/CodeGraphContext)** (4k+ stars) — MCP server + CLI that indexes local code into a graph database for AI assistant context
- [#1453 fix(viz): handle real FalkorDB Node/Edge shape in offline renderer](https://github.com/CodeGraphContext/CodeGraphContext/pull/1453) — merged. The offline graph renderer assumed a shape FalkorDB never actually returns, breaking visualization.
- [#1506 fix(viz): match LadybugDB's uppercase internal keys (_ID/_LABEL/_SRC/_DST)](https://github.com/CodeGraphContext/CodeGraphContext/pull/1506) — merged. Same renderer, a second backend with different key casing.

## 💻 Tech Stack

![Python](https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![TypeScript](https://img.shields.io/badge/typescript-3178C6?style=for-the-badge&logo=typescript&logoColor=white) ![Swift](https://img.shields.io/badge/swift-F54A2A?style=for-the-badge&logo=swift&logoColor=white) ![React](https://img.shields.io/badge/react-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) ![Rust](https://img.shields.io/badge/rust-000000?style=for-the-badge&logo=rust&logoColor=white) ![JavaScript](https://img.shields.io/badge/javascript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E) ![Shell](https://img.shields.io/badge/shell-4EAA25?style=for-the-badge&logo=gnu-bash&logoColor=white) ![Docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![PyTorch](https://img.shields.io/badge/pytorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white) ![Jupyter](https://img.shields.io/badge/jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white) ![DuckDB](https://img.shields.io/badge/duckdb-FFF000?style=for-the-badge&logo=duckdb&logoColor=black) ![Linux](https://img.shields.io/badge/linux-FCC624?style=for-the-badge&logo=linux&logoColor=black) ![GitHub](https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white)

## 📈 GitHub Stats

![](https://github-readme-stats.vercel.app/api?username=OfficialAbhinavSingh&theme=github_dark&hide_border=true&include_all_commits=true&count_private=true)
![](https://nirzak-streak-stats.vercel.app/?user=OfficialAbhinavSingh&theme=github-dark-blue&hide_border=true)

## 🔴 Recent Activity

<!--START_SECTION:activity-->
1. ❌ Closed PR [#30](https://github.com/OfficialAbhinavSingh/mergit-e2e-sandbox/pull/30) in [OfficialAbhinavSingh/mergit-e2e-sandbox](https://github.com/OfficialAbhinavSingh/mergit-e2e-sandbox)
2. 🎉 Merged PR [#16](https://github.com/mergit-io/Mergit-proto/pull/16) in [mergit-io/Mergit-proto](https://github.com/mergit-io/Mergit-proto)
3. 🎉 Merged PR [#18](https://github.com/mergit-io/Mergit-proto/pull/18) in [mergit-io/Mergit-proto](https://github.com/mergit-io/Mergit-proto)
4. 💪 Opened PR [#18](https://github.com/mergit-io/Mergit-proto/pull/18) in [mergit-io/Mergit-proto](https://github.com/mergit-io/Mergit-proto)
5. 🗣 Commented on [#26](https://github.com/OfficialAbhinavSingh/mergit-e2e-sandbox/pull/26#issuecomment-5294782392) in [OfficialAbhinavSingh/mergit-e2e-sandbox](https://github.com/OfficialAbhinavSingh/mergit-e2e-sandbox)
<!--END_SECTION:activity-->

## 🐍 Contribution Snake

![snake gif](https://raw.githubusercontent.com/OfficialAbhinavSingh/OfficialAbhinavSingh/output/github-contribution-grid-snake-dark.svg#gh-dark-mode-only)
![snake gif](https://raw.githubusercontent.com/OfficialAbhinavSingh/OfficialAbhinavSingh/output/github-contribution-grid-snake.svg#gh-light-mode-only)

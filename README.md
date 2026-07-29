<h1 align="center">Hi, I'm Abhinav Singh 👋</h1>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=20&pause=1000&color=58A6FF&center=true&vCenter=true&width=560&lines=AI%2FML+Developer;Agentic+AI+Builder;BITS+Pilani+CS+Undergrad;Building+Autonomous+Agents" alt="Typing SVG" />
</p>

CS Undergrad @ BITS Pilani | AI/ML Developer | GenAI • Agentic AI • Deep Learning • LLM Applications

<p align="center">
  🏆 <b>8 PRs merged upstream</b> — <a href="https://github.com/steipete/CodexBar">steipete/CodexBar</a> (19k+ ⭐, 5) · <a href="https://github.com/mem0ai/mem0">mem0ai/mem0</a> (61k+ ⭐, 2) · <a href="https://github.com/huggingface/OpenEnv">huggingface/OpenEnv</a> (1). Each one found by reading the code, reproduced with a failing test, then fixed. <a href="#-open-source-contributions">See the list →</a>
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
- 🏆 Contributor on **[steipete/CodexBar](https://github.com/steipete/CodexBar)** (19k+ ⭐) — 5 PRs merged, incl. a macOS Keychain fix ([#2102](https://github.com/steipete/CodexBar/pull/2102)) and the `codexbar guard` CLI ([#2237](https://github.com/steipete/CodexBar/pull/2237))
- 🧩 Shipping fixes into **[mem0ai/mem0](https://github.com/mem0ai/mem0)** (61k+ ⭐) and **[huggingface/OpenEnv](https://github.com/huggingface/OpenEnv)** — scope-isolation, vector-store scoring, and client API bugs, each with red→green regression tests

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

**⭐ [CodexBar](https://github.com/steipete/CodexBar)** (19k+ stars) — macOS menu bar app for AI usage tracking, by [Peter Steinberger](https://github.com/steipete) (creator of OpenClaw, ex-PSPDFKit founder) · **Contributor, 5 PRs merged**
- [#2102 fix: Claude no-prompt Keychain repair for missing credentials file](https://github.com/steipete/CodexBar/pull/2102) — merged, closes [#1975](https://github.com/steipete/CodexBar/issues/1975). Diagnosed a Keychain-access gate that blocked even guaranteed no-UI reads under "Avoid Keychain Prompts," shipped the fix with regression tests + a live macOS verification script, reviewed and merged by the maintainer.
- [#2237 feat: `codexbar guard` — quota-aware exit code to gate automation](https://github.com/steipete/CodexBar/pull/2237) — merged. Self-proposed feature: a CLI subcommand that exits non-zero when a provider's quota is spent, so scripts and CI can stop before burning a rate limit.
- Usage-percent correctness series — merged: [#2255](https://github.com/steipete/CodexBar/pull/2255) (Cursor), [#2265](https://github.com/steipete/CodexBar/pull/2265) (Abacus), [#2293](https://github.com/steipete/CodexBar/pull/2293) (ElevenLabs). Providers reporting over-quota or already-scaled values rendered as impossible percentages in the menu bar; each fix landed with a red→green test transcript in the PR body.
- OpenCode/OpenCodeGo percent unit double-scaling — a fraction heuristic also ran on the already-computed `used/limit` percent, so real usage under 1% got multiplied by 100. Fix landed in [#2331](https://github.com/steipete/CodexBar/pull/2331) ([commit](https://github.com/steipete/CodexBar/commit/bda63b9b3) authored by me).

**⭐ [mem0](https://github.com/mem0ai/mem0)** (61k+ stars) — universal memory layer for AI agents
- [#6343 fix(ts-oss): don't let `update()` metadata overwrite user_id/agent_id/run_id](https://github.com/mem0ai/mem0/pull/6343) — merged. Caller metadata was spread over the scope identifiers, silently re-homing a memory to a different user/agent/run.
- [#6435 fix(vector-stores/baidu): convert L2 distance to similarity score in `search()`](https://github.com/mem0ai/mem0/pull/6435) — merged. Baidu VectorDB returned raw L2 distance where every other store returns a similarity, inverting relevance order and breaking score thresholds.
- Open: reranker candidate-pool fix ([#6449](https://github.com/mem0ai/mem0/pull/6449) Python / [#6537](https://github.com/mem0ai/mem0/pull/6537) TS) and a hash-dedup TOCTOU race in `add()` ([#6516](https://github.com/mem0ai/mem0/pull/6516) Python / [#6532](https://github.com/mem0ai/mem0/pull/6532) TS).

**⭐ [OpenEnv](https://github.com/huggingface/OpenEnv)** (Hugging Face) — environment interface library for RL post-training
- [#959 feat(env-client): sync bootstrap constructors + public `base_url`](https://github.com/huggingface/OpenEnv/pull/959) — merged, closes [#935](https://github.com/huggingface/OpenEnv/issues/935). Made `from_docker_image` / `from_hub` usable from sync code and exposed the resolved base URL instead of forcing callers into private attributes.
- Open: [#1008](https://github.com/huggingface/OpenEnv/pull/1008) path traversal via agent-supplied names in `finqa_env`, [#1011](https://github.com/huggingface/OpenEnv/pull/1011) discovery cache moved out of world-writable `/tmp`, [#1006](https://github.com/huggingface/OpenEnv/pull/1006) execution-grounded DuckDB SQL-optimization environment.

## 💻 Tech Stack

![Python](https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![TypeScript](https://img.shields.io/badge/typescript-3178C6?style=for-the-badge&logo=typescript&logoColor=white) ![Swift](https://img.shields.io/badge/swift-F54A2A?style=for-the-badge&logo=swift&logoColor=white) ![React](https://img.shields.io/badge/react-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) ![Rust](https://img.shields.io/badge/rust-000000?style=for-the-badge&logo=rust&logoColor=white) ![JavaScript](https://img.shields.io/badge/javascript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E) ![Shell](https://img.shields.io/badge/shell-4EAA25?style=for-the-badge&logo=gnu-bash&logoColor=white) ![Docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![PyTorch](https://img.shields.io/badge/pytorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white) ![Jupyter](https://img.shields.io/badge/jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white) ![DuckDB](https://img.shields.io/badge/duckdb-FFF000?style=for-the-badge&logo=duckdb&logoColor=black) ![Linux](https://img.shields.io/badge/linux-FCC624?style=for-the-badge&logo=linux&logoColor=black) ![GitHub](https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white)

## 📈 GitHub Stats

![](https://github-readme-stats.vercel.app/api?username=OfficialAbhinavSingh&theme=github_dark&hide_border=true&include_all_commits=true&count_private=true)
![](https://nirzak-streak-stats.vercel.app/?user=OfficialAbhinavSingh&theme=github-dark-blue&hide_border=true)

## 🔴 Recent Activity

<!--START_SECTION:activity-->
1. 🗣 Commented on [#2475](https://github.com/steipete/CodexBar/pull/2475#issuecomment-5108973432) in [steipete/CodexBar](https://github.com/steipete/CodexBar)
2. 💪 Opened PR [#2483](https://github.com/steipete/CodexBar/pull/2483) in [steipete/CodexBar](https://github.com/steipete/CodexBar)
3. 🎉 Merged PR [#2335](https://github.com/steipete/CodexBar/pull/2335) in [steipete/CodexBar](https://github.com/steipete/CodexBar)
4. 🎉 Merged PR [#2342](https://github.com/steipete/CodexBar/pull/2342) in [steipete/CodexBar](https://github.com/steipete/CodexBar)
5. 🎉 Merged PR [#2343](https://github.com/steipete/CodexBar/pull/2343) in [steipete/CodexBar](https://github.com/steipete/CodexBar)
<!--END_SECTION:activity-->

## 🐍 Contribution Snake

![snake gif](https://raw.githubusercontent.com/OfficialAbhinavSingh/OfficialAbhinavSingh/output/github-contribution-grid-snake-dark.svg#gh-dark-mode-only)
![snake gif](https://raw.githubusercontent.com/OfficialAbhinavSingh/OfficialAbhinavSingh/output/github-contribution-grid-snake.svg#gh-light-mode-only)

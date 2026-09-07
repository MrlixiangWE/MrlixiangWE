<h1 align="center">Hi, I'm Lee</h1>

<p align="center">
  Inference systems and AI infrastructure. I work on the runtime side of multimodal model serving:
  attention dispatch, KV/weight transfer, LoRA and CUDA-graph lifecycles, and the measurements that prove a change is real.
</p>

<p align="center">
  <a href="mailto:mrdanaer@gmail.com"><img src="https://img.shields.io/badge/mrdanaer%40gmail.com-D14836?style=flat-square&logo=gmail&logoColor=white" alt="email"></a>
  <a href="https://github.com/vllm-project/vllm-omni/pulls?q=is%3Apr+author%3AMrlixiangWE"><img src="https://img.shields.io/badge/vLLM--Omni-contributor-4B8BBE?style=flat-square&logo=github&logoColor=white" alt="vllm-omni"></a>
  <a href="https://github.com/pytorch/helion/pulls?q=is%3Apr+author%3AMrlixiangWE"><img src="https://img.shields.io/badge/PyTorch%20Helion-contributor-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" alt="helion"></a>
  <a href="https://github.com/apache/otava/pulls?q=is%3Apr+author%3AMrlixiangWE"><img src="https://img.shields.io/badge/Apache%20Otava-contributor-D22128?style=flat-square&logo=apache&logoColor=white" alt="otava"></a>
</p>

## Contribution graph

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="profile-3d-contrib/dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="profile-3d-contrib/light.svg">
  <img src="profile-3d-contrib/light.svg" alt="3D contribution calendar" width="100%">
</picture>

## Upstream work

<!-- PRS:START -->
8 merged, 6 open, across `apache/bifromq`, `apache/otava`, `areal-project/AReaL`, `pytorch/helion`, `vllm-project/vllm-ascend`, `vllm-project/vllm-omni`

| Repository | Pull request | Status |
|---|---|---|
| vllm-project/vllm-omni | [#7094](https://github.com/vllm-project/vllm-omni/pull/7094) [Perf][Diffusion] Run MammothModa2 DiT attention through the shared attention layer | open |
| apache/otava | [#179](https://github.com/apache/otava/pull/179) Define the public API in otava/__init__.py | open |
| areal-project/AReaL | [#1676](https://github.com/areal-project/AReaL/pull/1676) perf(engine): encode each distinct image once per vision-tower forward | open |
| vllm-project/vllm-omni | [#6516](https://github.com/vllm-project/vllm-omni/pull/6516) [Model] Support SenseNova-U1.5-8B-MoT and its distilled 8-step LoRA | merged |
| pytorch/helion | [#3450](https://github.com/pytorch/helion/pull/3450) [compiler] Allow torch.matmul rank broadcasting; add sparse-attention indexer example | merged |
| vllm-project/vllm-omni | [#6317](https://github.com/vllm-project/vllm-omni/pull/6317) [Perf][Bugfix][OmniVoice] Restore float16 serving, and fuse the generator hot loop | merged |
| vllm-project/vllm-omni | [#6286](https://github.com/vllm-project/vllm-omni/pull/6286) [Model] Serve OpenVLA-7B as an autoregressive robot policy | open |
| apache/otava | [#169](https://github.com/apache/otava/pull/169) Make AnalyzedSeries change points lazy properties | merged |
| vllm-project/vllm-omni | [#6172](https://github.com/vllm-project/vllm-omni/pull/6172) [Bugfix] Stop reading the removed OmniRequestOutput.request_output accessor | merged |
| vllm-project/vllm-omni | [#6152](https://github.com/vllm-project/vllm-omni/pull/6152) [Bugfix] Carry ec_transfer_params and num_cache_creation_tokens on OmniRequestOutput | merged |
| vllm-project/vllm-omni | [#6111](https://github.com/vllm-project/vllm-omni/pull/6111) [Bugfix] Route text-only chat as per-request comprehension in HunyuanImage3 AR sampler | open |
| vllm-project/vllm-ascend | [#14110](https://github.com/vllm-project/vllm-ascend/pull/14110) [BugFix] Fix KeyError when remote_cached_tokens is missing in SFA PD RD2H producer | open |
| apache/bifromq | [#273](https://github.com/apache/bifromq/pull/273) Avoid reusing released APIServer response buffers | merged |
| apache/otava | [#166](https://github.com/apache/otava/pull/166) Make CSV importer configurable via ConfigArgParse | merged |

<!-- PRS:END -->

## Stack

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/CUDA-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="CUDA">
  <img src="https://img.shields.io/badge/Triton-000000?style=for-the-badge&logo=openai&logoColor=white" alt="Triton">
  <img src="https://img.shields.io/badge/vLLM-1F6FEB?style=for-the-badge&logoColor=white" alt="vLLM">
  <img src="https://img.shields.io/badge/C%2B%2B-00599C?style=for-the-badge&logo=cplusplus&logoColor=white" alt="C++">
  <img src="https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white" alt="Java">
  <img src="https://img.shields.io/badge/Shell-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white" alt="Shell">
  <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

## Activity

<p align="center">
  <img src="cards/languages.svg" alt="Languages" height="270">
  <img src="cards/activity.svg" alt="Activity" height="270">
</p>

<p align="center">
  <img src="https://github-readme-streak-stats.herokuapp.com/?user=MrlixiangWE&hide_border=true&theme=transparent" alt="Streak" height="165">
</p>

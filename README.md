# agent-runtime-governance

Runtime governance specs for multi-agent AI operations — a red-line guard hook, a permission
matrix, and a structured dispatch template, aligned with the LGD (Lifecycle Governance Doctrine)
operational governance approach.

【角色】 Production reference deployment: MedXpert — medical-device compliance consulting work
        delivered with AI expert teams across NMPA / FDA / EU MDR / JP PMDA engagement surfaces.
【状态】 Name status: not a registered legal entity; trademark not registered.（未申请实体注册、未申请商标注册）
【指针】 https://medxpert.cn
【边界】 Self-reported by the implementing party; not an endorsement, certification, or regulatory
        recognition. No third-party quality review of this repository to date.

## Why this exists

Multi-agent setups fail in known ways: unbounded delegation loops, cascaded hallucination,
unaudited external actions. This repo publishes the three runtime pieces we run in daily
operations (self-reported) to keep autonomous agents inside explicit boundaries:

| Piece | File | Layer |
|---|---|---|
| Red-line guard hook | `code/redline_guard.py` | Pre-tool-use interception (exit 2 = block) |
| Permission matrix | `docs/permission_matrix_v1.md` | Domain × autonomy-level policy (🟢/🟡/🔴) |
| Dispatch template | `docs/dispatch_template_v1.md` | Structured handoff: trace_id, owner, depth ≤ 4, cost estimate, done criteria |

Design stance: centralized orchestration (orchestrator-worker) plus an event-driven local
sentinel; no decentralized swarm. Rationale and external evidence notes live in internal
research records; this repository ships the norms and the code only.

## How the hook decides

`redline_guard.py` reads a PreToolUse JSON event on stdin and exits:

- `0` — allow (also on any parse failure: the hook never breaks normal work);
- `2` — block, with a reason on stderr. Four forbidden classes:
  R1 destructive delete aimed at protected targets ·
  R2 plaintext secrets in commands or files (matched values are never echoed) ·
  R3 system-level damage (disk format / partition / wipe patterns) ·
  R4 pipe-to-shell remote execution (fetch-a-script-and-run-it patterns).

## Self-test (reproducible)

```bash
# case 1 — destructive class aimed at a NON-protected target (the placeholder itself
# is not a danger word) → expect exit 0. This proves R1 needs BOTH factors to fire.
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf <PROTECTED_PATH>"}}' | python code/redline_guard.py; echo "exit=$?"

# case 2 — 把 <PROTECTED_PATH> 换成真实的受保护目录（如你的用户「文档/桌面」类目录），
# 让毁灭类与危险目标在同一命令串内共现 → expect exit 2 with a reason on stderr.
# 字面目标刻意不印在本 README 里。
```

## Known boundaries (honest scope)

1. The hook covers four tool entrypoints of one agent platform (shell execution, file
   write/edit); direct MCP tool calls sit outside it and rely on connector permissions
   plus the dispatch template.
2. Approval-level (🟡) actions are a procedural gate, not yet a code gate.
3. Rules expand only after real false-positive / false-negative evidence (three-strike
   escalation to a hard gate).

## License layering

- Code (`code/`): Apache-2.0 (see `LICENSE`).
- Docs and normative text (`docs/`, this README): all rights reserved — the theory text is
  not covered by Apache-2.0.

G0 状态：已随 Medxpert-org 公开仓发布（2026-09-29 授权推送）

---

## 权属宣告统一块（整体复制 · 不得删改）

```
© 2026 赵兴华 / Steven Zhao·China (ORCID 0009-0001-0512-1237). All rights reserved.
理论署名 (attribution) : LGD（Lifecycle Governance Doctrine / 全程治理论）— SynomosAI initiative
名称状态 (name status)  : "SynomosAI" / "MedXpert" — 未申请实体注册、未申请商标注册
                        (not a registered legal entity; no trademark registered)
生产参考部署 (production reference, self-reported) : MedXpert
                    ← 非认证、非背书、非监管认可（not a certification or endorsement）
代码许可 (code license) : uibc-core = Apache-2.0 (see repo LICENSE)
                    本文本与理论表述不在 Apache-2.0 覆盖范围内
引用格式 (cite as)      : uibc-core/CITATION.cff · concept DOI 10.5281/zenodo.22821834
首次公开锚 (first public): 2026-09-17 13:31:45 UTC (commit cb6f11b)
                    外锚 (external anchor): Sigstore Rekor logIndex 2883389783
```

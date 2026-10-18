# AGENTS.md — 给 AI Agent 的工作指引

本文件面向自动化 AI Agent（编码助手、运维脚本、知识库机器人）。人类读者请看 [README.md](README.md)。

## 这个仓库是什么

`agent-runtime-governance` 是一套**多智能体运行治理规范 + 一个可执行的 PreToolUse 钩子**，不是可独立运行的应用。核心资产：

- `code/redline_guard.py` — 🔴 红线守护钩子（Python 纯标准库，stdin 读 PreToolUse JSON，exit 0=放行 / 2=拦截+stderr 理由）。
- `docs/permission_matrix_v1.md` — 域 × 三级权限矩阵（🟢 可自治 / 🟡 须运营者点头 / 🔴 钩子拦）。
- `docs/dispatch_template_v1.md` — 派单模板（trace_id / owner / 委托深度 ≤ 4 / 成本预估 / Done 判据）。

设计立场：集中编排（orchestrator-worker）+ 本地事件驱动哨兵；**不做去中心化 swarm**。

## 可用的工作命令

```bash
# 自检测试（占位目标 ≠ 危险目标 → expect exit 0）
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf <PROTECTED_PATH>"}}' | python code/redline_guard.py; echo "exit=$?"

# 拦截测试（毁灭类 + 真实危险目标同现 → expect exit 2，理由打到 stderr）
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf ~/Documents"}}' | python code/redline_guard.py; echo "exit=$?"
```

前置依赖：Python ≥ 3.9。**无第三方包、无网络外发**。

## 约定（Do）

- 修改 `code/redline_guard.py` 前先读 `docs/permission_matrix_v1.md` 的 R1–R4 覆盖清单，保持拦截类与矩阵一致。
- 新增/修改规则后，用上面两条命令跑自检测试：非危险目标仍 exit 0（低误拦），危险目标 exit 2。
- 规则扩充只在拿到真实误拦/漏拦证据后进行（同类错误三击升级为硬门禁）。
- 文档（`docs/`、本 README）的权利口径：**代码 Apache-2.0，文档与理论表述 all rights reserved（不在 Apache 覆盖内）**——新增文件沿用此分层，不要写成单一 MIT/Apache 覆盖全部。

## 禁止（Don't）

- **不要改动任何「权属宣告统一块」**（README.md / docs/*.md 末尾 ``` 块）、`LICENSE`、`CITATION.cff` 的权属字段——这些只由维护者变更。
- 不要在仓库内提交任何密钥、令牌或真实客户数据；匹配到密钥形态时**永不回显匹配值**。
- 不要给 `redline_guard.py` 引入网络请求（`socket`/`requests`/`urllib`/`httpx` 等）——零网络外发是设计约束。
- 不要把本仓库的输出/规则描述为「已认证 / 已商用交付 / 已服务特定客户」——它是**自我陈述（self-reported），非第三方认证或监管认可**。
- 不要新增对外宣传措辞或品牌扩张内容。

## 边界

1. 钩子只覆盖单平台四个工具入口（shell 执行、文件写/改）；直连 MCP 工具调用不在其内，靠连接器权限 + 派单模板约束。
2. 🟡 审批级动作目前是**制度闸**（流程约束），不是代码闸。
3. 升级链：执行席 E0 → 调度官 E1 → 治理中枢 E2 → 运营者 E3；升级必带 attempt log。

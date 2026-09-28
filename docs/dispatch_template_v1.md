# Dispatch Template v1（派单模板）

> 配套内部派单规程使用。开单即复制本模板填写；🔴 字段缺一不开单（任务台账硬拦：无主不许开单）。
> 设计依据：集中编排 + 结构化交接（trace_id + 委托深度上限 + 成本预估），防级联幻觉与无限委托。

## 一、单据头
- **单号 trace_id**：`YYYYMMDD-HHMM-<域缩写>-<序号>`（例：`20260929-0900-REG-001`）
- **派单窗**：会话标记
- **对口专家**：映射总账命中项；查无对口 → 写「兜底」+ 一句理由（禁沉默顶替）

## 二、硬字段（缺一不开单）
- **owner**：具体执行者。留空或写泛称 = 无主，台账会拦
- **委托深度**：本单为第 N 跳，**≤ 4**；到 4 跳必须回收或升级，禁止再委（防级联幻觉 / 无限委托）
- **成本预估**：预计工具调用次数 + 模型档位（就低不就高；高耗操作先报运营者，无授权不跑）
- **期限 / 随访日**：
- **升级链**：E0 执行席 → E1 调度官 → E2 治理中枢 → E3 运营者。触发条件 + attempt log（试过什么 / 为何不行 / 诉求）；禁裸提问、禁越级甩球

## 三、交付定义
- **Done 判据**：可验证证据形态（命令输出 / 文件路径+时间戳 / 截图）。无证据不许说完成（宣称闸）
- **回收方式**：台账回填 → 共享看板广播 → 待办销账

## 四、红线自检（派单前 30 秒，3 项）
- [ ] 本单**不含**对外不可逆动作（对外 → 单独走外发权利门禁，本模板装不下这种事）
- [ ] **不传明文密钥**（执行方自读文件 / 本地凭据保险库；对话出现密钥 = 立即提醒轮换）
- [ ] 涉 🟡 审批级动作（删除 / 部署 / 支付 / 外发）已获运营者点头

## 五、结构化回执（收单方填，回收方核）
```json
{"trace_id": "", "owner": "", "status": "done|blocked|escalated", "depth": 1, "evidence": "路径或输出摘录", "cost_calls": 0}
```

## 六、一句话范例
> 派单：`20260929-0900-MED-001`｜owner=<对口专家包名>｜深度 1｜预估 6 次调用·就低档｜期限次日｜Done=《差距分析表》落盘 + 复算命令可复跑｜升级链=同因失败 2 次 → E1。

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

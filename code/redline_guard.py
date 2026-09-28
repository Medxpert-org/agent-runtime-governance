# Copyright 2026 赵兴华 / Steven Zhao·China. Licensed under Apache-2.0 (see LICENSE).
# redline_guard.py — red-line guard hook v1 (PreToolUse). Sanitized distribution of the
# production guard; interception logic identical to the deployed version (2026-09-28).
# -*- coding: utf-8 -*-
r"""
redline_guard.py — 🔴 red-line guard hook v1（PreToolUse）

作用：在工具执行**前**硬拦 🔴 禁止级动作（依据本仓 docs/permission_matrix_v1.md）。
拦截即 exit 2 + stderr 理由；放行 exit 0；stdin 解析异常一律放行（绝不误伤正常流程）。

覆盖 🔴 四类（只拦禁止级，🟡 审批类走运营规程，不在此拦）：
  R1 毁灭性删除 打在危险目标（个人目录/系统目录/配置与凭据目录/工作区根/裸根·通配）
  R2 明文密钥 进对话/命令/文件（铁律：密钥永不进对话；匹配值绝不回显）
  R3 系统级破坏（磁盘格式化/注册表 HKLM 删除/卷影删除/磁盘分区/写盘清除类）
  R4 远程代码直接执行（pipe-to-shell 类 —— 联网部署须运营者点头）

设计原则：宁缺勿滥、低误拦；规则扩充待误拦/漏拦实证后按「同类错误三击升级」规则修订。
"""
import json
import re
import sys

# ---- R1 毁灭性删除 + 危险目标（同一命令串内同时命中才拦） ----
DESTRUCTIVE = re.compile(
    r"(rm\s+-[a-zA-Z]*r[a-zA-Z]*\s|rm\s+[^;\n|&]*\s-[a-zA-Z]*r[a-zA-Z]*\s|rmdir\s+/s|rd\s+/s|del\s+/[fsq][^\n]*\s/s|del\s+/s|"
    r"Remove-Item[^;\n|&]*-Recurse|shutil\.rmtree|rimraf)",
    re.I)
DANGER_TARGET = re.compile(
    r"(?i)(\bdesktop\b|\bdownloads\b|\bdocuments\b|appdata|\.workbuddy|\.ucvault|\.ssh\b|"
    r"system32|c:[\\\\/]+['\"\s]*$|c:[\\\\/]+\s|/home\b|/users\b|~[/\s'\"]|"
    r"d:[\\\\/]+\s*workbuddy\s*[\\\\/]*['\"]?\s*$)")
ROOT_DELETE = re.compile(
    r"(rm|rimraf)\s+-[a-zA-Z]*r[a-zA-Z]*\s+[\"']?(/|~|\*|\.)($|\s)", re.I)

# ---- R2 明文密钥 ----
TOKEN_LITERALS = re.compile(
    r"(ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"sk-[A-Za-z0-9]{20,}|sk-proj-[A-Za-z0-9_\-]{20,}|AKIA[0-9A-Z]{16}|"
    r"xox[abprs]-[A-Za-z0-9\-]{10,}|AIza[0-9A-Za-z_\-]{35})")
KEY_ASSIGN = re.compile(
    r"(?i)(?<![A-Za-z])(api[_-]?key|secret|token|password|passwd|pwd)\s*[:=]\s*[\"']([^\"'\s]{12,})[\"']")
PLACEHOLDER_HINTS = ("your", "xxx", "example", "placeholder", "changeme",
                     "dummy", "redact", "<", "${", "{", "test", "n***", "…", "…")


def _is_placeholder(value: str) -> bool:
    low = value.lower()
    return any(h in low for h in PLACEHOLDER_HINTS)


def _check_text(text: str):
    if not text:
        return None
    if TOKEN_LITERALS.search(text):
        return "明文密钥形态（ghp_/sk-/AKIA/xox/AIza 等）进命令或文件 —— 铁律：密钥永不进对话；请走本地凭据保险库"
    m = KEY_ASSIGN.search(text)
    if m and not _is_placeholder(m.group(2)):
        return "疑似硬编码密钥赋值（键名=引号字面量）—— 请改环境变量/保险库读取"
    if ROOT_DELETE.search(text):
        return "对根/家目录/通配符的直接递归删除（rm -rf / · ~ · * · .）"
    if DESTRUCTIVE.search(text) and DANGER_TARGET.search(text):
        return "毁灭性删除 打在危险目标（个人目录/系统目录/配置目录/工作区根）"
    if re.search(r"(?i)(format\s+[a-z]:\s|reg\s+delete\s+hklm|vssadmin\s+delete\s+shadows|"
                 r"bcdedit[^;\n|&]*safeboot|cipher\s+/w:|diskpart\b|mkfs\.|dd\s+if=.*of=/dev/)", text):
        return "系统级破坏动作（format/reg HKLM/vssadmin/diskpart/bcdedit/cipher /w/mkfs/dd 写盘）"
    if re.search(r"(?i)(curl[^;\n|&]*\|\s*(sudo\s+)?(ba|z|da)?sh\b|wget[^;\n|&]*\|\s*(ba|z|da)?sh\b|"
                 r"iex\s*\(\s*iwr|iwr[^;\n|&]*\|\s*iex\b|"
                 r"invoke-expression[^;\n|&]*(iwr|invoke-webrequest|curl|wget)|"
                 r"curl[^;\n|&]*\|\s*powershell)", text):
        return "远程代码直接执行（pipe-to-shell 类）—— 联网部署须运营者明确点头"
    return None


def _collect_texts(tool_name, tool_input):
    texts = []
    if not isinstance(tool_input, dict):
        return texts
    if tool_name in ("Bash", "PowerShell"):
        texts.append(str(tool_input.get("command", "")))
    if tool_name in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        texts.append(str(tool_input.get("file_path", "") or tool_input.get("notebook_path", "")))
        texts.append(str(tool_input.get("content", "")))
        texts.append(str(tool_input.get("new_string", "")))
        texts.append(str(tool_input.get("code", "")))
    return texts


def decide(tool_name, tool_input):
    for text in _collect_texts(tool_name, tool_input):
        reason = _check_text(text)
        if reason:
            return reason
    return None


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)  # 解析不了就放行，钩子绝不误伤
    reason = decide(data.get("tool_name", ""), data.get("tool_input", {}))
    if reason:
        sys.stderr.write(
            "🛑 redline_guard 拦截（🔴 禁止级）：" + reason + "\n"
            "依据：本仓 docs/permission_matrix_v1.md / 密钥永不进对话铁律。\n"
            "确需执行：停下，向运营者显式申请授权（升级链 E0→E1→E2→E3，带 attempt log）。\n"
        )
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate the local Queqiao skill package and ecosystem drafts. No network publish."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "queqiao-remote-assist"
SKILL = SKILL_DIR / "SKILL.md"
ERRORS: list[str] = []


def error(msg: str) -> None:
    ERRORS.append(msg)


def read(path: Path) -> str:
    if not path.is_file():
        error(f"missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        error("SKILL.md must start with YAML frontmatter")
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        error("SKILL.md frontmatter is not closed")
        return {}
    body = text[4:end]
    data: dict[str, str] = {}
    for line in body.splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def forbidden_snippets(label: str, text: str) -> None:
    patterns = [
        (r"E:\\IdeaProjects\\remote-assist", "hard-coded workspace path"),
        (r"C:\\Users\\user\\", "hard-coded Windows user path"),
        (r"cloudEndpoint", "hosted MCP cloudEndpoint"),
    ]
    for pat, why in patterns:
        if re.search(pat, text, re.I):
            error(f"{label}: found {why}")
    # Mentions that forbid pipe-install are required; an unprefixed install command is not.
    for pipe in ("curl | sh", "iwr | iex"):
        if pipe in text.lower() or pipe.replace(" ", "") in text.replace(" ", "").lower():
            # allow if clearly forbidden nearby
            idx = text.lower().find(pipe)
            if idx < 0:
                idx = text.replace(" ", "").lower().find(pipe.replace(" ", ""))
            window = text[max(0, idx - 20): idx + 40]
            if not re.search(r"不要|禁止|不要用|不要使用", window):
                error(f"{label}: recommends {pipe}")


def main() -> int:
    skill_text = read(SKILL)
    install_text = read(SKILL_DIR / "references" / "install.md")
    tools_text = read(SKILL_DIR / "references" / "tools.md")
    meta = parse_frontmatter(skill_text)
    if meta.get("name") != "queqiao-remote-assist":
        error(f"frontmatter name must be queqiao-remote-assist, got {meta.get('name')!r}")
    if SKILL_DIR.name != meta.get("name", ""):
        error("skill directory name must match frontmatter name")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", meta.get("name", "")):
        error("frontmatter name must be lowercase kebab-case")
    desc = meta.get("description", "")
    if "排查远程电脑" not in desc and "排查远程电脑" not in skill_text:
        error("Chinese display name 排查远程电脑 missing from skill")
    if "鹊桥" not in skill_text:
        error("brand 鹊桥 missing from SKILL.md")
    for needle in ("不会自动获得远程权限", "临时", "长久", "不是", "托管 MCP", "用户", "授权"):
        if needle not in skill_text:
            error(f"SKILL.md missing required idea: {needle}")
    if "license:" in skill_text.split("---", 2)[1].lower() if skill_text.startswith("---") else "":
        fm = skill_text.split("---", 2)[1].lower()
        if "mit-0" in fm or re.search(r"^license:", fm, re.M):
            error("do not put a conflicting license field in SKILL.md frontmatter")

    license_text = read(ROOT / "LICENSE")
    if "MIT License" not in license_text or "MIT-0" in license_text:
        error("root LICENSE must remain MIT and must not be changed to MIT-0")

    for label, text in (
        ("SKILL.md", skill_text),
        ("install.md", install_text),
        ("tools.md", tools_text),
    ):
        if text:
            forbidden_snippets(label, text)

    if "同意" not in install_text:
        error("install.md must require user consent before download or config changes")
    if not re.search(r"不要使用 .*curl \| sh", install_text):
        error("install.md must explicitly forbid curl|sh blind install")
    if "REMOTE_ASSIST_PAYLOAD" in install_text and "不要" not in install_text:
        error("install.md must tell agents not to write REMOTE_ASSIST_PAYLOAD")

    lhm_path = ROOT / "lhm.plugin.json"
    lhm_text = read(lhm_path)
    if lhm_text:
        try:
            lhm = json.loads(lhm_text)
        except json.JSONDecodeError as exc:
            error(f"lhm.plugin.json is not valid JSON: {exc}")
        else:
            for key in ("identifier", "name", "version"):
                if not lhm.get(key):
                    error(f"lhm.plugin.json missing {key}")
            if not re.fullmatch(r"[0-9a-z][0-9a-z_-]*", str(lhm.get("identifier", ""))):
                error("lhm.plugin.json identifier does not match official first-publish pattern")
            if "cloudEndpoint" in lhm:
                error("lhm.plugin.json must not set cloudEndpoint for this stdio MCP")
            zh = next((x for x in lhm.get("localizations", []) if x.get("locale") == "zh-CN"), None)
            if not zh or zh.get("name") != "排查远程电脑":
                error("lhm.plugin.json zh-CN name must be 排查远程电脑")
            tools = {t.get("name") for t in lhm.get("tools", [])}
            expected = {
                "connect",
                "disconnect",
                "connection_status",
                "host_info",
                "list_processes",
                "list_services",
                "list_dir",
                "read_file",
                "read_log_tail",
                "take_screenshot",
                "run_command",
            }
            if tools != expected:
                error(f"lhm.plugin.json tools mismatch: {sorted(tools)}")

    entry_path = (
        ROOT
        / "docs/promo/ecosystem/cline-marketplace/registry/skills/queqiao-remote-assist/entry.json"
    )
    entry_text = read(entry_path)
    if entry_text:
        try:
            entry = json.loads(entry_text)
        except json.JSONDecodeError as exc:
            error(f"Cline entry.json is not valid JSON: {exc}")
        else:
            if entry.get("id") != "queqiao-remote-assist":
                error("Cline entry id must be queqiao-remote-assist")
            if entry.get("type") != "skill":
                error("Cline entry type must be skill")
            if entry.get("name") != "排查远程电脑":
                error("Cline entry display name must be 排查远程电脑")
            if entry.get("verified") is not False:
                error("Cline entry verified must be false")
            if entry.get("license") != "MIT":
                error("Cline entry license must remain MIT")
            tags = entry.get("tags") or []
            allowed = {
                "productivity",
                "marketing",
                "research",
                "data",
                "software",
                "business",
                "sales",
                "finance",
                "creative",
                "memory",
                "security",
                "databases",
            }
            if not tags or any(t not in allowed for t in tags):
                error(f"Cline tags must be from the official vocabulary, got {tags}")
            args = (entry.get("install") or {}).get("args")
            if args != ["CodeYuanG/queqiao", "--skill", "queqiao-remote-assist"]:
                error(f"unexpected Cline install.args: {args}")
            for key in ("tagline", "description"):
                if not entry.get(key):
                    error(f"Cline entry missing {key}")
            if len(str(entry.get("tagline", ""))) > 120:
                error("Cline tagline exceeds 120 characters")

    if ERRORS:
        print("verify-agent-skill: FAIL")
        for item in ERRORS:
            print(f"- {item}")
        return 1
    print("verify-agent-skill: PASS")
    print(f"skill: {SKILL}")
    print("local list command: npx skills add ./ --list")
    print("local install command (writes agent skill dirs): npx skills add ./ --skill queqiao-remote-assist")
    print("public command after push only: npx skills add CodeYuanG/queqiao --skill queqiao-remote-assist")
    return 0


if __name__ == "__main__":
    sys.exit(main())

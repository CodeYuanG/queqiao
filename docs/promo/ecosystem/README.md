# 生态发布说明

本目录和仓库根目录的 `lhm.plugin.json`、`skills/queqiao-remote-assist/` 是技能与市场列表的配套说明。技能通过 GitHub 仓库 `CodeYuanG/queqiao` 安装。ClawHub、LobeHub 和 Cline 市场尚未上架。

技能展示名：**排查远程电脑**。frontmatter / slug：`queqiao-remote-assist`。品牌：鹊桥 / Queqiao。主张：让 Agent 帮你排查另一台电脑。

规范来源（2026-11-16 查阅的现行文档）：

- skills.sh / `npx skills`：[Creating skills](https://github.com/vercel-labs/skills/blob/main/docs/creating-skills.md)、[Commands](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)、[skills.sh/docs](https://www.skills.sh/docs)
- ClawHub：[Publishing](https://docs.openclaw.ai/clawhub/publishing)、[Skill format](https://docs.openclaw.ai/clawhub/skill-format)
- LobeHub：[Publish MCP](https://market.lobehub.com/s/publish-mcp)、[lhm.plugin.json](https://market.lobehub.com/s/publish-mcp/references/manifest)
- Cline Marketplace：[CONTRIBUTING.md](https://github.com/cline/marketplace/blob/main/CONTRIBUTING.md)

主项目许可证保持 **MIT**（仓库根目录 `LICENSE`）。没有也不应把主项目或本技能改成 MIT-0，除非仓库所有者另行明确同意。

## 1. skills.sh（Vercel skills CLI）

技能位于 `skills/queqiao-remote-assist/SKILL.md`，符合官方发现路径（`skills/<name>/SKILL.md`，且 `name` 与目录名一致）。

公开安装命令：

```bash
npx skills add CodeYuanG/queqiao --skill queqiao-remote-assist
```

在仓库目录里也可以用 `npx skills add ./ --skill queqiao-remote-assist`，或用 `npx skills add ./ --list` 只列出、不写入助手目录。skills.sh 目录展示依赖安装数据，不保证上榜。

## 2. ClawHub

官方 skill format 仍写明：发布到 ClawHub 的技能一律按 **MIT-0** 授权；不要在 `SKILL.md` 中加入与之冲突的许可证条款，平台不支持为单个技能覆盖许可证。

因此：

- 仓库和技能说明继续按 MIT 保留，未改许可证，也未在技能 frontmatter 中写入 `license`。
- **在所有者明确同意「将该技能的 ClawHub 发布包按 MIT-0 授权」之前，不要执行发布。** 这不是助手可以代为同意的事项。
- 同意之后，需要登录的人在本机执行（以下命令不要在未授权时运行）：

```bash
# 先 clawhub login（浏览器登录，本轮未执行）
clawhub skill publish ./skills/queqiao-remote-assist --slug queqiao-remote-assist --name "排查远程电脑" --categories development,operations --topics "remote-assist,troubleshooting,mcp"
```

`--owner` 仅在发布到组织账号时才需要。发布后会进入安全扫描，通过前不会出现在公开搜索与安装里。

## 3. LobeHub MCP 市场

清单在仓库根目录 `lhm.plugin.json`，字段按官方 manifest 编写：

- `identifier`：`codeyuang-queqiao`（首次发布前可改，但发布后必须保持稳定）
- `name` / `description` / `tags` 为 en-US 源文案；中文展示名「排查远程电脑」放在 `localizations` 的 `zh-CN`
- **没有填写 `cloudEndpoint`**。鹊桥 MCP 是本机 stdio 控制端，不能把 `http://121.196.45.81/` 或中继端口写成托管 MCP
- `tools` 按当前 `apps/queqiao-mcp` 的工具名与参数列出
- `version` 暂用当前 Windows 桌面公开包 `0.1.8`；Linux / macOS 桌面包和 Linux MCP 包在下载页仍可能是 `0.1.5`，发布前请再核对

官方流程还要求：先把仓库（含更新后的 README）推到 GitHub，因为上架后会回读默认分支上的 README；然后由仓库所有者执行：

```bash
npx -y @lobehub/market-cli login
npx -y @lobehub/market-cli github connect
npx -y @lobehub/market-cli plugin publish https://github.com/CodeYuanG/queqiao --dir <本仓库绝对路径>
```

本轮未登录、未连接 GitHub、未执行 publish。若清单需要根据正在运行的 MCP 再生成一版，可用官方本地命令（同样未执行）：

```bash
npx -y @lobehub/market-cli plugin init --stdio "<本机 RemoteAssist.Mcp 绝对路径>" --dir <本仓库绝对路径>
```

生成后必须再检查：不得被写成 `cloudEndpoint`，也不得把 HTTP 网站当成远程 MCP。

## 4. Cline Marketplace

草稿按官方 CONTRIBUTING 放在：

`docs/promo/ecosystem/cline-marketplace/registry/skills/queqiao-remote-assist/entry.json`

这是给提交到 [`cline/marketplace`](https://github.com/cline/marketplace) 用的条目，**不要把这个目录误当成已经提交。** 字段要点：

- `id` 与文件夹名均为 `queqiao-remote-assist`
- `type` 为 `skill`（不是 MCP）。因为控制端不是 npm 包，也没有可公开配置的 HTTP MCP
- `install.args` 为 `["CodeYuanG/queqiao", "--skill", "queqiao-remote-assist"]`，对应 `cline skill install ...`（官方说明该命令与 `npx skills add` 同源）
- `tags` 只用了官方词汇表中的 `software`、`productivity`
- `verified` 必须保持 `false`
- `license` 为 `MIT`

提交前还需要：技能已出现在 `CodeYuanG/queqiao` 默认分支；把该 `entry.json` 拷到自己 fork 的 `cline/marketplace` 仓库对应路径；在该仓库运行 `npm run validate`；再开 PR。官方也提醒公开目录更新可能积压，不适合作为第一站。本轮未开 PR。

不要再单独提交一个把官网当成 `--transport http` 的 MCP 条目。

## 其余市场仍待完成

1. 若要上 ClawHub：先明确是否接受该技能发布包改为 MIT-0。
2. 若要上 LobeHub：由用户在浏览器完成登录与 GitHub 授权后，再发布 `lhm.plugin.json`。
3. 若要上 Cline：在官方 marketplace 仓库验证并开 PR。
4. 公开安装包版本目前为 Windows 桌面 0.1.8，macOS/Linux 桌面和 Linux MCP 为 0.1.5；发布市场清单前再核对。

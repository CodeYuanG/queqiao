# 鹊桥

让 Agent 帮你排查另一台电脑。

查看进程、服务和日志，不用把截图和日志传来传去。使用临时协助码时，执行命令需要对方在本机确认。长久码无人值守不再逐次弹窗，操作仍记在那台电脑上。无需注册，支持自托管。

官网：http://121.196.45.81/

## 最短接入

被协助的电脑安装[桌面版](http://121.196.45.81/#download)，打开鹊桥，点「开启接受协助」，把完整连接凭证发过来。协助方把[安装说明](http://121.196.45.81/agent.md)交给 Cursor 或 Claude Code，只安装 MCP 控制端，不必再装桌面版。

备用说明：https://raw.githubusercontent.com/guoshuaipeng/queqiao/master/site/agent.md

自托管中继见 [docs/relay-deploy.md](docs/relay-deploy.md)。

## 权限和记录

- 临时凭证：连上要本机点「允许协助」。查看进程、服务、日志和文件之后，执行命令或截屏还要再点允许或拒绝。拒绝则没有改动。可在本机停止接受。
- 长久码：在本机开启无人值守时确认一次。之后连上和改动不再逐次弹窗，操作仍记在这台电脑上。可随时在本机撤销。
- 中继只记录会话码的生成、连接成功或失败、结束，不保存完整连接凭证。
- 官网不加载第三方统计脚本。服务器记录访问和下载的时间、路径、IP 和浏览器标识。排查到的进程和日志不进这份记录。

桌面客户端只保留 **Tauri**（`apps/queqiao-tauri`）。旧的 .NET 8 / .NET Framework 4.8 客户端、WinForms / Avalonia 工程、安装器和对应的迭代记录已从仓库删除。

- `apps/queqiao-tauri` — Windows / macOS 桌面客户端（Tauri 2）
- `relay/` — Go 公网中继
- `site/` — 官网与 `/admin`
- `docs/` — 产品决策、界面规格、中继协议
- `private.example/` — 私有部署信息模板（复制为 `private/`，勿提交）

界面规格见 [docs/CLIENT-UI.md](docs/CLIENT-UI.md)。需求队列（迭代入口）见 [docs/PRODUCT-VERSIONS.md](docs/PRODUCT-VERSIONS.md)，文档地图见 [docs/architecture.md](docs/architecture.md)。客户端 **GitHub 打包 → 官网换包**（macOS / Linux 主路径）见 [docs/release.md](docs/release.md)。

## 客户端

在 `apps/queqiao-tauri`：

```bat
npm install
npm run check
npm run dev
```

默认连接本机中继 `127.0.0.1:17891`。正式发版默认地址见 `private.example/deploy.md`。

## 中继

```powershell
.\scripts\relay-smoke.ps1
```

协议与部署见 [docs/relay.md](docs/relay.md)、[docs/relay-protocol.md](docs/relay-protocol.md)、[docs/relay-deploy.md](docs/relay-deploy.md)。

## 私有信息

服务器 IP、口令、探活号、带生产链接的营销稿等放在本机 `private/`（gitignore）。开源仓库只保留占位符与模板。

## 安全底线

- 写操作必须在被协助的这台电脑上确认。
- 连接主路径仍是完整安全载荷（含证书指纹）。短码单独连接（R050）未授权。
- 不改 AI-SSH-Pro。

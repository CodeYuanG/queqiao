# 鹊桥 MCP 控制端安装说明（给 AI Agent）

你在帮用户把「鹊桥」的 **MCP 控制端** 装到这台电脑上，让当前这个智能体可以协助另一台已经打开鹊桥的电脑。装好之后，智能体可以查看远端的进程、服务、目录、文本文件和日志；要执行命令或截屏时，对方电脑上仍会弹出确认，不能绕过。

这是控制端，不是桌面软件。需要被连上的那台电脑要另外安装鹊桥桌面版，下载地址在文末「被协助的电脑」。你这台电脑不要下载、不要安装 Queqiao-Setup、dmg、AppImage 或 deb。

## 规则

1. **亲自在用户电脑上执行。** 先读完这份说明再动手。不要只把步骤列给用户。如果你不能执行命令、不能写文件（例如手机版或网页版聊天），直接告诉用户：请换成能在电脑上跑命令的智能体（Cursor、Claude Code、Codex、Trae 等），并允许它访问网络、写入配置。
2. **不要假装成功。** 每一步看命令的真实输出。最后必须完成「验收」，把原始输出原样贴给用户。没看到这些输出，就不能说装好了。
3. **只增加名为 `remote-assist` 的 MCP。** 可以新建配置文件；如果文件已经存在，只合并这一项。不要删除、不要改写用户已有的其他 MCP，不要卸载任何软件，不要改已经装好的鹊桥桌面版。
4. **程序只从下面两个地址下载**，不要从别的网站、网盘或 GitHub Release 另找一份：
   - Windows x64：`http://121.196.45.81/downloads/RemoteAssist.Mcp-windows-x64.exe`
   - Linux x64：`http://121.196.45.81/downloads/Queqiao-MCP-0.1.5-linux-x64.tar.gz`
5. 下载返回 404、校验对不上、或系统不是下面列出的平台时，停下来把输出给用户看。不要在这台电脑上改去安装桌面版凑合。对方那台电脑的桌面版地址见文末，发给对方自己下载。
6. 安装阶段不要调用 `connect`，也不要连任何远端电脑。用户没有另外给你连接凭证时，不要询问、不要编造短码。
7. 写完配置后，告诉用户需要重新加载 MCP 或重开这个智能体，当前对话里不一定立刻出现新工具。

## 第 1 步：确认系统和智能体

先确认操作系统和 CPU 架构。

- **Windows x64**：继续第 2 步，下 `.exe`。
- **Linux x86_64**：继续第 2 步，下 `.tar.gz`。
- **macOS，或 Windows ARM，或其他架构**：官网还没有单独的控制端文件。直接告诉用户现在装不了，不要下载桌面安装包代替。

同时确认你是哪个宿主，只改那个宿主的配置：

| 宿主 | 配置位置 |
|---|---|
| Cursor | 用户目录下的 `.cursor/mcp.json` |
| Claude Code | 优先用它自己的 `claude mcp add`；命令不存在就停下来，把帮助里和 mcp 有关的用法给用户看 |
| Codex | 用户目录下的 `.codex/config.toml` |
| 其他能跑命令的电脑版智能体 | 只用你确定会被读取的那个 MCP 配置。不确定就停下来问，不要写一个没人读的文件 |

## 第 2 步：下载控制端

程序放到用户目录的 `.queqiao` 里，不要放进临时目录，也不要覆盖桌面版的安装目录。

### Windows（PowerShell）

```powershell
$dir = Join-Path $env:USERPROFILE ".queqiao"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$dest = Join-Path $dir "RemoteAssist.Mcp.exe"
curl.exe -fL -o $dest "http://121.196.45.81/downloads/RemoteAssist.Mcp-windows-x64.exe"
Get-Item $dest | Select-Object FullName, Length
```

文件要存在，且大小大于 500000 字节。然后运行：

```powershell
& $dest --help
```

正常时退出码为 0，输出里有 `RemoteAssist MCP (stdio)`。如果系统拦截这个文件，告诉用户是哪一条提示，不要去关安全软件，也不要改注册表。

### Linux

```bash
mkdir -p "$HOME/.queqiao"
tmp=$(mktemp -d)
curl -fL -o "$tmp/mcp.tgz" "http://121.196.45.81/downloads/Queqiao-MCP-0.1.5-linux-x64.tar.gz"
tar -tzf "$tmp/mcp.tgz"
install -m 755 "$tmp/Queqiao-MCP-0.1.5-linux-x64/RemoteAssist.Mcp" "$HOME/.queqiao/RemoteAssist.Mcp"
rm -rf "$tmp"
ls -l "$HOME/.queqiao/RemoteAssist.Mcp"
"$HOME/.queqiao/RemoteAssist.Mcp" --help
```

`tar -tzf` 里应能看到 `Queqiao-MCP-0.1.5-linux-x64/RemoteAssist.Mcp`。`--help` 退出码为 0，输出里有 `RemoteAssist MCP (stdio)`。

## 第 3 步：写入 MCP 配置

命令使用上一步的绝对路径。环境变量只设置中继，不要写 `REMOTE_ASSIST_PAYLOAD`。

中继固定为：

```text
121.196.45.81:17891
```

### Cursor

编辑 `~/.cursor/mcp.json`（Windows 是 `%USERPROFILE%\.cursor\mcp.json`）。文件不存在就新建。已存在时先解析 JSON；解析失败就停下来把错误给用户看，不要整文件覆盖。

只合并 `mcpServers.remote-assist`。Windows 路径在 JSON 里写成正斜杠。

```json
{
  "mcpServers": {
    "remote-assist": {
      "command": "C:/Users/你的用户名/.queqiao/RemoteAssist.Mcp.exe",
      "args": [],
      "env": {
        "REMOTE_ASSIST_RELAY": "121.196.45.81:17891"
      }
    }
  }
}
```

Linux 的 `command` 是 `/home/你的用户名/.queqiao/RemoteAssist.Mcp`。

### Claude Code

在用户电脑上执行（把路径换成上一步的绝对路径）：

```bash
claude mcp add remote-assist --scope user -e REMOTE_ASSIST_RELAY=121.196.45.81:17891 -- "$HOME/.queqiao/RemoteAssist.Mcp"
```

Windows 把最后的程序路径换成 `%USERPROFILE%\.queqiao\RemoteAssist.Mcp.exe`。如果当前 `claude` 没有 `mcp add`，或参数和上面不一致，停下来把 `claude mcp --help` 的输出给用户看，不要猜一个配置文件覆盖掉。

### Codex

在 `~/.codex/config.toml` 里追加，不要删掉已有的其他服务器：

```toml
[mcp_servers.remote-assist]
command = "/绝对路径/RemoteAssist.Mcp"
args = []

[mcp_servers.remote-assist.env]
REMOTE_ASSIST_RELAY = "121.196.45.81:17891"
```

## 被协助的电脑：下载桌面客户端

控制端只能连上一台已经打开鹊桥的电脑。对方还没装时，把下面对应系统的地址原样发给对方，让对方在那台电脑上自己下载、安装。不要在你这台电脑上下载这些安装包，也不要替对方执行安装。

| 对方的电脑 | 下载地址 |
|---|---|
| Windows | http://121.196.45.81/downloads/Queqiao-Setup-0.1.8.exe |
| macOS（Apple 芯片，M1 / M2 / M3 及以后） | http://121.196.45.81/downloads/Queqiao-0.1.5-macos-arm64.dmg |
| macOS（Intel 芯片） | http://121.196.45.81/downloads/Queqiao-0.1.5-macos-x64.dmg |
| Linux（AppImage，不确定时用这个） | http://121.196.45.81/downloads/Queqiao-0.1.5-linux-x64.AppImage |
| Linux（.deb） | http://121.196.45.81/downloads/Queqiao-0.1.5-linux-x64.deb |

对方打开安装包之后：

1. 打开鹊桥，点「开启接受协助」。
2. 点「复制连接凭证」，把整段原样发回来。不要只发其中几位。
3. 你拿到凭证后，再按说明用 `connect` 连接。这次安装控制端时还不要连。

Windows 若浏览器提示「通常不会下载」，让对方选择保留。macOS 打开 dmg，把鹊桥拖到「应用程序」；若提示来自未识别的开发者，到「系统设置 → 隐私与安全性」里允许打开。Linux 选 AppImage 时，先 `chmod +x` 再运行。

验收结束时，除了控制端的安装结果，还要把上表里和对方系统对应的那一条地址写给用户。对方系统不清楚时，把 Windows、macOS、Linux 三条都写上，并说明按对方电脑的系统选一个。

## 验收

把下面几项的原始输出原样贴给用户，不要只写「成功」：

1. `--help` 的完整输出，以及退出码。
2. 程序的绝对路径和文件大小。
3. 你写入的配置文件绝对路径，以及其中 `remote-assist` 那一段原文。
4. 确认这一段里的中继是 `121.196.45.81:17891`，并且没有 `REMOTE_ASSIST_PAYLOAD`。
5. 明确写一句：这台电脑没有下载、没有安装桌面版。
6. 写出要发给被协助电脑的下载地址（见上一节的表）。对方系统已知就只写对应那一条，不知道就写 Windows、macOS、Linux 全部地址。

任一项做不到，就说明卡在哪一步。然后告诉用户：重新加载 MCP 或重开智能体之后，把对方的连接凭证发给它，用 `connect` 连接。对方还没装鹊桥时，先把下载地址发给对方。这次安装到此结束，不要现在就去连远端。

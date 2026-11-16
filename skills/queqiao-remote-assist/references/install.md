# 安装本机 MCP 控制端

这份说明教 Agent 在**协助方这台电脑**安装鹊桥 MCP 控制端。它不能代替被协助电脑上的桌面端。

当前公开安装说明与下载页仍以 HTTP 站点为准：

- 安装说明：http://121.196.45.81/agent.md
- 备用（需该文件已出现在默认分支）：https://raw.githubusercontent.com/CodeYuanG/queqiao/master/site/agent.md

下面的文件名取自本仓库当前的 `site/agent.md` 与官网下载页，版本可能更新。**动手前先征得用户同意访问网络、下载程序并写入 MCP 配置。** 若官网 `/agent.md` 里的文件名有变，改用官网当前地址，不要自行更换来源。

## 开始前

1. 向用户复述将要做的事：下载官方 MCP 控制端到用户目录下的 `.queqiao`，并只增加名为 `remote-assist` 的 MCP 配置。
2. 说明下载使用 HTTP，且不会在安装阶段连接任何远端电脑。
3. 用户没有明确同意就停止。
4. 不要使用 `curl | sh`、`iwr | iex` 或其他把远程脚本直接交给 shell 的安装方式。下面的命令应分步执行，并查看真实输出。
5. 不要删除或改写用户已有的其他 MCP。不要卸载软件，不要改已经装好的鹊桥桌面版。
6. 安装阶段不要调用 `connect`，也不要向用户索取连接凭证。

## 第 1 步：确认系统和宿主

先确认操作系统和 CPU 架构。

- **Windows x64**：继续，下载 `.exe`。
- **Linux x86_64**：继续，下载 `.tar.gz`。
- **macOS，或 Windows ARM，或其他架构**：当前没有单独的 MCP 控制端文件。告诉用户现在装不了，不要下载桌面安装包代替。

只改当前这个 Agent 会读取的配置：

| 宿主 | 配置位置 |
|---|---|
| Cursor | 用户目录下的 `.cursor/mcp.json` |
| Claude Code | 优先用它自己的 `claude mcp add`；命令不存在就停下来，把帮助里和 mcp 有关的用法给用户看 |
| Codex | 用户目录下的 `.codex/config.toml` |
| 其他能跑命令的电脑版智能体 | 只用你确定会被读取的那个 MCP 配置。不确定就停下来问，不要写一个没人读的文件 |

如果你不能在用户电脑上执行命令或写文件，直接请用户换成能在本机执行的 Agent，并允许它访问网络、写入配置。

## 第 2 步：下载控制端

程序放到用户目录的 `.queqiao` 里，不要放进临时目录，也不要覆盖桌面版的安装目录。路径用当前用户主目录拼接，不要写死某台电脑上的个人路径。

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

正常时退出码为 0，输出里有 `RemoteAssist MCP (stdio)`。如果系统拦截这个文件，把提示原样给用户，不要去关安全软件，也不要改注册表。

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

`tar -tzf` 里应能看到 `Queqiao-MCP-0.1.5-linux-x64/RemoteAssist.Mcp`。`--help` 退出码为 0，输出里有 `RemoteAssist MCP (stdio)`。如果官网已更换版本号，以 `/agent.md` 当时列出的文件名和解压路径为准。

## 第 3 步：写入 MCP 配置

命令使用上一步得到的**绝对路径**。环境变量只设置中继，**不要**写入 `REMOTE_ASSIST_PAYLOAD`。

公开默认中继：

```text
121.196.45.81:17891
```

这是中继地址，不是 MCP URL。配置里的 `command` 必须指向本机可执行文件。用户若自托管中继，改用其提供的 `host:port`，不要擅自改。

### Cursor

编辑 `~/.cursor/mcp.json`（Windows 是 `%USERPROFILE%\.cursor\mcp.json`）。文件不存在就新建。已存在时先解析 JSON；解析失败就停下来把错误给用户看，不要整文件覆盖。

只合并 `mcpServers.remote-assist`。Windows 路径在 JSON 里写成正斜杠。把下面的路径换成上一步的真实绝对路径：

```json
{
  "mcpServers": {
    "remote-assist": {
      "command": "/把这里换成控制端的绝对路径/",
      "args": [],
      "env": {
        "REMOTE_ASSIST_RELAY": "121.196.45.81:17891"
      }
    }
  }
}
```

### Claude Code

在用户电脑上执行（把路径换成上一步的绝对路径）：

```bash
claude mcp add remote-assist --scope user -e REMOTE_ASSIST_RELAY=121.196.45.81:17891 -- "$HOME/.queqiao/RemoteAssist.Mcp"
```

Windows 把最后的程序路径换成用户目录下 `.queqiao\RemoteAssist.Mcp.exe` 的绝对路径。如果当前 `claude` 没有 `mcp add`，或参数和上面不一致，停下来把 `claude mcp --help` 的输出给用户看，不要猜一个配置文件覆盖掉。

### Codex

在 `~/.codex/config.toml` 里追加，不要删掉已有的其他服务器：

```toml
[mcp_servers.remote-assist]
command = "/把这里换成控制端的绝对路径/"
args = []

[mcp_servers.remote-assist.env]
REMOTE_ASSIST_RELAY = "121.196.45.81:17891"
```

## 被协助的电脑：只发下载地址

控制端只能连上一台已经打开鹊桥的电脑。对方还没装时，把下面对应系统的地址原样发给对方，让对方自己下载、安装。不要在协助方这台电脑上下载这些安装包，也不要替对方执行安装。

本轮仓库记录的桌面版地址：

| 对方的电脑 | 下载地址 |
|---|---|
| Windows | http://121.196.45.81/downloads/Queqiao-Setup-0.1.8.exe |
| macOS（Apple 芯片） | http://121.196.45.81/downloads/Queqiao-0.1.5-macos-arm64.dmg |
| macOS（Intel 芯片） | http://121.196.45.81/downloads/Queqiao-0.1.5-macos-x64.dmg |
| Linux（AppImage，不确定时用这个） | http://121.196.45.81/downloads/Queqiao-0.1.5-linux-x64.AppImage |
| Linux（.deb） | http://121.196.45.81/downloads/Queqiao-0.1.5-linux-x64.deb |

对方打开软件之后：

1. 打开鹊桥，点「开启接受协助」，或按对方自己的需要启用长久码无人值守。
2. 点「复制连接凭证」，把整段原样发回来。不要只发其中几位。
3. 你拿到凭证后，再按主技能说明用 `connect` 连接。这次安装控制端时还不要连。

## 验收

把下面几项的原始输出原样贴给用户，不要只写「成功」：

1. `--help` 的完整输出，以及退出码。
2. 程序的绝对路径和文件大小。
3. 你写入的配置文件绝对路径，以及其中 `remote-assist` 那一段原文。
4. 确认这一段里的中继是用户同意的地址（公开默认是 `121.196.45.81:17891`），并且没有 `REMOTE_ASSIST_PAYLOAD`。
5. 明确写一句：这台电脑没有下载、没有安装桌面版。
6. 写出要发给被协助电脑的下载地址。对方系统已知就只写对应那一条，不知道就写 Windows、macOS、Linux 全部地址。

任一项做不到，就说明卡在哪一步。然后告诉用户：重新加载 MCP 或重开智能体之后，把对方的完整连接凭证发给它，再连接。这次安装到此结束，不要现在就去连远端。

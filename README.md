# SLURM Desktop Widget

Windows 桌面小组件，显示远程 SLURM 集群上正在运行的任务，每分钟自动刷新。

Rainmeter 皮肤 + Python 后台守护进程实现。

## 效果

桌面右上角显示半透明面板：

```
Hanhai22  |  09:03:49

* 1031065  md_run                1:23  RUNNING   gnode05
* 1031066  vasp_calc             0:45  RUNNING   gnode08
- 1031067  wait_job              0:00  PENDING   —
```

`*` RUNNING（运行中）| `-` PENDING（排队中）

## 文件说明

| 文件 | 作用 |
|------|------|
| `slurm_fetch.py` | 通过 SSH 执行 `squeue`，解析输出写入 `jobs.txt` |
| `slurm_daemon.pyw` | 后台守护进程，每 60 秒调用 fetch 脚本 |
| `Hanhai22Jobs.ini` | Rainmeter 皮肤定义（显示格式、字体、颜色） |

## 依赖

- **Rainmeter** — 免费的 Windows 桌面小组件平台
  - 官网：https://www.rainmeter.net/
  - 或 `winget install Rainmeter.Rainmeter`
- **Python 3.11+** — tkinter 内置，无需额外 pip 包
- **SSH 连接** — 需要能通过 SSH 连接到 SLURM 集群（本方案使用 `hpc-run.ps1` 包装器，可替换为任何 SSH 方式）

## 安装步骤

### 1. 安装 Rainmeter
```
winget install Rainmeter.Rainmeter
```

### 2. 部署皮肤
将 `Hanhai22Jobs.ini` 放到：
```
%USERPROFILE%\Documents\Rainmeter\Skins\Hanhai22Jobs\
```
右键系统托盘 Rainmeter 图标 → Skins → Hanhai22Jobs → Hanhai22Jobs.ini 加载。

### 3. 配置 SSH 连接
修改 `slurm_fetch.py` 中的以下变量为你自己的值：

```python
HPC_RUN = r"你的 SSH 包装器路径"        # Windows 上调用 SSH 的脚本
SQUEUE_FMT = "%.10i %.18j %.8u %.10M %.8T %N"  # squeue 输出格式
```

如果你用的是直接 SSH（而不是 hpc-run.ps1 包装器），把 `fetch_squeue()` 函数中的 subprocess 调用改为：

```python
result = subprocess.run(
    ["ssh", "user@host", f"squeue -u user -o '{SQUEUE_FMT}'"],
    ...
)
```

### 4. 启动守护进程
双击 `slurm_daemon.pyw`（后台运行，无控制台窗口）。

### 5. 设置开机自启（可选）
创建 `slurm_daemon.vbs` 放到启动文件夹：
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
```
内容：
```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """C:\path\to\pythonw.exe"" ""E:\path\to\slurm_daemon.pyw""", 0, False
```

## 迁移到其他电脑

1. **安装 Rainmeter**，拷贝 `Hanhai22Jobs.ini` 到 Skins 目录
2. **修改 `slurm_fetch.py`** 中的 SSH 连接参数：
   - 用户名、主机地址
   - squeue 格式（如需调整列）
   - SSH 认证方式（密钥/密码）
3. **调整 `Hanhai22Jobs.ini`** 中的路径：
   - `jobs.txt` 路径
   - 皮肤位置和窗口大小
4. **Python 路径** — `slurm_daemon.pyw` 和 `.vbs` 中改为目标电脑的 Python 路径

## 注意事项

- 守护进程每分钟向集群发送 1 次 `squeue` 请求，负载极低
- 如果 SSH 连接使用密码认证，需确保密码文件/凭证在正确路径
- Rainmeter 皮肤可拖动、可右键关闭
- 多个任务同时显示时，皮肤会自动扩展高度

## 技术架构

```
slurm_daemon.pyw (每 60s)
    └→ slurm_fetch.py
         └→ SSH → squeue -u user
              └→ jobs.txt
                   └→ Rainmeter WebParser (每 10s 读取)
                        └→ 桌面显示
```

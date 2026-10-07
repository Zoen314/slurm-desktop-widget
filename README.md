# SLURM Desktop Widget

A Windows desktop widget that displays jobs on a remote SLURM cluster and refreshes every minute.

Implemented with a Rainmeter skin and a Python background daemon.

## Preview

A translucent panel appears in the upper-right corner of the desktop:

```
Hanhai22  |  09:03:49

* 1031065  md_run                1:23  RUNNING   gnode05
* 1031066  vasp_calc             0:45  RUNNING   gnode08
- 1031067  wait_job              0:00  PENDING   —
```

`*` indicates RUNNING; `-` indicates PENDING.

## Files

| File | Purpose |
|------|---------|
| `slurm_fetch.py` | Run `squeue` over SSH, parse its output, and write `jobs.txt` |
| `slurm_daemon.pyw` | Call the fetch script every 60 seconds in the background |
| `Hanhai22Jobs.ini` | Define the Rainmeter skin's display format, font, and colors |

## Dependencies

- **Rainmeter** — Free Windows desktop widget platform
  - Website: https://www.rainmeter.net/
  - Install with `winget install Rainmeter.Rainmeter`
- **Python 3.11+** — No additional pip packages required
- **SSH access** — A working connection to the SLURM cluster; this implementation uses a PowerShell wrapper such as `hpc-run.ps1`, which can be replaced with direct SSH

## Installation

### 1. Install Rainmeter

```
winget install Rainmeter.Rainmeter
```

### 2. Install the skin

Place `Hanhai22Jobs.ini` in:

```
%USERPROFILE%\Documents\Rainmeter\Skins\Hanhai22Jobs\
```

Right-click the Rainmeter system tray icon, then select Skins → Hanhai22Jobs → Hanhai22Jobs.ini to load it.

### 3. Configure SSH access

Set the configuration variables in `slurm_fetch.py` for your environment:

```python
SSH_WRAPPER = r"C:\path\to\your-ssh-wrapper.ps1"  # PowerShell wrapper for SSH
SLURM_USER = "your_username"
OUTPUT_FILE = r"C:\Users\...\Documents\Rainmeter\Skins\Hanhai22Jobs\jobs.txt"
SQUEUE_FMT = "%.10i %.18j %.8u %.10M %.8T %N"  # squeue output columns
CLUSTER_NAME = "MyCluster"
```

To use direct SSH, replace the subprocess arguments in `fetch_squeue()` with:

```python
result = subprocess.run(
    ["ssh", "user@host", f"squeue -u user -o '{SQUEUE_FMT}'"],
    ...
)
```

### 4. Start the daemon

Set `PYTHON` and `FETCH_SCRIPT` in `slurm_daemon.pyw` to the paths of your Python interpreter and fetch script.

Double-click `slurm_daemon.pyw` to run it in the background without a console window.

### 5. Start automatically at login (optional)

Create `slurm_daemon.vbs` in the Startup folder:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
```

Contents:

```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """C:\path\to\pythonw.exe"" ""E:\path\to\slurm_daemon.pyw""", 0, False
```

## Moving to Another Computer

1. **Install Rainmeter** and copy `Hanhai22Jobs.ini` into the Skins directory.
2. **Configure SSH access** in `slurm_fetch.py`:
   - Username and host address
   - squeue output format, if different columns are needed
   - SSH authentication method, such as a key or password
3. **Update the paths**:
   - Set `OUTPUT_FILE` in `slurm_fetch.py` to the skin's `jobs.txt` path.
   - Adjust the skin location and window size as needed.
4. **Set the Python and script paths** in `slurm_daemon.pyw` and the optional `.vbs` startup script.

## Notes

- The daemon sends one `squeue` request per minute, keeping the query load low.
- For password-based SSH authentication, ensure that the wrapper can find its credential files.
- The Rainmeter skin can be dragged or closed through its context menu.
- The panel height expands automatically when multiple jobs are displayed.

## Architecture

```
slurm_daemon.pyw (every 60 seconds)
    └→ slurm_fetch.py
         └→ SSH → squeue -u user
              └→ jobs.txt
                   └→ Rainmeter WebParser (reads every 10 seconds)
                        └→ Desktop display
```

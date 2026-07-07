"""
Background daemon: runs slurm_fetch.py every 60 seconds.

Usage:
    pythonw slurm_daemon.pyw     # Windows (no console)
    python  slurm_daemon.pyw     # Debug mode (with console output)

Double-click .pyw to start silently. Exit via Task Manager (kill pythonw.exe).

Optional: also runs slurm_notify.py for WeChat push (see slurm-wechat-notify project).
"""
import subprocess
import time

# ── Configuration (edit these) ──────────────────────────────
PYTHON = r"C:\path\to\python.exe"           # Your Python path
FETCH_SCRIPT = r"C:\path\to\slurm_fetch.py"  # Desktop widget data fetcher
NOTIFY_SCRIPT = r""  # Optional: path to slurm_notify.py (WeChat push), or leave empty

print("SLURM daemon started. Updating every 60s...")
print("Close this window or Ctrl+C to stop.")

while True:
    try:
        # Refresh job display data
        subprocess.run(
            [PYTHON, FETCH_SCRIPT],
            capture_output=True,
            timeout=55,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        now = time.strftime("%H:%M:%S")
        print(f"[{now}] Data refreshed.")

        # Check for completed jobs → WeChat notify (optional)
        if NOTIFY_SCRIPT:
            subprocess.run(
                [PYTHON, NOTIFY_SCRIPT],
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")

    time.sleep(60)

"""
SLURM data fetcher for Rainmeter desktop widget.
Fetches squeue output via SSH and writes formatted text to disk.
"""
import subprocess
import time
import os

# ── Configuration (edit these) ──────────────────────────────
# Path to your SSH wrapper (e.g., hpc-run.ps1, or direct ssh)
SSH_WRAPPER = r"C:\path\to\your-ssh-wrapper.ps1"

# Output file (Rainmeter skin reads this)
OUTPUT_FILE = r"C:\Users\...\Documents\Rainmeter\Skins\Hanhai22Jobs\jobs.txt"

# SLURM username
SLURM_USER = "your_username"

# squeue format: JOBID, NAME, USER, TIME, STATE, NODELIST
SQUEUE_FMT = "%.10i %.18j %.8u %.10M %.8T %N"

# Cluster display name
CLUSTER_NAME = "MyCluster"


def fetch_squeue():
    """Run squeue via SSH and return list of job tuples."""
    try:
        result = subprocess.run(
            [
                "powershell", "-NoProfile", "-NoLogo",
                "-File", SSH_WRAPPER,
                "--", f"squeue -u {SLURM_USER} -o '{SQUEUE_FMT}'"
            ],
            capture_output=True,
            timeout=50,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )

        if result.returncode != 0:
            return None, result.stderr.decode("utf-8", errors="replace").strip()

        raw = result.stdout.decode("utf-8", errors="replace")
        jobs = []
        for line in raw.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("JOBID") or line.startswith("---"):
                continue
            parts = line.split()
            if len(parts) >= 5:
                jobid = parts[0]
                name  = parts[1]
                user  = parts[2]
                jtime = parts[3]
                state = parts[4]
                node  = parts[5] if len(parts) >= 6 else "-"
                jobs.append((jobid, name, user, jtime, state, node))
        return jobs, None

    except subprocess.TimeoutExpired:
        return None, "Connection timeout"
    except Exception as e:
        return None, str(e)


def format_output(jobs, error):
    """Format jobs into multi-line text block for Rainmeter display."""
    lines = []
    now = time.strftime("%H:%M:%S")
    lines.append(f"{CLUSTER_NAME}  |  {now}")

    if error:
        lines.append("")
        lines.append(f"! {error[:60]}")
    elif not jobs:
        lines.append("")
        lines.append("no jobs")
    else:
        lines.append("")
        for job in jobs:
            jid, name, user, jtime, state, node = job
            if state == "RUNNING":
                prefix = "*"
            elif state in ("PENDING", "CONFIGURING"):
                prefix = "-"
            else:
                prefix = " "
            lines.append(
                f"{prefix} {jid}  {name[:16]:<16}  "
                f"{jtime:>8}  {state:<8}  {node}"
            )

    return "\n".join(lines)


def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    jobs, error = fetch_squeue()
    text = format_output(jobs, error)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()

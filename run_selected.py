from pathlib import Path
import subprocess
import sys

FILES = [
    r"C:\Users\cheer\hcl\doclib\capabilities-guide.pdf",
    r"C:\Users\cheer\hcl\doclib\Cyber Security Managed Services.pdf",
    r"C:\Users\cheer\hcl\doclib\TCS-Cyber-Security-Implementation-Services.pdf",
]

def main():
    cmd = [sys.executable, "-m", "src.main_ingest", "--files", *FILES, "--out", "out_txt", "--cpu-only"]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)

if __name__ == "__main__":
    main()

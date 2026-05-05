import psutil
import time


# =========================
# CONFIG
# =========================
TARGET_PROCESS = "notepad.exe"
SIMULATOR_SCRIPT_KEYWORD = "simulation.py"

SYSTEM_PROCESSES = {
    "wsl.exe",
    "explorer.exe",
    "system",
    "wininit.exe",
    "services.exe",
    "csrss.exe",
    "python.exe"  # نحميه إلا ما تأكدناش أنه simulator
}


# =========================
# LOG FUNCTION
# =========================
def log(msg):
    print(msg)
    with open("defuse_log.txt", "a") as f:
        f.write(msg + "\n")


# =========================
# KILL TARGET PROCESS (NOTEPAD)
# =========================
def kill_notepad():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and TARGET_PROCESS in proc.info['name'].lower():
                log(f"[+] Killing Notepad PID: {proc.pid}")
                proc.kill()
        except:
            pass


# =========================
# FIND + KILL SIMULATOR (ROOT CAUSE)
# =========================
def kill_simulator():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = " ".join(proc.cmdline() or [])

            # نلقاو script اللي كيعيد تشغيل notepad
            if SIMULATOR_SCRIPT_KEYWORD in cmd.lower():

                log(f"\n[!] Simulator detected PID: {proc.pid}")
                log(f"[!] Command: {cmd}")

                # safety check
                if proc.name().lower() in SYSTEM_PROCESSES:
                    log("[SAFE] Skipping system process")
                    continue

                log(f"[🔥] Killing simulator process: {proc.pid}")
                proc.kill()

        except:
            pass


# =========================
# REAL-TIME LOOP
# =========================
def main():
    log("=== DEFUSE REAL-TIME ANTI-SIMULATOR STARTED ===")

    while True:
        kill_notepad()
        kill_simulator()
        time.sleep(2)


if __name__ == "__main__":
    main()
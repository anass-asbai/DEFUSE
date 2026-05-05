import psutil
import os
import winreg
import socket


MALWARE_NAME = "notepad.exe"  
MALWARE_PATH = "\\notepad.exe"


# =========================
# 2. KILL PROCESS
# =========================
def kill_malware_process():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if MALWARE_NAME.lower() in proc.info['name'].lower():
                print(f"[+] Killing process: {proc.info['name']} (PID {proc.info['pid']})")
                psutil.Process(proc.info['pid']).terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


# =========================
# 3. REMOVE FILE
# =========================
def remove_malware_file():
    if os.path.exists(MALWARE_PATH):
        try:
            os.remove(MALWARE_PATH)
            print("[+] Malware file deleted")
        except Exception as e:
            print(f"[-] Error deleting file: {e}")


# =========================
# 4. REMOVE STARTUP PERSISTENCE
# =========================
def remove_startup_entry():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_ALL_ACCESS
        )

        winreg.DeleteValue(key, "Malware")
        winreg.CloseKey(key)

        print("[+] Startup entry removed")

    except FileNotFoundError:
        print("[!] No startup entry found")
    except Exception as e:
        print(f"[-] Registry error: {e}")


# =========================
# 5. GET ATTACKER IP (SIMPLIFIED)
# =========================
def get_attacker_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"[+] Local/Observed IP: {local_ip}")
        return local_ip
    except Exception as e:
        print(f"[-] IP error: {e}")
        return None


# =========================
# 6. MAIN FUNCTION
# =========================
def main():
    print("=== Malware Removal Tool Started ===")

    kill_malware_process()
    remove_startup_entry()
    remove_malware_file()
    ip = get_attacker_ip()

    print("=== Done ===")
    print(f"Attacker IP (simulated): {ip}")


if __name__ == "__main__":
    main()
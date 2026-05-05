import psutil
import os
import winreg
import socket

# =========================
# =========================
MALWARE_NAME = "malware.exe"  
MALWARE_PATH = "C:\\malware\\malware.exe"


# =========================
# 2. KILL PROCESS
# =========================

def find_and_kill_parent_of_notepad():
    for proc in psutil.process_iter(['pid', 'name', 'ppid']):
        try:
            if proc.info['name'] and "notepad.exe" in proc.info['name'].lower():
                
                parent = psutil.Process(proc.info['ppid'])
                
                print(f"[+] Notepad PID: {proc.info['pid']}")
                print(f"[+] Parent PID: {parent.pid}")
                print(f"[+] Parent Name: {parent.name()}")

                # 🔥 Kill parent (source)
                print(f"[!] Killing parent process: {parent.name()}")
                parent.kill()

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

        winreg.DeleteValue(key, "Malware")  # اسم entry تخيلي
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

    find_and_kill_parent_of_notepad()
    remove_startup_entry()
    remove_malware_file()
    ip = get_attacker_ip()

    print("=== Done ===")
    print(f"Attacker IP (simulated): {ip}")


if __name__ == "__main__":
    main()
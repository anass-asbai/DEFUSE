import psutil
import os
import socket
import logging
import sys
from datetime import datetime

# Windows-only imports
try:
    import winreg
    WINDOWS = True
except ImportError:
    WINDOWS = False

# =========================
# CONFIGURATION
# =========================
MALWARE_NAME = "malware.exe"
MALWARE_PATH = r"C:\malware\malware.exe"
REGISTRY_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
REGISTRY_VALUE_NAME = "Malware"
PARENT_PROCESS_TRIGGER = "notepad.exe"

# =========================
# LOGGING SETUP
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"removal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
log = logging.getLogger(__name__)


# =========================
# PROCESS HANDLING
# =========================
def find_and_kill_process_by_name(target_name: str) -> bool:
    """Kill any process whose name matches target_name."""
    killed = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and target_name.lower() in proc.info['name'].lower():
                log.info(f"Found target process: {proc.info['name']} (PID {proc.info['pid']})")
                proc.kill()
                proc.wait(timeout=5)
                log.info(f"Killed PID {proc.info['pid']}")
                killed = True
        except psutil.NoSuchProcess:
            log.debug("Process already gone.")
        except psutil.AccessDenied:
            log.warning(f"Access denied when trying to kill PID {proc.info.get('pid')}")
        except psutil.TimeoutExpired:
            log.warning(f"Timeout waiting for PID {proc.info.get('pid')} to exit")
    return killed


def find_and_kill_parent_of(child_name: str) -> bool:
    """Find a process by name and kill its parent."""
    killed = False
    for proc in psutil.process_iter(['pid', 'name', 'ppid']):
        try:
            if proc.info['name'] and child_name.lower() in proc.info['name'].lower():
                parent = psutil.Process(proc.info['ppid'])
                log.info(f"Found child '{proc.info['name']}' (PID {proc.info['pid']}), "
                         f"parent: '{parent.name()}' (PID {parent.pid})")
                parent.kill()
                parent.wait(timeout=5)
                log.info(f"Killed parent PID {parent.pid}")
                killed = True
        except psutil.NoSuchProcess:
            log.debug("Process already gone.")
        except psutil.AccessDenied:
            log.warning(f"Access denied killing parent of '{child_name}'")
        except psutil.TimeoutExpired:
            log.warning("Timeout waiting for parent process to exit.")
    return killed


# =========================
# FILE REMOVAL
# =========================
def remove_file(path: str) -> bool:
    """Safely remove a file at the given path."""
    if not os.path.exists(path):
        log.warning(f"File not found: {path}")
        return False
    try:
        os.remove(path)
        log.info(f"Deleted file: {path}")
        return True
    except PermissionError:
        log.error(f"Permission denied deleting: {path}")
    except OSError as e:
        log.error(f"OS error deleting '{path}': {e}")
    return False


# =========================
# REGISTRY CLEANUP (Windows only)
# =========================
def remove_registry_startup_entry(value_name: str) -> bool:
    """Remove a startup registry entry by value name."""
    if not WINDOWS:
        log.warning("Registry cleanup skipped: not running on Windows.")
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_KEY_PATH,
            0,
            winreg.KEY_ALL_ACCESS
        ) as key:
            winreg.DeleteValue(key, value_name)
            log.info(f"Removed registry startup entry: '{value_name}'")
            return True
    except FileNotFoundError:
        log.info(f"Registry entry '{value_name}' not found (already clean).")
    except PermissionError:
        log.error("Permission denied accessing registry.")
    except OSError as e:
        log.error(f"Registry error: {e}")
    return False


# =========================
# NETWORK INFO
# =========================
def get_active_connections() -> list[dict]:
    """Return a list of active TCP connections with remote IPs."""
    connections = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_ESTABLISHED and conn.raddr:
                connections.append({
                    "local": f"{conn.laddr.ip}:{conn.laddr.port}",
                    "remote": f"{conn.raddr.ip}:{conn.raddr.port}",
                    "pid": conn.pid
                })
    except psutil.AccessDenied:
        log.warning("Access denied reading network connections.")
    return connections


def get_local_ip() -> str | None:
    """Get the machine's local IP address."""
    try:
        with socket.create_connection(("8.8.8.8", 80), timeout=3) as s:
            return s.getsockname()[0]
    except OSError as e:
        log.error(f"Could not determine local IP: {e}")
        return None


# =========================
# MAIN
# =========================
def main():
    log.info("=== Malware Removal Tool Started ===")

    log.info("-- Step 1: Kill suspicious parent process --")
    find_and_kill_parent_of(PARENT_PROCESS_TRIGGER)

    log.info("-- Step 2: Kill malware process directly --")
    find_and_kill_process_by_name(MALWARE_NAME)

    log.info("-- Step 3: Remove startup registry entry --")
    remove_registry_startup_entry(REGISTRY_VALUE_NAME)

    log.info("-- Step 4: Delete malware file --")
    remove_file(MALWARE_PATH)

    log.info("-- Step 5: Network info --")
    local_ip = get_local_ip()
    log.info(f"Local IP: {local_ip}")

    connections = get_active_connections()
    if connections:
        log.info(f"Active connections ({len(connections)}):")
        for c in connections:
            log.info(f"  {c['local']} -> {c['remote']} (PID {c['pid']})")
    else:
        log.info("No active established connections found.")

    log.info("=== Removal Complete ===")


if __name__ == "__main__":
    if WINDOWS and not ctypes_is_admin():
        log.warning("Not running as Administrator — some operations may fail.")
    main()


def ctypes_is_admin() -> bool:
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False
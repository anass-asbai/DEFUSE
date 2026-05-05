# 📄 DEFUSE - Malware Analysis Tool (TEST VERSION)

## 🧠 Project Overview

This is a **simple educational testing tool** made with Python to demonstrate basic process detection and cleanup concepts in a safe environment.

⚠️ This code is ONLY for testing and learning purposes.

It uses Notepad as a test process and does not represent real malware.

---

## ⚙️ What it does

* Detects `notepad.exe` (test process)
* Finds its parent process
* Tries to terminate the parent process (simulation)
* Deletes a test file path
* Removes a test registry entry
* Shows local IP address

---

## 🚀 How to run

```bash
pip install psutil
python main.py
```

---

## ⚠️ Safety note

* For **learning / testing only**
* Run only in a **virtual machine**
* Not real malware and not harmful in this context

---

## 🧠 Goal

To understand basic:

* Process monitoring
* Parent-child process structure
* Simple system cleanup concepts

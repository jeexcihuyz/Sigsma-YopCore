<div align="center">

# ⚡ Sigsma-YopCore
### High-Performance Yopmail Scraper & TLS Bypass Engine

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## 🚀 Overview
**Sigsma-YopCore** is a high-performance Yopmail scraper and API wrapper engineered to bypass strict anti-bot protections, Cloudflare challenges, and browser verification layers using advanced TLS fingerprint spoofing.

---

## ✨ Key Features
* **TLS Fingerprint Spoofing:** Powered by `curl_cffi` to accurately mimic real browser profiles (Chrome 120+) and evade WAF/Cloudflare blocks.
* **High-Speed Polling Engine:** Fully optimized request pipeline for fast inbox rendering and token extraction.
* **Robust Session Management:** Smart token extraction (`yp`, `yj`) and automated cookie handling for uninterrupted polling.
* **Lightweight & Modular:** Minimal third-party dependencies designed for maximum execution speed.

---

## 📦 Installation & Setup

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/jeexcihuyz/Sigsma-YopCore.git
cd Sigsma-YopCore
pip install curl_cffi beautifulsoup4
```

---

## 🛠️ Quick Usage

```python
from sigsma_yopcore import YopmailKiller

def main():
    # Initialize the core client
    target = "testuser@yopmail.com"
    client = YopmailKiller(target)
    
    # Fetch inbox
    inbox = client.get_inbox()
    print(f"Inbox items found: {len(inbox)}")
    
    # Read the latest email if available
    if inbox:
        print(f"Latest sender: {inbox[0]['sender']}")
        content = client.read_mail(inbox[0]['id'])
        print(content)

if __name__ == "__main__":
    main()
```

---

## 🛡️ Disclaimer
This tool is developed strictly for educational purposes and personal automation testing. The author assumes no liability and is not responsible for any misuse or damage caused by this software.

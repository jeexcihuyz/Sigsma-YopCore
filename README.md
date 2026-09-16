# 🧨 Yopmail-Killer
An advanced, lightweight, and anti-bot resistant Yopmail API Wrapper written in Python. 
Built to survive Cloudflare and hCaptcha in 2026 without using heavy headless browsers.

Unlike other libraries on GitHub that use standard HTTP requests (which get instantly blocked by Yopmail's WAF) or hardcoded tokens, this wrapper uses **TLS Fingerprint Spoofing** via `curl_cffi` to perfectly impersonate Chrome 120.

## 🌟 Why is this better?
*   ✅ **No Hardcoded Tokens:** Dynamically extracts `yp`, `yj`, and API version on every session.
*   ✅ **TLS Spoofing:** Perfect JA3/HTTP2 fingerprinting. Yopmail thinks you are a real human using Google Chrome.
*   ✅ **Zero Headless Browsers:** No Puppeteer, no Playwright. Pure HTTP requests. Very fast and consumes almost 0 RAM.
*   ✅ **Smart Cookie Handling:** Automatically generates human-like `ytime` cookies.

## 📦 Requirements
```bash
pip install curl_cffi beautifulsoup4
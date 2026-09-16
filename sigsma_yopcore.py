"""
Yopmail Killer - Proof of Concept 2026
Advanced Yopmail API Wrapper with TLS Fingerprint Spoofing
"""

import time
import random
import re
import datetime
from bs4 import BeautifulSoup
from curl_cffi import requests
from curl_cffi import CurlHttpVersion

class YopmailKiller:
    def __init__(self, email, proxy_dict=None):
        self.email = email
        self.username = email.split('@')[0]
        
        # Core Weapon: Impersonate Chrome 120 to bypass Cloudflare/hCaptcha
        self.session = requests.Session(impersonate="chrome120")
        self.session.http_version = CurlHttpVersion.V2_0
        if proxy_dict:
            self.session.proxies = proxy_dict
            
        self.url_base = "https://yopmail.com/"
        self.yp_token = None
        self.yj_token = None
        self.ver_str = "9.3" # Default fallback version
        self._is_ready = False

    def _handshake(self):
        """Extracts dynamic tokens (yp & yj) directly from the server to initialize the session."""
        print(f"[*] Initiating TLS handshake & spoofing for: {self.email}...")
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        })
        
        try:
            # 1. Extract YP Token
            res1 = self.session.get(f"{self.url_base}en/?login={self.username}", timeout=15)
            soup = BeautifulSoup(res1.text, "html.parser")
            yp_input = soup.find("input", {"name": "yp"})
            if not yp_input:
                raise Exception("Failed to extract YP token. Blocked by Cloudflare?")
            self.yp_token = yp_input.get("value")
            
            time.sleep(random.uniform(0.5, 1.5))
            
            # 2. Extract API Version & YJ Token from webmail.js
            payload = {"yp": self.yp_token, "login": self.username, "id": ""}
            res2 = self.session.post(self.url_base, data=payload, timeout=15)
            
            version_match = re.search(r'/ver/([\d\.]+)/webmail\.js', res2.text)
            if version_match:
                self.ver_str = version_match.group(1)
                
            res_js = self.session.get(f"{self.url_base}ver/{self.ver_str}/webmail.js", timeout=10)
            yj_match = re.search(r'yj=([a-zA-Z0-9]+)', res_js.text)
            if not yj_match:
                raise Exception("Failed to extract YJ token.")
            self.yj_token = yj_match.group(1)
            
            # 3. Inject Human-like Time Cookies
            now = datetime.datetime.now()
            self.session.cookies.set("ytime", f"{now.hour}:{now.minute:02d}", domain="yopmail.com")
            self.session.cookies.set("ywm", self.email, domain="yopmail.com")
            
            self._is_ready = True
            print("[+] Handshake successful! Session is now secure and ready.")
            return True
            
        except Exception as e:
            print(f"[-] Handshake failed: {e}")
            return False

    def get_inbox(self):
        """Fetches the list of incoming emails."""
        if not self._is_ready and not self._handshake():
            return []

        params = {
            "login": self.username, "p": "1", "d": "", "ctrl": "",
            "yp": self.yp_token, "yj": self.yj_token, "v": self.ver_str,
            "r_c": "", "id": "", "ad": "0"
        }
        self.session.headers.update({"Referer": f"{self.url_base}wm", "Sec-Fetch-Dest": "iframe"})
        
        try:
            res = self.session.get(f"{self.url_base}inbox", params=params, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            
            emails = []
            for div in soup.find_all("div", class_="m"):
                mail_id = "m" + div.get("id") if div.get("id") else None
                sender = div.find(class_="lmf").text if div.find(class_="lmf") else "Unknown"
                subject = div.find(class_="lms_m").text if div.find(class_="lms_m") else "No Subject"
                
                if mail_id:
                    emails.append({"id": mail_id, "sender": sender, "subject": subject})
            return emails
        except Exception as e:
            print(f"[-] Failed to fetch inbox: {e}")
            return []

    def read_mail(self, mail_id):
        """Reads the body of a specific email by ID."""
        if not self._is_ready: return None
        
        self.session.headers.update({"Referer": f"{self.url_base}"})
        try:
            res = self.session.get(f"{self.url_base}mail", params={"b": self.username, "id": mail_id}, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            body = soup.find(id="mailmillieu")
            return body.text.strip() if body else "Message body is empty."
        except Exception as e:
            print(f"[-] Failed to read message: {e}")
            return None

# ==========================================
# INTERACTIVE CLI FOR EASY TESTING
# ==========================================
if __name__ == "__main__":
    print("="*55)
    print(" 🚀 YOPMAIL KILLER - PROOF OF CONCEPT 2026 🚀 ")
    print("="*55)
    
    # User-Friendly Input Prompt
    target_input = input("[?] Enter target Yopmail address (leave blank for random): ").strip()
    
    if not target_input:
        random_suffix = random.randint(10000, 99999)
        target = f"testuser_{random_suffix}@yopmail.com"
        print(f"[*] No input provided. Auto-generated email: {target}")
    else:
        target = target_input if "@yopmail.com" in target_input else f"{target_input}@yopmail.com"

    print("\n" + "-"*55)
    bot = YopmailKiller(target)
    
    # Fetch Inbox
    inbox = bot.get_inbox()
    
    print(f"\n[📥] Inbox for {target}:")
    if not inbox:
        print("[-] The inbox is currently empty. Try sending an email first.")
    else:
        for idx, mail in enumerate(inbox):
            print(f"  {idx+1}. From: {mail['sender']} | Subject: {mail['subject']}")
            
        print("\n[📖] Reading the most recent message:")
        print("-" * 55)
        content = bot.read_mail(inbox[0]["id"])
        print(content)
        print("-" * 55)
        print("[+] Test completed successfully!")

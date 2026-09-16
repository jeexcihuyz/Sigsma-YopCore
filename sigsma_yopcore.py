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
                raise Exception("Failed to extract YP token. Blocked by Cloudflare WAF?")
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
                mail_id = div.get("id") if div.get("id") else None
                sender = div.find(class_="lmf").text.strip() if div.find(class_="lmf") else "Unknown"
                subject = div.find(class_="lms").text.strip() if div.find(class_="lms") else "No Subject"
                
                if mail_id:
                    emails.append({"id": mail_id, "sender": sender, "subject": subject})
            return emails
        except Exception as e:
            print(f"[-] Failed to fetch inbox: {e}")
            return []

    def _clean_text(self, raw_text):
        """Cleans up messy HTML whitespace for CLI rendering."""
        # 1. Remove excessive whitespace/tabs from each line
        lines = [line.strip() for line in raw_text.splitlines()]
        
        # 2. Recombine the lines
        cleaned_text = "\n".join(lines)
        
        # 3. Reduce multiple consecutive newlines (3 or more) to a maximum of 2 (paragraph spacing)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        return cleaned_text.strip()

    def read_mail(self, mail_id):
        """Reads the body of a specific email, preserving URLs."""
        if not self._is_ready: return None
        
        self.session.headers.update({"Referer": f"{self.url_base}wm"})
        
        # FIX 1: Add 'm' prefix to mail_id for HTML render mode
        fetch_id = f"m{mail_id}" if mail_id.startswith("e_") else mail_id
        
        try:
            res = self.session.get(f"{self.url_base}mail", params={"b": self.username, "id": fetch_id}, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 1. Check direct render (Modern Yopmail behavior)
            mail_div = soup.find(id="mail")
            if mail_div:
                # FIX 2: Preserve the href links so you can extract OTP/Magic Links
                for a_tag in mail_div.find_all('a'):
                    if a_tag.get('href'):
                        a_tag.replace_with(f"{a_tag.text} [ {a_tag.get('href')} ]")
                
                raw_text = mail_div.get_text(separator="\n")
                return self._clean_text(raw_text)
            
            # 2. Check if message is wrapped inside an iframe (Legacy behavior)
            iframe = soup.find("iframe", {"id": "ifmail"})
            if iframe and iframe.get("src"):
                iframe_src = iframe.get("src")
                if not iframe_src.startswith("http"):
                    iframe_src = self.url_base + iframe_src.lstrip("/")
                
                res_iframe = self.session.get(iframe_src, timeout=10)
                soup_iframe = BeautifulSoup(res_iframe.text, "html.parser")
                body = soup_iframe.find(id="mailmillieu") or soup_iframe.body
                raw_text = body.get_text(separator="\n") if body else res_iframe.text
                return self._clean_text(raw_text)
            
            # 3. Final fallback
            body = soup.find(id="mailmillieu")
            raw_text = body.get_text(separator="\n") if body else "Message body is empty."
            return self._clean_text(raw_text)
            
        except Exception as e:
            print(f"[-] Failed to read message: {e}")
            return None

# ==========================================
# INTERACTIVE CLI FOR EASY TESTING
# ==========================================
if __name__ == "__main__":
    print("="*60)
    print(" 🚀 YOPMAIL KILLER - PROOF OF CONCEPT 2026 🚀 ")
    print("="*60)
    
    target_input = input("[?] Enter target Yopmail address (leave blank for random): ").strip()
    
    if not target_input:
        random_suffix = random.randint(10000, 99999)
        target = f"testuser_{random_suffix}@yopmail.com"
        print(f"[*] No input provided. Auto-generated email: {target}")
    else:
        target = target_input if "@yopmail.com" in target_input else f"{target_input}@yopmail.com"

    print("\n" + "-"*60)
    bot = YopmailKiller(target)
    
    inbox = bot.get_inbox()
    
    print(f"\n[📥] Inbox for {target}:")
    if not inbox:
        print("[-] The inbox is currently empty. Try sending an email first.")
    else:
        # Display the list of all available messages
        for idx, mail in enumerate(inbox):
            print(f"  [{idx+1}] From: {mail['sender']}")
            print(f"      Subject: {mail['subject']}")
            
        # Interactive loop to allow the user to read multiple messages
        while True:
            print("\n" + "-"*60)
            choice = input(f"[?] Select a message to read (1 - {len(inbox)}) or type '0' to exit: ").strip()
            
            if choice == '0':
                print("[*] Exiting inbox. Goodbye!")
                break
                
            try:
                idx_choice = int(choice) - 1
                
                # Validate if the chosen number is within the list range
                if 0 <= idx_choice < len(inbox):
                    print(f"\n[📖] Reading Message #{idx_choice + 1}:")
                    print("="*60)
                    
                    content = bot.read_mail(inbox[idx_choice]["id"])
                    
                    if content:
                        print(content)
                    else:
                        print("[Empty Message / Failed to extract]")
                        
                    print("="*60)
                else:
                    print("[-] Invalid number. Out of range. Please try again.")
                    
            except ValueError:
                print("[-] Invalid input format! Please enter a valid number.")
                
    print("\n[+] Execution completed.")

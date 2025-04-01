import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
import json
import threading
from bs4 import BeautifulSoup
import webbrowser
from cryptography.fernet import Fernet
import base64
import os

CONFIG_FILE = "config.json"

ARSINEK_LOGO = """
  $$$$$$  /$$$$$$  /$$$$$$$  /$$$$$$  /$$   /$$ /$$$$$$$$
 /$$__  $$|_  $$_/ | $$__  $$|_  $$_/ | $$$ | $$| $$_____/
| $$  \ $$  | $$   | $$  \ $$  | $$   | $$$$| $$| $$      
| $$  | $$  | $$   | $$$$$$$   | $$   | $$ $$ $$| $$$$$   
| $$  | $$  | $$   | $$__  $$  | $$   | $$  $$$$| $$__/   
| $$  | $$  | $$   | $$  \ $$  | $$   | $$\  $$$| $$      
|  $$$$$$/ /$$$$$$ | $$$$$$$/ /$$$$$$ | $$ \  $$| $$$$$$$$
 \______/ |______/ |_______/ |______/ |__/  \__/|________/
"""

KEYWORDS = {
    "Twitter": ["#العربية", "#تكنولوجيا", "#gaming", "#كورة", "#trending", "#AI"],
    "Instagram": ["#موضة", "#سفر", "طبخ", "دبي", "fitness", "beauty"],
    "TikTok": ["#ترند", "رقص", "كوميديا", "مصر", "foryou", "viral"],
    "Facebook": ["برمجة", "سيارات", "أخبار", "سفر", "tech", "food"]
}

# --- Encryption Functions ---
def generate_key():
    return Fernet.generate_key()

def encrypt_message(message: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(message.encode()).decode()

def decrypt_message(encrypted_message: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted_message.encode()).decode()


# --- Helper Functions ---
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}, "accounts": {}}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def fetch_and_test_proxies(num_proxies=10):
    try:
        response = requests.get("https://free-proxy-list.net/", headers={"User-Agent": UserAgent().random}, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        proxies = [f"http://{row.find_all('td')[0].text}:{row.find_all('td')[1].text}" for row in soup.find("tbody").find_all("tr")[:num_proxies]]
        working_proxies = []
        for proxy in proxies:
            try:
                test_response = requests.get("https://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=5)
                if test_response.status_code == 200:
                    working_proxies.append(proxy)
            except:
                continue
        return working_proxies if working_proxies else None
    except:
        return None

def is_login_successful(driver, platform):
    try:
        if platform == "Twitter":
            return "home" in driver.current_url
        elif platform == "Instagram":
            return "instagram.com" in driver.current_url and "accounts/login" not in driver.current_url
        elif platform == "TikTok":
            return "tiktok.com" in driver.current_url and "login" not in driver.current_url
        elif platform == "Facebook":
            return "facebook.com" in driver.current_url and "login" not in driver.current_url
        return False
    except:
        return False

def login_to_platform(driver, platform, username, password, log_function):
    login_urls = {
        "Twitter": "https://x.com/login",
        "Instagram": "https://www.instagram.com/accounts/login/",
        "TikTok": "https://www.tiktok.com/login",
        "Facebook": "https://www.facebook.com/login"
    }
    driver.get(login_urls[platform])
    time.sleep(3)
    try:
        if platform == "Twitter":
            driver.find_element(By.NAME, "text").send_keys(username)
            driver.find_element(By.XPATH, "//span[text()='Next']").click()
            time.sleep(2)
            driver.find_element(By.NAME, "password").send_keys(password)
            driver.find_element(By.XPATH, "//span[text()='Log in']").click()
        elif platform == "Instagram":
            driver.find_element(By.NAME, "username").send_keys(username)
            driver.find_element(By.NAME, "password").send_keys(password)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
        elif platform == "TikTok":
            driver.find_element(By.XPATH, "//input[@name='username']").send_keys(username)
            driver.find_element(By.XPATH, "//input[@type='password']").send_keys(password)
            driver.find_element(By.XPATH, "//button[text()='Log in']").click()
        elif platform == "Facebook":
            driver.find_element(By.ID, "email").send_keys(username)
            driver.find_element(By.ID, "pass").send_keys(password)
            driver.find_element(By.NAME, "login").click()
        time.sleep(5)
        return is_login_successful(driver, platform)
    except Exception as e:
        log_function(f"Login error: {str(e)}", "error")
        return False

# --- Main Application Class ---
class FollowerBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("رشق المتابعين - ARSINEK")
        self.root.geometry("1080x1080")
        self.root.configure(bg="#2c2f33")
        self.running = False
        self.driver = None
        self.encryption_key = generate_key()

        self.main_frame = tk.Frame(root, bg="#2c2f33")
        self.main_frame.pack(expand=True, pady=20, padx=20)

        tk.Label(self.main_frame, text=ARSINEK_LOGO, font=("Courier", 12, "bold"), bg="#2c2f33", fg="#7289da").pack(pady=10)

        # Developer's Message - Placed at the TOP, made very clear
        
        
        self.developer_message = tk.Label(self.main_frame, text="""
            هام جداً:
               التطبيق متوقف مؤقتًا.
            بسبب ارتفاع تكاليف الاستضافة والخوادم، لا يمكننا الاستمرار في تقديم الخدمة حاليًا.

            لكن لا تقلقوا! التحديث الجديد قادم قريبًا جدًا!
            نعمل بجد على تطويره وإعادته بشكل أفضل.

            ترقبوا عودتنا القوية قريباً جداً!
            شكراً لتفهمكم ودعمكم المستمر.
            - تــــــــــــــــــــــــــيـــــــــــــــــــــم ARSINEK
        """, bg="#1c2f33", fg="#79906f", justify="center", font=("Arial", 14, "bold"))  # Made more prominent
        self.developer_message.pack(pady=20)

        # Platform Selection
        tk.Label(self.main_frame, text="اختر المنصة", bg="#2c2f33", fg="#ffffff", font=("Arial", 14, "bold")).pack(pady=5)
        self.platform_var = tk.StringVar(value="Twitter")
        self.platform_menu = ttk.Combobox(self.main_frame, textvariable=self.platform_var, values=["Twitter", "Instagram", "TikTok", "Facebook"], state="readonly", width=25)
        self.platform_menu.pack(pady=5)

        # Account Credentials Frame
        cred_frame = tk.LabelFrame(self.main_frame, text="بيانات الحساب", bg="#2c2f33", fg="#7289da", font=("Arial", 12, "bold"), padx=10, pady=10)
        cred_frame.pack(pady=10, fill="x")
        tk.Label(cred_frame, text="اسم المستخدم:", bg="#2c2f33", fg="#ffffff").grid(row=0, column=0, pady=5, padx=5)
        self.username_entry = tk.Entry(cred_frame, width=30, bg="#23272a", fg="white", insertbackground="white")
        self.username_entry.grid(row=0, column=1, pady=5)
        tk.Label(cred_frame, text="كلمة المرور:", bg="#2c2f33", fg="#ffffff").grid(row=1, column=0, pady=5, padx=5)
        self.password_entry = tk.Entry(cred_frame, width=30, show="*", bg="#23272a", fg="white", insertbackground="white")
        self.password_entry.grid(row=1, column=1, pady=5)

        # Settings Frame
        settings_frame = tk.LabelFrame(self.main_frame, text="الإعدادات", bg="#2c2f33", fg="#7289da", font=("Arial", 12, "bold"), padx=10, pady=10)
        settings_frame.pack(pady=10, fill="x")
        tk.Label(settings_frame, text="الكلمة المفتاحية:", bg="#2c2f33", fg="#ffffff").grid(row=0, column=0, pady=5, padx=5)
        self.keyword_var = tk.StringVar(value=KEYWORDS["Twitter"][0])
        self.keyword_menu = ttk.Combobox(settings_frame, textvariable=self.keyword_var, values=KEYWORDS["Twitter"], width=25)
        self.keyword_menu.grid(row=0, column=1, pady=5)
        self.platform_menu.bind("<<ComboboxSelected>>", self.update_keywords)
        tk.Label(settings_frame, text="عدد المتابعين:", bg="#2c2f33", fg="#ffffff").grid(row=1, column=0, pady=5, padx=5)
        self.follow_count_entry = tk.Entry(settings_frame, width=10, bg="#23272a", fg="white", insertbackground="white")
        self.follow_count_entry.grid(row=1, column=1, pady=5)
        tk.Label(settings_frame, text="سرعة المتابعة:", bg="#2c2f33", fg="#ffffff").grid(row=2, column=0, pady=5, padx=5)
        self.speed_var = tk.StringVar(value="متوسطة")
        ttk.Combobox(settings_frame, textvariable=self.speed_var, values=["بطيئة", "متوسطة", "سريعة"], state="readonly", width=25).grid(row=2, column=1, pady=5)
        tk.Label(settings_frame, text="استخدام Proxy:", bg="#2c2f33", fg="#ffffff").grid(row=3, column=0, pady=5, padx=5)
        self.use_proxy_var = tk.BooleanVar(value=False)
        tk.Checkbutton(settings_frame, variable=self.use_proxy_var, bg="#2c2f33", fg="#ffffff", selectcolor="#7289da").grid(row=3, column=1, pady=5)

        # Buttons Frame
        button_frame = tk.Frame(self.main_frame, bg="#2c2f33")
        button_frame.pack(pady=10)
        # Disable the start button
        self.start_button = tk.Button(button_frame, text="بدء الرشق", command=self.start_bot_thread, bg="#43b581", fg="white", font=("Arial", 12, "bold"), width=12, state="disabled")
        self.start_button.pack(side="left", padx=5)
        self.stop_button = tk.Button(button_frame, text="إيقاف", command=self.stop_bot, bg="#f04747", fg="white", font=("Arial", 12, "bold"), width=12, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        # Log Area
        self.log_area = scrolledtext.ScrolledText(self.main_frame, width=80, height=15, font=("Arial", 10), bg="#23272a", fg="white", insertbackground="white")
        self.log_area.pack(pady=10)

        # Statistics
        self.stats_label = tk.Label(self.main_frame, text="المتابعون الحاليون: غير معروف", bg="#2c2f33", fg="#ffffff")
        self.stats_label.pack(pady=5)

    def log(self, message, level="info"):
        colors = {"info": "white", "success": "#43b581", "error": "#f04747"}
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n", level)
        self.log_area.tag_config(level, foreground=colors.get(level, "white"))
        self.log_area.see(tk.END)

    def update_keywords(self, event):
        platform = self.platform_var.get()
        self.keyword_menu.config(values=KEYWORDS[platform])
        self.keyword_var.set(KEYWORDS[platform][0])

    def start_bot_thread(self):
        # show an error message telling the user that the bot is temporarily disabled
        messagebox.showinfo("تنبيه", "التطبيق متوقف مؤقتًا بسبب ارتفاع تكاليف التشغيل. التحديث قادم قريباً!")
        return

    def stop_bot(self):
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.log("تم إيقاف الرشق", "error")

    def get_follower_count(self, driver, platform):
        try:
            if platform == "Twitter":
                driver.get(f"https://twitter.com/{self.username_entry.get()}")
                time.sleep(2)
                return int(driver.find_element(By.XPATH, "//a[contains(@href, 'followers')]//span").text.replace(",", ""))
            elif platform == "Instagram":
                driver.get(f"https://www.instagram.com/{self.username_entry.get()}/")
                time.sleep(2)
                return int(driver.find_element(By.XPATH, "//span[@title]").text.replace(",", ""))
            return 0
        except Exception as e:
            self.log(f"Error getting follower count: {e}", "error")
            return None


    def start_bot(self):
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        platform = self.platform_var.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        keyword = self.keyword_var.get()
        use_proxy = self.use_proxy_var.get()
        speed = self.speed_var.get()

        try:
            max_follows = int(self.follow_count_entry.get())
            if max_follows <= 0:
                raise ValueError
        except:
            max_follows = 10
            self.log("خطأ في العدد، سيتم استخدام 10 كافتراضي", "error")

        if not all([username, password, keyword]):
            self.log("يرجى ملء جميع الحقول", "error")
            self.stop_bot()
            return


        config = load_config()
        config["accounts"][platform] = {"username": username, "password": password}
        save_config(config)

        self.log("جاري إعداد المتصفح...")
        options = Options()
        options.add_argument(f"user-agent={UserAgent().random}")

        if use_proxy:
            proxies = fetch_and_test_proxies()
            if proxies:
                proxy = random.choice(proxies)
                options.add_argument(f"--proxy-server={proxy}")
                self.log(f"استخدام Proxy: {proxy}")
            else:
                self.log("لم يتم العثور على Proxies، استخدام IP محلي", "error")
                use_proxy = False

        try:
            self.driver = webdriver.Chrome(options=options)
            self.log(f"تسجيل الدخول إلى {platform}...")
            if login_to_platform(self.driver, platform, username, password, self.log):
                self.log("تم تسجيل الدخول بنجاح", "success")
            else:
                self.log("فشل تسجيل الدخول", "error")
                raise Exception("فشل تسجيل الدخول")

            initial_followers = self.get_follower_count(self.driver, platform)
            if initial_followers is not None:
                self.stats_label.config(text=f"المتابعون الحاليون: {initial_followers}")

            delay_range = {"بطيئة": (10, 15), "متوسطة": (5, 10), "سريعة": (2, 5)}
            min_delay, max_delay = delay_range[speed]
            followed = 0

            while self.running and followed < max_follows:
                try:
                    if platform == "Twitter":
                        self.driver.get(f"https://twitter.com/search?q={keyword}&src=typed_query")
                        time.sleep(3)
                        follow_buttons = self.driver.find_elements(By.XPATH, "//div[@data-testid='placementTracking']//span[text()='Follow']")
                        for btn in follow_buttons[:max_follows - followed]:
                            if not self.running:
                                break
                            btn.click()
                            time.sleep(1)
                            parent_div = btn.find_element(By.XPATH, "..")
                            if "Following" in parent_div.text:
                                followed += 1
                                self.log(f"تم متابعة {followed}/{max_follows}", "success")
                            time.sleep(random.uniform(min_delay, max_delay))
                    elif platform == "Instagram":
                        self.driver.get(f"https://www.instagram.com/explore/tags/{keyword}/")
                        time.sleep(3)
                        follow_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Follow')]")
                        for btn in follow_buttons[:max_follows - followed]:
                            if not self.running:
                                break
                            btn.click()
                            time.sleep(1)
                            if "Following" in btn.text:
                                followed += 1
                                self.log(f"تم متابعة {followed}/{max_follows}", "success")
                            time.sleep(random.uniform(min_delay, max_delay))

                except Exception as e:
                    self.log(f"خطأ أثناء المتابعة: {e}", "error")

            if self.running:
                final_followers = self.get_follower_count(self.driver, platform)
                if final_followers is not None and initial_followers is not None:
                    self.stats_label.config(text=f"المتابعون الحاليون: {final_followers} (+{final_followers - initial_followers})")
                self.log("اكتمل الرشق بنجاح!", "success")
                messagebox.showinfo("نجاح", "تم الانتهاء من الرشق!")

        except Exception as e:
            self.log(f"خطأ فادح: {e}", "error")

        finally:
            self.stop_bot()

if __name__ == "__main__":
    root = tk.Tk()
    app = FollowerBotApp(root)
    root.mainloop()
    
    
    
    
"""

 /\/\/\   /\\   /\/\/\  /\\   /\  /\\\   /\/\/\  /\\
/ /  / /  /  \\ / /  / / /  \\ / / / //  / /  / / /  \\
\ \  \ \ / /\ \\ \  \ \ \ /\ \\ \/ /  \ \  \ \ \ /\ \\
 \/  \/ \/  \/  \/  \/  \/  \/   \/   \/  \/  \/  \/  \/

/\/\/\  /\\  /\   /\  /\\\   /\/\/\   /\\  /\   /\
/ /  / / /  \\ /  \ / / //  / /  / / /  \\ /  \ / /
\ \  \ \ \ /\ \\ /\  \ \/ /  \ \  \ \ \ /\ \\ /\  \ \
 \/  \/  \/  \/ \/  \/   \/   \/  \/  \/  \/ \/  \/

/\   /\/\/\   /\/\/\  /\\   /\/\/\  /\\
/  \ / /  / / / /  / / /  \\ / /  / / /  \\
\ /\ \ \  \ \ \ \  \ \ \ /\ \\ \  \ \ \ /\ \\
 \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/

""\  /""    /\  / /\    /\\
 \/ /    /\/ / /  \  /  \\
 /\ \   / /\/ /    \/ /\ \\
 \/  ""\/  ""\/     \/  \/  ""\/
"""
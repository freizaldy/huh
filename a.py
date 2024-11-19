import json
import time
import random
import string
import cloudscraper
# from random_username.generate import generate_username
from unique_names_generator import get_random_name
from unique_names_generator.data import ADJECTIVES, NAMES

# Konfigurasi akun password, refferal, dan captcha
password = "MasKri123#"
# reff = "8Fki69mIyWxPhgH"

key_2captcha = "99f9379b3d17c794025a2039600471b6"
url_web = "https://app.nodepay.ai"
googlekey = "0x4AAAAAAAx1CyDNL8zOEPe7"

def generate_username(length=12):
    # Kombinasi huruf dan angka
    characters = string.ascii_letters + string.digits
    # Membuat username acak
    username = ''.join(random.choice(characters) for _ in range(length))
    return username

# Fungsi untuk memuat proxy dari file
def load_proxies(filename):
    with open(filename, 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies

# Memilih proxy secara acak
def get_random_proxy(proxies):
    return random.choice(proxies) if proxies else None

# Inisialisasi cloudscraper dengan proxy
def create_scraper_with_proxy(proxy_url):
    scraper = cloudscraper.create_scraper()
    proxy_dict = {
        "http": proxy_url,
        "https": proxy_url
    }
    scraper.proxies = proxy_dict
    return scraper

# Fungsi untuk melakukan GET request
def get_request(url, scraper):
    response = scraper.get(url)
    if response.status_code == 200:
        return response.json()
    print(f"[x] equest gagal dengan status code {response.status_code}")
    return None

# Mendapatkan ID captcha dari 2captcha
def get_captcha_id(scraper):
    get_id_url = f"https://2captcha.com/in.php?key={key_2captcha}&method=turnstile&sitekey={googlekey}&pageurl={url_web}&json=1"
    response = get_request(get_id_url, scraper)
    return response['request'] if response and response['status'] == 1 else None

# Mengecek captcha hasil dari 2captcha
def check_captcha_response(res_id, scraper):
    while True:
        get_response_url = f"https://2captcha.com/res.php?key={key_2captcha}&action=get&id={res_id}&json=1"
        response = get_request(get_response_url, scraper)
        if response and response['status'] == 1:
            print("[#] \033[0;32mBERHASIL BYPASS CAPTCHA!!\033[0m")
            return response['request']
        time.sleep(2)

# Fungsi untuk menyimpan token ke dalam file
def save_token_to_file(token, filename='token.txt'):
    with open(filename, 'a') as file:  # Menggunakan mode 'a' untuk append
        file.write(f"{token}\n")  # Menyimpan token baru pada baris baru
    print(f"[#] Token akun berhasil disimpan ke {filename}")

# Fungsi untuk menyimpan akun ke dalam file
def save_akun_to_file(token, filename='akunRegis.txt'):
    with open(filename, 'a') as file:  # Menggunakan mode 'a' untuk append
        file.write(f"{token}\n")  # Menyimpan akun baru pada baris baru
    print(f"[#] Email akun berhasil disimpan ke {filename}")

# Fungsi untuk melakukan login dengan email, password, dan token captcha
def login(response_captcha, scraper, RegisterNew):
    payload = {"user": email, "password": password, "recaptcha_token": response_captcha}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/json',
        'authority': 'api.nodepay.org',
        'accept-language': 'id-ID,id;q=0.9',
        'origin': 'https://app.nodepay.ai',
        'referer': 'https://app.nodepay.ai/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site'
    }
    post_url = "https://api.nodepay.org/api/auth/login"
    response = scraper.post(post_url, json=payload, headers=headers, allow_redirects=True)

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            token = result['data']['token']
            user_info = result['data']['user_info']
            emailss = result['data']['user_info']['email']
            verifEmail(response_captcha, scraper, token)
            print("[#] Login Akun Berhasil!")
            print(f"[#] Username: {user_info['name']}")
            print(f"[#] Email: {user_info['email']}")
            print(f"[#] Token: {token}")
            # Jika pengguna memilih untuk register
            if RegisterNew == 'n':
                print(f"[#] Claim Verifikasi Email Task...")
                claimTaskEmail(response_captcha, scraper, token)
            print(f"[#] Claim Daily Treasure Task...")
            claimTaskDaily(response_captcha, scraper, token)
            print(f"[#] Submit Task QNA...")
            startQNA(response_captcha, scraper, token)
            print(f"[#] Aktivasi Ekstesi...")
            aktivasiAkun(response_captcha, scraper, token)
            
            # Simpan token ke dalam file
            save_token_to_file(f"{token}|{emailss}")
            save_akun_to_file(f"{emailss}|{password}")
        else:
            error_msg = result.get("msg", "Pesan tidak tersedia")
            # print("[x] Login Akun Gagal:", error_msg)

            # Jika captcha invalid, coba ulangi proses login dengan captcha baru
            if "Invalid captcha" in error_msg:
                print("[#] Captcha expired, mencoba bypass captcha ulang...")
                captcha_id = get_captcha_id(scraper)
                if captcha_id:
                    # print(f"[#] Melakukan Bypass Captcha...")
                    captcha_response = check_captcha_response(captcha_id, scraper)
                    # Panggil ulang fungsi login dengan captcha baru
                    login(captcha_response, scraper, RegisterNew)
                else:
                    print("\033[0;31mGAGAL GET ID!! GOOGLE KEY SALAH / APIKEY SALAH!!\033[0m\n")
    else:
        print(f"Request gagal dengan status code {response.status_code}")

        
# Melakukan login dengan email, password, dan token captcha
def register(response_captcha, scraper, generate_users, reff):
    payload = {"email": email, "username":generate_users, "password": password, "referral_code": reff, "recaptcha_token": response_captcha}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/json',
        'authority': 'api.nodepay.org',
        'accept-language': 'id-ID,id;q=0.9',
        'origin': 'https://app.nodepay.ai',
        'referer': 'https://app.nodepay.ai/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site'
    }
    post_url = "https://api.nodepay.org/api/auth/register"
    response = scraper.post(post_url, json=payload, headers=headers, allow_redirects=True)

    if response.status_code == 200:
        result = response.json()
        
        # Mengecek apakah respons success
        if result.get("success") == True:
            # Jika sukses, ambil token dan informasi pengguna
            token = result.get('data', {}).get('token')
            user_info = result.get('data', {}).get('user_info')
            print("[#] \033[0;32mBerhasil Membuat Akun!!\033[0m")

    
        else:
            # Jika gagal, tampilkan pesan kesalahan
            print("[x] Register Akun Gagal:", result.get("msg", "Pesan tidak tersedia"))
    else:
        print("Request gagal dengan status code:", response.status_code)
        
# Melakukan login dengan email, password, dan token captcha
def claimTaskDaily(response_captcha, scraper, token):
    payload = {"mission_id":"1"}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'authorization': f"Bearer {token}",
        'Content-Type': 'application/json',
        'authority': 'api.nodepay.org',
        'accept-language': 'id-ID,id;q=0.9',
        'origin': 'https://app.nodepay.ai',
        'referer': 'https://app.nodepay.ai/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site'
    }
    post_url = "https://api.nodepay.org/api/mission/complete-mission"
    response = scraper.post(post_url, json=payload, headers=headers, allow_redirects=True)

    if response.status_code == 200:
        result = response.json()
        
        # Mengecek apakah respons success
        if result.get("success") == True:
            # Jika sukses, ambil token dan informasi pengguna
            print("[#] \033[0;32mBerhasil Claim Treasure Daily Task!!\033[0m")

    
        else:
            # Jika gagal, tampilkan pesan kesalahan
            print("[x] Claim Task Daily:", result.get("msg", "Pesan tidak tersedia"))
    else:
        print("Request gagal dengan status code:", response.status_code)
        
# Melakukan login dengan email, password, dan token captcha
def claimTaskQuestion(response_captcha, scraper, token):
    payload = {"mission_id":"8"}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'authorization': f"Bearer {token}",
        'Content-Type': 'application/json',
        'authority': 'api.nodepay.org',
        'accept-language': 'id-ID,id;q=0.9',
        'origin': 'https://app.nodepay.ai',
        'referer': 'https://app.nodepay.ai/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site'
    }
    post_url = "https://api.nodepay.org/api/mission/complete-mission"
    response = scraper.post(post_url, json=payload, headers=headers, allow_redirects=True)

    if response.status_code == 200:
        result = response.json()
        
        # Mengecek apakah respons success
        if result.get("success") == True:
            # Jika sukses, ambil token dan informasi pengguna
            print("[#] \033[0;32mBerhasil Claim QNA Task!!\033[0m")

    
        else:
            # Jika gagal, tampilkan pesan kesalahan
            print("[x] Claim Task Daily:", result.get("msg", "Pesan tidak tersedia"))
    else:
        print("Request gagal dengan status code:", response.status_code)
        
# Melakukan login dengan email, password, dan token captcha
def claimTaskEmail(response_captcha, scraper, token):
    payload = {"mission_id":"5"}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'authorization': f"Bearer {token}",
        'Content-Type': 'application/json',
        'authority': 'api.nodepay.org',
        'accept-language': 'id-ID,id;q=0.9',
        'origin': 'https://app.nodepay.ai',
        'referer': 'https://app.nodepay.ai/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site'
    }
    post_url = "https://api.nodepay.org/api/mission/complete-mission"
    response = scraper.post(post_url, json=payload, headers=headers, allow_redirects=True)

    if response.status_code == 200:
        result = response.json()
        
        # Mengecek apakah respons success
        if result.get("success") == True:
            # Jika sukses, ambil token dan informasi pengguna
            print("[#] \033[0;32mBerhasil Claim Verif Email Task!!\033[0m")

    
        else:
            # Jika gagal, tampilkan pesan kesalahan
            print("[x] Claim Verif Email Task:", result.get("msg", "Pesan tidak tersedia"))
    else:
        print("Request gagal dengan status code:", response.status_code)
        
# Melakukan login dengan email, password, dan token captcha
def startQNA(response_captcha, scraper, token):
    payload = {"is_new_in_web3":"false","location":"Indonesia","gender":"male","occupation":"Software Engineer","industry":"Information Technology (IT)","age_range":"BETWEEN_25_34"}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'authorization': f"Bearer {token}",
        'Content-Type': 'application/json',
        'authority': 'api.nodepay.org',
        'accept-language': 'id-ID,id;q=0.9',
        'origin': 'https://app.nodepay.ai',
        'referer': 'https://app.nodepay.ai/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site'
    }
    post_url = "https://api.nodepay.org/api/mission/survey/qna-challenge"
    response = scraper.post(post_url, json=payload, headers=headers, allow_redirects=True)

    if response.status_code == 200:
        result = response.json()
        
        # Mengecek apakah respons success
        if result.get("success") == True:
            # Jika sukses, ambil token dan informasi pengguna
            print("[#] \033[0;32mBerhasil Submit Task QNA!!\033[0m Claim Now...")
            claimTaskQuestion(response_captcha, scraper, token)

    
        else:
            # Jika gagal, tampilkan pesan kesalahan
            print("[x] Submit QNA Task:", result.get("msg", "Pesan tidak tersedia"))
    else:
        print("Request gagal dengan status code:", response.status_code)
        
# Melakukan login dengan email, password, dan token captcha
def verifEmail(response_captcha, scraper, token):
    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'authorization': f"Bearer {token}",
        'Content-Type': 'application/json',
        'authority': 'api.nodepay.org',
        'accept-language': 'id-ID,id;q=0.9',
        'origin': 'https://app.nodepay.ai',
        'referer': 'https://app.nodepay.ai/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site'
    }
    post_url = "https://api.nodepay.org/api/auth/send-verify-email"
    response = scraper.post(post_url, json=payload, headers=headers, allow_redirects=True)

    if response.status_code == 200:
        result = response.json()
        
        # Mengecek apakah respons success
        if result.get("success") == True:
            # Jika sukses, ambil token dan informasi pengguna
            print("[#] \033[0;32mBerhasil Mengirim Verifikasi Email!!\033[0m")

    
        else:
            # Jika gagal, tampilkan pesan kesalahan
            print("[x] Mengirim Verifikasi Email Akun Gagal:", result.get("msg", "Pesan tidak tersedia"))
    else:
        print("Request gagal dengan status code:", response.status_code)
        
# Melakukan login dengan email, password, dan token captcha
def aktivasiAkun(response_captcha, scraper, token):
    payload = {}
    headers = {
        'authorization': f"Bearer {token}",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        'Content-Type': "application/json",
        'accept-language': "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        'origin': "chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm",
        'priority': "u=1, i",
        'sec-ch-ua': "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
        'sec-ch-ua-mobile': "?0",
        'sec-ch-ua-platform': "\"Windows\"",
        'sec-fetch-dest': "empty",
        'sec-fetch-mode': "cors",
        'sec-fetch-site': "none",
    }
    post_url = "https://api.nodepay.org/api/auth/active-account"
    response = scraper.post(post_url, json=payload, headers=headers, allow_redirects=True)

    if response.status_code == 200:
        result = response.json()
        
        # Mengecek apakah respons success
        if result.get("success") == True:
            # Jika sukses, ambil token dan informasi pengguna
            print("[#] \033[0;32mBerhasil Aktivasi Ekstensi!!\033[0m")

    
        else:
            # Jika gagal, tampilkan pesan kesalahan
            print("[x] Aktivasi Ekstensi Akun Gagal:", result.get("msg", "Pesan tidak tersedia"))
    else:
        print("Request gagal dengan status code:", response.status_code)

# Main eksekusi


RegisterNew = input("[?] Register Sekalian Gak ?? (y / n) : ").lower()
bikinBanyak = input("[?] Banyak Register Gak ?? (y / n) : ").lower()
reff = input("[?] Masukkan Reff Code: ")

while(True):
    # Memuat dan memilih proxy secara acak
    all_proxies = load_proxies('proxies.txt')
    proxy = get_random_proxy(all_proxies)
    scraper = create_scraper_with_proxy(proxy)
    generate_users = get_random_name(separator="", style="lowercase")
    
    
    # Mendapatkan captcha_id untuk bypass captcha
    captcha_id = get_captcha_id(scraper)
    if captcha_id:
        print(f"[#] Melakukan Bypass Captcha...")
        
        # Mendapatkan response captcha
        captcha_response = check_captcha_response(captcha_id, scraper)
        
        # Jika pengguna memilih untuk register
        if RegisterNew == 'y':
            if bikinBanyak == 'y':
                email = f"{generate_users}@gmail.com"
            else:
                # Meminta input email
                email = input("[?] Masukkan email: ")
            print(f"[#] Menggunakan Email: {email} | Reff: {reff}")
            register(captcha_response, scraper, generate_users, reff)
        else:
            # Meminta input email
            email = input("[?] Masukkan email: ")
            print(f"[#] Menggunakan Email: {email} | Reff: {reff}")
            
        print(f"[#] Mengambil Token Bearer...")
        login(captcha_response, scraper, RegisterNew)
    else:
        # Menangani kasus jika gagal mendapatkan captcha_id
        print("\033[0;31mGAGAL GET ID!! GOOGLE KEY SALAH / APIKEY SALAH!!\033[0m\n")


from web3 import Web3
from eth_utils import to_hex
from eth_account import Account
from fake_useragent import FakeUserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading, requests, json, random, time, sys, os
from datetime import datetime

RPC_URL = "https://atlantic.dplabs-internal.com/"
EXPLORER = "https://atlantic.pharosscan.xyz/tx/"

# 2captcha.com
CAPTCHA_API = "https://api.2captcha.com" 

# Using capmonster.cloud? => "https://api.capmonster.cloud"

PAGE_URL = "https://faroswap.xyz/"
SITE_KEY = "6LcFofArAAAAAMUs2mWr4nxx0OMk6VygxXYeYKuO"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

session = requests.Session()

Account.enable_unaudited_hdwallet_features()

print_lock = threading.Lock()

# Color codes for better terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def safe_print(*args, **kwargs):
    with print_lock:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{Colors.CYAN}{timestamp}{Colors.ENDC}]", *args, **kwargs)

def load_api_key(file_path="2captcha.txt"):
    """Load API key from file"""
    if not os.path.exists(file_path):
        safe_print(f"{Colors.RED}❌ File {file_path} not found!{Colors.ENDC}")
        return None
    
    with open(file_path, "r") as f:
        api_key = f.read().strip()
        if api_key:
            safe_print(f"{Colors.GREEN}✅ API Key loaded from {file_path}{Colors.ENDC}")
            return api_key
        else:
            safe_print(f"{Colors.RED}❌ API Key is empty in {file_path}{Colors.ENDC}")
            return None

def load_recipient_address(file_path="address.txt"):
    """Load recipient address from file"""
    if not os.path.exists(file_path):
        safe_print(f"{Colors.RED}❌ File {file_path} not found!{Colors.ENDC}")
        return None
    
    with open(file_path, "r") as f:
        address = f.read().strip()
        if address and address.startswith("0x"):
            safe_print(f"{Colors.GREEN}✅ Recipient address loaded: {address}{Colors.ENDC}")
            return address
        else:
            safe_print(f"{Colors.RED}❌ Invalid address in {file_path}{Colors.ENDC}")
            return None

def load_proxies(file_path="proxy.txt"):
    proxies = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                proxy = line.strip()
                if proxy:
                    proxies.append(proxy)
        if proxies:
            safe_print(f"{Colors.GREEN}✅ Loaded {len(proxies)} proxies{Colors.ENDC}")
    else:
        safe_print(f"{Colors.YELLOW}⚠️  No proxy.txt found, running without proxies{Colors.ENDC}")
    return proxies

def get_random_wallet(wallets):
    if not wallets:
        safe_print(f"{Colors.RED}❌ No wallets available!{Colors.ENDC}")
        return None
    return random.choice(wallets)

def get_random_proxy(proxies):
    if not proxies:
        return None
    proxy = random.choice(proxies)
    return {"http": proxy, "https": proxy}

def generate_evm_wallet():
    private_key = os.urandom(32).hex()
    acct = Account.from_key(bytes.fromhex(private_key))
    return private_key, acct.address

def solve_recaptcha(page_url, site_key, api_key, retries=5):
    for attempt in range(retries):
        try:
            if api_key is None:
                return {"success": False, "message": "API Key not found"}

            url = f"{CAPTCHA_API}/createTask"
            data = json.dumps({
                "clientKey": api_key,
                "task": {
                    "type": "RecaptchaV2TaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": site_key
                }
            })
            response = session.post(url=url, data=data)
            response.raise_for_status()
            result_text = response.text
            result_json = json.loads(result_text)

            if result_json.get("errorId") != 0:
                err_text = result_json.get("errorDescription", "Unknown Error")
                return {"success": False, "message": str(err_text)}

            request_id = result_json.get("taskId")

            for _ in range(30):
                res_url = f"{CAPTCHA_API}/getTaskResult"
                res_data = json.dumps({
                    "clientKey": api_key,
                    "taskId": request_id
                })

                res_response = session.post(url=res_url, data=res_data)
                res_response.raise_for_status()
                res_result_text = res_response.text
                res_result_json = json.loads(res_result_text)

                if res_result_json.get("status") == "ready":
                    recaptcha_token = res_result_json["solution"]["gRecaptchaResponse"]
                    return {"success": True, "message": recaptcha_token}
                
                elif res_result_json.get("status") == "processing":
                    time.sleep(5)
                    continue
                else:
                    break

        except (Exception, requests.RequestException) as e:
            if attempt < retries - 1:
                time.sleep(5)
                continue
            return {"success": False, "message": f"Network error → {str(e)[:50]}..."}

def request_faucet(address, recaptcha_token, proxies): 
    url = "https://api.dodoex.io/gas-faucet-server/faucet/claim"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json",
        "Origin": "https://faroswap.xyz",
        "Referer": "https://faroswap.xyz/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": FakeUserAgent().random
    }

    payload = {
        "chainId": 688689,
        "address": address,
        "recaptchaToken": recaptcha_token
    }

    proxy = get_random_proxy(proxies)

    try:
        response = session.post(url, json=payload, headers=headers, proxies=proxy, timeout=120)
        resp_json = response.json()

        if resp_json.get("code") == 0:
            return {"success": True, "message": resp_json.get("data").get("txHash")}
        else:
            return {"success": False, "message": resp_json.get("msg", "Unknown Error")}
    except requests.RequestException as e:
        return {"success": False, "message": f"Network error → {str(e)[:50]}..."}

def get_balance(address):
    balance_wei = w3.eth.get_balance(address)
    return w3.from_wei(balance_wei, "ether")

def send_all_balance(private_key, from_address, recipient, job_id=0, total_jobs=0, max_retries=5):
    job_prefix = f"{Colors.BLUE}[Job {job_id:2d}/{total_jobs}]{Colors.ENDC}" if job_id > 0 else ""
    
    for attempt in range(1, max_retries + 1):
        try:
            balance = w3.eth.get_balance(from_address)
            if balance == 0:
                return {"success": False, "message": "Balance 0"}

            gas_price = w3.eth.gas_price
            gas_limit = 21000
            fee = gas_price * gas_limit
            tx_value = balance - fee

            if tx_value <= 0:
                return {"success": False, "message": "Insufficient funds for gas"}

            nonce = w3.eth.get_transaction_count(from_address, 'pending')
            
            tx = {
                "nonce": nonce,
                "to": w3.to_checksum_address(recipient),
                "value": tx_value,
                "gas": gas_limit,
                "gasPrice": gas_price,
                "chainId": w3.eth.chain_id,
            }

            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            
            # --- INI ADALAH PERBAIKANNYA ---
            raw_tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            # --------------------------------
            
            tx_hash = to_hex(raw_tx_hash)

            time.sleep(2)
            
            try:
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
                if receipt and receipt['status'] == 1:
                    return {"success": True, "tx_hash": tx_hash, "receipt": receipt}
                else:
                    safe_print(f"{job_prefix} {Colors.YELLOW}⚠️  Attempt {attempt}: Transaction failed (status=0){Colors.ENDC}")
                    
            except Exception as receipt_error:
                safe_print(f"{job_prefix} {Colors.YELLOW}⚠️  Attempt {attempt}: Receipt error → {str(receipt_error)[:50]}...{Colors.ENDC}")
                return {"success": True, "tx_hash": tx_hash, "warning": "Could not verify transaction"}

        except Exception as e:
            error_msg = str(e).lower()
            
            if "insufficient funds" in error_msg:
                return {"success": False, "message": "Insufficient funds for gas"}
            elif "nonce too low" in error_msg:
                safe_print(f"{job_prefix} {Colors.YELLOW}⚠️  Attempt {attempt}: Nonce too low, retrying...{Colors.ENDC}")
                time.sleep(2)
                continue
            elif "replacement transaction underpriced" in error_msg:
                safe_print(f"{job_prefix} {Colors.YELLOW}⚠️  Attempt {attempt}: Transaction underpriced, retrying with higher gas...{Colors.ENDC}")
                time.sleep(2)
                continue
            elif "transaction not found" in error_msg:
                safe_print(f"{job_prefix} {Colors.YELLOW}⚠️  Attempt {attempt}: Transaction not found, retrying...{Colors.ENDC}")
                time.sleep(3)
                continue
            elif "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
                safe_print(f"{job_prefix} {Colors.YELLOW}⚠️  Attempt {attempt}: Network issue → {str(e)[:50]}...{Colors.ENDC}")
                time.sleep(random.randint(3, 6))
                continue
            else:
                safe_print(f"{job_prefix} {Colors.YELLOW}⚠️  Attempt {attempt}: Unexpected error → {str(e)[:50]}...{Colors.ENDC}")
                
        if attempt < max_retries:
            delay = random.randint(2, 5)
            safe_print(f"{job_prefix} {Colors.CYAN}⏳ Retrying transfer in {delay} seconds...{Colors.ENDC}")
            time.sleep(delay)

    return {"success": False, "message": f"Transfer failed after {max_retries} attempts"}


def run_job(index, total_jobs, proxies, api_key, recipient):
    job_prefix = f"{Colors.BLUE}[Job {index:2d}/{total_jobs}]{Colors.ENDC}"
    
    safe_print(f"\n{job_prefix} {Colors.BOLD}🚀 Starting job...{Colors.ENDC}")
    priv, addr = generate_evm_wallet()
    safe_print(f"{job_prefix} 🔑 From: {Colors.YELLOW}{addr}{Colors.ENDC}")
    safe_print(f"{job_prefix} 🎯 To: {Colors.GREEN}{recipient}{Colors.ENDC}")

    recaptcha = solve_recaptcha(PAGE_URL, SITE_KEY, api_key)
    if recaptcha.get("success"):
        recaptcha_token = recaptcha.get("message")
        safe_print(f"{job_prefix} {Colors.GREEN}✅ Recaptcha Solved{Colors.ENDC}")

        safe_print(f"{job_prefix} 💧 Requesting faucet...")
        result = request_faucet(addr, recaptcha_token, proxies)

        if result.get("success"):
            tx_hash = result.get('message')
            safe_print(f"{job_prefix} {Colors.GREEN}✅ Faucet success!{Colors.ENDC}")
            safe_print(f"{job_prefix} 🔗 {EXPLORER}{tx_hash}")

            wait_time = 5
            safe_print(f"{job_prefix} {Colors.CYAN}⏳ Waiting {wait_time}s to check balance...{Colors.ENDC}")
            time.sleep(wait_time)

            bal = 0
            for attempt in range(1, 6):
                bal = get_balance(addr)
                if bal > 0:
                    break
                safe_print(f"{job_prefix} {Colors.YELLOW}⚠️  Balance still 0 (attempt {attempt}/5), retrying in {wait_time}s...{Colors.ENDC}")
                time.sleep(wait_time)

            safe_print(f"{job_prefix} 💰 Balance: {Colors.GREEN}{bal:.6f} PHRS{Colors.ENDC}")

            if bal > 0:
                safe_print(f"{job_prefix} 📤 Transferring to recipient...")
                transfer_result = send_all_balance(priv, addr, recipient, index, total_jobs)
                
                if transfer_result["success"]:
                    safe_print(f"{job_prefix} {Colors.GREEN}{Colors.BOLD}🎉 Transfer Successful!{Colors.ENDC}")
                    safe_print(f"{job_prefix} 🔗 {EXPLORER}{transfer_result['tx_hash']}")
                    return True
                else:
                    safe_print(f"{job_prefix} {Colors.RED}❌ Transfer failed: {transfer_result['message']}{Colors.ENDC}")
            else:
                safe_print(f"{job_prefix} {Colors.RED}❌ Balance still 0 after retries, skipping transfer{Colors.ENDC}")
        else:
            safe_print(f"{job_prefix} {Colors.RED}❌ Faucet request failed: {result.get('message')}{Colors.ENDC}")
    else:
        safe_print(f"{job_prefix} {Colors.RED}❌ Recaptcha failed: {recaptcha.get('message')}{Colors.ENDC}")

    safe_print(f"{job_prefix} {Colors.RED}❌ Job completed with failure{Colors.ENDC}")
    return False

if __name__ == "__main__":
    try:
        print("\n" + "="*70)
        print(f"{Colors.BOLD}{Colors.CYAN}           🚰 PHAROS ATLANTIC FAUCET AUTO BOT - VONSSY 🚰{Colors.ENDC}")
        print("="*70 + "\n")
        
        # Check RPC connection
        if not w3.is_connected():
            safe_print(f"{Colors.RED}❌ Failed to connect to RPC. Check network/RPC_URL.{Colors.ENDC}")
            exit(1)
        safe_print(f"{Colors.GREEN}✅ Connected to RPC{Colors.ENDC}")

        # Load API Key
        api_key = load_api_key("2captcha.txt")
        if not api_key:
            safe_print(f"{Colors.RED}❌ Please create 2captcha.txt file with your API key{Colors.ENDC}")
            exit(1)

        # Load Recipient Address
        recipient = load_recipient_address("address.txt")
        if not recipient:
            safe_print(f"{Colors.RED}❌ Please create address.txt file with your recipient address{Colors.ENDC}")
            exit(1)

        # Load Proxies
        proxies = load_proxies("proxy.txt")

        # Get user input
        print()
        total_runs = int(input(f"{Colors.CYAN}📢 Enter number of loops: {Colors.ENDC}"))
        max_threads = int(input(f"{Colors.CYAN}🧵 Enter number of threads: {Colors.ENDC}"))

        print(f"\n{Colors.BOLD}🚀 Starting {total_runs} jobs with {max_threads} threads...{Colors.ENDC}")
        print("="*70 + "\n")

        total_success = 0
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(run_job, i+1, total_runs, proxies, api_key, recipient) for i in range(total_runs)]
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                success = future.result()
                if success:
                    total_success += 1
                
                progress = (completed / total_runs) * 100
                safe_print(f"\n{Colors.BOLD}📊 Progress: {completed}/{total_runs} ({progress:.1f}%) | Success: {Colors.GREEN}{total_success}{Colors.ENDC}")

        end_time = time.time()
        duration = end_time - start_time

        rate = (total_success / total_runs * 100) if total_runs > 0 else 0

        print("\n" + "="*70)
        print(f"{Colors.BOLD}{Colors.CYAN}                    📊 FINAL SUMMARY{Colors.ENDC}")
        print("="*70)
        print(f"{Colors.GREEN}✅ Total Success    : {total_success}{Colors.ENDC}")
        print(f"{Colors.BLUE}📢 Total Jobs       : {total_runs}{Colors.ENDC}")
        print(f"{Colors.RED}❌ Failed Jobs      : {total_runs - total_success}{Colors.ENDC}")
        print(f"{Colors.CYAN}📊 Success Rate     : {rate:.2f}%{Colors.ENDC}")
        print(f"{Colors.YELLOW}⏱️  Duration        : {duration:.2f} seconds{Colors.ENDC}")
        print(f"{Colors.YELLOW}⚡ Average per job  : {duration/total_runs:.2f} seconds{Colors.ENDC}")
        print("="*70 + "\n")

    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}🛑 Keyboard Interrupt detected. Program stopped.{Colors.ENDC}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {str(e)}{Colors.ENDC}\n")
        sys.exit(1)

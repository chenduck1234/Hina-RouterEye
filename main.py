import os
import platform
import socket
import subprocess
import re
import time
import speedtest
import requests

# 1. 區網裝置 IP 偵測
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_network_segment(ip):
    parts = ip.split('.')
    return '.'.join(parts[:3]) + '.'

def ping_sweep(network_segment):
    print("正在掃描區網裝置，請稍候...")
    for i in range(1, 255):
        ip = f"{network_segment}{i}"
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        subprocess.Popen(['ping', param, '1', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_arp_table():
    arp_result = subprocess.check_output('arp -a', shell=True).decode()
    devices = re.findall(r'(\d+\.\d+\.\d+\.\d+)\s+([\w-]+)', arp_result)
    return devices

def scan_lan_devices():
    local_ip = get_local_ip()
    network_segment = get_network_segment(local_ip)
    ping_sweep(network_segment)
    time.sleep(8)
    devices = get_arp_table()
    ip_list = []
    for ip, mac in devices:
        if ip.startswith(network_segment):
            ip_list.append(ip)
    return ip_list

# 2&3. Port/社群服務封鎖偵測
def check_port(host, port, timeout=2, repeat=5):
    latencies = []
    for _ in range(repeat):
        start = time.time()
        try:
            with socket.create_connection((host, port), timeout=timeout):
                latency = (time.time() - start) * 1000
                latencies.append(latency)
        except Exception:
            latencies.append(None)
    valid_latencies = [l for l in latencies if l is not None]
    if valid_latencies:
        avg_latency = sum(valid_latencies) / len(valid_latencies)
        return "open", avg_latency
    else:
        return "blocked", None

def port_and_social_check():
    targets = [
        ("Google DNS", "8.8.8.8", 53),
        ("Cloudflare DNS", "1.1.1.1", 53),
        ("OpenDNS", "208.67.222.222", 53),
        ("Comodo Secure DNS", "8.26.56.26", 53),
        ("CleanBrowsing DNS", "185.228.168.9", 53),
        ("Verisign DNS", "64.6.64.6", 53),
        ("Google HTTP", "google.com", 80),
        ("Google HTTPS", "google.com", 443),
        ("GitHub SSH", "github.com", 22),
        ("FTP dlptest", "ftp.dlptest.com", 21),
        ("FTP Rebex", "test.rebex.net", 21),
        ("FTP GNU", "ftp.gnu.org", 21),
        ("Facebook", "facebook.com", 443),
        ("Instagram", "instagram.com", 443),
        ("YouTube", "youtube.com", 443),
        ("Twitter", "twitter.com", 443),
        ("LINE", "line.me", 443),
        ("Telegram", "telegram.org", 443)
    ]
    result = {}
    for name, host, port in targets:
        status, avg_latency = check_port(host, port)
        result[name] = {
            "status": status,
            "latency": round(avg_latency, 2) if avg_latency else None
        }
    return result

# 4. 網速測量
def test_speed():
    try:
        s = speedtest.Speedtest()
        print("正在取得最佳伺服器...")
        s.get_best_server()
        print("開始測量下載速度...")
        download_speed = s.download() / 1_000_000
        print("開始測量上傳速度...")
        upload_speed = s.upload() / 1_000_000
        ping = s.results.ping
        return {
            "download": round(download_speed, 2),
            "upload": round(upload_speed, 2),
            "latency": round(ping, 2)
        }
    except Exception as e:
        print(f"Speedtest 發生錯誤: {e}")
        return {
            "download": None,
            "upload": None,
            "latency": None,
            "error": str(e)
        }

def test_speed_cli():
    try:
        result = subprocess.check_output(["speedtest", "--format", "json"], text=True)
        import json
        data = json.loads(result)
        return {
            "download": round(data["download"]["bandwidth"] * 8 / 1_000_000, 2),  # Mbps
            "upload": round(data["upload"]["bandwidth"] * 8 / 1_000_000, 2),      # Mbps
            "latency": round(data["ping"]["latency"], 2)
        }
    except Exception as e:
        print(f"Speedtest CLI 發生錯誤: {e}")
        return {
            "download": None,
            "upload": None,
            "latency": None,
            "error": str(e)
        }

# 5. Traceroute
def traceroute(target):
    print(f"\n對 {target} 執行路由追蹤：")
    system = platform.system().lower()
    if system == "windows":
        cmd = ["tracert", target]
    else:
        cmd = ["traceroute", target]
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        return result
    except Exception as e:
        return f"執行 traceroute 時發生錯誤: {e}"

def parse_traceroute(raw):
    hops = []
    for line in raw.splitlines():
        # 只抓 hop 行
        m = re.match(r'\s*(\d+)\s+([\d\.]+|\*)', line)
        if m:
            hop_num = int(m.group(1))
            ip = m.group(2)
            hops.append(ip)
    return hops

# 6. 回報狀態
def report_status(data, url="https://yuhina0515.ddns.net/api/report"):
    try:
        response = requests.post(url, json=data, timeout=10, verify=False)
        if response.status_code == 200:
            print("狀態已成功回報到自架 WEB。")
        else:
            print(f"回報失敗，狀態碼: {response.status_code}")
    except Exception as e:
        print(f"回報時發生錯誤: {e}")

if __name__ == "__main__":
    # 1. 區網裝置 IP 偵測
    ip_list = scan_lan_devices()
    print("區網裝置 IP：", ip_list)

    # 2&3. Port/社群服務封鎖偵測
    port_status = port_and_social_check()
    print("Port/社群服務檢查：", port_status)

    # 4. 網速測量
    speed_result = test_speed()
    print("網速測量：", speed_result)

    # 5. Traceroute
    traceroute_result_1 = traceroute("8.8.8.8")
    traceroute_result_2 = traceroute("google.com")
    traceroute_hops_1 = parse_traceroute(traceroute_result_1)
    traceroute_hops_2 = parse_traceroute(traceroute_result_2)

    # 彙整所有結果
    status_data = {
        "ip_scan": ip_list,
        "port_check": port_status,
        "speed": speed_result,
        "traceroute_8.8.8.8": traceroute_hops_1,
        "traceroute_google.com": traceroute_hops_2
    }

    # 6. 回報狀態
    report_status(status_data)
import os
import json
import requests

# 🔹 从 GitHub Secrets 里读取配置
SEARCH_URLS = os.getenv("SEARCH_URLS", "").splitlines()
SERVER_SENDKEY = os.getenv("SERVER_SENDKEY", "")

# ✅ 模拟 Mercari iOS App 请求头（完整版）
HEADERS = {
    "User-Agent": "Mercari_r/14352 CFNetwork/1399 Darwin/22.1.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Platform": "iOS",
    "X-Client-Info": "app/1.0.0 (iOS 16.0; iPhone14,3)"  # 可以随便填，不要空
}

SEEN_FILE = "seen.json"
seen_items = {}

# 读取历史已推送商品
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        try:
            seen_items = json.load(f)
        except:
            seen_items = {}

def send_push(title, link, price):
    if not SERVER_SENDKEY:
        print("⚠️ 没有配置 Server酱，无法推送")
        return
    url = f"https://sctapi.ftqq.com/{SERVER_SENDKEY}.send"
    data = {
        "title": title,
        "desp": f"{title}\n价格: {price}\n[点我查看]({link})"
    }
    try:
        r = requests.post(url, data=data)
        print("推送结果:", r.text)
    except Exception as e:
        print("推送失败:", e)

def check_url(url):
    print(f"请求地址: {url}")
    try:
        resp = requests.get(url, headers=HEADERS)
        print("返回状态:", resp.status_code)

        if resp.status_code != 200:
            print("请求失败:", resp.text[:300])
            return

        # 尝试解析 JSON
        try:
            data = resp.json()
        except Exception:
            print("❌ 返回不是 JSON，前500字符如下：")
            print(resp.text[:500])
            return

        items = data.get("items", [])
        if not items:
            print("❌ 没有新商品")
            return

        for item in items[:5]:  # 只看最新 5 个
            item_id = item.get("id")
            title = item.get("name")
            price = item.get("price")
            link = f"https://jp.mercari.com/item/{item_id}"

            if item_id not in seen_items:
                print("🆕 新商品:", title, price, link)
                send_push(title, link, price)
                seen_items[item_id] = True
    except Exception as e:
        print("Error:", e)

def main():
    for url in SEARCH_URLS:
        url = url.strip()
        if not url:
            continue
        check_url(url)

    # 保存已推送商品
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen_items, f, ensure_ascii=False)

if __name__ == "__main__":
    main()

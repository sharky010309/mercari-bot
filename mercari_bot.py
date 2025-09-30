import os
import json
import requests
import time

# 从 Render 环境变量读取配置
SEARCH_URLS = os.getenv("SEARCH_URLS", "").splitlines()
SERVER_SENDKEY = os.getenv("SERVER_SENDKEY", "")

# 模拟 Mercari iOS App 请求头（完整版）
HEADERS = {
    "User-Agent": "Mercari_r/14352 CFNetwork/1399 Darwin/22.1.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Platform": "iOS",
    "X-Client-Info": "app/1.0.0 (iOS 16.0; iPhone14,3)"  # 随便填，不要空
}

# 保存已推送的商品 ID，避免重复
seen_items = {}

def send_push(title, link, price):
    """推送到 Server酱"""
    if not SERVER_SENDKEY:
        print("⚠️ 没有配置 Server酱，无法推送")
        return
    url = f"https://sctapi.ftqq.com/{SERVER_SENDKEY}.send"
    data = {
        "title": f"Mercari 新品：{title}",
        "desp": f"{title}\n价格: {price}\n[点我查看]({link})"
    }
    try:
        r = requests.post(url, data=data)
        print("推送结果:", r.text)
    except Exception as e:
        print("推送失败:", e)

def check_url(url):
    """抓取一个搜索链接"""
    print(f"👉 请求地址: {url}")
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
            print("❌ 没有新商品（items为空）")
            return

        # 打印前3个商品，作为测试
        for item in items[:3]:
            item_id = item.get("id")
            title = item.get("name")
            price = item.get("price")
            link = f"https://jp.mercari.com/item/{item_id}"
            print("🆕 抓到商品:", title, price, link)

            # 如果是新商品就推送
            if item_id not in seen_items:
                send_push(title, link, price)
                seen_items[item_id] = True

    except Exception as e:
        print("Error:", e)

def main():
    """主循环，每隔 60s 跑一次"""
    while True:
        for url in SEARCH_URLS:
            url = url.strip()
            if not url:
                continue
            check_url(url)
        print("⏳ 本轮结束，等待 60 秒...\n")
        time.sleep(60)

if __name__ == "__main__":
    main()

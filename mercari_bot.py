import requests
import os

# 从 GitHub Secrets 读取配置
URLS = os.getenv("SEARCH_URLS", "").splitlines()
SERVER_KEY = os.getenv("SERVER_SENDKEY")

# 开关：True = 强制推送测试消息，不跑逻辑
TEST_MODE = False

seen = set()

def send_wechat(text):
    url = f"https://sctapi.ftqq.com/{SERVER_KEY}.send"
    data = {"title": "Mercari 新上架提醒", "desp": text}
    try:
        r = requests.post(url, data=data)
        print("推送结果:", r.status_code, r.text[:200])
    except Exception as e:
        print("推送失败:", e)

def check_url(url):
    try:
        res = requests.get(url, headers={
            "User-Agent": "Mercari_r/14352 CFNetwork/1399 Darwin/22.1.0",
            "Accept": "application/json"
        })
        if res.status_code != 200:
            print("Fetch failed:", res.status_code)
            return []

        data = res.json()
        items = data.get("items") or data.get("data") or []
        new_items = []
        for it in items:
            item_id = it.get("id") or it.get("itemId") or it.get("item_id")
            if not item_id or item_id in seen:
                continue
            seen.add(item_id)
            title = it.get("name") or it.get("title") or "无标题"
            price = it.get("price") or "?"
            link = f"https://jp.mercari.com/item/{item_id}"
            new_items.append(f"{title} - ¥{price}\n{link}")
        return new_items
    except Exception as e:
        print("Error:", e)
        return []

def main():
    all_new = []
    for url in URLS:
        if not url.strip():
            continue
        new_items = check_url(url.strip())
        if new_items:
            all_new.extend(new_items)

    if all_new:
        send_wechat("\n\n".join(all_new))
        print("推送成功:", len(all_new))
    else:
        print("没有新商品")

if __name__ == "__main__":
    if TEST_MODE:
        send_wechat("这是一个 Mercari 推送链路测试消息 🐺💌")
    else:
        main()

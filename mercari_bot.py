import requests
import os
import re
import json

URLS = os.getenv("SEARCH_URLS", "").splitlines()
SERVER_KEY = os.getenv("SERVER_SENDKEY")

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

def parse_webpage(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/122.0.0.0 Safari/537.36"
        }
        res = requests.get(url, headers=headers)
        print("请求地址:", url)
        print("返回状态:", res.status_code)

        if res.status_code != 200:
            print("Fetch failed:", res.status_code)
            return []

        html = res.text
        json_text = None

        # 方法1: <script id="__NEXT_DATA__">
        match1 = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        if match1:
            json_text = match1.group(1)

        # 方法2: window.__NEXT_DATA__ = {...};
        if not json_text:
            match2 = re.search(r'window\.__NEXT_DATA__\s*=\s*(\{.*?\});', html, re.S)
            if match2:
                json_text = match2.group(1)

        if not json_text:
            print("❌ 未找到 JSON，调试输出前500字符：")
            print(html[:500])
            return []

        data = json.loads(json_text)
        items = data.get("props", {}).get("pageProps", {}).get("initialSearchResult", {}).get("items", [])

        results = []
        for it in items:
            item_id = it.get("id")
            if not item_id or item_id in seen:
                continue
            seen.add(item_id)
            title = it.get("name") or "无标题"
            price = it.get("price") or "?"
            link = f"https://jp.mercari.com/item/{item_id}"
            results.append(f"{title} - ¥{price}\n{link}")
        return results
    except Exception as e:
        print("解析失败:", e)
        return []

def main():
    all_new = []
    for url in URLS:
        if not url.strip():
            continue
        new_items = parse_webpage(url.strip())
        if new_items:
            all_new.extend(new_items)

    if all_new:
        send_wechat("\n\n".join(all_new))
        print("推送成功:", len(all_new))
    else:
        print("没有新商品")

if __name__ == "__main__":
    if TEST_MODE:
        send_wechat("这是 Mercari 网页版推送测试 🐺💌")
    else:
        main()

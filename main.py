import requests
import os
import sys
import time

def send_notification(title, content):
    """
    简易推送函数
    """
    token = os.getenv("PUSHPLUS_TOKEN")
    if not token: return
    try:
        requests.post("http://www.pushplus.plus/send", json={
            "token": token, "title": title, "content": content, "template": "html"
        })
    except: pass

def luogu_punch():
    # ---------------------------------------------------------
    # 1. 准备工作
    # ---------------------------------------------------------
    cookie_str = os.getenv("LUOGU_COOKIE")
    if not cookie_str:
        print("❌ 错误：未找到 LUOGU_COOKIE")
        return

    timestamp = int(time.time() * 1000)
    url = f"https://www.luogu.com.cn/index/ajax_punch?_={timestamp}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Cookie": cookie_str,
        "Referer": "https://www.luogu.com.cn/",
        "x-requested-with": "XMLHttpRequest"
    }

    try:
        print("🚀 正在连接洛谷服务器...")
        response = requests.get(url, headers=headers, timeout=15)
        
        # 预防返回非 JSON
        try:
            data = response.json()
        except:
            print(f"❌ 解析失败，服务器可能返回了网页: {response.text[:50]}...")
            return

        code = data.get('code')
        message = data.get('message', '无详细信息')

        # ---------------------------------------------------------
        # 2. 结果判定逻辑优化
        # ---------------------------------------------------------
        if response.status_code == 200:
            if code == 200:
                # 成功打卡
                html = data.get('more', {}).get('html', '未知')
                import re
                clean_text = re.sub(r'<[^>]+>', '', html).replace('&nbsp;', ' ').strip()
                msg = f"✅ 打卡成功！\n🎉 运势: {clean_text}"
                print(msg)
                
            elif code == 201:
                # 🛠️而是打印服务器原话
                # 洛谷的 message 通常是 "今天已经打过卡了"
                # 但也可能是 "频率过快" 等其他提示
                print(f"⚠️ 服务器提示 (Code 201): {message}")
                
                if "已经" in message:
                    print("✅ 确认状态: 今日确实已打卡")
                else:
                    print("❓ 异常状态: 虽然返回 201，但提示信息不符，建议人工检查！")
                    send_notification("洛谷打卡异常", f"Code 201 但内容异常: {message}")
            
            else:
                # 其他错误 (Code 401, 403 等)
                print(f"❌ 打卡失败: {message} (Code: {code})")
                if code == 401:
                    print("👉 原因: Cookie 可能过期了")
                    send_notification("洛谷 Cookie 失效", "请重新获取 Cookie")
        else:
            print(f"❌ HTTP 请求失败: {response.status_code}")

    except Exception as e:
        print(f"❌ 脚本运行出错: {e}")

if __name__ == "__main__":
    luogu_punch()

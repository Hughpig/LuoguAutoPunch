import requests
import os
import sys
from datetime import datetime

try:
    from dotenv import load_dotenv
    if load_dotenv(): # 只有真的找到了文件并加载成功，才打印
        print("✅ 本地调试模式：已加载 .env 文件")
    else:
        print("⚙️ 云端/无文件模式：将使用系统环境变量 (Secrets)")
except ImportError:
    pass

# -----------------------------------------------------------------------------
# 通知函数：使用 PushPlus 发送消息
# -----------------------------------------------------------------------------
def send_notification(title, content):
    """
    通过 PushPlus 发送微信通知
    """
    token = os.getenv("PUSHPLUS_TOKEN")
    
    # 如果没有设置 Token，就不发通知，只在日志里打印
    if not token:
        print("⚠️ 未检测到 PUSHPLUS_TOKEN，跳过消息推送")
        return

    url = "http://www.pushplus.plus/send"
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content += f"<br><br>------------<br>推送时间: {current_time}"
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "html" # 使用 HTML 格式，这样内容可以换行
    }
    
    try:
        resp = requests.post(url, json=data)
        if resp.json().get('code') == 200:
            print("✅ 消息推送成功")
        else:
            print(f"❌ 消息推送失败: {resp.text}")
    except Exception as e:
        print(f"❌ 消息推送异常: {e}")

# -----------------------------------------------------------------------------
# 主逻辑
# -----------------------------------------------------------------------------
def luogu_punch():
    cookie_str = os.getenv("LUOGU_COOKIE")
    
    if not cookie_str:
        print("❌ 错误：未检测到环境变量 LUOGU_COOKIE")
        # 既然没有 Cookie，肯定要通知一下，不然你都不知道脚本挂了
        send_notification("洛谷打卡脚本报错", "❌ 未找到 LUOGU_COOKIE，请检查 GitHub Secrets 设置。")
        sys.exit(1)

    url = "https://www.luogu.com.cn/index/ajax_punch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": cookie_str,
        "Referer": "https://www.luogu.com.cn/",
        "x-requested-with": "XMLHttpRequest"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # 预防服务器直接崩了，不是 JSON 格式
        try:
            data = response.json()
        except:
            msg = f"❌ 服务器返回了非 JSON 数据，可能是网站崩溃或 Cookie 失效。\n状态码: {response.status_code}"
            print(msg)
            send_notification("洛谷打卡失败 🚨", msg)
            return

        # ---------------------------------------------------------
        # 根据结果决定是否通知
        # ---------------------------------------------------------
        code = data.get('code')
        
        if code == 200:
            html_msg = data.get('more', {}).get('html', '未知')
            msg = f"✅ 打卡成功！\n🎉 运势: {html_msg}"
            print(msg)
            # 【可选】如果你想每天成功也发微信，把下面这行的 # 去掉：
            send_notification("洛谷打卡成功 ✅", msg)
            
        elif code == 201:
            msg = "✅ 今天已经打过卡了"
            print(msg)
            send_notification("今日已经打卡 ✅", msg)
            # 这种通常不需要通知，太频繁了烦人
            
        else:
            # 其他所有非 200/201 的情况，都视为失败，必须通知！
            error_msg = data.get('message', '未知错误')
            msg = f"⚠️ 打卡失败，服务器返回 Code: {code}\n❌ 错误信息: {error_msg}"
            print(msg)
            
            # 特别处理：如果是 401，明确提示 Cookie 过期
            if code == 401:
                msg += "\n❗ 你的 Cookie 可能已过期，请重新获取！"
            
            # 发送失败通知
            send_notification("洛谷打卡失败 🚨", msg)

    except Exception as e:
        msg = f"❌ 脚本运行发生异常: {e}"
        print(msg)
        send_notification("洛谷脚本崩溃 💥", msg)

if __name__ == "__main__":
    luogu_punch()



import os
import time
import requests
from playwright.sync_api import sync_playwright
from datetime import datetime

try:
    from dotenv import load_dotenv
    if load_dotenv(): # 只有真的找到了文件并加载成功，才打印
        print("✅ 本地调试模式：已加载 .env 文件")
    else:
        print("⚙️ 云端/无文件模式：将使用系统环境变量 (Secrets)")
except ImportError:
    pass

# ----------------------------------------------------------------
# 通用通知函数
# ----------------------------------------------------------------
def send_notification(title, content):
    token = os.getenv("PUSHPLUS_TOKEN")
    if not token: return
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content += f"<br><br>------------<br>推送时间: {current_time}"
    try:
        requests.post("http://www.pushplus.plus/send", json={
            "token": token, "title": title, "content": content, "template": "html"
        })
    except: pass

class JuejinBrowser:
    def __init__(self):
        self.cookie_str = os.getenv("JUEJIN_COOKIE", "")
        if not self.cookie_str:
            print("❌ 错误：未找到 JUEJIN_COOKIE")
            exit(1)

    def parse_cookie(self):
        """把 Cookie 字符串转换为 Playwright 需要的字典列表格式"""
        cookies = []
        # 简单的解析逻辑：按分号分割
        for item in self.cookie_str.split(';'):
            if '=' in item:
                name, value = item.strip().split('=', 1)
                cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.juejin.cn', # 关键：指定域名
                    'path': '/'
                })
        return cookies

    def run(self):
        print("🚀 启动 Playwright 浏览器模式...")
        
        with sync_playwright() as p:
            # 启动 Chrome
            is_github = os.getenv("GITHUB_ACTIONS") == "true"
            print(f"⚙️ 当前运行环境: {'GitHub Actions (云端)' if is_github else 'Local (本地)'}")
            
            browser = p.chromium.launch(headless=is_github, slow_mo=1000)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            
            # 1. 注入 Cookie
            cookies_list = self.parse_cookie()
            context.add_cookies(cookies_list)
            
            page = context.new_page()
            msg_log = []

            # -------------------------------------------------------
            # 🛡️ 步骤零：Cookie 有效性检测 (新增模块)
            # -------------------------------------------------------
            try:
                print("🌍 正在打开页面检测登录状态...")
                # 我们尝试访问签到页，如果没登录，通常会跳到登录页
                page.goto("https://juejin.cn/user/center/signin", timeout=30000)
                time.sleep(3) # 等待跳转或渲染

                # 检测逻辑：
                # 1. 检查 URL 是否包含 'login' (被重定向)
                # 2. 检查右上角是否有 "登录 | 注册" 按钮出现
                # 3. 检查是否有头像元素 (class="avatar")
                
                if "login" in page.url:
                    raise Exception("页面被自动重定向到登录页，Cookie 已失效")

                # 尝试寻找登录按钮
                login_btn = page.get_by_text("登录 | 注册")
                if login_btn.is_visible():
                    raise Exception("检测到页面显示'登录'按钮，Cookie 已失效")
                
                # 尝试寻找头像 (登录后的标志)
                avatar = page.locator(".avatar-wrapper, .avatar").first
                if not avatar.is_visible():
                    print("⚠️ 警告：未检测到头像，但也未检测到登录按钮，尝试继续...")
                else:
                    print("✅ 登录状态确认：检测到用户头像")

            except Exception as e:
                err_msg = f"❌ 严重错误：Cookie 已失效，脚本终止！\n原因: {e}"
                print(err_msg)
                # 发送报警通知
                send_notification("掘金脚本停止运行 🚨", err_msg)
                browser.close()
                return # 直接退出，不执行后面的签到和抽奖

            # -------------------------------------------------------
            # 任务一：去签到
            # -------------------------------------------------------
            try:
                print("🌍 正在打开签到页面...")
                # 此时页面已经在 signin 了，不需要再次 goto，但为了保险还是写上
                if page.url != "https://juejin.cn/user/center/signin":
                    page.goto("https://juejin.cn/user/center/signin", timeout=30000)
                
                signin_btn = page.locator("button.signin").first
                
                if signin_btn.is_visible():
                    btn_text = signin_btn.inner_text()
                    if "已签到" in btn_text:
                        print("✅ 检测到今日已签到")
                        msg_log.append("✅ 签到: 今日已完成")
                    else:
                        print("👆 点击签到按钮...")
                        signin_btn.click()
                        time.sleep(3)
                        print("✅ 点击完成")
                        msg_log.append("✅ 签到: 点击成功")
                else:
                    check_btn = page.get_by_text("立即签到")
                    if check_btn.count() > 0:
                        check_btn.first.click()
                        time.sleep(3)
                        msg_log.append("✅ 签到: 点击成功 (文字定位)")
                    elif page.get_by_text("已签到").count() > 0:
                        msg_log.append("✅ 签到: 今日已完成")
                    else:
                        # 截图保存 (云端可在 Artifacts 查看，本地直接看目录)
                        # page.screenshot(path="debug_signin_fail.png")
                        msg_log.append("❌ 签到: 未找到按钮 (可能页面结构变更)")
            
            except Exception as e:
                print(f"❌ 签到出错: {e}")
                msg_log.append(f"❌ 签到异常: {e}")

            # -------------------------------------------------------
            # 任务二：去抽奖
            # -------------------------------------------------------
            try:
                print("🌍 正在打开抽奖页面...")
                page.goto("https://juejin.cn/user/center/lottery", timeout=30000)
                time.sleep(3)
                
                # 1. 尝试寻找“免费抽奖”按钮 (精确匹配)
                free_draw_btn = page.get_by_text("免费抽奖", exact=True)
                
                if free_draw_btn.is_visible():
                    print("👆 发现免费次数，点击抽奖...")
                    free_draw_btn.click()
                    time.sleep(3)
                    msg_log.append("🎉 抽奖: 点击成功")
                
                else:
                    # 2. 检查是否变成了“单抽”或“200”
                    has_paid_btn = page.get_by_text("单抽").count() > 0
                    has_cost_text = page.get_by_text("200", exact=True).count() > 0
                    
                    if has_paid_btn or has_cost_text:
                        print("✅ 检测到今日已抽奖 (付费按钮已显示)")
                        msg_log.append("✅ 抽奖: 今日已完成")
                    else:
                        # 最后的保底：如果既没免费也没单抽，可能是页面改版，但也算“没报错”
                        print("⚠️ 未找到抽奖按钮 (可能已完成)")
                        msg_log.append("⚠️ 抽奖: 状态未知 (未找到按钮)")
                        
            except Exception as e:
                print(f"❌ 抽奖出错: {e}")
                if "Timeout" not in str(e):
                    msg_log.append(f"❌ 抽奖异常: {e}")
                else:
                     msg_log.append("⚠️ 抽奖: 操作超时 (可能已完成)")

            browser.close()
            print("🏁 浏览器关闭")
            
            # 汇总结果
            final_msg = "<br>".join(msg_log)
            print(f"📊 最终报告: {final_msg}")
            
            if "❌" in final_msg or "🎉" in final_msg:
                send_notification("掘金浏览器打卡", final_msg)

if __name__ == "__main__":
    JuejinBrowser().run()



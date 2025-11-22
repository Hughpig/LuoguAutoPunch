# 洛谷自动打卡
此仓库旨在通过 Github Actions 帮助您自动在洛谷打卡。
## 快速上手
- 请先 Fork 本仓库
- 在 `Settings`-`Secrets and Variables`-`Actions`-`Repository secrets`中添加以下三个Secrets：
  - `EMAIL_PASSWORD` : 由你的邮箱服务商的提供的关于您邮箱账号的 SMTP 授权码
  - `EMAIL_USERNAME` : 接受邮件的人的邮箱，例：your_name@qq.com
  - `LUOGU_COOKIE` : 洛谷名为 `__client_id` 的 Cookie 的内容
每天北京时间 8:00 脚本将自动运行，并自动发送执行情况到名为 `EMAIL_USERNAME` 的邮箱中。
> Tip: 您也可以手动执行 Actions.

# 洛谷自动打卡

**免责声明：本项目仅供技术学习与交流使用。使用者在使用本项目时应遵守洛谷用户协议。严禁使用本项目进行攻击、高频抓取或任何干扰洛谷正常运行的行为。作者不对使用本项目导致的账号封禁或 Cookie 泄露负责。**

此仓库旨在通过 Github Actions 帮助您自动在洛谷打卡。

（掘金社区打卡功能还在测试，如果不需要请在 `daily_punch.yml` 中删除相关部分）
## 快速上手
- 请先 Fork 本仓库
- 在 `Settings`-`Secrets and Variables`-`Actions`-`Repository secrets`中添加以下三个 Secrets：
  - `EMAIL_PASSWORD` : 由你的邮箱服务商的提供的关于您邮箱账号的 SMTP 授权码
  - `EMAIL_USERNAME` : 接受邮件的人的邮箱，例：your_name@qq.com
  - `LUOGU_COOKIE` : 洛谷名为 `__client_id` 的 Cookie 的内容
  如果您希望通过 PushPlus 推送，请加入一个名为 `PUSHPLUS_TOKEN` 的 Secrets。
每天北京时间 8:00 脚本将自动运行，并自动发送执行情况到名为 `EMAIL_USERNAME` 的邮箱中。
> Tip: 您也可以手动执行 Actions.

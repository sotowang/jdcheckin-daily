# 京东免费签到、领京豆与可选抽奖机会

此私有仓库每天使用 GitHub Actions 执行京东免费任务：

1. 调用 `signBeanAct` 完成每日签到并领取京豆。
2. 可选调用“天天领好礼”接口，尝试领取免费抽奖机会。

**免费抽奖机会任务当前默认未启用。** 所选开源项目中的固定活动参数在 2026-10-11 实测返回京东 `errCode=102`（入参数据不合规）；未找到可信的更新参数。为避免每天发送无效请求、导致整个工作流失败，只有在设置经验证的活动 ID 后才会尝试领取。

若有当前有效的活动 ID，请在仓库 **Settings → Secrets and variables → Actions → Variables** 添加普通 Repository variable：

- Name：`JD_FREE_DRAW_EALD`
- Value：当前免费活动 ID（不是 Cookie，也不是秘密）

设置后可手动运行工作流验证。抽奖任务只尝试领取免费机会，**不会消耗机会去抽奖、下单、支付或参加付费活动**。

## 运行时间

工作流按 `25 0 * * *` 运行，即北京时间每天 08:25（UTC 00:25）。GitHub 的定时工作流可能因队列负载稍有延迟；也可以在 Actions 页面手动运行。

## 凭据与数据流

Actions 使用私有仓库 Repository secret `JD_COOKIE`。Cookie 是账号会话凭据，不要写入代码、README、Issue 或 Actions 日志。京东 Cookie 可能过期；收到失效提示后，需要重新登录京东并更新该 Secret。

业务请求发往 `https://api.m.jd.com/client.action`。抽奖机会任务设置京东活动页的 `Referer`/`Origin`，不会把 Cookie 发送到其他服务。脚本不输出 Cookie、请求头或原始响应正文；异常消息会经过敏感内容过滤。

## 来源

领京豆和抽奖机会请求参数参考 [destineylu/jdcheckin-daily](https://github.com/destineylu/jdcheckin-daily)（截至 2026-10-11 所核对候选中的最近代码提交为 2025-12-21）。

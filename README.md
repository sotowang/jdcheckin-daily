# 京东免费签到、领京豆与抽奖机会

此私有仓库每天使用 GitHub Actions 执行两项免费任务：

1. 调用京东 `signBeanAct` 完成每日签到并领取京豆。
2. 调用项目支持的“天天领好礼”接口，尝试领取一份免费抽奖机会。

第二项只尝试领取抽奖机会，**不会消耗机会去抽奖、下单、支付或参加付费活动**。活动 ID 由项目提供，京东可能轮换活动；若活动失效，运行日志会显示领取未成功，需要更新活动参数。

## 运行时间

工作流按 `25 0 * * *` 运行，即北京时间每天 08:25（UTC 00:25）。GitHub 的定时工作流可能因队列负载稍有延迟；也可以在 Actions 页面手动运行。

## 凭据

Actions 使用私有仓库 Repository secret `JD_COOKIE`。Cookie 是账号会话凭据，不要写入代码、README、Issue 或 Actions 日志。京东 Cookie 可能过期；收到失效提示后，需要重新登录京东并更新该 Secret。

## 数据流与日志

两个业务请求都发往 `https://api.m.jd.com/client.action`。抽奖机会任务设置京东活动页的 `Referer`/`Origin`，不会把 Cookie 发送到其他服务。脚本不输出 Cookie、请求头或原始响应正文。

## 来源

请求参数参考 [destineylu/jdcheckin-daily](https://github.com/destineylu/jdcheckin-daily)（截至 2026-10-11 所核对的候选中，其最近代码提交为 2025-12-21）；本仓库只启用免费签到、领京豆和免费抽奖机会领取。

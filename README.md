# 京东每日领京豆

此私有仓库使用 GitHub Actions 每天定时调用京东 `signBeanAct` 领京豆；不执行仓库原候选代码中的抽奖活动请求。

## 运行时间

工作流按 `25 0 * * *` 运行，即北京时间每天 08:25（UTC 00:25）。GitHub 的定时工作流可能因队列负载稍有延迟；也可以在 Actions 页面手动运行。

## 设置凭据

在仓库 **Settings → Secrets and variables → Actions** 中添加 Repository secret：

- Name：`JD_COOKIE`
- Value：京东登录 Cookie

Cookie 是账号会话凭据，不要写入代码、README、Issue 或 Actions 日志。京东 Cookie 可能过期；收到失效提示后，需要在京东重新登录并更新该 Secret。

## 工作流范围

唯一的业务请求是向 `https://api.m.jd.com/client.action` 发送 `signBeanAct` 签到请求。脚本不会输出 Cookie，也不会请求抽奖任务接口。仓库 Secret 由 GitHub-hosted Actions runner 在运行时读取。

## 来源

签到请求参数参考 [destineylu/jdcheckin-daily](https://github.com/destineylu/jdcheckin-daily)（截至 2026-10-11 所核对的候选中，其最近代码提交为 2025-12-21）；本仓库仅启用领京豆签到。

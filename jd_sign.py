import json
import os
import sys
import time

import requests


URL = "https://api.m.jd.com/client.action"
COOKIE = os.environ.get("JD_COOKIE", "").strip()


def parse_response(text):
    text = text.strip()
    if not text:
        return None
    if text.startswith("{") or text.startswith("["):
        payload = text
    else:
        start = text.find("(")
        end = text.rfind(")")
        if start < 0 or end <= start:
            return None
        payload = text[start + 1 : end]
    try:
        return json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return None


def main():
    if not COOKIE:
        print("Missing required GitHub Actions secret: JD_COOKIE", file=sys.stderr)
        return 2

    now_ms = int(time.time() * 1000)
    body = {
        "fp": "-1",
        "shshshfp": "-1",
        "shshshfpa": "-1",
        "referUrl": "-1",
        "userAgent": "-1",
        "jda": "-1",
        "rnVersion": "3.9",
    }
    params = {
        "functionId": "signBeanAct",
        "body": json.dumps(body, separators=(",", ":")),
        "appid": "ld",
        "client": "apple",
        "clientVersion": "10.0.4",
        "networkType": "wifi",
        "osVersion": "14.8.1",
        "uuid": str(now_ms),
        "openudid": str(now_ms),
        "jsonp": f"jsonp_{now_ms}_58482",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": COOKIE,
    }

    try:
        response = requests.post(URL, params=params, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        # Do not print request headers or response bodies; they may contain session data.
        print(f"京东签到请求失败（{type(exc).__name__}）", file=sys.stderr)
        return 1

    data = parse_response(response.text)
    if not isinstance(data, dict):
        print("无法解析京东签到响应")
        return 1

    code = str(data.get("code", ""))
    if code == "0":
        award = data.get("data", {}).get("dailyAward", {}).get("beanAward", {}).get("beanCount")
        if award is None:
            print("签到成功")
        else:
            print(f"签到成功，获得 {award} 京豆")
        return 0

    if "已签到" in response.text or "已签到" in str(data):
        print("今天已经签到过了")
        return 0

    if code == "3":
        print("京东 Cookie 已失效，请更新 GitHub Actions Secret JD_COOKIE")
        return 1

    print("签到未成功；请在 Actions 运行日志中查看京东返回状态（不会显示 Cookie）")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

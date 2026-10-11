import json
import os
import re
import sys
import time

import requests


URL = "https://api.m.jd.com/client.action"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
COOKIE = os.environ.get("JD_COOKIE", "").strip()
FREE_DRAW_EALD = os.environ.get("JD_FREE_DRAW_EALD", "").strip()


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


def safe_message_excerpt(value):
    text = str(value or "").strip()
    if not text:
        return ""
    if len(text) > 120:
        return "[内容已省略]"
    if re.search(r"(?i)(cookie|token|authorization|thor|sdtoken|_pst|pin=)", text):
        return "[内容已省略]"
    if re.search(r"\b\d{11}\b|[A-Za-z0-9_+/=-]{24,}", text):
        return "[内容已省略]"
    return text


def jd_bean_sign():
    print("开始执行京东领京豆签到")
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
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": COOKIE,
    }
    try:
        response = requests.post(URL, params=params, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"京豆签到请求失败（{type(exc).__name__}）", file=sys.stderr)
        return False

    data = parse_response(response.text)
    if not isinstance(data, dict):
        print("京豆签到响应无法解析")
        return False

    code = str(data.get("code", ""))
    if code == "0":
        award = data.get("data", {}).get("dailyAward", {}).get("beanAward", {}).get("beanCount")
        if award is None:
            print("京豆签到成功")
        else:
            print(f"京豆签到成功，获得 {award} 京豆")
        return True

    if "已签到" in response.text or "已签到" in str(data):
        print("今天已经完成京豆签到")
        return True

    if code == "3":
        print("京东 Cookie 已失效，请更新 Actions Secret JD_COOKIE")
    else:
        print(f"京豆签到未成功（京东返回 code={code or 'unknown'}）")
    return False


def jd_claim_free_draw_chance(activity_id):
    """Claim a free daily draw chance; never spends a chance or submits a draw."""
    print("开始领取京东免费抽奖机会")
    function_id = "pc_interact_assign_execute"
    body = {
        "eald": activity_id,
        "type": 5,
        "itemId": "1",
        "extraType": "sign",
        "rk": False,
        "actionType": 1,
    }
    payload = {
        "functionId": function_id,
        "body": json.dumps(body, separators=(",", ":")),
        "appid": "pc_interact_center",
        "client": "pc",
        "clientVersion": "1.0.0",
        "t": int(time.time() * 1000),
    }
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": COOKIE,
        "Referer": "https://interact.jd.com/",
        "Origin": "https://interact.jd.com",
    }
    try:
        response = requests.post(URL, headers=headers, data=payload, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"免费抽奖机会请求失败（{type(exc).__name__}）", file=sys.stderr)
        return False

    try:
        data = response.json()
    except ValueError:
        print("免费抽奖机会响应无法解析")
        return False
    if not isinstance(data, dict):
        print("免费抽奖机会响应无法解析")
        return False

    success = data.get("success") is True or str(data.get("success", "")).lower() == "true"
    if success:
        print("已领取一份免费抽奖机会")
        return True

    code = str(data.get("code") or data.get("errCode") or data.get("err_code") or "")
    message = str(data.get("message") or data.get("msg") or data.get("errorMessage") or data.get("errMessage") or "")
    if any(word in message for word in ("重复", "上限", "已完成", "已领取", "已经领取")):
        print("免费抽奖任务今日已完成或已达到领取上限")
        return True

    if code == "102":
        print("免费抽奖机会未领取（errCode=102：活动参数不合规，请核对当前活动 ID）")
    elif code == "3" or any(word in message.lower() for word in ("未登录", "登录失效", "cookie")):
        print("京东登录状态异常，请检查 Actions Secret JD_COOKIE")
    elif "活动" in message and any(word in message for word in ("不存在", "结束", "过期", "失效")):
        print("免费抽奖活动可能已结束或活动 ID 已轮换")
    else:
        excerpt = safe_message_excerpt(message) or "未知"
        print(f"免费抽奖机会未确认（errCode={code or 'unknown'}，原因={excerpt}）")
    return False


def main():
    if not COOKIE:
        print("Missing required GitHub Actions secret: JD_COOKIE", file=sys.stderr)
        return 2

    bean_ok = jd_bean_sign()
    if FREE_DRAW_EALD:
        time.sleep(2)
        draw_ok = jd_claim_free_draw_chance(FREE_DRAW_EALD)
    else:
        print("免费抽奖机会任务未启用：未配置经验证的 Actions Variable JD_FREE_DRAW_EALD")
        draw_ok = True
    return 0 if bean_ok and draw_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

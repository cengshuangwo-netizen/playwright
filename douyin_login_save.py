# -*- coding: utf-8 -*-
"""
抖音登录状态保存脚本

功能：
1. 打开抖音创作者中心
2. 等待用户手动扫码登录
3. 保存登录状态到 auth.json

使用方法：
1. 运行此脚本
2. 在打开的浏览器中扫码登录
3. 登录成功后按 Enter 键保存状态
"""

from playwright.sync_api import sync_playwright
import time
import sys
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

AUTH_FILE = "auth.json"
LOGIN_URL = "https://creator.douyin.com/"


def log(message: str):
    """打印带时间戳的日志"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def main():
    log("=" * 50)
    log("[LOGIN] 抖音登录状态保存工具")
    log("=" * 50)
    
    with sync_playwright() as p:
        # 启动浏览器
        log("[BROWSER] 启动浏览器...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        # 访问抖音创作者中心
        log(f"[NAVIGATE] 访问: {LOGIN_URL}")
        page.goto(LOGIN_URL)
        page.wait_for_load_state("networkidle")
        
        log("")
        log("=" * 50)
        log("[ACTION] 请在浏览器中扫码登录抖音")
        log("[WAIT] 登录成功后，请按 Enter 键保存登录状态...")
        log("=" * 50)
        input()
        
        # 保存登录状态
        log(f"[SAVE] 保存登录状态到 {AUTH_FILE}...")
        context.storage_state(path=AUTH_FILE)
        log(f"[OK] 登录状态已保存到 {AUTH_FILE}")
        
        context.close()
        browser.close()
        
        log("")
        log("[DONE] 完成！现在可以运行 douyin_auto_uploader.py 上传视频")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
录制生成的抖音上传脚本（已修复）
"""
import os
import sys
import io
from playwright.sync_api import Playwright, sync_playwright

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        storage_state="auth.json",
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    
    # 导航到上传页面
    print("[1] 导航到上传页面...")
    page.goto("https://creator.douyin.com/creator-micro/content/upload")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    # 上传视频文件（修复：使用隐藏的 input[type="file"]）
    print("[2] 上传视频文件...")
    video_path = os.path.abspath("video.mp4")
    file_input = page.locator("input[type='file']").first
    file_input.set_input_files(video_path)
    
    # 等待页面跳转
    print("[3] 等待上传完成...")
    try:
        page.wait_for_url("**/publish**", timeout=60000)
    except Exception:
        page.wait_for_selector("button:has-text('发布')", timeout=60000)
    page.wait_for_timeout(3000)
    
    # 填写标题
    print("[4] 填写标题...")
    title_input = page.get_by_role("textbox", name="填写作品标题，为作品获得更多流量")
    title_input.click()
    title_input.fill("第二条vlog")
    page.wait_for_timeout(1000)
    
    # 点击暂存离开
    print("[5] 点击暂存离开...")
    page.get_by_role("button", name="暂存离开").click()
    page.wait_for_timeout(3000)
    
    print("[OK] 视频已暂存为草稿！")
    print("按 Enter 键关闭浏览器...")
    input()
    
    # 保存状态并关闭
    context.storage_state(path="auth.json")
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

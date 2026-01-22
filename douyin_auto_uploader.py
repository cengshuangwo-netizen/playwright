

# -*- coding: utf-8 -*-
"""
Douyin-Auto-Uploader
抖音自动上传脚本

功能：
1. 使用已保存的登录状态 (auth.json) 启动浏览器
2. 先填写视频标题
3. 上传视频文件
4. 点击发布

前置条件：
- 根目录下有 auth.json (登录状态)
- 根目录下有 video.mp4 (待上传视频)
"""

from playwright.sync_api import sync_playwright # test branch
import time
import os
import sys
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ==================== 配置区域 ====================
AUTH_FILE = "auth.json"          # 登录状态文件
VIDEO_FILE = "video.mp4"         # 待上传的视频文件
VIDEO_TITLE = "这是我的第一条自动发布视频 #VibeCoding"  # 视频标题
UPLOAD_URL = "https://creator.douyin.com/creator-micro/content/upload"

# 录制配置
ENABLE_RECORDING = True          # 是否启用屏幕录制
RECORDING_DIR = "recordings"     # 录制文件保存目录

# ==================== 工具函数 ====================
def log(message: str):
    """打印带时间戳的日志"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def wait_with_log(page, seconds: float, reason: str):
    """等待并打印原因"""
    log(f"等待 {seconds} 秒: {reason}")
    page.wait_for_timeout(seconds * 1000)


def fill_title(page, title: str) -> bool:
    """填写视频标题，返回是否成功"""
    log("[ACTION] 填写视频标题...")
    
    # 尝试多种方式定位标题输入框
    title_selectors = [
        "input[placeholder*='标题']",
        "input[placeholder*='填写作品标题']",
        "[placeholder*='标题']",
        ".title-input input",
        "[class*='title'] input",
        # contenteditable div 的情况
        "[contenteditable='true'][placeholder*='标题']",
        "[contenteditable='true'][data-placeholder*='标题']"
    ]
    
    title_input = None
    for selector in title_selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible(timeout=2000):
                title_input = element
                log(f"[OK] 找到标题输入框: {selector}")
                break
        except Exception:
            continue
    
    if title_input:
        # 清空并输入标题
        title_input.click()
        title_input.fill("")
        title_input.fill(title)
        log(f"[OK] 标题已填写: {title}")
        return True
    else:
        log("[WARN] 未找到标题输入框，尝试使用 contenteditable div...")
        # 尝试 contenteditable 方式
        try:
            editable_div = page.locator("[contenteditable='true']").first
            editable_div.click()
            editable_div.fill(title)
            log(f"[OK] 标题已填写 (contenteditable): {title}")
            return True
        except Exception as e:
            log(f"[ERROR] 标题填写失败: {e}")
            return False


# ==================== 主流程 ====================
def main():
    # 检查前置文件
    if not os.path.exists(AUTH_FILE):
        log(f"[ERROR] 找不到登录状态文件 '{AUTH_FILE}'")
        log("请先运行登录脚本生成 auth.json")
        return
    
    if not os.path.exists(VIDEO_FILE):
        log(f"[ERROR] 找不到视频文件 '{VIDEO_FILE}'")
        return
    
    log("=" * 50)
    log("[START] Douyin-Auto-Uploader 启动")
    log("=" * 50)
    
    with sync_playwright() as p:
        # ========== Step 1: 启动浏览器 ==========
        log("[Step 1] 启动浏览器...")
        
        # 准备录制目录
        if ENABLE_RECORDING:
            os.makedirs(RECORDING_DIR, exist_ok=True)
            log(f"[RECORD] 屏幕录制已启用，保存目录: {RECORDING_DIR}")
        
        # 加载已保存的登录状态
        browser = p.chromium.launch(headless=False)
        
        # 创建上下文（带录制功能）
        context_options = {
            "storage_state": AUTH_FILE,
            "viewport": {"width": 1920, "height": 1080}  # 防止布局错乱
        }
        
        if ENABLE_RECORDING:
            context_options["record_video_dir"] = RECORDING_DIR
            context_options["record_video_size"] = {"width": 1920, "height": 1080}
        
        context = browser.new_context(**context_options)
        page = context.new_page()
        
        log("[OK] 浏览器启动成功，Viewport: 1920x1080")
        
        try:
            # ========== Step 2: 导航到上传页面 ==========
            log("[Step 2] 导航到抖音创作者上传页面...")
            page.goto(UPLOAD_URL)
            page.wait_for_load_state("networkidle")
            log(f"[OK] 页面加载完成: {page.url}")
            
            # 给页面一些额外的加载时间
            wait_with_log(page, 3, "等待页面元素渲染")
            
            # ========== Step 3: 先填写视频标题 ==========
            log("[Step 3] 填写视频标题...")
            
            # 尝试在上传前填写标题（如果页面支持）
            title_filled_before_upload = fill_title(page, VIDEO_TITLE)
            
            if title_filled_before_upload:
                wait_with_log(page, 1, "标题填写完成")
            else:
                log("[INFO] 上传前未找到标题输入框，将在上传后填写")
            
            # ========== Step 4: 上传视频文件 ==========
            log("[Step 4] 上传视频文件...")
            
            # 定位隐藏的文件上传 input 标签
            # 抖音的上传按钮实际上是一个隐藏的 input[type="file"]
            file_input = page.locator("input[type='file']").first
            
            # 获取视频文件的绝对路径
            video_path = os.path.abspath(VIDEO_FILE)
            log(f"[FILE] 视频文件路径: {video_path}")
            
            # 上传文件
            file_input.set_input_files(video_path)
            log("[OK] 视频文件已选择，开始上传...")
            
            # ========== Step 5: 等待上传完成 ==========
            log("[Step 5] 等待视频上传完成...")
            
            # 等待页面跳转或"发布"按钮出现
            # 抖音上传后会跳转到编辑页面
            try:
                # 方法1: 等待URL变化（跳转到编辑页）
                page.wait_for_url("**/publish**", timeout=60000)
                log("[OK] 已跳转到发布编辑页面")
            except Exception:
                log("[WARN] URL未变化，尝试检测发布按钮...")
                # 方法2: 等待发布按钮出现
                page.wait_for_selector("button:has-text('发布')", timeout=60000)
            
            # 等待上传进度完成
            log("[WAIT] 等待视频处理完成...")
            try:
                # 等待上传成功的标识
                page.wait_for_selector(
                    "text=上传成功, text=重新上传, .upload-success",
                    timeout=120000  # 大文件可能需要更长时间
                )
                log("[OK] 视频上传成功")
            except Exception:
                log("[WARN] 未检测到明确的上传成功标识，继续执行...")
            
            wait_with_log(page, 3, "确保视频处理完成")
            
            # ========== Step 6: 如果之前没填标题，现在填写 ==========
            if not title_filled_before_upload:
                log("[Step 6] 页面跳转后填写标题...")
                fill_title(page, VIDEO_TITLE)
                wait_with_log(page, 2, "等待标题输入完成")
            
            # ========== Step 7: 暂存离开 ==========
            log("[Step 7] 点击暂存离开...")
            
            # 滚动到页面底部
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            wait_with_log(page, 1, "滚动到底部")
            
            # 定位暂存离开按钮
            save_selectors = [
                "button:has-text('暂存离开')",
                "text=暂存离开",
                "//button[contains(text(), '暂存离开')]"
            ]
            
            save_button = None
            for selector in save_selectors:
                try:
                    if selector.startswith("//"):
                        element = page.locator(f"xpath={selector}").first
                    else:
                        element = page.locator(selector).first
                    
                    if element.is_visible(timeout=2000):
                        save_button = element
                        log(f"[OK] 找到暂存离开按钮: {selector}")
                        break
                except Exception:
                    continue
            
            if save_button:
                wait_with_log(page, 2, "确保按钮可点击")
                
                # 点击暂存离开
                save_button.click()
                log("[OK] 已点击暂存离开按钮")
                
                # 等待保存完成
                wait_with_log(page, 3, "等待保存处理")
                
                log("[SUCCESS] 视频已暂存为草稿！")
                log("[INFO] 请稍后在抖音创作者中心手动发布")
            else:
                log("[ERROR] 未找到暂存离开按钮")
            
            # 保持浏览器打开以便查看结果
            log("=" * 50)
            log("[DONE] 脚本执行完成")
            log("按 Enter 键关闭浏览器...")
            log("=" * 50)
            input()
            
        except Exception as e:
            log(f"[ERROR] 发生错误: {e}")
            log("保持浏览器打开以便调试...")
            log("按 Enter 键关闭浏览器...")
            input()
        
        finally:
            # 获取录制文件路径
            if ENABLE_RECORDING:
                video_path = page.video.path()
                log(f"[RECORD] 录制文件已保存: {video_path}")
            
            context.close()
            browser.close()
            log("[CLOSE] 浏览器已关闭")


if __name__ == "__main__":
    main()

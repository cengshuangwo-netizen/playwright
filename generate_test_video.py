# -*- coding: utf-8 -*-
"""
生成测试视频脚本
创建一个 5 秒的竖屏测试视频 (1080x1920)
"""

import cv2
import numpy as np

# 视频参数
OUTPUT_FILE = "video.mp4"
WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 5  # 秒

def main():
    print(f"[INFO] 生成测试视频: {OUTPUT_FILE}")
    print(f"[INFO] 分辨率: {WIDTH}x{HEIGHT}, FPS: {FPS}, 时长: {DURATION}秒")
    
    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_FILE, fourcc, FPS, (WIDTH, HEIGHT))
    
    total_frames = FPS * DURATION
    
    for i in range(total_frames):
        # 创建渐变背景
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        
        # 动态颜色变化
        progress = i / total_frames
        hue = int(progress * 180)  # HSV 色相变化
        
        # 创建渐变效果
        for y in range(HEIGHT):
            color_val = int(255 * (1 - y / HEIGHT * 0.5))
            frame[y, :] = [hue, color_val, color_val]
        
        # 转换 HSV 到 BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
        
        # 添加文字
        text = "Test Video"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        thickness = 4
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (WIDTH - text_size[0]) // 2
        text_y = HEIGHT // 2
        
        # 文字阴影
        cv2.putText(frame, text, (text_x + 3, text_y + 3), font, font_scale, (0, 0, 0), thickness)
        # 白色文字
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
        
        # 显示帧数
        frame_text = f"Frame: {i+1}/{total_frames}"
        cv2.putText(frame, frame_text, (50, HEIGHT - 100), font, 1, (255, 255, 255), 2)
        
        # 时间显示
        seconds = i / FPS
        time_text = f"Time: {seconds:.1f}s"
        cv2.putText(frame, time_text, (50, HEIGHT - 50), font, 1, (255, 255, 255), 2)
        
        out.write(frame)
        
        # 进度显示
        if i % 30 == 0:
            print(f"[PROGRESS] {int(progress * 100)}%")
    
    out.release()
    print(f"[OK] 视频已生成: {OUTPUT_FILE}")
    print(f"[INFO] 文件大小: {round(cv2.os.path.getsize(OUTPUT_FILE) / 1024 / 1024, 2)} MB")


if __name__ == "__main__":
    main()

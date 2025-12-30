import cv2
import torch
import math
import numpy as np

class VideoIntervalCalculator:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "video_path": ("STRING", {"default": "input.mp4"}),
                "rows": ("INT", {"default": 4, "min": 1, "max": 100}),
                "cols": ("INT", {"default": 4, "min": 1, "max": 100}),
                "start_time": ("FLOAT", {"default": 0.0, "min": 0.0, "step": 0.1, "display": "number"}),
                "end_time": ("FLOAT", {"default": 0.0, "min": 0.0, "step": 0.1, "display": "number"}), 
            }
        }

    # 增加了 skip_first_frames 输出，用于告诉 VHS 从哪一帧开始
    RETURN_TYPES = ("INT", "INT", "INT", "INT")
    RETURN_NAMES = ("select_every_nth", "frame_load_cap", "skip_first_frames", "total_count")
    FUNCTION = "calculate"
    CATEGORY = "ContactSheet"

    def calculate(self, video_path, rows, cols, start_time, end_time):
        # 移除路径两端的引号
        video_path = video_path.strip('"')
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        # 获取 FPS 和 总帧数
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        # 1. 计算起始帧 (Start Frame)
        start_frame = int(start_time * fps)
        
        # 2. 计算结束帧 (End Frame)
        # 如果 end_time 为 0，或者设置得比视频还长，则默认使用视频结尾
        if end_time <= 0 or end_time * fps > total_frames:
            end_frame = total_frames
        else:
            end_frame = int(end_time * fps)

        # 3. 安全检查：确保 start 小于 end
        if start_frame >= end_frame:
            # 如果设置错误，回退到默认：从头开始，到结尾
            print(f"Warning: Start time ({start_time}s) is after End time. Resetting to full video.")
            start_frame = 0
            end_frame = total_frames

        # 4. 计算有效时间段的帧数
        duration_frames = end_frame - start_frame
        target_count = rows * cols
        
        # 5. 计算间隔
        # 逻辑：在 (End - Start) 的范围内，均匀取出 Target 张
        nth = max(1, duration_frames // target_count)
        
        print(f"Video Info: FPS={fps:.2f}, Total={total_frames}")
        print(f"Range: {start_frame} to {end_frame} (Duration: {duration_frames} frames)")
        print(f"Calc: Need {target_count} images. Skip Interval: {nth}")
        
        # 返回值说明：
        # 1. select_every_nth: 间隔
        # 2. frame_load_cap: 总共要加载多少张 (rows * cols)
        # 3. skip_first_frames: 告诉 VHS 跳过前面多少帧 (即 start_frame)
        # 4. total_count: 备用数据
        return (nth, target_count, start_frame, target_count)

class SimpleGridImage:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                "cols": ("INT", {"default": 4, "min": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "make_grid"
    CATEGORY = "ContactSheet"

    def make_grid(self, images, cols):
        # images shape: [Batch, Height, Width, Channel]
        batch_size, h, w, c = images.shape
        
        rows = math.ceil(batch_size / cols)
        
        # 创建一个全黑的大画布
        grid_h = rows * h
        grid_w = cols * w
        grid = torch.zeros((1, grid_h, grid_w, c), dtype=images.dtype)
        
        for idx, img in enumerate(images):
            r = idx // cols
            c_idx = idx % cols
            
            y_start = r * h
            y_end = y_start + h
            x_start = c_idx * w
            x_end = x_start + w
            
            # 将图片填入画布
            grid[0, y_start:y_end, x_start:x_end, :] = img
            
        return (grid,)

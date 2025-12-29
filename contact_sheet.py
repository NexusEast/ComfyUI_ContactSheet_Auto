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
            }
        }

    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("select_every_nth", "frame_load_cap", "total_count")
    FUNCTION = "calculate"
    CATEGORY = "ContactSheet"

    def calculate(self, video_path, rows, cols):
        # 移除路径两端的引号（防止用户复制路径时带入）
        video_path = video_path.strip('"')
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        target_count = rows * cols
        
        # 计算间隔：总帧数 / 目标张数
        # max(1, ...) 确保间隔至少为1
        nth = max(1, total_frames // target_count)
        
        # 为了防止因为取整导致最后多出一两帧，我们设置一个上限
        # 比如 100帧，要10张，间隔10，正好。
        # 比如 105帧，要10张，间隔10，会取到11张。
        # 所以我们将 load_cap 设为 target_count + 1 (留一点余量给后续处理，或者严格限制)
        # 这里建议严格限制为 target_count，VHS loader 会截断
        
        print(f"Video: {total_frames} frames. Target: {target_count}. Interval: {nth}")
        
        return (nth, target_count, target_count)

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

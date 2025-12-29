from .contact_sheet import VideoIntervalCalculator, SimpleGridImage

NODE_CLASS_MAPPINGS = {
    "VideoIntervalCalculator": VideoIntervalCalculator,
    "SimpleGridImage": SimpleGridImage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoIntervalCalculator": "🎥 Video Interval Auto-Calc",
    "SimpleGridImage": "🖼️ Batch to Grid Image"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

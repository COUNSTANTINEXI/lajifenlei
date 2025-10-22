"""
服务模块
包含图片识别等服务
"""

try:
    from .image_classifier import ImageGarbageClassifier
    IMAGE_CLASSIFIER_AVAILABLE = True
except ImportError:
    IMAGE_CLASSIFIER_AVAILABLE = False
    ImageGarbageClassifier = None

__all__ = ['ImageGarbageClassifier', 'IMAGE_CLASSIFIER_AVAILABLE']


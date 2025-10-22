"""
垃圾分类系统 - 图片识别模块
使用中文预训练模型进行垃圾图片识别
"""

import os
import numpy as np
from typing import Tuple, Optional, List
from PIL import Image
import io

# Lazy import model libraries to avoid loading at startup
_model = None
_model_loaded = False


def _load_model():
    """Load Chinese CLIP pretrained model"""
    global _model, _model_loaded
    
    if _model_loaded:
        return _model
    
    try:
        import torch
        from transformers import CLIPProcessor, CLIPModel, AutoProcessor, AutoModel
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Try multiple Chinese CLIP models (by priority)
        model_options = [
            # Option 1: OFA-Sys Chinese CLIP (best, but larger)
            ("OFA-Sys/chinese-clip-vit-base-patch16", "chinese_clip"),
            # Option 2: OpenAI multilingual CLIP (general, supports Chinese)
            ("openai/clip-vit-base-patch32", "openai_clip"),
        ]
        
        model_loaded_successfully = False
        
        for model_name, model_type in model_options:
            try:
                print(f"正在尝试加载模型: {model_name}...")
                
                if model_type == "chinese_clip":
                    # Use dedicated Chinese CLIP
                    processor = AutoProcessor.from_pretrained(model_name)
                    model = AutoModel.from_pretrained(model_name).to(device)
                else:
                    # Use standard CLIP
                    processor = CLIPProcessor.from_pretrained(model_name)
                    model = CLIPModel.from_pretrained(model_name).to(device)
                
                model.eval()
                
                print(f"✅ {model_name} 模型加载成功 (设备: {device})")
                
                _model = {
                    'model': model,
                    'processor': processor,
                    'device': device,
                    'type': model_type,
                    'name': model_name
                }
                model_loaded_successfully = True
                break
                
            except Exception as e:
                print(f"⚠️  {model_name} 加载失败: {e}")
                print(f"尝试下一个模型...")
                continue
        
        if not model_loaded_successfully:
            raise RuntimeError("所有模型加载失败，请检查网络连接或安装 transformers")
        
        _model_loaded = True
        return _model
        
    except ImportError as e:
        print(f"模型加载失败: {e}")
        print("请安装必要的依赖:")
        print("  pip install torch torchvision transformers")
        print("  # CPU 版本: pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu")
        raise
    except Exception as e:
        print(f"模型加载失败: {e}")
        raise


class ImageGarbageClassifier:
    """Image garbage classifier (using Chinese model)"""
    
    def __init__(self):
        """Initialize image classifier"""
        self.model_info = None
        
        # Chinese candidate labels (garbage classification related)
        self.candidate_labels = {
            # Recyclable waste
            '可回收垃圾': ['塑料瓶', '玻璃瓶', '易拉罐', '纸箱', '报纸', '杂志', '书本', '纸板', 
                          '塑料容器', '玻璃杯', '金属罐', '铁罐', '铝罐', '纸盒', '包装盒',
                          '饮料瓶', '矿泉水瓶', '啤酒瓶', '红酒瓶', '牛奶盒', '快递盒'],
            
            # Kitchen waste
            '厨余垃圾': ['苹果', '香蕉', '橙子', '橘子', '柠檬', '菠萝', '草莓', '西瓜', '葡萄',
                        '西红柿', '黄瓜', '白菜', '青菜', '萝卜', '土豆', '红薯', '玉米',
                        '茄子', '辣椒', '蘑菇', '面包', '米饭', '面条', '剩菜', '剩饭',
                        '鱼骨', '果皮', '果核', '菜叶', '蛋壳', '咖啡渣', '茶叶渣'],
            
            # Hazardous waste
            '有害垃圾': ['电池', '纽扣电池', '充电电池', '干电池', '灯管', '灯泡', '节能灯',
                        '荧光灯', '温度计', '血压计', '药品', '药瓶', '油漆桶', '杀虫剂',
                        '消毒剂', '指甲油', '过期化妆品', '水银温度计'],
            
            # Other waste
            '其他垃圾': ['烟蒂', '纸巾', '卫生纸', '湿纸巾', '尿布', '卫生巾', '猫砂', '狗屎',
                        '陶瓷', '碎陶瓷', '砖块', '瓦片', '灰土', '毛发', '一次性餐具',
                        '塑料袋', '食品袋', '保鲜膜', '胶带', '口香糖']
        }
        
        # All possible item labels (Chinese)
        self.all_labels = []
        for labels in self.candidate_labels.values():
            self.all_labels.extend(labels)
        
        # Quick mapping from item to garbage type
        self.label_to_type = {}
        for garbage_type, labels in self.candidate_labels.items():
            for label in labels:
                self.label_to_type[label] = garbage_type
    
    def load_model(self):
        """Load model"""
        if self.model_info is None:
            self.model_info = _load_model()
    
    def preprocess_image(self, image_data: bytes):
        """
        Preprocess image
        
        Args:
            image_data: Image binary data
            
        Returns:
            Preprocessed PIL image
        """
        try:
            # Load image from binary data
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB (if RGBA or other formats)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            raise ValueError(f"图片预处理失败: {e}")
    
    def predict_object(self, image_data: bytes, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Recognize objects in image (using Chinese labels)
        
        Args:
            image_data: Image binary data
            top_k: Return top k predictions
            
        Returns:
            [(item_name, similarity), ...]
        """
        try:
            import torch
            
            # Ensure model is loaded
            self.load_model()
            
            # Preprocess image
            image = self.preprocess_image(image_data)
            
            processor = self.model_info['processor']
            model = self.model_info['model']
            model_type = self.model_info['type']
            
            # Process input
            inputs = processor(
                text=self.all_labels,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.model_info['device'])
            
            # Inference
            with torch.no_grad():
                if model_type == "chinese_clip":
                    # Chinese CLIP may use different output format
                    outputs = model(**inputs)
                    # Try to get image-text similarity
                    if hasattr(outputs, 'logits_per_image'):
                        logits_per_image = outputs.logits_per_image
                    else:
                        # Manually calculate similarity
                        image_embeds = outputs.image_embeds
                        text_embeds = outputs.text_embeds
                        # Normalize
                        image_embeds = image_embeds / image_embeds.norm(dim=-1, keepdim=True)
                        text_embeds = text_embeds / text_embeds.norm(dim=-1, keepdim=True)
                        # Calculate similarity
                        logits_per_image = torch.matmul(image_embeds, text_embeds.t()) * 100
                else:  # openai_clip
                    outputs = model(**inputs)
                    logits_per_image = outputs.logits_per_image
                
                # Calculate probabilities
                probs = logits_per_image.softmax(dim=1)[0]
                values, indices = probs.topk(min(top_k, len(self.all_labels)))
            
            # Format results
            results = []
            for i in range(len(values)):
                label = self.all_labels[indices[i].item()]
                score = values[i].item()
                results.append((label, score))
            
            return results
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"物体识别失败: {e}")
    
    def map_object_to_garbage_type(self, object_name: str) -> Tuple[Optional[str], str]:
        """
        Map recognized object to garbage type
        
        Args:
            object_name: Object name (Chinese)
            
        Returns:
            (garbage_type, mapping_reason)
        """
        # Direct lookup
        garbage_type = self.label_to_type.get(object_name)
        if garbage_type:
            return garbage_type, f"识别到物品'{object_name}'属于{garbage_type}"
        
        # If no direct mapping, try fuzzy matching
        for label, gtype in self.label_to_type.items():
            if object_name in label or label in object_name:
                return gtype, f"根据'{label}'判断为{gtype}"
        
        return None, f"未能将'{object_name}'映射到垃圾分类"
    
    def classify_image(self, image_data: bytes, confidence_threshold: float = 0.1) -> Tuple[bool, str, str, str, List[dict]]:
        """
        Classify garbage from image
        
        Args:
            image_data: Image binary data
            confidence_threshold: Confidence threshold
            
        Returns:
            (success, garbage_type, reason, object_name, detailed_predictions)
        """
        try:
            # Recognize objects in image
            predictions = self.predict_object(image_data, top_k=5)
            
            # Format prediction results
            detailed_results = []
            for object_name, confidence in predictions:
                garbage_type, reason = self.map_object_to_garbage_type(object_name)
                detailed_results.append({
                    'object_name': object_name,
                    'confidence': round(confidence * 100, 2),
                    'garbage_type': garbage_type if garbage_type else '未知',
                    'can_classify': garbage_type is not None
                })
            
            # Find first classifiable result with sufficient confidence
            for pred in detailed_results:
                if pred['can_classify'] and pred['confidence'] / 100 >= confidence_threshold:
                    garbage_type = pred['garbage_type']
                    object_name = pred['object_name']
                    confidence = pred['confidence']
                    
                    reason = f"图片识别结果：{object_name} (置信度: {confidence}%)"
                    
                    return True, garbage_type, reason, object_name, detailed_results
            
            # If no suitable classification found, return highest confidence result
            if detailed_results:
                best = detailed_results[0]
                return False, "未知", f"识别到{best['object_name']}，但无法确定垃圾分类", best['object_name'], detailed_results
            else:
                return False, "未知", "未能识别图片内容", "", []
                
        except Exception as e:
            return False, "错误", f"图片分类失败: {str(e)}", "", []
    
    def get_disposal_suggestion(self, garbage_type: str) -> str:
        """
        Get disposal suggestion
        
        Args:
            garbage_type: Garbage type
            
        Returns:
            Disposal suggestion
        """
        suggestions = {
            '可回收垃圾': '清洗干净后投入蓝色回收桶，可换取积分或现金',
            '有害垃圾': '投入红色有害垃圾桶，由专业机构处理',
            '厨余垃圾': '沥干水分后投入绿色厨余垃圾桶，可用于堆肥',
            '其他垃圾': '投入灰色其他垃圾桶，进行填埋或焚烧处理'
        }
        return suggestions.get(garbage_type, '请按照当地垃圾分类标准处理')


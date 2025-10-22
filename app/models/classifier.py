"""
垃圾分类系统 - 分类逻辑模块
实现智能垃圾分类算法
"""

from typing import Tuple, Optional, List
from .data_manager import GarbageDataManager


class GarbageClassifier:
    """垃圾分类器"""
    
    def __init__(self, data_manager: GarbageDataManager = None):
        """
        初始化分类器
        
        Args:
            data_manager: 数据管理器实例
        """
        self.data_manager = data_manager or GarbageDataManager()
        
        # Garbage type color mapping (for UI display)
        self.type_colors = {
            '可回收垃圾': '#4CAF50',  # Green
            '有害垃圾': '#F44336',    # Red
            '厨余垃圾': '#FF9800',    # Orange
            '其他垃圾': '#9E9E9E'     # Gray
        }
        
        # Garbage type icon mapping
        self.type_icons = {
            '可回收垃圾': '♻️',
            '有害垃圾': '☠️',
            '厨余垃圾': '🍎',
            '其他垃圾': '🗑️'
        }
    
    def classify(self, item_name: str) -> Tuple[bool, str, str, str]:
        """
        Classify item into garbage category
        
        Args:
            item_name: Item name
            
        Returns:
            Tuple(success, garbage_type, reason, suggestion)
        """
        if not item_name or not item_name.strip():
            return False, "", "请输入物品名称", ""
        
        # Get classification from data manager
        result = self.data_manager.get_classification(item_name)
        
        if result:
            garbage_type, reason = result
            suggestion = self._get_disposal_suggestion(garbage_type)
            return True, garbage_type, reason, suggestion
        else:
            # Try keyword analysis
            predicted_result = self._keyword_analysis(item_name)
            if predicted_result:
                garbage_type, reason = predicted_result
                suggestion = self._get_disposal_suggestion(garbage_type)
                return True, garbage_type, f"智能预测：{reason}", suggestion
            else:
                return False, "未知", f"抱歉，未找到'{item_name}'的分类规则", "建议咨询相关部门或添加到规则库"
    
    def _keyword_analysis(self, item_name: str) -> Optional[Tuple[str, str]]:
        """
        Keyword-based intelligent analysis
        
        Args:
            item_name: Item name
            
        Returns:
            Tuple(garbage_type, reason) or None
        """
        item_lower = item_name.lower()
        
        # Recyclable waste keywords
        recyclable_keywords = [
            '纸', '塑料', '玻璃', '金属', '铁', '铝', '铜', '钢', '瓶', '罐', 
            '盒', '箱', '袋', '报纸', '杂志', '书', '本', '卡片'
        ]
        
        # Hazardous waste keywords
        hazardous_keywords = [
            '电池', '灯管', '灯泡', '温度计', '血压计', '药', '油漆', '农药',
            '化学', '汞', '铅', '镉', '荧光', '节能灯', '水银'
        ]
        
        # Kitchen waste keywords
        kitchen_keywords = [
            '菜', '果', '肉', '鱼', '虾', '蛋', '米', '面', '豆', '奶',
            '剩', '皮', '核', '渣', '骨', '壳', '叶', '根', '茎'
        ]
        
        # Other waste keywords
        other_keywords = [
            '烟', '灰', '尿布', '卫生', '陶瓷', '砖', '瓦', '灰土', '毛发',
            '织物', '皮革', '橡胶', '木材'
        ]
        
        # Check keyword matches
        for keyword in hazardous_keywords:
            if keyword in item_name:
                return "有害垃圾", f"包含关键词'{keyword}'，可能含有有害物质"
        
        for keyword in kitchen_keywords:
            if keyword in item_name:
                return "厨余垃圾", f"包含关键词'{keyword}'，属于有机废料"
        
        for keyword in recyclable_keywords:
            if keyword in item_name:
                return "可回收垃圾", f"包含关键词'{keyword}'，材料可回收利用"
        
        for keyword in other_keywords:
            if keyword in item_name:
                return "其他垃圾", f"包含关键词'{keyword}'，难以回收处理"
        
        return None
    
    def _get_disposal_suggestion(self, garbage_type: str) -> str:
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
    
    def get_type_color(self, garbage_type: str) -> str:
        """Get color for garbage type"""
        return self.type_colors.get(garbage_type, '#000000')
    
    def get_type_icon(self, garbage_type: str) -> str:
        """Get icon for garbage type"""
        return self.type_icons.get(garbage_type, '❓')
    
    def batch_classify(self, item_names: List[str]) -> List[Tuple[str, bool, str, str, str]]:
        """
        Batch classification
        
        Args:
            item_names: List of item names
            
        Returns:
            List of classification results [(item_name, success, garbage_type, reason, suggestion)]
        """
        results = []
        for item_name in item_names:
            success, garbage_type, reason, suggestion = self.classify(item_name)
            results.append((item_name, success, garbage_type, reason, suggestion))
        return results
    
    def get_similar_items(self, item_name: str, limit: int = 5) -> List[str]:
        """
        Get similar item suggestions
        
        Args:
            item_name: Item name
            limit: Result limit
            
        Returns:
            List of similar item names
        """
        all_items = list(self.data_manager.get_all_rules().keys())
        similar = []
        
        item_lower = item_name.lower()
        
        # Find items containing same characters
        for stored_item in all_items:
            stored_lower = stored_item.lower()
            if any(char in stored_lower for char in item_lower if char.isalnum()):
                similar.append(stored_item)
        
        return similar[:limit]


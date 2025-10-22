"""
垃圾分类系统 - 数据管理模块
负责CSV文件的读写操作和数据管理
"""

import csv
import os
from typing import Dict, List, Tuple, Optional


class GarbageDataManager:
    """垃圾分类数据管理器"""
    
    def __init__(self, csv_file: str = None):
        """
        初始化数据管理器
        
        Args:
            csv_file: CSV文件路径，如果为None则从配置读取
        """
        if csv_file is None:
            from flask import current_app
            csv_file = current_app.config['DATA_FILE']
        
        self.csv_file = csv_file
        self.rules_dict = {}
        self.load_rules()
    
    def load_rules(self) -> None:
        """从CSV文件加载垃圾分类规则"""
        try:
            if not os.path.exists(self.csv_file):
                print(f"警告: CSV文件 {self.csv_file} 不存在，将创建空规则")
                return
            
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    item_name = row['物品名称'].strip()
                    garbage_type = row['垃圾类型'].strip()
                    reason = row['分类依据'].strip()
                    
                    self.rules_dict[item_name] = {
                        'type': garbage_type,
                        'reason': reason
                    }
            
            print(f"成功加载 {len(self.rules_dict)} 条垃圾分类规则")
            
        except Exception as e:
            print(f"加载规则时出错: {e}")
            self.rules_dict = {}
    
    def save_rules(self) -> bool:
        """将规则保存到CSV文件"""
        try:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['物品名称', '垃圾类型', '分类依据']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for item_name, rule_info in self.rules_dict.items():
                    writer.writerow({
                        '物品名称': item_name,
                        '垃圾类型': rule_info['type'],
                        '分类依据': rule_info['reason']
                    })
            
            print(f"成功保存 {len(self.rules_dict)} 条规则到文件")
            return True
            
        except Exception as e:
            print(f"保存规则时出错: {e}")
            return False
    
    def get_classification(self, item_name: str) -> Optional[Tuple[str, str]]:
        """
        获取物品的垃圾分类信息
        
        Args:
            item_name: 物品名称
            
        Returns:
            元组(垃圾类型, 分类依据) 或 None
        """
        item_name = item_name.strip()
        
        # Exact match
        if item_name in self.rules_dict:
            rule = self.rules_dict[item_name]
            return rule['type'], rule['reason']
        
        # Fuzzy match - check if contains keyword
        for stored_name, rule in self.rules_dict.items():
            if item_name in stored_name or stored_name in item_name:
                return rule['type'], f"根据相似物品'{stored_name}'分类：{rule['reason']}"
        
        return None
    
    def add_rule(self, item_name: str, garbage_type: str, reason: str) -> bool:
        """
        添加新的分类规则
        
        Args:
            item_name: 物品名称
            garbage_type: 垃圾类型
            reason: 分类依据
            
        Returns:
            操作是否成功
        """
        try:
            item_name = item_name.strip()
            garbage_type = garbage_type.strip()
            reason = reason.strip()
            
            if not all([item_name, garbage_type, reason]):
                return False
            
            self.rules_dict[item_name] = {
                'type': garbage_type,
                'reason': reason
            }
            
            return self.save_rules()
            
        except Exception as e:
            print(f"添加规则时出错: {e}")
            return False
    
    def update_rule(self, item_name: str, garbage_type: str, reason: str) -> bool:
        """
        更新现有规则
        
        Args:
            item_name: 物品名称
            garbage_type: 垃圾类型
            reason: 分类依据
            
        Returns:
            操作是否成功
        """
        return self.add_rule(item_name, garbage_type, reason)
    
    def delete_rule(self, item_name: str) -> bool:
        """
        删除规则
        
        Args:
            item_name: 物品名称
            
        Returns:
            操作是否成功
        """
        try:
            item_name = item_name.strip()
            if item_name in self.rules_dict:
                del self.rules_dict[item_name]
                return self.save_rules()
            return False
            
        except Exception as e:
            print(f"删除规则时出错: {e}")
            return False
    
    def get_all_rules(self) -> Dict[str, Dict[str, str]]:
        """获取所有规则"""
        return self.rules_dict.copy()
    
    def get_statistics(self) -> Dict[str, int]:
        """获取分类统计信息"""
        stats = {}
        for rule in self.rules_dict.values():
            garbage_type = rule['type']
            stats[garbage_type] = stats.get(garbage_type, 0) + 1
        return stats


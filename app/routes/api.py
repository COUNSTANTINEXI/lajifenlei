"""
API路由
所有RESTful API接口定义
"""

from flask import request
from flask_restful import Resource
from datetime import datetime
import logging

from app.models import GarbageDataManager, GarbageClassifier
from app.services import ImageGarbageClassifier, IMAGE_CLASSIFIER_AVAILABLE

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize data manager and classifier (singleton pattern)
data_manager = None
classifier = None
image_classifier = None


def get_data_manager():
    """Get or create data manager instance"""
    global data_manager
    if data_manager is None:
        data_manager = GarbageDataManager()
    return data_manager


def get_classifier():
    """Get or create classifier instance"""
    global classifier
    if classifier is None:
        classifier = GarbageClassifier(get_data_manager())
    return classifier


def get_image_classifier():
    """Get or create image classifier instance"""
    global image_classifier
    if IMAGE_CLASSIFIER_AVAILABLE and image_classifier is None:
        image_classifier = ImageGarbageClassifier()
    return image_classifier


class ClassifyAPI(Resource):
    """Garbage classification API"""
    
    def post(self):
        """
        垃圾分类识别
        ---
        tags:
          - 分类识别
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                item_name:
                  type: string
                  description: 物品名称
                  example: "电池"
        responses:
          200:
            description: 分类成功
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  description: 是否分类成功
                item_name:
                  type: string
                  description: 物品名称
                garbage_type:
                  type: string
                  description: 垃圾类型
                reason:
                  type: string
                  description: 分类依据
                suggestion:
                  type: string
                  description: 处理建议
                color:
                  type: string
                  description: 类型颜色
                icon:
                  type: string
                  description: 类型图标
                timestamp:
                  type: string
                  description: 分类时间
          400:
            description: 请求参数错误
        """
        try:
            data = request.get_json()
            if not data or 'item_name' not in data:
                return {'error': '请提供物品名称'}, 400
            
            item_name = data['item_name'].strip()
            if not item_name:
                return {'error': '物品名称不能为空'}, 400
            
            # Execute classification
            clf = get_classifier()
            success, garbage_type, reason, suggestion = clf.classify(item_name)
            
            # Build response
            response = {
                'success': success,
                'item_name': item_name,
                'garbage_type': garbage_type,
                'reason': reason,
                'suggestion': suggestion,
                'color': clf.get_type_color(garbage_type) if success else '#666666',
                'icon': clf.get_type_icon(garbage_type) if success else '❓',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"分类请求: {item_name} -> {garbage_type}")
            return response
            
        except Exception as e:
            logger.error(f"分类错误: {e}")
            return {'error': f'分类处理失败: {str(e)}'}, 500


class BatchClassifyAPI(Resource):
    """Batch garbage classification API"""
    
    def post(self):
        """
        批量垃圾分类识别
        ---
        tags:
          - 分类识别
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                items:
                  type: array
                  items:
                    type: string
                  description: 物品名称列表
                  example: ["电池", "纸箱", "苹果核"]
        responses:
          200:
            description: 批量分类成功
        """
        try:
            data = request.get_json()
            if not data or 'items' not in data:
                return {'error': '请提供物品列表'}, 400
            
            items = data['items']
            if not isinstance(items, list):
                return {'error': '物品列表格式错误'}, 400
            
            # Batch classification
            clf = get_classifier()
            results = clf.batch_classify(items)
            
            # Format results
            formatted_results = []
            for item_name, success, garbage_type, reason, suggestion in results:
                formatted_results.append({
                    'item_name': item_name,
                    'success': success,
                    'garbage_type': garbage_type,
                    'reason': reason,
                    'suggestion': suggestion,
                    'color': clf.get_type_color(garbage_type) if success else '#666666',
                    'icon': clf.get_type_icon(garbage_type) if success else '❓'
                })
            
            return {
                'results': formatted_results,
                'total': len(items),
                'successful': sum(1 for r in formatted_results if r['success']),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"批量分类错误: {e}")
            return {'error': f'批量分类失败: {str(e)}'}, 500


class RulesAPI(Resource):
    """Rules management API"""
    
    def get(self):
        """
        获取所有分类规则
        ---
        tags:
          - 规则管理
        responses:
          200:
            description: 获取规则成功
        """
        try:
            dm = get_data_manager()
            clf = get_classifier()
            rules = dm.get_all_rules()
            
            # Format rules data
            formatted_rules = []
            for item_name, rule_info in rules.items():
                formatted_rules.append({
                    'item_name': item_name,
                    'garbage_type': rule_info['type'],
                    'reason': rule_info['reason'],
                    'color': clf.get_type_color(rule_info['type']),
                    'icon': clf.get_type_icon(rule_info['type'])
                })
            
            return {
                'rules': formatted_rules,
                'total': len(formatted_rules)
            }
            
        except Exception as e:
            logger.error(f"获取规则错误: {e}")
            return {'error': f'获取规则失败: {str(e)}'}, 500
    
    def post(self):
        """
        添加新的分类规则
        ---
        tags:
          - 规则管理
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                item_name:
                  type: string
                  description: 物品名称
                garbage_type:
                  type: string
                  description: 垃圾类型
                reason:
                  type: string
                  description: 分类依据
        responses:
          200:
            description: 添加成功
          400:
            description: 参数错误
        """
        try:
            data = request.get_json()
            required_fields = ['item_name', 'garbage_type', 'reason']
            
            if not data or not all(field in data for field in required_fields):
                return {'error': '请提供完整的规则信息'}, 400
            
            item_name = data['item_name'].strip()
            garbage_type = data['garbage_type'].strip()
            reason = data['reason'].strip()
            
            if not all([item_name, garbage_type, reason]):
                return {'error': '所有字段都不能为空'}, 400
            
            # Validate garbage type
            valid_types = ['可回收垃圾', '有害垃圾', '厨余垃圾', '其他垃圾']
            if garbage_type not in valid_types:
                return {'error': f'垃圾类型必须是: {", ".join(valid_types)}'}, 400
            
            # Add rule
            dm = get_data_manager()
            success = dm.add_rule(item_name, garbage_type, reason)
            
            if success:
                logger.info(f"添加规则: {item_name} -> {garbage_type}")
                return {
                    'success': True,
                    'message': '规则添加成功',
                    'rule': {
                        'item_name': item_name,
                        'garbage_type': garbage_type,
                        'reason': reason
                    }
                }
            else:
                return {'error': '规则添加失败'}, 500
                
        except Exception as e:
            logger.error(f"添加规则错误: {e}")
            return {'error': f'添加规则失败: {str(e)}'}, 500
    
    def put(self):
        """
        更新分类规则
        ---
        tags:
          - 规则管理
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                item_name:
                  type: string
                  description: 物品名称
                garbage_type:
                  type: string
                  description: 垃圾类型
                reason:
                  type: string
                  description: 分类依据
        responses:
          200:
            description: 更新成功
        """
        try:
            data = request.get_json()
            required_fields = ['item_name', 'garbage_type', 'reason']
            
            if not data or not all(field in data for field in required_fields):
                return {'error': '请提供完整的规则信息'}, 400
            
            item_name = data['item_name'].strip()
            garbage_type = data['garbage_type'].strip()
            reason = data['reason'].strip()
            
            # Update rule
            dm = get_data_manager()
            success = dm.update_rule(item_name, garbage_type, reason)
            
            if success:
                logger.info(f"更新规则: {item_name} -> {garbage_type}")
                return {
                    'success': True,
                    'message': '规则更新成功'
                }
            else:
                return {'error': '规则更新失败'}, 500
                
        except Exception as e:
            logger.error(f"更新规则错误: {e}")
            return {'error': f'更新规则失败: {str(e)}'}, 500
    
    def delete(self):
        """
        删除分类规则
        ---
        tags:
          - 规则管理
        parameters:
          - name: item_name
            in: query
            type: string
            required: true
            description: 要删除的物品名称
        responses:
          200:
            description: 删除成功
        """
        try:
            item_name = request.args.get('item_name')
            if not item_name:
                return {'error': '请提供物品名称'}, 400
            
            dm = get_data_manager()
            success = dm.delete_rule(item_name.strip())
            
            if success:
                logger.info(f"删除规则: {item_name}")
                return {
                    'success': True,
                    'message': '规则删除成功'
                }
            else:
                return {'error': '规则删除失败或规则不存在'}, 400
                
        except Exception as e:
            logger.error(f"删除规则错误: {e}")
            return {'error': f'删除规则失败: {str(e)}'}, 500


class StatisticsAPI(Resource):
    """Statistics API"""
    
    def get(self):
        """
        获取统计信息
        ---
        tags:
          - 统计分析
        responses:
          200:
            description: 获取统计信息成功
        """
        try:
            dm = get_data_manager()
            clf = get_classifier()
            stats = dm.get_statistics()
            total = sum(stats.values())
            
            # Format statistics data
            formatted_stats = []
            for garbage_type, count in stats.items():
                percentage = (count / total * 100) if total > 0 else 0
                formatted_stats.append({
                    'garbage_type': garbage_type,
                    'count': count,
                    'percentage': round(percentage, 1),
                    'color': clf.get_type_color(garbage_type),
                    'icon': clf.get_type_icon(garbage_type)
                })
            
            return {
                'statistics': formatted_stats,
                'total_rules': total,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"获取统计错误: {e}")
            return {'error': f'获取统计信息失败: {str(e)}'}, 500


class SimilarItemsAPI(Resource):
    """Similar items API"""
    
    def get(self):
        """
        获取相似物品建议
        ---
        tags:
          - 智能建议
        parameters:
          - name: item_name
            in: query
            type: string
            required: true
            description: 物品名称
          - name: limit
            in: query
            type: integer
            default: 5
            description: 返回数量限制
        responses:
          200:
            description: 获取建议成功
        """
        try:
            item_name = request.args.get('item_name')
            limit = int(request.args.get('limit', 5))
            
            if not item_name:
                return {'error': '请提供物品名称'}, 400
            
            clf = get_classifier()
            similar_items = clf.get_similar_items(item_name.strip(), limit)
            
            return {
                'item_name': item_name,
                'similar_items': similar_items,
                'count': len(similar_items)
            }
            
        except Exception as e:
            logger.error(f"获取相似物品错误: {e}")
            return {'error': f'获取相似物品失败: {str(e)}'}, 500


class ImageClassifyAPI(Resource):
    """Image classification API"""
    
    def post(self):
        """
        图片垃圾分类识别
        ---
        tags:
          - 图片识别
        consumes:
          - multipart/form-data
        parameters:
          - name: image
            in: formData
            type: file
            required: true
            description: 垃圾图片文件 (支持 jpg, png, jpeg)
          - name: confidence_threshold
            in: formData
            type: number
            default: 0.1
            description: 置信度阈值 (0-1)
        responses:
          200:
            description: 识别成功
          400:
            description: 请求错误
          503:
            description: 图片识别功能不可用
        """
        try:
            # Check if image recognition is available
            if not IMAGE_CLASSIFIER_AVAILABLE:
                return {
                    'error': '图片识别功能不可用',
                    'message': '请安装依赖: pip install torch transformers pillow'
                }, 503
            
            # Check if file exists
            if 'image' not in request.files:
                return {'error': '请上传图片文件'}, 400
            
            file = request.files['image']
            
            # Check filename
            if file.filename == '':
                return {'error': '未选择文件'}, 400
            
            # Check file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            if file_ext not in allowed_extensions:
                return {
                    'error': f'不支持的文件类型: .{file_ext}',
                    'allowed_types': list(allowed_extensions)
                }, 400
            
            # Get confidence threshold
            confidence_threshold = float(request.form.get('confidence_threshold', 0.1))
            if not 0 <= confidence_threshold <= 1:
                return {'error': '置信度阈值必须在0-1之间'}, 400
            
            # Read image data
            image_data = file.read()
            
            # Check file size
            if len(image_data) == 0:
                return {'error': '图片文件为空'}, 400
            
            if len(image_data) > 16 * 1024 * 1024:  # 16MB
                return {'error': '图片文件过大，请上传小于16MB的图片'}, 400
            
            # Execute image classification
            logger.info(f"开始识别图片，文件大小: {len(image_data)} bytes")
            img_clf = get_image_classifier()
            success, garbage_type, reason, object_name, predictions = img_clf.classify_image(
                image_data, 
                confidence_threshold=confidence_threshold
            )
            
            # Get disposal suggestion
            suggestion = img_clf.get_disposal_suggestion(garbage_type) if success else ""
            
            # Build response
            clf = get_classifier()
            response = {
                'success': success,
                'object_name': object_name,
                'garbage_type': garbage_type,
                'reason': reason,
                'suggestion': suggestion,
                'color': clf.get_type_color(garbage_type) if success else '#666666',
                'icon': clf.get_type_icon(garbage_type) if success else '❓',
                'predictions': predictions,
                'confidence_threshold': confidence_threshold,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"图片识别完成: {object_name} -> {garbage_type}")
            return response
            
        except ValueError as e:
            logger.error(f"图片处理错误: {e}")
            return {'error': f'图片处理失败: {str(e)}'}, 400
        except Exception as e:
            logger.error(f"图片识别错误: {e}")
            return {'error': f'图片识别失败: {str(e)}'}, 500


class ImageStatusAPI(Resource):
    """Image recognition status API"""
    
    def get(self):
        """
        检查图片识别功能状态
        ---
        tags:
          - 图片识别
        responses:
          200:
            description: 状态信息
        """
        img_clf = get_image_classifier()
        return {
            'available': IMAGE_CLASSIFIER_AVAILABLE and img_clf is not None,
            'message': '图片识别功能可用' if IMAGE_CLASSIFIER_AVAILABLE else '图片识别功能不可用，请安装依赖',
            'required_packages': ['torch', 'transformers', 'pillow'] if not IMAGE_CLASSIFIER_AVAILABLE else [],
            'model_loaded': img_clf.model_info is not None if img_clf else False
        }


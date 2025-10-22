"""
主路由
处理主页和健康检查等基础路由
"""

from flask import send_from_directory, jsonify
from datetime import datetime
import os


def register_main_routes(app):
    """
    注册主路由
    
    Args:
        app: Flask应用实例
    """
    
    @app.route('/')
    def index():
        """Main page route, return frontend application"""
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/api/info')
    def api_info():
        """API information endpoint"""
        return jsonify({
            'name': '智能垃圾分类系统API',
            'version': '2.0.0',
            'description': '提供垃圾分类识别和规则管理的RESTful API',
            'documentation': '/apidocs/',
            'endpoints': {
                'classify': '/api/classify',
                'batch_classify': '/api/batch-classify',
                'rules': '/api/rules',
                'statistics': '/api/statistics',
                'similar_items': '/api/similar-items',
                'image_classify': '/api/classify-image',
                'image_status': '/api/image-status'
            }
        })


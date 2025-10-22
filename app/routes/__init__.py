"""
路由模块
注册所有API路由和错误处理器
"""

from flask import jsonify
from datetime import datetime


def register_routes(app, api):
    """
    注册所有路由
    
    Args:
        app: Flask应用实例
        api: Flask-RESTful API实例
    """
    from .api import (
        ClassifyAPI, BatchClassifyAPI, RulesAPI, 
        StatisticsAPI, SimilarItemsAPI, 
        ImageClassifyAPI, ImageStatusAPI
    )
    from .main import register_main_routes
    
    # Register API routes
    api.add_resource(ClassifyAPI, '/api/classify')
    api.add_resource(BatchClassifyAPI, '/api/batch-classify')
    api.add_resource(RulesAPI, '/api/rules')
    api.add_resource(StatisticsAPI, '/api/statistics')
    api.add_resource(SimilarItemsAPI, '/api/similar-items')
    api.add_resource(ImageClassifyAPI, '/api/classify-image')
    api.add_resource(ImageStatusAPI, '/api/image-status')
    
    # Register main routes
    register_main_routes(app)


def register_error_handlers(app):
    """
    注册错误处理器
    
    Args:
        app: Flask应用实例
    """
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({'error': 'API接口不存在', 'status': 404}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify({'error': '服务器内部错误', 'status': 500}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors"""
        return jsonify({'error': '请求参数错误', 'status': 400}), 400
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle 413 errors (file too large)"""
        return jsonify({'error': '上传文件过大', 'status': 413}), 413


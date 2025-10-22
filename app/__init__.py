"""
智能垃圾分类系统 - Flask应用工厂
提供RESTful API接口和Web服务
"""

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flasgger import Swagger
import os
import logging

def create_app(config_name='default'):
    """
    创建Flask应用实例
    
    Args:
        config_name: 配置名称 ('development', 'production', 'testing')
        
    Returns:
        Flask应用实例
    """
    app = Flask(__name__, 
                static_folder='static',
                static_url_path='/static')
    
    # 加载配置
    from config import config
    app.config.from_object(config[config_name])
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 启用CORS支持
    CORS(app)
    
    # 创建API实例
    api = Api(app)
    
    # 配置Swagger API文档
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }
    
    swagger_template = {
        "info": {
            "title": "智能垃圾分类系统API",
            "description": "提供垃圾分类识别和规则管理的RESTful API",
            "version": "2.0.0",
            "contact": {
                "name": "垃圾分类系统",
                "url": "https://github.com/your-repo"
            }
        },
        "schemes": ["http", "https"],
        "tags": [
            {"name": "分类识别", "description": "垃圾分类识别相关接口"},
            {"name": "规则管理", "description": "分类规则管理接口"},
            {"name": "统计分析", "description": "数据统计分析接口"},
            {"name": "图片识别", "description": "图片识别相关接口"}
        ]
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)
    
    # 注册路由
    from app.routes import register_routes
    register_routes(app, api)
    
    # 注册错误处理器
    from app.routes import register_error_handlers
    register_error_handlers(app)
    
    return app


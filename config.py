"""
配置文件
不同环境的Flask应用配置
"""

import os


class Config:
    """基础配置"""
    
    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'garbage-classification-system-2024'
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 限制上传文件大小为16MB
    
    # 数据文件路径
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_FILE = os.path.join(BASE_DIR, 'garbage_rules.csv')
    
    # JSON配置
    JSON_AS_ASCII = False  # 支持中文JSON
    JSON_SORT_KEYS = False
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        pass


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 生产环境额外配置
        import logging
        from logging.handlers import RotatingFileHandler
        
        # 配置日志文件
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/garbage_classification.log',
            maxBytes=10240000,
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('垃圾分类系统启动')


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    
    # 使用测试数据文件
    DATA_FILE = 'test_garbage_rules.csv'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


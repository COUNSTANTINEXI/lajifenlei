#!/usr/bin/env python3
"""
智能垃圾分类系统 - 启动脚本
Flask应用启动入口
"""

import os
import sys


def main():
    """主函数"""
    # Set default config
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    # Create app
    from app import create_app
    app = create_app(config_name)
    
    # Get host and port from environment or use defaults
    host = os.environ.get('FLASK_HOST', 'localhost')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = config_name == 'development'
    
    print("\n" + "="*60)
    print("🚀 智能垃圾分类系统")
    print("="*60)
    print(f"📍 运行环境: {config_name}")
    print(f"🌐 服务器地址: http://{host}:{port}")
    print(f"📋 API文档: http://{host}:{port}/apidocs/")
    print("="*60)
    print("💡 提示:")
    print("   - 按 Ctrl+C 停止服务器")
    if debug:
        print("   - 修改代码后服务器会自动重启")
    print("="*60)
    print()
    
    # Run app
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


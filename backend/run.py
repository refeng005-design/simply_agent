#!/usr/bin/env python3
"""
Simply Agent Backend - 应用启动入口

运行开发服务器:
    python run.py

运行生产服务器 (使用 gunicorn):
    gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
"""
import os
from dotenv import load_dotenv
from app import create_app

# 加载环境变量
load_dotenv()

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('API_PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'

    app.run(host='0.0.0.0', port=port, debug=debug)

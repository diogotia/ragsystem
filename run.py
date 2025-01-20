#!/usr/bin/env python3
from rag.com.app import app
from rag.com.config import SERVER_CONFIG

if __name__ == '__main__':
    app.run(
        host=SERVER_CONFIG['host'],
        port=SERVER_CONFIG['port'],
        debug=SERVER_CONFIG['debug'],
        threaded=SERVER_CONFIG['threaded']
    )

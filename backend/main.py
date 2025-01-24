from flask import Flask, request, jsonify, send_from_directory, Response
import json
from flask_cors import CORS
import os
import mysql.connector
from openai import OpenAI
import os
from dotenv import load_dotenv
from collections import defaultdict

# 数据库结构缓存
schema_cache = defaultdict(dict)

load_dotenv()

app = Flask(__name__)
CORS(app)

# 全局数据库连接对象
db_connection = None

# 数据库连接配置
db_config = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'), 
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# DeepSeek API配置
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_API_KEY = ''

@app.route('/api/db/connect', methods=['POST'])
def db_connect():
    global db_connection
    try:
        config = request.json
        db_connection = mysql.connector.connect(**config)
        return jsonify({"message": "连接成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def serve_db_config():
    return send_from_directory('../frontend', 'db-config.html')

@app.route('/api/db/dbOperateHtml', methods=['GET'])
def serve_db_operate():
    return send_from_directory('../frontend', 'db-operate.html')

@app.route('/static/<filename>', methods=['GET'])
def serve_webfont(filename):
    return send_from_directory('../frontend/static', filename)

def get_schema(database):
    """获取数据库结构"""
    if database in schema_cache:
        return schema_cache[database]
        
    cursor = None
    try:
        if not db_connection:
            return None
            
        cursor = db_connection.cursor()
        cursor.execute(f"USE {database}")

        # 获取表信息
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        schema = {}
        for table in tables:
            # 获取表结构
            cursor.execute(f"DESCRIBE {table}")
            columns = [row[0] for row in cursor.fetchall()]
            schema[table] = columns
            
        schema_cache[database] = schema
        print(f"schema: {schema}")
        return schema
        
    except Exception as e:
        print(f"获取数据库结构失败: {str(e)}")
        return None
    finally:
        if cursor:
            cursor.close()

@app.route('/api/db/generate-sql', methods=['POST'])
def generate_sql():
    try:
        data = request.json
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        current_db = data.get('database')
        schema = get_schema(current_db) if current_db else None
        
        system_prompt = f"你是一个SQL专家，根据用户需求生成MySQL操作语句。只回复可执行的SQL语句，忽略无关内容，不要其他废话,不需要格式化。"
        if current_db:
            system_prompt += f"。当前使用的数据库是：{current_db}"
            if schema:
                system_prompt += f"\n数据库结构如下：\n{schema}"
        
        def generate():
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": data['prompt']}
                ],
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield f"data: {json.dumps({'sql': chunk.choices[0].delta.content})}\n\n"
            yield 'data: [DONE]\n\n'
            
        return Response(generate(), mimetype='text/event-stream')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/db/disconnect', methods=['POST'])
def db_disconnect():
    global db_connection
    try:
        if db_connection:
            db_connection.close()
            db_connection = None
        return jsonify({"message": "断开连接成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/db/databases', methods=['GET'])
def get_databases():
    global db_connection
    try:
        if not db_connection:
            return jsonify({"error": "未连接数据库"}), 400
            
        cursor = db_connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [{"name": row[0], "tables": [], "expanded": False} for row in cursor.fetchall()]
        cursor.close()
        return jsonify(databases)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/db/tables', methods=['GET'])
def get_tables():
    global db_connection
    try:
        if not db_connection:
            return jsonify({"error": "未连接数据库"}), 400
            
        database = request.args.get('db')
        cursor = db_connection.cursor()
        cursor.execute(f"USE {database}")
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return jsonify(tables)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/db/execute', methods=['POST'])
def execute_sql():
    global db_connection
    try:
        if not db_connection:
            return jsonify({"error": "未连接数据库"}), 400
            
        sql = request.json['sql']
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute(sql)
        result = cursor.fetchall()
        
        # 获取列名
        columns = [col[0] for col in cursor.description]
        
        cursor.close()
        return {
            'type': 'query', 
            'results': result,
            'columns': columns
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 静态文件路由
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('../frontend/assets', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=33061)

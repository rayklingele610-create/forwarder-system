import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid

app = Flask(__name__, static_folder='static')
CORS(app)

# 从环境变量获取 Neon 连接字符串
DATABASE_URL = os.environ.get('DATABASE_URL')

# 文件上传目录（Railway Volume 挂载路径）
UPLOAD_FOLDER = '/app/static/uploads'


def get_conn():
    """获取数据库连接"""
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """初始化数据库表结构"""
    conn = get_conn()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS forwarders (
            id SERIAL PRIMARY KEY,
            company_name TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            wechat TEXT,
            qrcode_image TEXT,
            countries TEXT,
            transport_modes TEXT,
            service_types TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS tag_options (
            id SERIAL PRIMARY KEY,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0
        )
    ''')

    # 检查是否已有 forwarders 数据
    c.execute('SELECT COUNT(*) FROM forwarders')
    count = c.fetchone()[0]

    if count == 0:
        # 插入示例数据
        sample_data = [
            {
                'company_name': '美线国际物流',
                'contact_person': '张经理',
                'phone': '13800138001',
                'wechat': 'meixian_express',
                'qrcode_image': '',
                'countries': json.dumps(['美国', '加拿大']),
                'transport_modes': json.dumps(['海运', '空运']),
                'service_types': json.dumps(['FOB', 'DDP', '到门']),
                'notes': '专注美线10年，时效稳定'
            },
            {
                'company_name': '欧亚速递',
                'contact_person': '李小姐',
                'phone': '13900139002',
                'wechat': 'europe_express',
                'qrcode_image': '',
                'countries': json.dumps(['德国', '法国', '英国', '意大利']),
                'transport_modes': json.dumps(['空运', '铁路']),
                'service_types': json.dumps(['DDP', 'DDU', '到门']),
                'notes': '欧洲专线，清关能力强'
            },
            {
                'company_name': '日韩通物流',
                'contact_person': '王先生',
                'phone': '13700137003',
                'wechat': 'japan_korea_logistics',
                'qrcode_image': '',
                'countries': json.dumps(['日本', '韩国']),
                'transport_modes': json.dumps(['海运', '空运']),
                'service_types': json.dumps(['FOB', '到门']),
                'notes': '日韩专线，价格优势明显'
            },
            {
                'company_name': '东南亚快运',
                'contact_person': '陈经理',
                'phone': '13600136004',
                'wechat': 'sea_express',
                'qrcode_image': '',
                'countries': json.dumps(['越南', '泰国', '马来西亚', '新加坡']),
                'transport_modes': json.dumps(['海运']),
                'service_types': json.dumps(['FOB', 'DDP']),
                'notes': '东南亚专线，海运为主'
            },
            {
                'company_name': '全球空运专家',
                'contact_person': '赵总',
                'phone': '13500135005',
                'wechat': 'global_air',
                'qrcode_image': '',
                'countries': json.dumps(['美国', '欧洲', '日本', '澳大利亚']),
                'transport_modes': json.dumps(['空运']),
                'service_types': json.dumps(['DDP', '到门']),
                'notes': '紧急空运，时效保证'
            }
        ]

        for data in sample_data:
            c.execute('''
                INSERT INTO forwarders
                (company_name, contact_person, phone, wechat, qrcode_image,
                 countries, transport_modes, service_types, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                data['company_name'], data['contact_person'], data['phone'],
                data['wechat'], data['qrcode_image'], data['countries'],
                data['transport_modes'], data['service_types'], data['notes']
            ))

    # 迁移：如果 tag_options 为空但 forwarders 有数据，则从 forwarders 去重迁移
    c.execute('SELECT COUNT(*) FROM tag_options')
    tag_count = c.fetchone()[0]
    if tag_count == 0:
        c.execute('SELECT COUNT(*) FROM forwarders')
        fwd_count = c.fetchone()[0]
        if fwd_count > 0:
            c.execute('SELECT countries, transport_modes, service_types FROM forwarders')
            rows = c.fetchall()
            all_countries = set()
            all_transport = set()
            all_services = set()
            for row in rows:
                all_countries.update(json.loads(row[0]))
                all_transport.update(json.loads(row[1]))
                all_services.update(json.loads(row[2]))
            for i, name in enumerate(sorted(all_countries)):
                c.execute('INSERT INTO tag_options (category, name, sort_order) VALUES (%s, %s, %s)',
                          ('country', name, i))
            for i, name in enumerate(sorted(all_transport)):
                c.execute('INSERT INTO tag_options (category, name, sort_order) VALUES (%s, %s, %s)',
                          ('transport_mode', name, i))
            for i, name in enumerate(sorted(all_services)):
                c.execute('INSERT INTO tag_options (category, name, sort_order) VALUES (%s, %s, %s)',
                          ('service_type', name, i))

    conn.commit()
    conn.close()


@app.route('/')
def index():
    """返回前端页面"""
    return send_from_directory('.', 'index.html')


@app.route('/api/forwarders', methods=['GET'])
def get_forwarders():
    """获取所有货代公司（支持搜索和筛选）"""
    search = request.args.get('search', '')
    countries = request.args.getlist('countries[]')
    transport_modes = request.args.getlist('transport_modes[]')
    service_types = request.args.getlist('service_types[]')

    conn = get_conn()
    c = conn.cursor(cursor_factory=RealDictCursor)

    query = 'SELECT * FROM forwarders WHERE 1=1'
    params = []

    if search:
        query += ' AND (company_name LIKE %s OR contact_person LIKE %s OR phone LIKE %s OR wechat LIKE %s)'
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'])

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    forwarders = []
    for row in rows:
        forwarder = dict(row)
        forwarder['countries'] = json.loads(forwarder['countries'])
        forwarder['transport_modes'] = json.loads(forwarder['transport_modes'])
        forwarder['service_types'] = json.loads(forwarder['service_types'])

        if countries and not any(country in forwarder['countries'] for country in countries):
            continue
        if transport_modes and not any(mode in forwarder['transport_modes'] for mode in transport_modes):
            continue
        if service_types and not any(service in forwarder['service_types'] for service in service_types):
            continue

        forwarders.append(forwarder)

    return jsonify(forwarders)


@app.route('/api/forwarders/<int:forwarder_id>', methods=['GET'])
def get_forwarder(forwarder_id):
    """获取单个货代公司"""
    conn = get_conn()
    c = conn.cursor(cursor_factory=RealDictCursor)
    c.execute('SELECT * FROM forwarders WHERE id = %s', (forwarder_id,))
    row = c.fetchone()
    conn.close()

    if row:
        forwarder = dict(row)
        forwarder['countries'] = json.loads(forwarder['countries'])
        forwarder['transport_modes'] = json.loads(forwarder['transport_modes'])
        forwarder['service_types'] = json.loads(forwarder['service_types'])
        return jsonify(forwarder)
    return jsonify({'error': 'Not found'}), 404


@app.route('/api/forwarders', methods=['POST'])
def create_forwarder():
    """创建新货代公司"""
    data = request.json

    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO forwarders
        (company_name, contact_person, phone, wechat, qrcode_image,
         countries, transport_modes, service_types, notes, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (
        data['company_name'],
        data.get('contact_person', ''),
        data.get('phone', ''),
        data.get('wechat', ''),
        data.get('qrcode_image', ''),
        json.dumps(data.get('countries', [])),
        json.dumps(data.get('transport_modes', [])),
        json.dumps(data.get('service_types', [])),
        data.get('notes', ''),
        datetime.now().isoformat()
    ))

    forwarder_id = c.fetchone()[0]
    conn.commit()
    conn.close()

    return jsonify({'id': forwarder_id, 'message': 'Created successfully'}), 201


@app.route('/api/forwarders/<int:forwarder_id>', methods=['PUT'])
def update_forwarder(forwarder_id):
    """更新货代公司"""
    data = request.json

    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        UPDATE forwarders
        SET company_name = %s, contact_person = %s, phone = %s, wechat = %s,
            qrcode_image = %s, countries = %s, transport_modes = %s,
            service_types = %s, notes = %s, updated_at = %s
        WHERE id = %s
    ''', (
        data['company_name'],
        data.get('contact_person', ''),
        data.get('phone', ''),
        data.get('wechat', ''),
        data.get('qrcode_image', ''),
        json.dumps(data.get('countries', [])),
        json.dumps(data.get('transport_modes', [])),
        json.dumps(data.get('service_types', [])),
        data.get('notes', ''),
        datetime.now().isoformat(),
        forwarder_id
    ))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Updated successfully'})


@app.route('/api/forwarders/<int:forwarder_id>', methods=['DELETE'])
def delete_forwarder(forwarder_id):
    """删除货代公司"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM forwarders WHERE id = %s', (forwarder_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Deleted successfully'})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传图片（二维码）"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = f"{uuid.uuid4().hex}_{file.filename}"
    # 优先使用 Railway Volume 路径，本地回退到 static/uploads
    upload_dir = UPLOAD_FOLDER if os.path.exists('/app') else os.path.join(app.static_folder, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    return jsonify({'url': f'/static/uploads/{filename}'})


@app.route('/api/filters', methods=['GET'])
def get_filters():
    """获取所有可用的筛选标签"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT category, name FROM tag_options ORDER BY sort_order, name")
    rows = c.fetchall()
    conn.close()

    countries = []
    transport_modes = []
    service_types = []

    for row in rows:
        category, name = row
        if category == 'country':
            countries.append(name)
        elif category == 'transport_mode':
            transport_modes.append(name)
        elif category == 'service_type':
            service_types.append(name)

    return jsonify({
        'countries': countries,
        'transport_modes': transport_modes,
        'service_types': service_types
    })


@app.route('/api/tag-options', methods=['GET'])
def get_tag_options():
    """获取所有标签选项（按 category 分组）"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM tag_options ORDER BY category, sort_order, name")
    rows = c.fetchall()
    conn.close()

    options = []
    for row in rows:
        options.append({
            'id': row[0],
            'category': row[1],
            'name': row[2],
            'sort_order': row[3]
        })

    return jsonify({'options': options})


@app.route('/api/tag-options', methods=['POST'])
def create_tag_option():
    """新增一个标签选项"""
    data = request.json
    category = data.get('category')
    name = data.get('name')

    if not category or not name:
        return jsonify({'error': 'category and name are required'}), 400

    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM tag_options WHERE category = %s AND name = %s", (category, name))
    if c.fetchone():
        conn.close()
        return jsonify({'error': 'Tag already exists'}), 409

    c.execute("SELECT MAX(sort_order) FROM tag_options WHERE category = %s", (category,))
    max_order = c.fetchone()[0] or 0

    c.execute("INSERT INTO tag_options (category, name, sort_order) VALUES (%s, %s, %s) RETURNING id",
              (category, name, max_order + 1))
    tag_id = c.fetchone()[0]
    conn.commit()
    conn.close()

    return jsonify({'id': tag_id, 'message': 'Created successfully'}), 201


@app.route('/api/tag-options/<int:tag_id>', methods=['PUT'])
def update_tag_option(tag_id):
    """编辑标签名称"""
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'error': 'name is required'}), 400

    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE tag_options SET name = %s WHERE id = %s", (name, tag_id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Updated successfully'})


@app.route('/api/tag-options/<int:tag_id>', methods=['DELETE'])
def delete_tag_option(tag_id):
    """删除标签选项"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM tag_options WHERE id = %s", (tag_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Deleted successfully'})


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print(f"数据库初始化完成，访问地址: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)

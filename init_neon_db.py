"""
一键初始化 Neon PostgreSQL 数据库表结构
运行方式：DATABASE_URL=你的连接字符串 python init_neon_db.py
"""
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL', '')

if not DATABASE_URL:
    print("错误：请设置 DATABASE_URL 环境变量")
    print("示例：set DATABASE_URL=postgresql://xxx:xxx@xxx.neon.tech/neondb?sslmode=require")
    exit(1)

print("正在连接 Neon 数据库...")
conn = psycopg2.connect(DATABASE_URL)
c = conn.cursor()

print("正在创建 forwarders 表...")
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

print("正在创建 tag_options 表...")
c.execute('''
    CREATE TABLE IF NOT EXISTS tag_options (
        id SERIAL PRIMARY KEY,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        sort_order INTEGER DEFAULT 0
    )
''')

conn.commit()
conn.close()
print("数据库初始化成功！两张表已创建完毕。")
print("现在可以部署到 Railway，首次启动会自动插入示例数据。")

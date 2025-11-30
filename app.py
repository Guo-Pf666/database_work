# ==============================================================================
# Flask 应用主文件 (app.py)
# 整合所有模块，处理 Web 路由和业务逻辑。
# ==============================================================================
from flask import Flask, render_template, request, redirect, url_for, session
from admin_schema import ADMIN_TABLE_CONFIG
from typing import List, Dict, Any, Optional
import markdown

# 导入所有自定义模块
from config import MASTER_DB_CONFIG, TARGET_DB_NAME, ALLOWED_ROLES
from database import Database
from auth import AuthManager
from permission import PermissionChecker
from llm import LLMClient

app = Flask(__name__)
# 确保设置一个安全的密钥用于session管理
app.secret_key = 'super_secret_key_for_session' 

# 初始化 LLM 客户端和用户表
llm_client = LLMClient()
AuthManager.initialize_user_table() # 启动时确保用户表存在

# ==============================================================================
# 路由定义
# ==============================================================================

@app.route('/admin', methods=['GET'])
def admin_panel():
    """管理后台主页：显示表单和当前数据列表。"""
    # 1. 权限检查：只有 admin 可以进入
    if 'logged_in' not in session or session.get('role') != 'admin':
        return render_template('login.html', error="权限拒绝：只有管理员可以访问后台管理系统。")

    # 2. 获取当前选中的表，默认为 'Enterprises'
    current_table = request.args.get('table', 'Enterprises')
    if current_table not in ADMIN_TABLE_CONFIG:
        current_table = 'Enterprises'
        
    table_config = ADMIN_TABLE_CONFIG[current_table]
    
    # 3. 获取该表的现有数据 (用于展示和删除)
    db = None
    table_data = []
    error = None
    try:
        db = Database()
        # 简单查询前50条数据用于展示
        pk = table_config['pk']
        sql = f"SELECT * FROM {current_table} ORDER BY {pk} DESC LIMIT 50"
        table_data = db.execute_query(sql)
    except Exception as e:
        error = f"读取数据失败: {e}"
    finally:
        if db: db.close()

    return render_template('admin.html', 
                           tables=ADMIN_TABLE_CONFIG, 
                           current_table=current_table,
                           current_config=table_config,
                           data=table_data,
                           username=session.get('username'),
                           error=error)

@app.route('/admin/operate', methods=['POST'])
def admin_operate():
    """处理增删改操作。"""
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    action = request.form.get('action')
    table_name = request.form.get('table_name')
    
    if table_name not in ADMIN_TABLE_CONFIG:
        return "Invalid Table", 400
        
    config = ADMIN_TABLE_CONFIG[table_name]
    db = None
    
    try:
        db = Database()
        
        # --- 处理添加 (INSERT) ---
        if action == 'add':
            cols = []
            vals = []
            placeholders = []
            
            for col in config['columns']:
                field_name = col['name']
                user_input = request.form.get(field_name)
                
                # 如果用户填了值，则加入 SQL
                if user_input is not None and user_input.strip() != '':
                    cols.append(field_name)
                    vals.append(user_input)
                    placeholders.append('%s')
            
            if not cols:
                raise ValueError("未提交任何数据。")

            sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
            db.execute_non_query(sql, tuple(vals))
            session['reg_success_msg'] = "数据添加成功！" # 借用这个 session key 显示提示
            
        # --- 处理删除 (DELETE) ---
        elif action == 'delete':
            pk_name = config['pk']
            pk_val = request.form.get('pk_val')
            
            if not pk_val:
                raise ValueError("未提供主键ID。")
                
            sql = f"DELETE FROM {table_name} WHERE {pk_name} = %s"
            db.execute_non_query(sql, (pk_val,))
            session['reg_success_msg'] = f"ID为 {pk_val} 的记录已删除。"

    except Exception as e:
        session['reg_success_msg'] = f"操作失败: {e}" # 借用 key 传递错误信息
    finally:
        if db: db.close()
        
    return redirect(url_for('admin_panel', table=table_name))

@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录界面"""
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('chat'))

    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_data = AuthManager.login_user(username, password)
        
        if user_data:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user_data['role']
            # 修改：不再存储 session['region']
            session['role_display'] = ALLOWED_ROLES.get(user_data['role'], '未知角色')
            
            return redirect(url_for('chat'))
        else:
            error = '无效的用户名或密码 (身份验证失败)。'
            
    message = session.pop('reg_success_msg', None)
    return render_template('login.html', error=error, message=message, roles=ALLOWED_ROLES)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        # 修改：不再获取 region

        try:
            # 修改：调用时不传 region
            AuthManager.register_user(username, password, role)
            session['reg_success_msg'] = f"用户 '{username}' 注册成功，角色: {ALLOWED_ROLES.get(role, '未知')}"
            return redirect(url_for('login'))
        except ValueError as e:
            error = str(e)
        except RuntimeError as e:
            error = f"数据库操作失败: {e}"

    return render_template('register.html', error=error, roles=ALLOWED_ROLES, target_db=TARGET_DB_NAME)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """主对话界面"""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    username = session.get('username')
    role = session.get('role')
    role_display = session.get('role_display')
    # 修改：不再获取 region
    
    user_query = ""
    db_result: Optional[List[Dict[str, Any]]] = None
    sql_statement = ""
    error_message = None
    report = None
    report_html = ""

    if request.method == 'POST':
        user_query = request.form.get('query')
        
        if user_query:
            db = None
            try:
                # 1. LLM 生成 SQL (不再需要地区上下文)
                sql_statement = llm_client.generate_sql(user_query)
                
                # 2. 权限检查 (修改：移除了 region 参数)
                permission_status = PermissionChecker.check_permission(role, sql_statement)
                
                if permission_status != "OK":
                    error_message = permission_status
                    report = f"对不起，您的角色（{role_display}）权限不足。{permission_status}"
                else:
                    # 3. 执行 SQL
                    db = Database()
                    if sql_statement.upper().startswith("SELECT"):
                        db_result = db.execute_query(sql_statement)
                    else:
                        rows_affected = db.execute_non_query(sql_statement)
                        db_result = [{'status': f'操作成功', 'rows_affected': rows_affected}]
                    
                    # 4. 生成报告 (传入 role_display)
                    report = llm_client.generate_report(user_query, sql_statement, db_result or [], role_display)
                    
                    if report and not error_message:
                        report_html = markdown.markdown(report)
                    else:
                        report_html = report
                    
            except Exception as e:
                error_message = f"系统错误：{e}"
                report = f"发生意外错误：{e}"
            finally:
                if db: db.close()
        
    return render_template('chat.html', 
                           username=username,
                           role=role_display,
                           # region=region, # 已删除
                           user_query=user_query,
                           sql_statement=sql_statement,
                           db_result=db_result,
                           error_message=error_message,
                           report=report_html)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
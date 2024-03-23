from flask import Flask, request, jsonify, render_template

from tools.database.sqlite_connect import *

app = Flask(__name__)

# 数据库文件路径
DB_PATH = 'data_storage.db'


# 显示所有项目
@app.route('/')
def show_projects():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM project')
        projects = cursor.fetchall()

    return render_template('index.html', projects=projects)


# 添加项目
@app.route('/add_project', methods=['POST'])
def add_project():
    if request.method == 'POST':
        project_name = request.form.get('name')

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO project (name) VALUES (?)', (project_name,))
            conn.commit()

    return show_projects()



if __name__ == '__main__':
    app.run(debug=True)

import sqlite3

import pandas as pd
import streamlit as st

# 连接到 SQLite 数据库
conn = sqlite3.connect('/data_storage.db')
c = conn.cursor()


# 增加数据
def add_data(name, age):
    c.execute('''INSERT INTO ui_element (ele_name, nth) VALUES (?, ?)''', (name, age))
    conn.commit()


# 删除数据
def delete_data(user_id):
    c.execute('''DELETE FROM ui_element WHERE id = ?''', (user_id,))
    conn.commit()


# 查询数据
def get_data():
    c.execute('''SELECT * FROM ui_element''')
    return c.fetchall()


# Streamlit 应用
st.title('SQLite 数据库操作示例')

# 添加数据
name = st.text_input('请输入姓名')
age = st.number_input('请输入年龄', min_value=0)
if st.button('添加数据'):
    add_data(name, age)

# 删除数据
delete_id = st.number_input('请输入要删除的用户 ID', min_value=1)
if st.button('删除数据'):
    delete_data(delete_id)

# 展示数据
st.write('当前数据库中的数据：')
df = pd.DataFrame(get_data(), columns=[i[0] for i in c.description])

# 显示DataFrame作为表格
st.write(df)

# 删除按钮
if st.button('删除选定行'):
    selected_index = st.multiselect("选择要删除的行的索引", df.index)
    for index in selected_index:
        delete_data(df.iloc[index]['id'])

# 关闭数据库连接
conn.close()

# streamlit run D:\GitCode\PytestAutoTest\cache\edit_data.py

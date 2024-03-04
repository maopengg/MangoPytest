# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-03-04 11:41
# @Author : 毛鹏
import streamlit as st
import pandas as pd

# 创建示例数据
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35]
}
df = pd.DataFrame(data)

# Streamlit 应用
st.title('Pandas 数据操作示例')

# 展示数据
st.write('当前表格数据：')
st.write(df)

# 添加数据
st.subheader('添加数据')
new_name = st.text_input('姓名')
new_age = st.number_input('年龄', min_value=0)
if st.button('添加'):
    new_row = {'Name': new_name, 'Age': new_age}
    df = df.append(new_row, ignore_index=True)
    st.write('添加后的数据：')
    st.write(df)

# 删除数据
st.subheader('删除数据')
delete_index = st.number_input('要删除的行索引', min_value=0, max_value=len(df)-1)
if st.button('删除'):
    df = df.drop(delete_index).reset_index(drop=True)
    st.write('删除后的数据：')
    st.write(df)

# 更新数据
st.subheader('更新数据')
update_index = st.number_input('要更新的行索引', min_value=0, max_value=len(df)-1)
update_name = st.text_input('更新后的姓名', value=df.loc[update_index, 'Name'])
update_age = st.number_input('更新后的年龄', value=df.loc[update_index, 'Age'], min_value=0)
if st.button('更新'):
    df.loc[update_index] = [update_name, update_age]
    st.write('更新后的数据：')
    st.write(df)

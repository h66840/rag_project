import pandas as pd
import mysql.connector
import xlrd
# 读取 XLS 文件
try:
    
    # 读取 XLS 文件
    excel_file = pd.ExcelFile('project/table/002180_main_year.xls')
    sheet_names = excel_file.sheet_names
    # for i in range(nrows):
    #     for j in range(ncols):
    #         print(table.cell(i,j).value)

    
except FileNotFoundError:
    print("文件不存在")
    exit()
sheet_names = excel_file.sheet_names
print(sheet_names)
# 连接到 MySQL 数据库
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="200220lhy",
    database="chikawaka"
)
mycursor = mydb.cursor()

# 遍历每个工作表
for sheet_name in sheet_names:
    df = excel_file.parse(sheet_name)
    df = df.T
    
        # 插入数据
        # placeholders = ', '.join(['%s'] * len(row))
        # insert_query = f"INSERT INTO {sheet_name} VALUES ({placeholders})"
        # mycursor.execute(insert_query, tuple(row))
    
    
    # print(df)
    # 创建表名，这里简单使用工作表名作为表名
    table_name = "shujubiao"
    for i in range(len(df.columns)):
        print(df.columns[i])
    # 创建表
    columns = ", ".join([f"`{col}` TEXT" for col in df.columns])
    print(columns)
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
    mycursor.execute(create_table_query)

    # 插入数据
    placeholders = ', '.join(['%s'] * len(df.columns))
    insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
    for row in df.values.tolist():
        mycursor.execute(insert_query, row)

# 提交更改并关闭连接
mydb.commit()
mycursor.close()
mydb.close()
# import chardet
# import pandas as pd
# def get_encoding(file):
#     with open(file,'rb') as f:
#         return chardet.detect(f.read(1024))['encoding']

# if __name__ == '__main__':
    
#     fullPath = "project/table/002180_main_year.xls"
#     encoding = get_encoding(fullPath)
#     print(encoding)
#     data = pd.read_csv(fullPath, encoding = encoding)
#     print(data.head(2))
import pandas as pd

# 若文件编码为 GBK，需要指定编码
data = pd.ExcelFile('project/table/002180_main_year.xls')





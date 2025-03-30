import PyPDF2

# 打开 PDF 文件
pdf_file = open('project/data/1.pdf', 'rb')

# 创建 PDF 阅读器对象
pdf_reader = PyPDF2.PdfReader(pdf_file)

# 获取 PDF 文件的页数
num_pages = len(pdf_reader.pages)

# 逐页读取 PDF 文件内容
for page_num in range(num_pages):
    page = pdf_reader.pages[page_num]
    text = page.extract_text()
    print(text)

# 关闭 PDF 文件
pdf_file.close()
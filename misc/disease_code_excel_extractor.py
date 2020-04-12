# 从疾病编码的excel文件中提取数据

from openpyxl import Workbook
from openpyxl import load_workbook
import json

# 载入工作表
source_data = load_workbook('../source_data/disease_code.xlsx')
print('载入完成')
sheet = source_data.get_sheet_by_name('Sheet1')

# 指定表格数据读取范围
disease_code_range = sheet['A3':'A32199']
disease_name_range = sheet['B3':'B32199']
# 读取数据
disease_code_list = list()
disease_name_list = list()
for row_of_cell in disease_code_range:
    for cell in row_of_cell:
        disease_code_list.append(cell.value)
for row_of_cell in disease_name_range:
    for cell in row_of_cell:
        disease_name_list.append(cell.value)

# 存入JSON
# 如果有编码对应的是空格值就舍弃
disease_to_code_dict = dict()
for i in range(len(disease_name_list)):
    code = disease_code_list[i]
    name = disease_name_list[i]
    if code != '' and code is not None:
        disease_to_code_dict[name] = code
        print((name + ': ' + code).encode('gbk', 'ignore').decode('gbk'))

with open('disease_code.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(disease_to_code_dict, ensure_ascii=False, indent=4))



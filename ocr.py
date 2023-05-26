'''
Author: Derry
Date: 2023-05-26 14:49:43
LastEditors: Derry
Email: drlv@mail.ustc.edu.cn
LastEditTime: 2023-05-26 20:19:55
FilePath: /OCR/ocr.py
Description: None
'''

import PyPDF2
from tqdm import tqdm


import json
import os


def gen_ocrmypdf(sh_file, pdf_names=None, input_dir='input', output_dir='output', lang='chi_sim'):
    output_txt_dir = f"{output_dir}_txt"
    commands = []
    print(len(os.listdir(input_dir)))
    for infile in os.listdir(input_dir):
        if pdf_names and infile not in pdf_names:
            continue
        input_path = os.path.join(input_dir, infile)
        output_path = os.path.join(output_dir, infile)
        output_txt_path = os.path.join(
            output_txt_dir, infile.replace('.pdf', '.txt'))
        command = f'ocrmypdf --redo-ocr -l {lang} --sidecar "{output_txt_path}" "{input_path}" "{output_path}"'
        commands.append(command)
    with open(sh_file, 'w') as f:
        f.write('\n'.join(commands))


def file_filter(info_path="standard_info.json", department_name="住房和城乡建设部"):
    with open(info_path, 'r', encoding='utf-8') as f:
        standard_info = json.load(f)
    pdf_names = []
    for standard in standard_info:
        if standard["基础信息"]["批准发布部门"] == department_name:
            pdf_names.append(standard['pdf_name'])
    pdf_names = set(pdf_names)
    print(f"筛选出{len(pdf_names)}/{len(standard_info)}个pdf文件")
    return pdf_names


def pdf2txt(pdf_names=None, input_dir='input', output_dir='output_txt'):
    no_ocr_pdf_names = []
    for infile in tqdm(os.listdir(input_dir)):
        if pdf_names and infile not in pdf_names:
            continue
        input_path = os.path.join(input_dir, infile)
        output_path = os.path.join(output_dir, infile.replace('.pdf', '.txt'))
        with open(input_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)  # 创建PDF阅读器对象
            num_pages = len(pdf_reader.pages)  # 获取PDF中的页数
            text = ""
            for page in range(num_pages):
                pdf_page = pdf_reader.pages[page]  # 获取当前页
                page_text = pdf_page.extract_text()  # 提取当前页的文本
                text += page_text  # 将提取的文本添加到字符串中
        if len(text) < 100:
            no_ocr_pdf_names.append(infile)
        else:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(text)
    ocr_num = len(pdf_names)-len(no_ocr_pdf_names)
    no_ocr_num = len(no_ocr_pdf_names)
    print(f"OCR{ocr_num}) vs. no OCR ({no_ocr_num}) / total({len(pdf_names)})")
    return no_ocr_pdf_names


pdf_names = file_filter()
no_ocr_pdf_names = pdf2txt(pdf_names)
gen_ocrmypdf("OCR.sh", pdf_names=no_ocr_pdf_names)

os.system("sh OCR.sh")

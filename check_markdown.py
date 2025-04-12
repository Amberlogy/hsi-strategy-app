"""
簡單的 Markdown 格式檢查腳本
"""

import re
import sys

def check_blanks_around_headings(text):
    """檢查標題前後是否有空行"""
    lines = text.splitlines()
    errors = []
    
    for i, line in enumerate(lines):
        if line.startswith('#'):
            # 檢查標題前是否有空行 (除非是第一行)
            if i > 0 and lines[i-1].strip() != '':
                errors.append(f"行 {i+1}: 標題前應有空行")
            
            # 檢查標題後是否有空行 (除非是最後一行)
            if i < len(lines) - 1 and lines[i+1].strip() != '':
                errors.append(f"行 {i+1}: 標題後應有空行")
    
    return errors

def check_blanks_around_lists(text):
    """檢查列表前後是否有空行"""
    lines = text.splitlines()
    errors = []
    in_list = False
    
    for i, line in enumerate(lines):
        is_list_item = re.match(r'^\s*(-|\*|\d+\.)\s', line)
        
        # 列表開始
        if not in_list and is_list_item:
            in_list = True
            # 檢查列表前是否有空行 (除非是第一行)
            if i > 0 and lines[i-1].strip() != '':
                errors.append(f"行 {i+1}: 列表前應有空行")
        
        # 列表結束
        elif in_list and not is_list_item and line.strip() != '':
            in_list = False
            # 檢查列表後是否有空行
            if i > 0 and lines[i-1].strip() != '' and is_list_item:
                errors.append(f"行 {i+1}: 列表後應有空行")
    
    return errors

def check_blanks_around_fences(text):
    """檢查代碼塊前後是否有空行"""
    lines = text.splitlines()
    errors = []
    in_code_block = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            if not in_code_block:  # 代碼塊開始
                in_code_block = True
                # 檢查代碼塊前是否有空行 (除非是第一行)
                if i > 0 and lines[i-1].strip() != '':
                    errors.append(f"行 {i+1}: 代碼塊前應有空行")
            else:  # 代碼塊結束
                in_code_block = False
                # 檢查代碼塊後是否有空行 (除非是最後一行)
                if i < len(lines) - 1 and lines[i+1].strip() != '':
                    errors.append(f"行 {i+1}: 代碼塊後應有空行")
    
    return errors

def check_code_language(text):
    """檢查代碼塊是否指定語言"""
    # 修改正則表達式，只匹配代碼塊的開始標記，例如 ```，但不匹配 ```txt 或 ```bash
    pattern = r'^```\s*$'
    line_num = 1
    errors = []
    in_code_block = False
    
    for line in text.splitlines():
        # 如果是代碼塊的開始並且沒有指定語言
        if not in_code_block and re.match(pattern, line):
            errors.append(f"行 {line_num}: 代碼塊未指定語言")
            in_code_block = True
        # 如果是代碼塊的開始並且有指定語言
        elif not in_code_block and line.startswith('```'):
            in_code_block = True
        # 如果是代碼塊的結束
        elif in_code_block and line.strip() == '```':
            in_code_block = False
        
        line_num += 1
    
    return errors

def check_trailing_spaces(text):
    """檢查行尾是否有多餘空格"""
    lines = text.splitlines()
    errors = []
    
    for i, line in enumerate(lines):
        if line.rstrip() != line:
            errors.append(f"行 {i+1}: 行尾有多餘空格")
    
    return errors

def check_bare_urls(text):
    """檢查URL是否被包圍"""
    lines = text.splitlines()
    errors = []
    
    # 修正后的URL检测规则，直接检查未被<>包围的URL
    pattern = r'(?<!<)http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+(?!>)'
    
    for i, line in enumerate(lines):
        if "http" in line:
            # 检查行是否包含未被<>包围的URL
            if re.search(pattern, line):
                # 排除Markdown链接中的URL
                markdown_link_pattern = r'\[.+?\]\((http[s]?://[^)]+)\)'
                markdown_links = re.findall(markdown_link_pattern, line)
                
                # 查找所有未被<>包围且不在Markdown链接中的URL
                for match in re.finditer(pattern, line):
                    url = match.group(0)
                    is_in_markdown_link = False
                    
                    for link_url in markdown_links:
                        if url in link_url:
                            is_in_markdown_link = True
                            break
                    
                    if not is_in_markdown_link:
                        errors.append(f"行 {i+1}: URL未被<>包圍")
    
    return errors

def check_markdown_file(file_path):
    """檢查Markdown文件的格式"""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    all_errors = []
    all_errors.extend(check_blanks_around_headings(text))
    all_errors.extend(check_blanks_around_lists(text))
    all_errors.extend(check_blanks_around_fences(text))
    all_errors.extend(check_code_language(text))
    all_errors.extend(check_trailing_spaces(text))
    all_errors.extend(check_bare_urls(text))
    
    return all_errors

if __name__ == "__main__":
    file_path = "README.md"
    errors = check_markdown_file(file_path)
    
    if errors:
        print(f"發現 {len(errors)} 個問題:")
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("未發現Markdown格式問題")
        sys.exit(0) 
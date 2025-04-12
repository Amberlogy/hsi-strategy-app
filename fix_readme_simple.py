with open('README.md', 'rb') as f:
    content = f.read()

# 嘗試使用 iso-8859-1 編碼讀取
content_text = content.decode('iso-8859-1')

# 寫入新文件並編碼為 UTF-8
with open('README_fixed.md', 'w', encoding='utf-8') as f:
    f.write(content_text)

print("已創建修復後的文件 README_fixed.md") 
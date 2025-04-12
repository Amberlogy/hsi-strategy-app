import io

# 讀取原始二進制數據
with open('README.md', 'rb') as f:
    binary_data = f.read()

# 嘗試不同的編碼讀取
encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'gb18030', 'big5', 'iso-8859-1']
content = None

for enc in encodings:
    try:
        content = binary_data.decode(enc)
        print(f"成功使用 {enc} 編碼讀取文件")
        break
    except UnicodeDecodeError:
        continue

if content is None:
    print("無法以任何編碼讀取文件")
    exit(1)

# 寫入新文件
with open('README_fixed.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("已創建修復後的文件 README_fixed.md") 
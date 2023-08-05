import re
import csv

with open('en_US.ts', 'r', encoding='utf-8') as f:
    text = f.read()

ret = re.findall(r'<source>(.*)</source>', text)
print(ret)

with open('midtool 待翻译文本.csv', 'w', newline='', encoding='gbk') as f:
    writer = csv.writer(f)
    for i in ret:
        i = [i]
        writer.writerow(i)

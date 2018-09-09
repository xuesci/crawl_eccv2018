#conding:utf-8
import os
import re
import lxml
import xlwt
import requests
from xlwt import Workbook
from bs4 import BeautifulSoup as bs

headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
print("***********************start*********************")
link = "http://openaccess.thecvf.com/ECCV2018.py"
res = requests.get(link, headers=headers)
soup = bs(res.text, "lxml")
paper_titles = soup.find_all("dt", class_="ptitle")
paper_urls = soup.find_all("a", text="pdf")

# 获取文章文件，并保存在"ECCV2018_PAPERS"目录下
def get_papers(paper_title, paper_url):
    relative_url = paper_url['href']
    root_url = "http://openaccess.thecvf.com/"
    abs_url = root_url + relative_url  # 获取文章的绝对路径
    paper_name = re.sub('[\/:*?"<>|]', '_', paper_title.text.strip()) + ".pdf"  # 获取文章名，用"_"替代不符合命名规则的文件
    print(abs_url, paper_name) # 输出文章路径和文章标题，以便随时查看进展
    save_path = "ECCV2018_PAPERS" # 文件保存路径，当前目录下的"ECCV2018_PAPERS"文件夹下
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    r = requests.get(abs_url, stream=True)  # 获取网页PDF内容
    if not os.path.exists(os.path.join(save_path, paper_name)):
        with open(os.path.join(save_path, paper_name), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): #保存论文内容
                if chunk:
                    f.write(chunk)
                    f.flush()
					
# 获取文章摘要，并保存在Excel文件中
def get_abstract(row, paper_list, paper_title):
    paper_details_url = paper_title.a['href']
    paper_details_abs_url = "http://openaccess.thecvf.com/" + paper_details_url
    print(paper_details_abs_url) # 输出文章详情页的路径
    title = paper_title.text.strip()
    res_details = requests.get(paper_details_abs_url, headers=headers)
    soup_details = bs(res_details.text, "lxml")
    abstract = soup_details.find("div", id="abstract").text.strip()
    paper_name = re.sub('[\/:*?"<>|]', '_', paper_title.text.strip()) + ".pdf"
    hyper_link = "./ECCV2018_PAPERS/" + paper_name
    link = 'HYPERLINK("%s";"%s")' % (str(hyper_link), str(title))
    paper_list.write(row, 0, xlwt.Formula(link))
    paper_list.write(row, 1, abstract)

row = 1
paper_book = Workbook(encoding='utf-8')
paper_list = paper_book.add_sheet("paper_list")
paper_list.write(0, 0, "title")
paper_list.write(0, 1, "abstract")
for (paper_title, paper_url) in zip(paper_titles, paper_urls):
    get_papers(paper_title, paper_url)
    get_abstract(row, paper_list, paper_title)
    row = row + 1
paper_book.save("ECCV2018_PAPERS.xls")
print("**********************end*********************")

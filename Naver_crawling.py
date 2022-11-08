import requests
from bs4 import BeautifulSoup
import cx_Oracle as ora
import os
#=======================
import time
import schedule
#======================
import csv

from konlpy import jvm
from konlpy.tag import Okt, Kkma, Komoran, Hannanum
  # class import
import matplotlib.pyplot as plt
class NewsTitle:

    def get_news(self, news_list):  # 뉴스 내용 가져오는 함수
        # https://n.news.naver.com/article/052/0001770651?ntype=RANKING    // 뉴스 내용
        headers = {"User-Agent" : "Chrome/63.0.3239.132 (Windows NT 6.3; Win64; x64)"}
        request = requests.get(news_list, headers=headers)
        soup = BeautifulSoup(request.text, "html.parser")
        press_title = soup.find("a", class_="ofhd_float_title_text").text # 언론사 이름 태그
        body = (soup.find("div", class_="go_trans _article_content").text).strip().splitlines() # 뉴스 내용 태그
        title = soup.find("h2", class_="media_end_head_headline").text # 뉴스 제목 태그
        content =  {"press_title" : press_title,
                    "title" : title,
                    "body": body}
        return content

    def get_news_type(self, link):  # 언론사 가져 오는 함수
        # https://news.naver.com/main/ranking/popularDay.naver
        headers = {"User-Agent": "Chrome/63.0.3239.132 (Windows NT 6.3; Win64; x64)"}
        url = link
        news_type_list = []
        request = requests.get(url, headers=headers)
        soup = BeautifulSoup(request.text, "html.parser")
        divs = soup.find_all("div", class_='rankingnews_box')   # 언론사별 랭킹 뉴스 태그
        for links in divs:
            link = links.find("a", class_="rankingnews_box_head nclicks('RBP.rnkpname')")["href"]  # 77개의 언론사 링크 태그
            name = links.find("strong", class_="rankingnews_name").text # 언론사 이름 태그
            news_types = {
                "press_name": name,
                "press_link": link
            }
            news_type_list.append(news_types)
        return news_type_list

    def get_news_link(self, press_link): # 내용
        # https://media.naver.com/press/052/ranking?type=popular
        headers = {"User-Agent": "Chrome/63.0.3239.132 (Windows NT 6.3; Win64; x64)"}
        f = open(time.strftime("./title_txtfile/news_titles_%y%b%d.txt"), 'a', newline='', encoding="utf-8")
        url = press_link

        request = requests.get(url, headers=headers)
        request.raise_for_status()
        soup = BeautifulSoup(request.text, "html.parser")
        list = soup.find_all("li", class_='as_thumb') # 뉴스 제목 랭킹 태그(랭킹번호, 이미지, 조회수 모두)
        list_file = []

        for i in range(0, len(list)):
            title = list[i].find("strong", class_="list_title").text  # 뉴스 제목 태그
            news_link = list[i].a.attrs.get("href")      # 뉴스 링크
            f.write(title)
            list_file.append(news_link)
        f.close()
        return list_file

    def main_function(self):
        link_base= "https://news.naver.com/main/ranking/popularDay.naver" # 메인 링크
        rep = self.get_news_type(link_base)
        news_links = []
        for link in rep:
            links = self.get_news_link(link["press_link"]) # link 가져오기
            news_link_dic = {
                "news_links": links
            }
            news_links.append(news_link_dic)

        ora.init_oracle_client(lib_dir="./instantclient_21_6")

        for link in news_links:
            for li in link["news_links"]:
                try:
                    print(li)
                    press_title = self.get_news(li)["press_title"],
                    link = li,
                    title = self.get_news(li)["title"],
                    content = self.get_news(li)["body"]
                    #=======================Insert DB=======================
                    conn = ora.connect(user="admin", password="....", dsn="....db_high")
                    cursor = conn.cursor()
                    cursor.execute('insert into news_title_final (create_date, name, link, title, content) values(sysdate, :2, :3, :4, :5)', (str(press_title), str(link), str(title), str(content)))
                    cursor.close()
                    conn.commit()
                    conn.close()
                except Exception as msg:
                    print(msg)
                    pass

# newstitle.main_function()

#=========================================WordCloud=============================================

class Wordcloud:
    def get_title_wordcloud(self):  # wordcloud 만드는 함수
        okt = Komoran()
        word_dic = {} # dictionary
        lines = [] # list
        with open(time.strftime("./title_txtfile/news_titles_%y%b%d.txt"), 'r', encoding="utf-8") as raws:
             reader = csv.reader(raws)
             for raw in reader:
                lines.append(raw)
        for line in lines:
             malist = okt.pos(' '.join(line))  # '구분자'.join(리스트)
             for word in malist:
                 print(word)  # [단어, 태그]
                 if word[1] == 'NNG':
                     if not(word[0] in word_dic):
                           word_dic[word[0]] = 0   # [단어 : 0] => 저장
                     word_dic[word[0]] += 1  # 단어(키)의 값 1증가
        keys = sorted(word_dic.items(), key=lambda x:x[1], reverse=True)
        # 50개까지 결과값을 출력
        for word, count in keys[:50]:
            print('{0}({1})'.format(word, count), end=', ')
        wordcloud = WordCloud(font_path='malgun.ttf', background_color = 'white',width = 1000, height = 1000)\
            .generate_from_frequencies(word_dic)
        plt.figure(figsize=(10,10))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.title(str(time.strftime("%y%b%d")), loc='right', fontsize=25)
        plt.savefig(time.strftime("./title_pngfile/result_title_%y%b%d.png"))
        plt.show()

word.get_title_wordcloud()

schedule.every().day.at("18:00").do(main_function)
schedule.every().day.at("18:10").do(wordcloud)
while True:
    schedule.run_pending()
    time.sleep(1)













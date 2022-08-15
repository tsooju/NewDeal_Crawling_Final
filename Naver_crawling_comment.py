import requests
from bs4 import BeautifulSoup
import cx_Oracle as ora
import os
#=======================
import time
import schedule
#======================
import csv
from konlpy.tag import Okt, Komoran

from wordcloud import WordCloud  # class import
import matplotlib.pyplot as plt
class NewsComment:

    def get_news(self, news_list):  # 뉴스 내용 가져오는 함수
        headers = {"User-Agent" : "Chrome/63.0.3239.132 (Windows NT 6.3; Win64; x64)"}
        request = requests.get(news_list, headers=headers)
        soup = BeautifulSoup(request.text, "html.parser")
        press_title = soup.find("a", class_="ofhd_float_title_text").text
        body = (soup.find("div", class_="go_trans _article_content").text).strip().splitlines()
        title = soup.find("h2", class_="media_end_head_headline").text
        content =  {"press_title" : press_title,
                    "title" : title,
                    "body": body}
        return content

    def get_news_type(self, link):  # 언론사 가져 오는 함수
        headers = {"User-Agent": "Chrome/63.0.3239.132 (Windows NT 6.3; Win64; x64)"}
        url = link
        news_type_list = []
        request = requests.get(url, headers=headers)
        request.raise_for_status()
        soup = BeautifulSoup(request.text, "html.parser")
        divs = soup.find_all("div", class_='rankingnews_box')
        for links in divs:
            link = links.find("a", class_="rankingnews_box_head nclicks('RBP.cmtpname')")["href"]
            name = links.find("strong", class_="rankingnews_name").text
            news_types = {
                "press_name": name,
                "press_link": link
            }
            news_type_list.append(news_types)

        return news_type_list

    def get_news_link(self, press_link): # 내용
        headers = {"User-Agent": "Chrome/63.0.3239.132 (Windows NT 6.3; Win64; x64)"}
        f = open(time.strftime("./comment_txtfile/news_comment_%y%b%d.txt"), 'a', newline='', encoding="utf-8")
        url = press_link

        request = requests.get(url, headers=headers)
        request.raise_for_status()
        soup = BeautifulSoup(request.text, "html.parser")
        list = soup.find_all("li", class_='as_thumb')
        list_file = []

        for i in range(0, len(list)):
            title = list[i].find("strong", class_="list_title").text  # 뉴스 제목
            news_link = list[i].a.attrs.get("href")      # 뉴스 링크
            f.write(title)
            list_file.append(news_link)

        f.close()
        return list_file

    def main_function(self):
        link_base= "https://news.naver.com/main/ranking/popularMemo.naver"
        rep = self.get_news_type(link_base)
        news_links = []
        for link in rep:
            links = self.get_news_link(link["press_link"])
            news_link_dic = {
                "news_links": links
            }
            news_links.append(news_link_dic)
        try:
            ora.init_oracle_client(lib_dir="./instantclient_21_6")
        except:
            pass

        for link in news_links:
            for li in link["news_links"]:
                try:
                    print(li)
                    press_title = self.get_news(li)["press_title"],
                    link = li,
                    title = self.get_news(li)["title"],
                    content = self.get_news(li)["body"]

                    #=======================Insert DB=======================

                    conn = ora.connect(user="admin", password="Amjilt39260193", dsn="gtsoojdb_high")
                    cursor = conn.cursor()
                    cursor.execute('insert into news_comment_final (create_date, name, link, title, content) values(sysdate, :2, :3, :4, :5)', (str(press_title), str(link), str(title), str(content)))
                    cursor.close()
                    conn.commit()
                    conn.close()
                except Exception as msg:
                    print(msg)
                    pass

# newscomment = NewsComment()
# newscomment.main_function()

#=========================================WordCloud=============================================

class CommentWordcloud:
    def get_comment_wordcloud(self):  # wordcloud 만드는 함수

        okt = Komoran()
        word_dic = {} # dictionary
        lines = [] # list

        with open(time.strftime("./comment_txtfile/news_comment_%y%b%d.txt"), 'r', encoding="utf-8") as raws:
             reader = csv.reader(raws)
             for raw in reader:
                lines.append(raw)

        for line in lines:
             malist = okt.pos(' '.join(line))  # '구분자'.join(리스트)
             for word in malist:
                 print(word)  # [단어, 태그]
                 if word[1] == 'NNG':
                     if not(word[0] in word_dic):
                                # 해당 단어가 사전에 저장되어 있지 않다면
                           word_dic[word[0]] = 0   # [단어 : 0] => 저장

                        # 딕셔너리는 저장안 된 키에 값 대입하면 자동 저장됨
                     word_dic[word[0]] += 1  # 단어(키)의 값 1증가


        keys = sorted(word_dic.items(), key=lambda x:x[1], reverse=True)

        for word, count in keys[:50]:
            print('{0}({1})'.format(word, count), end=', ')

        wordcloud = WordCloud(font_path='malgun.ttf', background_color = 'white', width = 1000, height = 1000).generate_from_frequencies(word_dic)

        plt.figure(figsize=(10,10))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.title(str(time.strftime("%y%b%d")), loc='right', fontsize=25)
        plt.savefig(time.strftime("./comment_pngfile/result_comment_%y%b%d.png"))
        # plt.show()

# schedule.every().day.at("18:00").do(main_function)
# schedule.every().day.at("18:10").do(wordcloud)
# while True:
#     schedule.run_pending()
#     time.sleep(1)

# comment = CommentWordcloud()
# comment_wordcloud.get_comment_wordcloud()











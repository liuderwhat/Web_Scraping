import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
import ssl
import pandas as pd

class BasicData(object):

    def __init__(self, context):

        self.context = context

    def get_col_name(self, p_soup):
        # 存所有的欄位名稱
        col = []

        # 所有欄位都是在dl底下
        dl = p_soup.find('dl')
        col.extend(['pid', 'team', 'name', 'number'])

        # 其他欄位都在dd
        dd = dl.find_all('dd')
        dd_col = [v for ele in dd for v in ele['class']]
        col.extend(dd_col)

        # 將身高與體重分開
        body_index = col.index('ht_wt')
        col.remove('ht_wt')
        [col.insert(body_index, i) for i in (['ht', 'wt'])]

        return col

    def save_data(self, p_link):

        players_info = []

        c = 0
        # 透過情緣連結到個別球員的畫面
        for i in p_link:

                p_page = urlopen(i, context = self.context)
                p_html = p_page.read().decode("utf-8")
                p_soup = BeautifulSoup(p_html, "html.parser")

                # 建立欄位名稱，參考官方的html
                cols = self.get_col_name(p_soup)

                # 球員編號，不然沒有pk
                pid = i.split('=')[1]

                # 球員基本資料
                players_info.append(self.get_p_data(p_soup, pid))
              
                p_table = pd.DataFrame(players_info, columns = cols)

        return p_table

    def get_p_data(self, p_soup, pid):
        # class為隊伍、名字、背號
        team, name_tmp = p_soup.find(class_='team').text, p_soup.find(class_='name').text

        # 因為名字的欄位也包含背號，所以就用數字判斷
        # 然後用長度區分
        name = ''.join([i for i in name_tmp if not i.isdigit()])
        number = name_tmp[len(name):]
        p_info1 = [pid, team, name, number]

        # 下面的欄位的class都是desc
        p_info = [i.text for i in p_soup.find_all(class_='desc')]

        # 身高跟體重那欄是寫在一起的，而且還有/跟kg之類的
        # 所以直接用數字判斷，身高直接取前三個，這邊假設沒有侏儒 ㄏ
        body = ''.join([i for i in p_info[2] if i.isdigit()])
        b_shape = body[3:], body[:3]
        p_info.remove(p_info[2])
        [p_info.insert(2, b_shape[i]) for i in range(2)]
        p_info1.extend(p_info)

        return p_info1

class PerformanceData(BasicData):

    # def __init__(self, context):
    #     BasicData.__init__(self, context)
    def __init__(self, context):
        self.context = context
        
    def save_data(self):
        print("123")



if __name__ == '__main__':
    context = ssl._create_unverified_context()
    url = "https://www.cpbl.com.tw/player"
    page = urlopen(url, context = context)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    basic_data = BasicData(context)
    performance_data = PerformanceData(context)

    performance_data.save_data()
    # 球員連結
    # 後面三個是社群媒體，不納入
    # p_link = [url.replace('/player', i.a['href']) for i in soup.find_all('dd')][:-3]
    # p_table = basic_data.save_data(p_link)
    # p_table.to_csv('data/player_info.csv', index=False, encoding='utf-8-sig')



'''
module_name, package_name, ClassName, method_name, ExceptionName, function_name, GLOBAL_CONSTANT_NAME, 
global_var_name, instance_var_name, function_parameter_name, local_var_name.
'''
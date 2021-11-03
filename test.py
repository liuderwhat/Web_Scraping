import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
import ssl
import pandas as pd

def get_p_data(p_html, pid):
    # class為隊伍、名字、背號
    team, name_tmp = p_html.find(class_='team').text, p_html.find(class_='name').text
    # 因為名字的欄位也包含背號，所以就用數字判斷
    # 然後用長度區分
    name = ''.join([i for i in name_tmp if not i.isdigit()])
    number = name_tmp[len(name):]
    p_info1 = [pid, team, name, number]
    # 下面的欄位的class都是desc
    p_info = [i.text for i in p_html.find_all(class_='desc')]
    # 身高跟體重那欄是寫在一起的，而且還有/跟kg之類的
    # 所以直接用數字判斷，身高直接取前三個，這邊假設沒有侏儒 ㄏ
    body = ''.join([i for i in p_info[2] if i.isdigit()])
    b_shape = body[3:], body[:3]
    p_info.remove(p_info[2])
    [p_info.insert(2, b_shape[i]) for i in range(2)]
    p_info1.extend(p_info)
    return p_info1

def get_col_name(p_html):
    classes = []
    dl = p_html.find('dl')
    classes.extend(['pid', 'team', 'name', 'number'])
    dd = dl.find_all('dd')
    dd_class = [v for ele in dd for v in ele['class']]
    classes.extend(dd_class)
    body_index = classes.index('ht_wt')
    classes.remove('ht_wt')
    [classes.insert(body_index, i) for i in (['ht', 'wt'])]
    return classes


if __name__ == '__main__':
    context = ssl._create_unverified_context()
    url = "https://www.cpbl.com.tw/player"
    page = urlopen(url, context = context)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # 球員連結
    p_link = [url.replace('/player', i.a['href']) for i in soup.find_all('dd')][:-3]

    players_info = []
    # 透過情緣連結到個別球員的畫面
    for i in p_link:
        p_page = urlopen(i, context = context)
        p_html = p_page.read().decode("utf-8")
        p_soup = BeautifulSoup(p_html, "html.parser")

        # 建立欄位名稱，參考官方的html
        col = get_col_name(p_soup)

        # 球員編號，不然沒有pk
        pid = i.split('=')[1]
        # 球員基本資料
        players_info.append(get_p_data(p_soup, pid))
      
        p_table = pd.DataFrame(players_info, columns = col)

        break

    print(p_table)
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="安全衛生NEWS", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
}

@st.cache_data(ttl=3600)
def fetch_all_news():
    data = []
    
    # 1. 職場のあんぜんサイト
    try:
        url1 = "https://anzeninfo.mhlw.go.jp/index.html"
        res1 = requests.get(url1, headers=HEADERS, timeout=10)
        res1.encoding = 'utf-8'
        soup1 = BeautifulSoup(res1.text, 'html.parser')
        news_list = soup1.find('dl', class_='news_list')
        if news_list:
            for dt, dd in zip(news_list.find_all('dt')[:5], news_list.find_all('dd')[:5]):
                a = dd.find('a')
                if a:
                    link = a['href']
                    full_url = "https://anzeninfo.mhlw.go.jp" + link if link.startswith('/') else link
                    data.append({"日付": dt.text, "カテゴリ": "事例・行政", "タイトル": a.text, "URL": full_url, "ソース": "職場のあんぜんサイト"})
    except: pass

    # 2. 安全衛生情報センター（事故速報）
    try:
        url2 = "https://www.jaish.gr.jp/anzen/new/shasin_list.html"
        res2 = requests.get(url2, headers=HEADERS, timeout=10)
        res2.encoding = 'shift_jis'
        soup2 = BeautifulSoup(res2.text, 'html.parser')
        for r in soup2.find_all('tr')[1:6]:
            tds = r.find_all('td')
            if len(tds) >= 2:
                a2 = tds[1].find('a')
                if a2:
                    l2 = "https://www.jaish.gr.jp/anzen/" + a2['href'].replace('../', '')
                    data.append({"日付": "最新", "カテゴリ": "事故速報", "タイトル": a2.text, "URL": l2, "ソース": "安全衛生情報センター"})
    except: pass

    # 3. 労働新聞社（安全衛生カテゴリ）
    try:
        url3 = "https://www.rodo.co.jp/news/category/safety/"
        res3 = requests.get(url3, headers=HEADERS, timeout=10)
        soup3 = BeautifulSoup(res3.text, 'html.parser')
        # 記事タイトル部分を抽出
        articles = soup3.select('article.post-list-item')
        for art in articles[:5]:
            a3 = art.select_one('h2.post-title a')
            date3 = art.select_one('time')
            if a3:
                data.append({
                    "日付": date3.text if date3 else "不明", 
                    "カテゴリ": "法令・送検", 
                    "タイトル": a3.text, 
                    "URL": a3['href'], 
                    "ソース": "労働新聞社"
                })
    except: pass

    # 4. 建設通信新聞（安全カテゴリを想定）
    try:
        url4 = "https://www.kensetsunews.com/category/policy" # 行政・施策系
        res4 = requests.get(url4, headers=HEADERS, timeout=10)
        soup4 = BeautifulSoup(res4.text, 'html.parser')
        for art in soup4.select('article')[:5]:
            a4 = art.find('a')
            h2 = art.find('h2')
            if a4 and h2:
                data.append({
                    "日付": "最近", 
                    "カテゴリ": "建築・施策", 
                    "タイトル": h2.get_text(strip=True), 
                    "URL": a4['href'] if a4['href'].startswith('http') else "https://www.kensetsunews.com" + a4['href'], 
                    "ソース": "建設通信新聞"
                })
    except: pass
    
    return pd.DataFrame(data)

st.title("🛡️ 安全衛生ニュース収集")

if st.sidebar.button("最新の情報に更新"):
    st.cache_data.clear()
    st.rerun()

with st.spinner('情報を取得しています...'):
    df = fetch_all_news()

if not df.empty:
    df = df.drop_duplicates(subset=['タイトル'])
    src_list = df["ソース"].unique().tolist()
    sources = st.sidebar.multiselect("フィルタ", src_list, default=src_list)
    disp = df[df["ソース"].isin(sources)]

    cols = st.columns(2)
    for i, (_, r) in enumerate(disp.iterrows()):
        with cols[i % 2]:
            with st.container(border=True):
                # 出典ごとにラベルの色を変える簡易演出
                label_color = "🔴" if "事故" in r['カテゴリ'] else "🔵"
                st.caption(f"{label_color} {r['日付']} | {r['カテゴリ']}")
                st.markdown(f"**{r['タイトル']}**")
                st.write(f"出典: {r['ソース']}")
                st.link_button("記事を見る", r['URL'])
else:
    st.info("ニュースが見つかりませんでした。")

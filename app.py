import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# ページ設定
st.set_page_config(page_title="安全衛生NEWS", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

@st.cache_data(ttl=3600)
def fetch_news():
    data = []
    
    # 1. 職場のあんぜんサイト
    try:
        url = "https://anzeninfo.mhlw.go.jp/index.html"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        news_list = soup.find('dl', class_='news_list')
        if news_list:
            dts = news_list.find_all('dt')
            dds = news_list.find_all('dd')
            for dt, dd in zip(dts[:10], dds[:10]):
                a = dd.find('a')
                if a:
                    link = a['href']
                    full_url = "https://anzeninfo.mhlw.go.jp" + link if link.startswith('/') else link
                    data.append({"日付": dt.text, "カテゴリ": "事例", "タイトル": a.text, "URL": full_url, "ソース": "職場のあんぜんサイト"})
    except:
        pass

    # 2. 安全衛生情報センター
    try:
        url2 = "https://www.jaish.gr.jp/anzen/new/shasin_list.html"
        res2 = requests.get(url2, headers=HEADERS, timeout=10)
        res2.encoding = 'shift_jis'
        soup2 = BeautifulSoup(res2.text, 'html.parser')
        rows = soup2.find_all('tr')
        for r in rows[1:11]:
            tds = r.find_all('td')
            if len(tds) >= 2:
                a2 = tds[1].find('a')
                if a2:
                    l2 = "https://www.jaish.gr.jp" + a2['href'].replace('../', '/')
                    data.append({"日付": "最新", "カテゴリ": "速報", "タイトル": a2.text, "URL": l2, "ソース": "安全衛生情報センター"})
    except:
        pass
    
    return pd.DataFrame(data)

# メイン画面表示
st.title("🛡️ 安全衛生ニュース収集")

with st.spinner('更新中...'):
    df = fetch_news()

if not df.empty:
    df = df.drop_duplicates(subset=['タイトル'])
    sources = st.sidebar.multiselect("フィルタ", df["ソース"].unique(), default=df["ソース"].unique())
    disp = df[df["ソース"].isin(sources)]

    cols = st.columns(2)
    for i, (_, r) in enumerate(disp.iterrows()):
        with cols[i % 2]:
            with st.container(border=True):
                st.caption(f"{r['日付']} | {r['カテゴリ']}")
                st.markdown(f"**{r['タイトル']}**")
                st.link_button("詳細を開く", r['URL'])
else:
    st.info("ニュースが見つかりませんでした。")

if st.sidebar.button("更新"):
    st.cache_data.clear()
    st.rerun()

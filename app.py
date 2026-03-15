import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="安全衛生NEWS", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def safe_get(url):
    """エラーが起きても止まらない取得関数"""
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        return res
    except:
        return None

@st.cache_data(ttl=1800)
def fetch_news():
    data = []
    
    # --- 1. 職場のあんぜんサイト ---
    res = safe_get("https://anzeninfo.mhlw.go.jp/index.html")
    if res:
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        for dt, dd in zip(soup.select('dl.news_list dt')[:5], soup.select('dl.news_list dd')[:5]):
            a = dd.find('a')
            if a:
                data.append({"日付": dt.text, "カテゴリ": "事例・行政", "タイトル": a.text, "URL": "https://anzeninfo.mhlw.go.jp" + a['href'], "ソース": "職場のあんぜんサイト"})

    # --- 2. 安全衛生情報センター ---
    res = safe_get("https://www.jaish.gr.jp/anzen/new/shasin_list.html")
    if res:
        res.encoding = 'shift_jis'
        soup = BeautifulSoup(res.text, 'html.parser')
        for r in soup.find_all('tr')[1:6]:
            tds = r.find_all('td')
            if len(tds) >= 2:
                a = tds[1].find('a')
                if a:
                    data.append({"日付": "最新", "カテゴリ": "事故速報", "タイトル": a.text, "URL": "https://www.jaish.gr.jp/anzen/" + a['href'].replace('../',''), "ソース": "安全衛生情報センター"})

    # --- 3. 労働新聞社 ---
    res = safe_get("https://www.rodo.co.jp/news/category/safety/")
    if res:
        soup = BeautifulSoup(res.text, 'html.parser')
        for art in soup.select('h2.post-title a')[:5]:
            data.append({"日付": "最近", "カテゴリ": "法令・送検", "タイトル": art.text, "URL": art['href'], "ソース": "労働新聞社"})

    return pd.DataFrame(data)

st.title("🛡️ 安全衛生ニュース収集")

if st.sidebar.button("最新の情報に更新"):
    st.cache_data.clear()
    st.rerun()

with st.spinner('情報を取得しています...'):
    df = fetch_news()

if not df.empty:
    df = df.drop_duplicates(subset=['タイトル']).reset_index(drop=True)
    sources = st.sidebar.multiselect("フィルタ", df["ソース"].unique(), default=df["ソース"].unique())
    disp = df[df["ソース"].isin(sources)]

    cols = st.columns(2)
    for i, (_, r) in enumerate(disp.iterrows()):
        with cols[i % 2]:
            with st.container(border=True):
                icon = "🔴" if "事故" in r['カテゴリ'] else "🔵"
                st.caption(f"{icon} {r['日付']} | {r['カテゴリ']}")
                st.markdown(f"**{r['タイトル']}**")
                st.write(f"出典: {r['ソース']}")
                st.link_button("記事を見る", r['URL'])
else:
    st.info("ニュースを取得できませんでした。サイドバーの「更新」ボタンを何度か押してみてください。")

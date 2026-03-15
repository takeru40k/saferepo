import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="安全衛生NEWS", layout="wide")

# ヘッダー（ブラウザからのアクセスに見せかける設定）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

@st.cache_data(ttl=3600)
def fetch_all_news():
    news_list = []
    
    # 1. 職場のあんぜんサイト（新着情報）
    try:
        url_mhlw = "https://anzeninfo.mhlw.go.jp/index.html"
        res = requests.get(url_mhlw, headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # サイト構造に合わせて再調整
        news_list_tags = soup.find_all(['dt', 'dd'])
        temp_date = ""
        for tag in news_list_tags:
            if tag.name == 'dt':
                temp_date = tag.get_text(strip=True)
            elif tag.name == 'dd' and temp_date:
                a_tag = tag.find('a')
                if a_tag:
                    news_list.append({
                        "日付": temp_date,
                        "カテゴリ": "行政・事例",
                        "タイトル": a_tag.get_text(strip=True),
                        "URL": "https://anzeninfo.mhlw.go.jp" + a_tag['href'] if a_tag['href'].startswith('/') else a_tag['href'],
                        "ソース": "職場のあんぜんサイト"
                    })
    except Exception as e:
        st.error(f"厚労省サイトの取得失敗: {e}")

    # 2. 安全衛生情報センター（事故速報）
    try:
        url_jish = "https://www.jaish.gr.jp/anzen/new/shasin_list.html"
        res = requests.get(url_jish, headers=HEADERS, timeout=10)
        res.encoding = 'shift_jis'
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find_all('tr')
        for row in rows[1:15]:
            cols = row.find_all('td')
            if len(cols) >= 2:
                a_tag = cols[1].find('a')
                if a_tag:
                    news_list.append({
                        "日付": "最新",
                        "カテゴリ": "事故速報",
                        "タイトル": a_tag.get_text(strip=True),
                        "URL": "https://www.jaish.gr.jp" + a_tag['href'].replace('../', '/anzen/'),
                        "ソース": "安全衛生情報センター"
                    })
    except Exception as e:
        st.error(f"安全衛生情報センターの取得失敗: {e}")
    
    return pd.DataFrame(news_list)

st.title("🛡️ 安全衛生ニュース収集アプリ")

with st.spinner('最新情報を取得中...'):
    df = fetch_all_news()

if not df.empty:
    # 重複削除
    df = df.drop_duplicates(subset=['タイトル'])
    
    # カテゴリ選択
    sources = st.multiselect("情報源フィルタ", options=df["ソース"].unique(), default=df["ソース"].unique())
    display_df = df[df["ソース"].isin(sources)]

    cols = st.columns(2)
    for i, (_, row) in enumerate(display_df.iterrows()):
        with cols[i % 2]:
            with st.container(border=True):
                st.caption(f"{row

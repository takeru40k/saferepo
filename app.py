import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# --- ページ設定 (レスポンシブ対応) ---
st.set_page_config(page_title="安全衛生NEWS", layout="wide", initial_sidebar_state="collapsed")

# --- カスタムCSS（スマホでの視認性向上） ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .news-card {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e6e9ef;
        background-color: white;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- スクレイピング関数 ---
@st.cache_data(ttl=3600) # 1時間はキャッシュを保持（相手サーバーへの負荷軽減）
def fetch_all_news():
    news_list = []
    
    # 1. 職場のあんぜんサイト（新着情報）
    try:
        url_mhlw = "https://anzeninfo.mhlw.go.jp/index.html"
        res = requests.get(url_mhlw, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        news_section = soup.find('dl', class_='news_list')
        if news_section:
            dts = news_section.find_all('dt')
            dds = news_section.find_all('dd')
            for dt, dd in zip(dts[:10], dds[:10]): # 最新10件
                news_list.append({
                    "日付": dt.get_text(strip=True),
                    "カテゴリ": "行政・事例",
                    "タイトル": dd.get_text(strip=True),
                    "URL": "https://anzeninfo.mhlw.go.jp" + dd.find('a')['href'] if dd.find('a') else url_mhlw,
                    "ソース": "職場のあんぜんサイト"
                })
    except: pass

    # 2. 安全衛生情報センター（写真で見る労災ニュース）
    try:
        url_jish = "https://www.jaish.gr.jp/anzen/new/shasin_list.html"
        res = requests.get(url_jish, timeout=10)
        res.encoding = 'shift_jis'
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find_all('tr')
        for row in rows[1:11]: # ヘッダーを除いた最新10件
            cols = row.find_all('td')
            if len(cols) >= 2:
                a_tag = cols[1].find('a')
                if a_tag:
                    news_list.append({
                        "日付": "最新",
                        "カテゴリ": "事故速報",
                        "タイトル": a_tag.get_text(strip=True),
                        "URL": "https://www.jaish.gr.jp" + a_tag['href'],
                        "ソース": "安全衛生情報センター"
                    })
    except: pass
    
    return pd.DataFrame(news_list)

# --- 画面構成 ---
st.title("🛡️ 安全衛生ニュース収集アプリ")
st.caption("PC・スマホ対応：現場の安全管理・教育のネタ探しに")

with st.spinner('最新情報を取得中...'):
    df = fetch_all_news()

# --- フィルタリング（スマホでは上部に、PCでは横に） ---
st.sidebar.header("表示フィルタ")
selected_source = st.sidebar.multiselect(
    "情報源を選択", 
    options=df["ソース"].unique() if not df.empty else [],
    default=df["ソース"].unique() if not df.empty else []
)

if not df.empty:
    display_df = df[df["ソース"].isin(selected_source)]
    
    # --- ニュース表示エリア ---
    # PCでは2列、スマホ（画面幅が狭い時）は自動で1列になる
    cols = st.columns(2) 
    
    for i, row in display_df.iterrows():
        with cols[i % 2]:
            with st.container(border=True):
                st.write(f"🏷️ {row['カテゴリ']} | {row['日付']}")
                st.markdown(f"#### {row['タイトル']}")
                st.write(f"📍 出典: {row['ソース']}")
                
                # ボタンクリックでリンクへ
                st.link_button("元記事を確認する", row['URL'])
else:
    st.warning("ニュースの取得に失敗したか、データがありません。")

st.divider()
st.caption("※このアプリは学習・業務支援用のプロトタイプです。相手サイトの負荷に配慮し、短時間での連続更新は避けてください。")

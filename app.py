import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import requests

# ページ設定
st.set_page_config(page_title="Safety News Tracker", layout="wide", initial_sidebar_state="collapsed")

# カスタムCSSでデザインをモダンに
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        border: 1px solid #e0e0e0;
        background-color: white;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border-color: #007bff;
        color: #007bff;
    }
    .news-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def fetch_google_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ja&gl=JP&ceid=JP:ja"
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        news_items = []
        for item in root.findall('.//item')[:10]:
            title = item.find('title').text
            # ジャンル判定
            category = "🏗️ 建設・転落"
            if any(k in title for k in ["中毒", "溶剤", "化学", "ガス"]):
                category = "🧪 化学・溶剤"
            elif any(k in title for k in ["送検", "違反", "判決"]):
                category = "⚖️ 法令・送検"

            news_items.append({
                "タイトル": title,
                "URL": item.find('link').text,
                "ソース": item.find('source').text if item.find('source') is not None else "Googleニュース",
                "日付": item.find('pubDate').text[5:16],
                "カテゴリ": category
            })
        return news_items
    except:
        return []

# ヘッダー
st.title("🛡️ Safety News Tracker")
st.caption("Fukuoka QC Division - 安全管理情報の自動収集・解析")

# メイン処理
with st.spinner('最新の安全情報をロード中...'):
    results = fetch_google_news("労働災害 建設 転落") + fetch_google_news("有機溶剤 中毒 化学")
    df = pd.DataFrame(results).drop_duplicates(subset=['タイトル']).reset_index(drop=True)

if not df.empty:
    # グリッドレイアウト
    cols = st.columns(2)
    for i, (_, r) in enumerate(df.iterrows()):
        with cols[i % 2]:
            # カード風のコンテナ
            with st.container(border=True):

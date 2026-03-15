import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import requests

st.set_page_config(page_title="安全衛生NEWS", layout="wide")

def fetch_google_news(keyword):
    """GoogleニュースからキーワードでRSSを取得（標準ライブラリのみ使用）"""
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ja&gl=JP&ceid=JP:ja"
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        news_items = []
        for item in root.findall('.//item')[:10]:
            news_items.append({
                "タイトル": item.find('title').text,
                "URL": item.find('link').text,
                "ソース": item.find('source').text if item.find('source') is not None else "Googleニュース",
                "日付": item.find('pubDate').text[:16]
            })
        return news_items
    except:
        return []

st.title("🛡️ 安全衛生ニュース収集")
st.caption("最新の労働災害・化学物質・建設事故情報を抽出中")

# 1. ニュースを取得（建築・化学の2軸で検索）
with st.spinner('情報を取得しています...'):
    results = fetch_google_news("労働災害 建設 転落") + fetch_google_news("有機溶剤 中毒 化学")
    df = pd.DataFrame(results)

if not df.empty:
    df = df.drop_duplicates(subset=['タイトル']).reset_index(drop=True)
    
    # 2. 画面に表示
    cols = st.columns(2)
    for i, (_, r) in enumerate(df.iterrows()):
        with cols[i % 2]:
            with st.container(border=True):
                # タイトルによってアイコンを切り替え
                icon = "🧪" if any(k in r['タイトル'] for k in ["中毒", "溶剤", "化学"]) else "🏗️"
                
                st.caption(f"{icon} {r['日付']} | {r['ソース']}")
                st.markdown(f"**{r['タイトル']}**")
                st.link_button("記事をブラウザで開く", r['URL'])
else:
    st.info("現在ニュースを取得できませんでした。サイドバーから更新を試すか、しばらくお待ちください。")

if st.sidebar.button("最新情報に更新"):
    st.rerun()

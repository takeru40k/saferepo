import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="安全衛生NEWS", layout="wide")

# ニュースの本文（冒頭）を取得する関数
def get_article_summary(url):
    try:
        # 記事のURLを読み込み、最初の150文字程度を抽出
        res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # ページ内のテキストを結合（広告などを除外するため主要なタグのみ）
        paragraphs = soup.find_all('p')
        text = "".join([p.get_text() for p in paragraphs])
        
        # 冒頭120文字を返す
        summary = text[:120].replace('\n', '').strip()
        return summary + "..." if len(text) > 120 else summary
    except:
        return "※詳細はリンク先をご確認ください。"

def fetch_google_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ja&gl=JP&ceid=JP:ja"
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        news_items = []
        for item in root.findall('.//item')[:8]: # 読み込みを速くするため各8件
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

with st.spinner('情報を取得しています...'):
    # 建築と化学、それぞれのニュースを取得
    raw_results = fetch_google_news("労働災害 建設 転落") + fetch_google_news("有機溶剤 中毒 化学")
    df = pd.DataFrame(raw_results).drop_duplicates(subset=['タイトル']).reset_index(drop=True)

if not df.empty:
    cols = st.columns(2)
    for i, (_, r) in enumerate(df.iterrows()):
        with cols[i % 2]:
            with st.container(border=True):
                icon = "🧪" if any(k in r['タイトル'] for k in ["中毒", "溶剤", "化学"]) else "🏗️"
                st.caption(f"{icon} {r['日付']} | {r['ソース']}")
                st.markdown(f"### {r['タイトル']}")
                
                # --- APIを使わない「簡易要約（冒頭チラ見せ）」 ---
                with st.expander("📝 記事の概要をチラ見する"):
                    summary_text = get_article_summary(r['URL'])
                    st.write(summary_text)
                
                st.link_button("記事をブラウザで開く", r['URL'])
else:
    st.info("現在ニュースを取得できませんでした。")

if st.sidebar.button("最新情報に更新"):
    st.rerun()

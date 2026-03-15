import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse

st.set_page_config(page_title="安全衛生NEWS", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

@st.cache_data(ttl=1800)
def fetch_civilian_news():
    data = []

    # --- 1. 労働新聞社（安全衛生） ---
    try:
        r = requests.get("https://www.rodo.co.jp/news/category/safety/", headers=HEADERS, timeout=10)
        s = BeautifulSoup(r.text, 'html.parser')
        for art in s.select('h2.post-title a')[:5]:
            data.append({"カテゴリ": "法令・管理", "タイトル": art.text, "URL": art['href'], "ソース": "労働新聞社"})
    except: pass

    # --- 2. Yahoo!ニュース（検索: 労働災害） ---
    try:
        # Yahooニュースの検索結果を利用（速報性が高い）
        query = urllib.parse.quote("労働災害")
        url = f"https://news.yahoo.co.jp/search?p={query}&ei=utf-8"
        r = requests.get(url, headers=HEADERS, timeout=10)
        s = BeautifulSoup(r.text, 'html.parser')
        for item in s.select('li.sw-Card-list')[:5]:
            a = item.find('a')
            if a:
                data.append({"カテゴリ": "事故速報", "タイトル": a.text, "URL": a['href'], "ソース": "Yahoo!ニュース"})
    except: pass

    # --- 3. Googleニュース（検索: 有機溶剤 中毒 or 墜落事故） ---
    # 化学系・建築系を狙い撃ち
    for keyword in ["有機溶剤 中毒", "建設現場 墜落"]:
        try:
            query = urllib.parse.quote(keyword)
            url = f"https://news.google.com/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
            r = requests.get(url, headers=HEADERS, timeout=10)
            s = BeautifulSoup(r.text, 'html.parser')
            for art in s.select('article')[:3]:
                a = art.find('a', class_='Wwrz6e') or art.find('a')
                if a:
                    title = art.find('h3') or art.find('h4')
                    link = "https://news.google.com" + a['href'][1:] if a['href'].startswith('.') else a['href']
                    data.append({
                        "カテゴリ": "建築・化学" if "中毒" in keyword else "建築・落下",
                        "タイトル": title.text if title else "詳細リンク",
                        "URL": link,
                        "ソース": "Googleニュース"
                    })
        except: pass

    return pd.DataFrame(data)

st.title("🛡️ 安全衛生ニュース収集")
st.caption("民間ニュースサイト・検索エンジンから最新情報を抽出中")

if st.sidebar.button("最新の情報に更新"):
    st.cache_data.clear()
    st.rerun()

with st.spinner('情報を取得しています...'):
    df = fetch_civilian_news()

if not df.empty:
    df = df.drop_duplicates(subset=['タイトル']).reset_index(drop=True)
    
    # カテゴリ判別タグ
    cols = st.columns(2)
    for i, (_, r) in enumerate(df.iterrows()):
        with cols[i % 2]:
            with st.container(border=True):
                # アイコン設定
                icon = "🧪" if "中毒" in r['タイトル'] or "溶剤" in r['タイトル'] else "🏗️"
                if "送検" in r['タイトル'] or "違反" in r['タイトル']: icon = "⚖️"

                st.caption(f"{icon} {r['カテゴリ']}")
                st.markdown(f"**{r['タイトル']}**")
                st.write(f"出典: {r['ソース']}")
                st.link_button("記事を読む", r['URL'])
else:
    st.warning("現在ニュースを取得できませんでした。Yahoo!やGoogleの検索制限、またはネットワークの問題の可能性があります。")

st.divider()
st.caption("※民間サイトの情報を収集しています。詳細は必ずリンク先の一次情報（官公庁発表等）を確認してください。")

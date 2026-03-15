import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import requests
import re

st.set_page_config(page_title="安全衛生NEWS", layout="wide")

def fetch_google_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ja&gl=JP&ceid=JP:ja"
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        news_items = []
        for item in root.findall('.//item')[:10]:
            # RSS内のdescriptionタグからHTMLタグを除去してテキストのみ抽出
            desc_raw = item.find('description').text if item.find('description') is not None else ""
            clean_desc = re.sub('<[^<]+?>', '', desc_raw) # HTMLタグを掃除
            
            news_items.append({
                "タイトル": item.find('title').text,
                "URL": item.find('link').text,
                "ソース": item.find('source').text if item.find('source') is not None else "Googleニュース",
                "日付": item.find('pubDate').text[:16],
                "概要": clean_desc
            })
        return news_items
    except:
        return []

st.title("🛡️ 安全衛生ニュース収集")
st.caption("最新の労働災害・化学物質・建設事故情報を抽出中")

with st.spinner('情報を取得しています...'):
    results = fetch_google_news("労働災害 建設 転落") + fetch_google_news("有機溶剤 中毒 化学")
    df = pd.DataFrame(results).drop_duplicates(subset=['タイトル']).reset_index(drop=True)

if not df.empty:
    cols = st.columns(2)
    for i, (_, r) in enumerate(df.iterrows()):
        with cols[i % 2]:
            with st.container(border=True):
                icon = "🧪" if any(k in r['タイトル'] for k in ["中毒", "溶剤", "化学"]) else "🏗️"
                st.caption(f"{icon} {r['日付']} | {r['ソース']}")
                st.markdown(f"**{r['タイトル']}**")
                
                # RSSに元々含まれている概要を表示
                with st.expander("📝 記事の概要をチラ見する"):
                    if r['概要']:
                        st.write(r['概要'])
                    else:
                        st.write("概要データが含まれていません。詳細はリンク先をご確認ください。")
                
                st.link_button("記事をブラウザで開く", r['URL'])
else:
    st.info("現在ニュースを取得できませんでした。")

if st.sidebar.button("最新情報に更新"):
    st.rerun()

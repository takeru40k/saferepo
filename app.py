import streamlit as st
import feedparser
import pandas as pd

st.set_page_config(page_title="安全衛生NEWS", layout="wide")

@st.cache_data(ttl=1800)
def fetch_rss_news():
    # 信頼性の高いRSSフィード（ブロックされにくい公式配信）
    feeds = {
        "労働新聞社": "https://www.rodo.co.jp/category/news/safety/feed/",
        "時事通信 (社会)": "https://www.jiji.com/rss/category/soci.xml"
    }
    
    all_articles = []
    for source_name, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                # 安全衛生に関係ありそうなキーワードで時事通信をフィルタリング
                if source_name == "時事通信 (社会)":
                    keywords = ["事故", "転落", "転落", "中毒", "火災", "爆発", "労働", "現場"]
                    if not any(k in entry.title for k in keywords):
                        continue
                
                all_articles.append({
                    "ソース": source_name,
                    "タイトル": entry.title,
                    "URL": entry.link,
                    "日付": entry.get("published", "最新")
                })
        except:
            pass
    return pd.DataFrame(all_articles)

st.title("🛡️ 安全衛生ニュース収集")
st.caption("公式RSSフィードより安定取得中")

if st.sidebar.button("最新情報に更新"):
    st.cache_data.clear()
    st.rerun()

with st.spinner('情報を取得しています...'):
    df = fetch_rss_news()

if not df.empty:
    df = df.drop_duplicates(subset=['タイトル'])
    
    cols = st.columns(2)
    for i, (_, r) in enumerate(df.iterrows()):
        with cols[i % 2]:
            with st.container(border=True):
                # アイコンの自動選択
                icon = "🏗️" if any(k in r['タイトル'] for k in ["事故", "転落", "建設"]) else "⚖️"
                if "中毒" in r['タイトル'] or "化学" in r['タイトル']: icon = "🧪"
                
                st.caption(f"{icon} {r['ソース']} | {r['日付']}")
                st.markdown(f"**{r['タイトル']}**")
                st.link_button("記事を読む", r['URL'])
else:
    st.info("ニュースが配信されていません。時間を置いて更新してください。")

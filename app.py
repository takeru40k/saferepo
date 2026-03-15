import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="安全衛生NEWS", layout="wide")

# より詳細なヘッダーを設定
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
}

@st.cache_data(ttl=1800)
def fetch_news():
    data = []
    
    # 1. 職場のあんぜんサイト（新着情報ページを直接指定）
    try:
        url = "https://anzeninfo.mhlw.go.jp/index.html"
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # もし news_list が見つからない場合の予備ルート
        items = soup.select('dl.news_list dt, dl.news_list dd')
        if not items:
            # 別のタグ構成を試行
            items = soup.find_all(['dt', 'dd'])

        temp_date = ""
        for item in items:
            if item.name == 'dt':
                temp_date = item.get_text(strip=True)
            elif item.name == 'dd' and temp_date:
                a = item.find('a')
                if a:
                    link = a.get('href', '')
                    full_url = "https://anzeninfo.mhlw.go.jp" + link if link.startswith('/') else link
                    data.append({
                        "日付": temp_date, 
                        "カテゴリ": "事例・行政", 
                        "タイトル": a.get_text(strip=True), 
                        "URL": full_url, 
                        "ソース": "職場のあんぜんサイト"
                    })
    except:
        pass

    # 2. 安全衛生情報センター（事故速報）
    try:
        url2 = "https://www.jaish.gr.jp/anzen/new/shasin_list.html"
        res2 = requests.get(url2, headers=HEADERS, timeout=15)
        res2.encoding = 'shift_jis'
        soup2 = BeautifulSoup(res2.text, 'html.parser')
        
        # テーブルの各行を精査
        for r in soup2.find_all('tr'):
            tds = r.find_all('td')
            if len(tds) >= 2:
                a2 = tds[1].find('a')
                if a2:
                    href = a2.get('href', '')
                    l2 = "https://www.jaish.gr.jp/anzen/" + href.replace('../', '')
                    data.append({
                        "日付": "最新", 
                        "カテゴリ": "事故速報", 
                        "タイトル": a2.get_text(strip=True), 
                        "URL": l2, 
                        "ソース": "安全衛生情報センター"
                    })
    except:
        pass
    
    return pd.DataFrame(data)

st.title("🛡️ 安全衛生ニュース収集")

# サイドバーに更新ボタン
if st.sidebar.button("最新の情報に更新"):
    st.cache_data.clear()
    st.rerun()

with st.spinner('情報を取得しています...'):
    df = fetch_news()

if not df.empty:
    df = df.drop_duplicates(subset=['タイトル']).reset_index(drop=True)
    # デフォルトで全選択
    src_list = df["ソース"].unique().tolist()
    sources = st.sidebar.multiselect("フィルタ", src_list, default=src_list)
    disp = df[df["ソース"].isin(sources)]

    # 画面表示
    cols = st.columns(2)
    for i, (_, r) in enumerate(disp.iterrows()):
        with cols[i % 2]:
            with st.container(border=True):
                st.caption(f"{r['日付']} | {r['カテゴリ']}")
                st.markdown(f"**{r['タイトル']}**")
                st.link_button("詳細を開く", r['URL'])
else:
    st.info("現在ニュースを読み込めませんでした。サイトがメンテナンス中か、アクセスが制限されている可能性があります。")
    st.write("しばらく待ってから「最新の情報に更新」を押してみてください。")

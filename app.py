import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="安全衛生NEWS", layout="wide")

# ヘッダー（アクセスブロック回避用）
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
        
        news_section = soup.find('dl', class_='news_list')
        if news_section:
            dts = news_section.find_all('dt')
            dds = news_section.find_all('dd')
            for dt, dd in zip(dts[:10], dds[:10]):
                a_tag = dd.find('a')
                if a_tag:
                    news_list.append({
                        "日付": dt.get_text(strip=True),
                        "カテゴリ": "行政・事例",
                        "タイトル": a_tag.get_text(strip=True),
                        "URL": "https://anzeninfo.mhlw.go.

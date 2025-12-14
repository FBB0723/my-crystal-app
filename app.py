import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- 設定網頁標題 ---
st.set_page_config(page_title="F的礦圖鑑", page_icon="💎")

# --- 讀取資料函數 (維持不變) ---
# 請將下方的連結換成你 Google Sheet "發布到網路" 的 CSV 連結
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQe1zOKqN2u29JOZwM101MexXcI2l3TM5tFNieWaHgDQ8DAXClR9ab3NgKwxsj3w6AvrwcYaUxg2x1v/pub?gid=0&single=true&output=csv" 

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(sheet_url)
        if 'ID' not in df.columns:
            return pd.DataFrame()
        df['ID'] = df['ID'].astype(str)
        return df
    except Exception as e:
        return pd.DataFrame()

# --- 載入資料 ---
df = load_data()

# --- 手機版面設計 ---
st.title("💎 F的礦圖鑑")

# 檢查資料是否載入成功
if df.empty:
    st.error("⚠️ 資料讀取失敗，請檢查 CSV 連結是否正確！")
    st.stop()

# ==========================================
# 🔮 新功能：今日穿搭靈感 (Daily Inspiration)
# ==========================================
with st.expander("🔮 點擊查看【今日FuKi搭配】", expanded=True):
    # 1. 取得今天的日期作為隨機鑰匙 (例如 20231027)
    today_str = datetime.now().strftime("%Y%m%d")
    # 2. 設定隨機種子：保證今天不管開幾次，推薦的都一樣
    random.seed(int(today_str))
    
    # 3. 篩選出「服役中」的手串
    active_df = df[df['Status'] == '服役中']
    
    if len(active_df) < 2:
        st.warning("⚠️ 服役中的手串少於 2 條，無法推薦搭配喔！")
    else:
        # 4. 隨機抽出第一條 (主角)
        first_choice = active_df.sample(n=1, random_state=int(today_str)).iloc[0]
        
        # 5. 尋找第二條 (配角)：嘗試找「同色系」但「不同條」的
        # 先找同色系
        same_color_candidates = active_df[
            (active_df['Color'] == first_choice['Color']) & 
            (active_df['ID'] != first_choice['ID'])
        ]
        
        # 如果同色系有貨，就從裡面選；如果沒貨(例如這顏色只有一條)，就從全部剩餘的選
        if not same_color_candidates.empty:
            # 使用另一個隨機種子，避免跟第一條邏輯打架
            second_choice = same_color_candidates.sample(n=1, random_state=int(today_str)+1).iloc[0]
            match_type = "✨ 色系呼應"
        else:
            remaining = active_df[active_df['ID'] != first_choice['ID']]
            second_choice = remaining.sample(n=1, random_state=int(today_str)+1).iloc[0]
            match_type = "🌈 撞色驚喜"

        # 6. 顯示推薦結果
        st.markdown(f"### 📅 {datetime.now().strftime('%m/%d')} 今日建議：{match_type}")
        
        col_rec1, col_rec2 = st.columns(2)
        
        with col_rec1:
            st.caption("主要選擇")
            if pd.notna(first_choice['Image_URL']) and str(first_choice['Image_URL']).startswith('http'):
                st.image(first_choice['Image_URL'], use_container_width=True)
            else:
                st.markdown("📷 *無照片*")
            st.markdown(f"**#{first_choice['ID']} {first_choice['Name']}**")
            st.markdown(f"色系: {first_choice['Color']}")
            
        with col_rec2:
            st.caption("搭配建議")
            if pd.notna(second_choice['Image_URL']) and str(second_choice['Image_URL']).startswith('http'):
                st.image(second_choice['Image_URL'], use_container_width=True)
            else:
                st.markdown("📷 *無照片*")
            st.markdown(f"**#{second_choice['ID']} {second_choice['Name']}**")
            st.markdown(f"色系: {second_choice['Color']}")

# ==========================================
# 下方：原本的圖鑑與篩選功能
# ==========================================
st.markdown("---")
st.header("📚 全部收藏")

# 側邊欄：篩選工具
st.sidebar.header("🔍 篩選工具")
all_status = df['Status'].unique().tolist()
selected_status = st.sidebar.multiselect("狀態", all_status, default=["服役中"] if "服役中" in all_status else all_status)
all_colors = df['Color'].unique().tolist()
selected_color = st.sidebar.multiselect("色系", all_colors, default=[])
all_crystals = df['Main_Crystal'].unique().tolist()
selected_crystal = st.sidebar.multiselect("主要水晶", all_crystals, default=[])

# 執行篩選
filtered_df = df.copy()
if selected_status:
    filtered_df = filtered_df[filtered_df['Status'].isin(selected_status)]
if selected_color:
    filtered_df = filtered_df[filtered_df['Color'].isin(selected_color)]
if selected_crystal:
    filtered_df = filtered_df[filtered_df['Main_Crystal'].isin(selected_crystal)]

# 顯示清單
st.caption(f"顯示 {len(filtered_df)} / {len(df)} 條")

if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        with st.container():
            st.markdown("---") 
            c1, c2 = st.columns([1, 2])
            with c1:
                if pd.notna(row['Image_URL']) and str(row['Image_URL']).startswith('http'):
                    st.image(row['Image_URL'], use_container_width=True)
                else:
                    st.markdown("📷 *無照片*")
            with c2:
                st.subheader(f"#{row['ID']} {row['Name']}")
                st.write(f"🔮 {row['Main_Crystal']} | 🎨 {row['Color']} | 📏 {row['Size']}mm")
                if pd.notna(row['Note']):
                    st.info(f"{row['Note']}")
                # 狀態標籤
                if row['Status'] == '服役中':
                    st.success(row['Status'])
                elif row['Status'] == '已拆解':
                    st.warning(row['Status'])
                else:
                    st.secondary_action(row['Status'])
else:
    st.info("沒有符合條件的手串")

# 重新整理
if st.button('🔄 重新整理資料'):
    st.cache_data.clear()
    st.rerun()

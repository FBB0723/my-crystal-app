import streamlit as st
import pandas as pd

# --- 設定網頁標題 ---
st.set_page_config(page_title="我的水晶手串圖鑑", page_icon="💎")

# --- 讀取資料函數 ---
# 請將下方的連結換成你 Google Sheet "發布到網路" 的 CSV 連結
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQe1zOKqN2u29JOZwM101MexXcI2l3TM5tFNieWaHgDQ8DAXClR9ab3NgKwxsj3w6AvrwcYaUxg2x1v/pub?gid=0&single=true&output=csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(sheet_url)
        # 把 ID 轉成文字，避免變成數字運算
        df['ID'] = df['ID'].astype(str)
        return df
    except Exception as e:
        st.error(f"讀取資料失敗，請檢查連結是否正確。錯誤訊息: {e}")
        return pd.DataFrame()

# --- 載入資料 ---
df = load_data()

# --- 手機版面設計 ---
st.title("💎 我的水晶寶庫")

# 側邊欄：篩選條件
st.sidebar.header("🔍 篩選工具")

# 1. 狀態篩選 (預設排除已送人/已拆解，只看服役中，除非手動選)
all_status = df['Status'].unique().tolist()
selected_status = st.sidebar.multiselect("狀態", all_status, default=["服役中"] if "服役中" in all_status else all_status)

# 2. 色系篩選
all_colors = df['Color'].unique().tolist()
selected_color = st.sidebar.multiselect("色系", all_colors, default=[])

# 3. 水晶種類篩選
all_crystals = df['Main_Crystal'].unique().tolist()
selected_crystal = st.sidebar.multiselect("主要水晶", all_crystals, default=[])

# --- 執行篩選邏輯 ---
filtered_df = df.copy()

if selected_status:
    filtered_df = filtered_df[filtered_df['Status'].isin(selected_status)]

if selected_color:
    filtered_df = filtered_df[filtered_df['Color'].isin(selected_color)]

if selected_crystal:
    filtered_df = filtered_df[filtered_df['Main_Crystal'].isin(selected_crystal)]

# --- 顯示統計資訊 ---
st.caption(f"目前顯示 {len(filtered_df)} 條手串 (總收藏: {len(df)})")

# --- 顯示卡片式清單 ---
if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        with st.container():
            # 卡片邊框設計
            st.markdown("---") 
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # 顯示圖片，如果沒有連結就顯示預設文字
                if pd.notna(row['Image_URL']) and str(row['Image_URL']).startswith('http'):
                    st.image(row['Image_URL'], use_container_width=True)
                else:
                    st.markdown("📷 *無照片*")
            
            with col2:
                st.subheader(f"#{row['ID']} {row['Name']}")
                st.markdown(f"**種類:** {row['Main_Crystal']} | **色系:** {row['Color']}")
                st.markdown(f"**手圍:** {row['Size']}mm | **類型:** {row['Type']}")
                if pd.notna(row['Note']):
                    st.info(f"📝 {row['Note']}")
                
                # 狀態標籤顏色
                status = row['Status']
                if status == '服役中':
                    st.success(status)
                elif status == '已拆解':
                    st.warning(status)
                else:
                    st.secondary_action(status)
else:
    st.info("沒有找到符合條件的手串，試試看別的篩選條件？")

# --- 重新整理按鈕 (手機上方便更新) ---
if st.button('🔄 重新整理資料'):
    st.cache_data.clear()
    st.rerun()

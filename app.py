import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- 設定網頁標題 ---
st.set_page_config(page_title="F水晶手串圖鑑", page_icon="💎")

# ==========================================
# 🎨 介面樣式設定 (午後書店風 - Afternoon Bookstore)
# ==========================================
# 說明：這裡使用 CSS 來覆蓋 Streamlit 預設樣式，實現米色背景與抹茶綠按鈕
st.markdown("""
    <style>
    /* 1. 全站主背景：米色紙張感 */
    .stApp {
        background-color: #FDFBF7;
    }
    
    /* 2. 側邊欄背景：稍微深一點的米灰，增加層次 */
    section[data-testid="stSidebar"] {
        background-color: #F4F1EA;
    }

    /* 3. 文字顏色：深咖灰 (取代純黑，更溫柔) */
    h1, h2, h3, h4, h5, h6, p, li, .stMarkdown {
        color: #5A554E !important;
        font-family: 'Noto Serif TC', 'Songti TC', serif; /* 嘗試使用襯線體 */
    }
    
    /* 4. 按鈕樣式：抹茶綠 + 微圓角 */
    div.stButton > button {
        background-color: #8F9F7A !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #7A8C66 !important; /* 滑鼠經過變深 */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* 5. Expander (摺疊區) 樣式：白色底 + 細灰框 */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        border: 1px solid #E6E2D8 !important;
        border-radius: 8px !important;
        color: #5A554E !important;
    }
    div[data-testid="stExpander"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E6E2D8;
    }

    /* 6. 圖片樣式：加一點圓角 */
    img {
        border-radius: 12px;
    }
    
    /* 7. 狀態訊息框 (Success/Info/Warning) 微調 */
    .stAlert {
        border-radius: 8px;
        opacity: 0.9;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 讀取資料函數 (維持不變) ---
# ⚠️ 請記得確認這邊的 URL 是正確的
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
st.title("💎 F的水晶庫")

# 檢查資料是否載入成功
if df.empty:
    st.error("⚠️ 資料讀取失敗，請檢查 CSV 連結是否正確！")
    st.stop()

# ==========================================
# 🔮 新功能：今日穿搭靈感 (Daily Inspiration)
# ==========================================
# 這裡稍微調整標題文字，加上一點裝飾
with st.expander("✨ 點擊查看【今日午後靈感】", expanded=True):
    # 1. 取得今天的日期
    today_str = datetime.now().strftime("%Y%m%d")
    random.seed(int(today_str))
    
    # 2. 篩選出「服役中」的手串
    active_df = df[df['Status'] == '服役中']
    
    if len(active_df) < 2:
        st.warning("⚠️ 服役中的手串少於 2 條，無法推薦搭配喔！")
    else:
        # 3. 隨機抽出第一條 (主角)
        first_choice = active_df.sample(n=1, random_state=int(today_str)).iloc[0]
        
        # 4. 尋找第二條 (配角)
        same_color_candidates = active_df[
            (active_df['Color'] == first_choice['Color']) & 
            (active_df['ID'] != first_choice['ID'])
        ]
        
        if not same_color_candidates.empty:
            second_choice = same_color_candidates.sample(n=1, random_state=int(today_str)+1).iloc[0]
            match_type = "🍵 色系呼應・溫柔協調"
        else:
            remaining = active_df[active_df['ID'] != first_choice['ID']]
            second_choice = remaining.sample(n=1, random_state=int(today_str)+1).iloc[0]
            match_type = "🎨 撞色驚喜・獨特風格"

        # 5. 顯示推薦結果
        st.markdown(f"##### 📅 {datetime.now().strftime('%m/%d')} 穿搭建議：{match_type}")
        
        col_rec1, col_rec2 = st.columns(2)
        
        with col_rec1:
            st.caption("🌿 主要選擇")
            if pd.notna(first_choice['Image_URL']) and str(first_choice['Image_URL']).startswith('http'):
                st.image(first_choice['Image_URL'], use_container_width=True)
            else:
                st.markdown("📷 *無照片*")
            st.markdown(f"**#{first_choice['ID']} {first_choice['Name']}**")
            st.caption(f"色系: {first_choice['Color']}")
            
        with col_rec2:
            st.caption("🍂 搭配建議")
            if pd.notna(second_choice['Image_URL']) and str(second_choice['Image_URL']).startswith('http'):
                st.image(second_choice['Image_URL'], use_container_width=True)
            else:
                st.markdown("📷 *無照片*")
            st.markdown(f"**#{second_choice['ID']} {second_choice['Name']}**")
            st.caption(f"色系: {second_choice['Color']}")

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
st.caption(f"共收藏 {len(filtered_df)} 條美好") # 改了一點點文案

if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        with st.container():
            # 使用 CSS 讓這個 container 看起來像一張一張的小卡片
            # 這裡我們不寫額外的 CSS，保持簡潔，靠分隔線區隔
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
                    st.info(f"📝 {row['Note']}")
                # 狀態標籤
                if row['Status'] == '服役中':
                    st.success(row['Status'])
                elif row['Status'] == '已拆解':
                    st.warning(row['Status'])
                else:
                    st.caption(f"狀態：{row['Status']}")
else:
    st.info("沒有符合條件的手串")

# 重新整理
st.markdown("<br>", unsafe_allow_html=True) # 增加一點底部留白
if st.button('🔄 重新整理'):
    st.cache_data.clear()
    st.rerun()

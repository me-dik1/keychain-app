import streamlit as st
import random
import base64
import json

st.set_page_config(page_title="我的鎖匙扣抽籤", layout="wide", page_icon="🔑")

# 自訂CSS讓介面更漂亮
st.markdown("""
    <style>
    .stButton > button { background-color: #4CAF50; color: white; border-radius: 8px; }
    .stSuccess { background-color: #E8F5E9; }
    .stWarning { background-color: #FFF3E0; }
    .item { display: flex; align-items: center; margin-bottom: 10px; }
    .item img { max-width: 80px; margin-left: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🔑 我的鎖匙扣抽籤機")
st.markdown("可愛又實用的工具，記錄你的鎖匙扣收藏！")

# 初始化
if 'keychains' not in st.session_state:
    st.session_state.keychains = []  # list of dict: {'name': str, 'image': base64 or None}
if 'drawn' not in st.session_state:
    st.session_state.drawn = set()

# ==== 添加鎖匙扣 ====
with st.expander("➕ 添加新鎖匙扣", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("輸入名稱", placeholder="例如：香蕉、初音未來...")
    with col2:
        uploaded_file = st.file_uploader("上傳圖片（可選）", type=["jpg", "png", "jpeg"])
    add_col, shuffle_col = st.columns(2)
    if add_col.button("添加", use_container_width=True):
        if new_name.strip():
            image_base64 = None
            if uploaded_file:
                image_bytes = uploaded_file.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            st.session_state.keychains.append({'name': new_name.strip(), 'image': image_base64})
            st.success(f"已加入：{new_name.strip()}")
            st.rerun()
    if shuffle_col.button("隨機排序列表", use_container_width=True):
        random.shuffle(st.session_state.keychains)
        st.success("順序已打亂！")
        st.rerun()

# ==== 顯示列表 ====
if st.session_state.keychains:
    st.markdown(f"### 目前擁有（共 {len(st.session_state.keychains)} 個）")
    for i, kc in enumerate(st.session_state.keychains):
        col1, col2 = st.columns([3, 1])
        col1.write(f"{i+1}. {kc['name']}")
        if kc['image']:
            col2.image(f"data:image/png;base64,{kc['image']}", width=80)
else:
    st.info("還沒有鎖匙扣，快去添加吧！")

# ==== 抽籤 ====
st.markdown("---")
if st.session_state.keychains:
    available = [kc for kc in st.session_state.keychains if kc['name'] not in st.session_state.drawn]
    if available:
        if st.button("🎲 今日用哪個？抽！", use_container_width=True, type="primary"):
            chosen = random.choice(available)
            st.session_state.drawn.add(chosen['name'])
            st.balloons()
            st.success(f"抽中啦！！今天用：**{chosen['name']}**")
            if chosen['image']:
                st.image(f"data:image/png;base64,{chosen['image']}", width=200)
    else:
        st.warning("全部都用過了喔！")
else:
    st.info("請先添加鎖匙扣再來抽籤")

# ==== 抽取歷史 + 手動記錄 ====
with st.expander(f"📜 抽取歷史（已用 {len(st.session_state.drawn)} 個）"):
    if st.session_state.drawn:
        for name in st.session_state.drawn:
            kc = next((k for k in st.session_state.keychains if k['name'] == name), None)
            st.write(f"• {name}")
            if kc and kc['image']:
                st.image(f"data:image/png;base64,{kc['image']}", width=80)
    else:
        st.write("還沒用過任何一個")
    
    # 新功能: 手動記錄
    manual_available = [kc['name'] for kc in st.session_state.keychains if kc['name'] not in st.session_state.drawn]
    if manual_available:
        selected = st.selectbox("手動標記已用", manual_available)
        if st.button("標記為已用"):
            st.session_state.drawn.add(selected)
            st.success(f"已手動記錄：{selected}")
            st.rerun()

# ==== 重置 ====
col_reset, col_clear = st.columns(2)
if col_reset.button("重置抽籤記錄", use_container_width=True):
    st.session_state.drawn.clear()
    st.success("已重置！可以重新抽啦～")
    st.rerun()
if col_clear.button("⚠️ 清空所有資料", use_container_width=True):
    st.session_state.keychains = []
    st.session_state.drawn.clear()
    st.rerun()

# 雲端版自動儲存session，但若想手動備份，可加JSON下載
data = {'keychains': st.session_state.keychains, 'drawn': list(st.session_state.drawn)}
st.download_button("下載備份", json.dumps(data), "keychain_backup.json")

import streamlit as st
import random
import base64
import json
from datetime import date

st.set_page_config(page_title="鎖匙扣抽籤＋使用記錄", layout="centered", page_icon="🔑")

# 靚仔 CSS
st.markdown("""
<style>
    .big-button button {height: 60px !important; font-size: 20px !important;}
    .used-today {background-color: #E8F5E9; padding: 10px; border-radius: 10px; margin: 10px 0;}
    .stButton > button {border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

st.title("🔑 我的鎖匙扣抽籤＋使用記錄")

# 初始化
if 'keychains' not in st.session_state:
    st.session_state.keychains = []      # [{'name': '香蕉', 'image': base64}]
if 'drawn_history' not in st.session_state:   # 抽籤歷史（自動）
    st.session_state.drawn_history = set()
if 'used_records' not in st.session_state:    # 實際使用記錄（手動）
    st.session_state.used_records = {}   # { "2025-12-09": "香蕉" }

# ==================== 1. 添加鎖匙扣 ====================
with st.expander("➕ 添加新鎖匙扣", expanded=True):
    c1, c2 = st.columns(2)
    name = c1.text_input("名稱", placeholder="例如：香蕉、初音、史努比")
    pic = c2.file_uploader("圖片（可選）", type=["png","jpg","jpeg","webp"])
    a1, a2 = st.columns(2)
    if a1.button("✅ 添加", use_container_width=True):
        if name.strip():
            img64 = None
            if pic:
                img64 = base64.b64encode(pic.read()).decode()
            st.session_state.keychains.append({"name": name.strip(), "image": img64})
            st.success(f"已加入：{name.strip()}")
            st.rerun()
    if a2.button("🎲 隨機排序", use_container_width=True):
        random.shuffle(st.session_state.keychains)
        st.success("順序已打亂")
        st.rerun()

# ==================== 2. 當前列表 ====================
st.subheader(f"📋 目前擁有 {len(st.session_state.keychains)} 個")
for i, item in enumerate(st.session_state.keychains):
    c1, c2 = st.columns([4,1])
    c1.write(f"**{i+1}. {item['name']}**")
    if item['image']:
        c2.image(f"data:image/png;base64,{item['image']}", width=80)

# ==================== 3. 抽籤區（自動記錄） ====================
st.markdown("---")
if st.session_state.keychains:
    未抽過 = [k for k in st.session_state.keychains if k['name'] not in st.session_state.drawn_history]
    if 未抽過:
        if st.button("🎲 今日運勢！抽一個！", use_container_width=True, type="primary"):
            chosen = random.choice(未抽過)
            st.session_state.drawn_history.add(chosen['name'])
            st.balloons()
            st.success(f"抽中：**{chosen['name']}**")
            if chosen['image']:
                st.image(f"data:image/png;base64,{chosen['image']}", width=200)
    else:
        st.warning("⚠️ 全部都抽過晒！")
        if st.button("重置抽籤歷史"):
            st.session_state.drawn_history.clear()
            st.rerun()
else:
    st.info("請先添加鎖匙扣")

# ==================== 4. 實際使用記錄（全新手動區） ====================
st.markdown("---")
st.subheader("✍️ 今日實際用咗邊個？（手動記錄）")

today = date.today().isoformat()
today_used = st.session_state.used_records.get(today)

if today_used:
    kc = next((k for k in st.session_state.keychains if k['name']==today_used), None)
    st.markdown(f"<div class='used-today'>✅ 今日已記錄使用：<b>{today_used}</b></div>", 
                unsafe_allow_html=True)
    if kc and kc['image']:
        st.image(f"data:image/png;base64,{kc['image']}", width=150)

# 手動選擇今天用咗邊個
options = [k['name'] for k in st.session_state.keychains]
selected = st.selectbox("選擇今日實際使用的鎖匙扣", [""] + options, index=0 if not today_used else options.index(today_used)+1)

colA, colB = st.columns(2)
if colA.button("✔️ 記錄今日使用", use_container_width=True, type="primary"):
    if selected:
        st.session_state.used_records[today] = selected
        st.success(f"已記錄：今日用咗 {selected}")
        st.rerun()
if colB.button("🗑️ 刪除今日記錄", use_container_width=True):
    st.session_state.used_records.pop(today, None)
    st.rerun()

# ==================== 歷史區分開顯示 ====================
col1, col2 = st.columns(2)
with col1:
    with st.expander("🎲 抽籤歷史（自動）"):
        if st.session_state.drawn_history:
            for n in st.session_state.drawn_history:
                st.write(f"• {n}")
        else:
            st.write("未有")
with col2:
    with st.expander("✍️ 實際使用日曆"):
        for d, name in sorted(st.session_state.used_records.items(), reverse=True):
            st.write(f"**{d}** → {name}")

# ==================== 重置 & 備份 ====================
st.markdown("---")
c1, c2, c3 = st.columns(3)
if c1.button("重置抽籤歷史"):
    st.session_state.drawn_history.clear()
    st.rerun()
if c2.button("清空實際使用記錄"):
    st.session_state.used_records.clear()
    st.rerun()
if c3.button("⚠️ 全部清空"):
    st.session_state.keychains = []
    st.session_state.drawn_history = set()
    st.session_state.used_records = {}
    st.rerun()

# 備份功能
backup = {
    "keychains": st.session_state.keychains,
    "drawn": list(st.session_state.drawn_history),
    "used": st.session_state.used_records
}
st.download_button("💾 下載備份", json.dumps(backup, ensure_ascii=False), "鎖匙扣備份.json")

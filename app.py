import streamlit as st
import random
import base64
import json
from datetime import date
import firebase_admin
from firebase_admin import credentials, firestore, auth
import extra_streamlit_components as stx
import jwt
from functools import partial
from typing import Optional

# 美化CSS（漸變背景、字體、主題）
st.markdown("""
<style>
    .stApp { background: linear-gradient(to bottom right, #f0f8ff, #e0f7fa); font-family: 'Serif', serif; }
    .card { background: #ffffff; border: 2px solid #4CAF50; border-radius: 15px; padding: 20px; margin: 15px 0; box-shadow: 0 6px 12px rgba(0,0,0,0.15); }
    .stButton > button { background: linear-gradient(to right, #4CAF50, #2196F3); color: white; border-radius: 12px; font-size: 16px; padding: 10px; }
    .stDataFrame { border: 1px solid #ddd; border-radius: 10px; }
    .green-check { color: green; font-weight: bold; }
    .gray-blank { color: gray; }
    h1, h2, h3 { color: #2c3e50; }
    .sidebar .stRadio > div { background: #e8f5e9; border-radius: 10px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# Firebase初始化（用secrets）
if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"]))
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Auth functions (simplified from gist)
def authenticate_user(email, password):
    try:
        user = auth.verify_id_token(auth.sign_in_with_email_and_password(email, password)['idToken'])
        return user['localId']
    except:
        return None

def register_user(email, password, name):
    try:
        user = auth.create_user(email=email, password=password, display_name=name)
        return user.uid
    except:
        return None

# Session & Auth
cookie_manager = stx.b64_cookie_manager()
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# 登入/註冊頁
if not st.session_state.user_id:
    st.title("請登入或註冊")
    tab1, tab2 = st.tabs(["登入", "註冊"])
    with tab1:
        email = st.text_input("電郵")
        password = st.text_input("密碼", type="password")
        if st.button("登入"):
            uid = authenticate_user(email, password)
            if uid:
                st.session_state.user_id = uid
                st.rerun()
            else:
                st.error("登入失敗")
    with tab2:
        new_email = st.text_input("新電郵")
        new_name = st.text_input("名字")
        new_password = st.text_input("新密碼", type="password")
        if st.button("註冊"):
            uid = register_user(new_email, new_password, new_name)
            if uid:
                st.success("註冊成功，請登入")
            else:
                st.error("註冊失敗")
    st.stop()

# 載入數據從Firestore
doc_ref = db.collection("users").document(st.session_state.user_id)
data = doc_ref.get().to_dict() or {}
st.session_state.keychains = data.get("keychains", [])
st.session_state.drawn = set(data.get("drawn", []))
st.session_state.used = set(data.get("used", []))  # 改為set，記錄用過邊樣

# 保存函數
def save_data():
    doc_ref.set({
        "keychains": st.session_state.keychains,
        "drawn": list(st.session_state.drawn),
        "used": list(st.session_state.used)
    })

# Sidebar按鈕列表分頁
page = st.sidebar.radio("頁面", ["主頁（抽籤）", "管理檔案庫", "備份與匯入"])

if page == "主頁（抽籤）":
    st.title("🔑 我的鎖匙扣抽籤")
    if st.session_state.keychains:
        avail = [k for k in st.session_state.keychains if k['name'] not in st.session_state.drawn]
        if avail:
            if st.button("🎲 抽一個！", type="primary", use_container_width=True):
                win = random.choice(avail)
                st.session_state.drawn.add(win['name'])
                save_data()
                st.balloons()
                st.success(f"抽中：**{win['name']}**")
                if win['image']: st.image(f"data:image/png;base64,{win['image']}", width=200)
        else:
            st.warning("全部抽晒！")
            if st.button("重置抽籤歷史"): st.session_state.drawn.clear(); save_data(); st.rerun()
    else:
        st.info("請先添加鎖匙扣")

elif page == "管理檔案庫":
    st.title("📂 檔案庫管理 + 歷史統計")
    # 添加
    with st.expander("➕ 添加新鎖匙扣", expanded=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("名稱")
        pic = c2.file_uploader("圖片")
        a1, a2 = st.columns(2)
        if a1.button("添加"):
            if name.strip():
                img64 = None if not pic else base64.b64encode(pic.read()).decode()
                st.session_state.keychains.append({"name": name.strip(), "image": img64})
                save_data()
                st.rerun()
        if a2.button("隨機排序"):
            random.shuffle(st.session_state.keychains)
            save_data()
            st.rerun()

    # 表格顯示所有 + 狀態 + 編輯
    st.subheader(f"擁有 {len(st.session_state.keychains)} 個 | 抽過 {len(st.session_state.drawn)} 個 | 用過 {len(st.session_state.used)} 個")
    if st.session_state.keychains:
        df_data = []
        for i, k in enumerate(st.session_state.keychains):
            drawn_mark = '<span class="green-check">✓</span>' if k['name'] in st.session_state.drawn else '<span class="gray-blank">-</span>'
            used_mark = '<span class="green-check">✓</span>' if k['name'] in st.session_state.used else '<span class="gray-blank">-</span>'
            preview = f'<img src="data:image/png;base64,{k["image"]}" width="50">' if k['image'] else ''
            df_data.append({
                "編號": i+1,
                "名稱": k['name'],
                "預覽": preview,
                "抽過": drawn_mark,
                "用過": used_mark
            })
        st.dataframe(df_data, use_container_width=True, hide_index=True)  # 修正error，用dataframe

    # 編輯/刪除/狀態toggle
    with st.expander("✏️ 編輯/刪除/狀態"):
        sel = st.selectbox("選擇鎖匙扣", [""] + [k['name'] for k in st.session_state.keychains])
        if sel:
            idx = next(i for i,k in enumerate(st.session_state.keychains) if k['name']==sel)
            new_name = st.text_input("新名稱", value=st.session_state.keychains[idx]['name'])
            new_pic = st.file_uploader("加/換圖片")
            c1,c2,c3,c4 = st.columns(4)
            if c1.button("保存編輯"):
                if new_name.strip(): st.session_state.keychains[idx]['name'] = new_name.strip()
                if new_pic: st.session_state.keychains[idx]['image'] = base64.b64encode(new_pic.read()).decode()
                save_data(); st.rerun()
            if c2.button("刪除"):
                del st.session_state.keychains[idx]; save_data(); st.rerun()
            if c3.button("標記用過" if sel not in st.session_state.used else "取消用過"):
                if sel in st.session_state.used: st.session_state.used.remove(sel)
                else: st.session_state.used.add(sel)
                save_data(); st.rerun()
            if c4.button("重置這個抽過"):
                if sel in st.session_state.drawn: st.session_state.drawn.remove(sel); save_data(); st.rerun()

elif page == "備份與匯入":
    st.title("💾 備份（雲端自動，但可手動）")
    backup = {"keychains": st.session_state.keychains, "drawn": list(st.session_state.drawn), "used": list(st.session_state.used)}
    st.download_button("下載本地備份", json.dumps(backup, ensure_ascii=False), f"備份_{date.today()}.json")
    up = st.file_uploader("匯入本地備份", type="json")
    if up:
        data = json.load(up)
        st.session_state.keychains = data.get("keychains", [])
        st.session_state.drawn = set(data.get("drawn", []))
        st.session_state.used = set(data.get("used", []))
        save_data()
        st.success("匯入成功"); st.rerun()

# 登出
if st.sidebar.button("登出"):
    st.session_state.user_id = None
    st.rerun()

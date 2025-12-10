import streamlit as st
import random
import base64
import json
from datetime import date
from firebase_admin import credentials, firestore, auth

# ============ Firebase 初始化 (用secrets) ============
if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"]))
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ============ 登入/註冊 (Email/Password) ============
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    tab1, tab2 = st.tabs(["登入", "註冊"])
    with tab1:
        email = st.text_input("電郵")
        pwd = st.text_input("密碼", type="password")
        if st.button("登入"):
            try:
                user = auth.get_user_by_email(email)
                st.session_state.user = user.uid
                st.success("登入成功")
                st.rerun()
            except:
                st.error("登入失敗")
    with tab2:
        new_email = st.text_input("新電郵")
        new_pwd = st.text_input("新密碼", type="password")
        if st.button("註冊"):
            try:
                user = auth.create_user(email=new_email, password=new_pwd)
                st.session_state.user = user.uid
                st.success("註冊成功，請登入")
            except:
                st.error("註冊失敗")
    st.stop()

# ============ 載入/儲存數據 (Firestore) ============
doc_ref = db.collection("users").document(st.session_state.user)
data = doc_ref.get().to_dict() or {"items": [], "drawn": [], "used": []}
items = data["items"]
drawn = set(data["drawn"])
used = set(data["used"])

def save():
    doc_ref.set({"items": items, "drawn": list(drawn), "used": list(used)})

# ============ 美化 (用搜索圖片URL做裝飾) ============
st.set_page_config(page_title="鎖匙扣App", layout="wide")
st.markdown("""
<style>
    .stApp {background: linear-gradient(to bottom right, #e0f2fe, #bfdbfe); color: #1e40af; font-family: Arial, sans-serif;}
    .stTabs [data-testid="stTab"] {background: #3b82f6; color: white; border-radius: 12px; padding: 12px 24px; margin: 0 10px;}
    .stButton>button {background: #3b82f6; color: white; border-radius: 12px; padding: 12px 24px; font-size: 18px;}
    .deco {position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; opacity: 0.1; z-index: -1;}
    .deco img {position: absolute; animation: float 20s infinite linear;}
    @keyframes float {0% {transform: translateY(100vh) rotate(0deg);} 100% {transform: translateY(-100px) rotate(360deg);}}
</style>
<div class="deco">
    <img src="https://www.shutterstock.com/image-vector/keychains-set-decorations-isolated-on-600nw-2505596473.jpg" style="top:10%;left:10%;animation-delay:0s;" width=100>
    <img src="https://www.shutterstock.com/image-vector/cute-keychain-icons-set-design-260nw-2634129399.jpg" style="top:30%;left:70%;animation-delay:5s;" width=100>
    <img src="https://i.etsystatic.com/31957251/r/il/ca076c/3824465843/il_1080xN.3824465843_c005.jpg" style="top:60%;left:20%;animation-delay:10s;" width=100>
</div>
""", unsafe_allow_html=True)

# ============ 按鈕分頁 (tabs) ============
tab1, tab2, tab3 = st.tabs(["抽籤主頁", "檔案庫管理", "備份"])

with tab1:
    st.title("抽籤主頁")
    if items:
        avail = [k for k in items if k["name"] not in drawn]
        if avail:
            if st.button("抽籤！"):
                win = random.choice(avail)
                drawn.add(win["name"])
                save()
                st.balloons()
                st.success(f"抽中：{win['name']}")
                if win["image"]:
                    st.image(f"data:image/png;base64,{win['image']}", width=250)
        else:
            st.warning("全部抽過晒！")
            if st.button("重置抽籤記錄"):
                drawn.clear()
                save()
                st.rerun()
    else:
        st.info("去檔案庫管理加鎖匙扣啦")

with tab2:
    st.title("檔案庫管理")
    name = st.text_input("名稱")
    pic = st.file_uploader("圖片")
    if st.button("加入"):
        if name.strip():
            img64 = base64.b64encode(pic.read()).decode() if pic else None
            items.append({"name": name.strip(), "image": img64})
            save()
            st.success("加入成功")
            st.rerun()

    st.subheader(f"總 {len(items)} 個 | 抽過 {len(drawn)} | 用過 {len(used)}")
    for i, k in enumerate(items[:]):
        cols = st.columns([3,2,1,1,3])
        cols[0].write(f"{i+1}. {k['name']}")
        if k["image"]:
            cols[1].image(f"data:image/png;base64,{k['image']}", width=80)
        cols[2].write("✓" if k["name"] in drawn else "—")
        cols[3].write("✓" if k["name"] in used else "—")
        if cols[4].button("用過", key=f"use_{i}"):
            if k["name"] in used: used.remove(k["name"])
            else: used.add(k["name"])
            save()
            st.rerun()
        if st.button("刪除", key=f"del_{i}"):
            items.pop(i)
            save()
            st.rerun()
        if st.button("編輯圖片", key=f"edit_{i}"):
            new_pic = st.file_uploader("換圖片", key=f"new_pic_{i}")
            if new_pic:
                k["image"] = base64.b64encode(new_pic.read()).decode()
                save()
                st.success("圖片更新成功")
                st.rerun()

with tab3:
    st.title("備份")
    backup = json.dumps({"items": items, "drawn": list(drawn), "used": list(used)}, ensure_ascii=False)
    st.download_button("下載備份", backup, f"備份_{date.today()}.json")
    uploaded = st.file_uploader("上載備份", type="json")
    if uploaded:
        newdata = json.load(uploaded)
        items[:] = newdata["items"]
        drawn = set(newdata["drawn"])
        used = set(newdata["used"])
        save()
        st.success("還原成功")
        st.rerun()

# ============ 登出 ============
if st.sidebar.button("登出"):
    st.session_state.logged_in = False
    st.rerun()

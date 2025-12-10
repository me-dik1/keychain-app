import streamlit as st
import random
import base64
import json
from datetime import date

# ============ 密碼（改這行）============
PASSWORD = "123456"  # ← 改成你想要的密碼

# ============ 登入頁 ============
if st.session_state.get("auth") != True:
    st.title("登入我的鎖匙扣 App")
    pwd = st.text_input("密碼", type="password")
    if st.button("登入"):
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("密碼錯誤")
    st.stop()

# ============ 美化（高對比：淺藍底 + 深藍字 + 裝飾）============
st.markdown("""
<style>
    .stApp {background: #f0f7ff; color: #1e3a8a; font-family: 'Arial', sans-serif;}
    .header {text-align: center; color: #1d4ed8;}
    .stButton>button {background: #3b82f6; color: white; border-radius: 12px; padding: 12px 24px; font-size: 18px;}
    .stTextInput > div > div > input {border-radius: 10px; border: 2px solid #93c5fd;}
    .stFileUploader {border: 2px dashed #93c5fd; border-radius: 12px; padding: 20px;}
    .green {color: #15803d;}
    .gray {color: #6b7280;}
    .deco {position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; opacity: 0.1; z-index: -1;}
    .deco img {position: absolute; animation: float 20s infinite linear;}
    @keyframes float {0% {transform: translateY(100vh) rotate(0deg);} 100% {transform: translateY(-100px) rotate(360deg);}}
</style>
<div class="deco">
    <img src="https://i.pinimg.com/originals/1f/3d/9a/1f3d9a8f8f8f8f8f8f8f8f8f8f8f8f8f.jpg" style="top:10%;left:10%;animation-delay:0s;" width=100>
    <img src="https://i.pinimg.com/originals/2g/4e/9b/2g4e9b8f8f8f8f8f8f8f8f8f8f8f8f8f.jpg" style="top:30%;left:70%;animation-delay:5s;" width=100>
    <img src="https://i.pinimg.com/originals/3h/5f/9c/3h5f9c8f8f8f8f8f8f8f8f8f8f8f8f8f.jpg" style="top:60%;left:20%;animation-delay:10s;" width=100>
</div>
""", unsafe_allow_html=True)

# ============ 數據儲存（關閉不丟）============
DATA_KEY = "keychain_data"
if DATA_KEY not in st.session_state:
    saved = st.query_params.get("d")
    if saved:
        try:
            st.session_state[DATA_KEY] = json.loads(saved[0])
        except:
            st.session_state[DATA_KEY] = {"items": [], "drawn": [], "used": []}
    else:
        st.session_state[DATA_KEY] = {"items": [], "drawn": [], "used": []}

data = st.session_state[DATA_KEY]
items = data["items"]
drawn = set(data["drawn"])
used = set(data["used"])

def save():
    st.session_state[DATA_KEY] = {"items": items, "drawn": list(drawn), "used": list(used)}
    st.query_params["d"] = json.dumps(st.session_state[DATA_KEY], ensure_ascii=False)

# ============ 按鈕分頁 ============
tab1, tab2, tab3 = st.tabs(["抽籤主頁", "檔案庫管理", "備份與同步"])

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
    name = st.text_input("名稱", key="add_name")
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
        cols[0].write(k["name"])
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
    st.title("備份與同步")
    backup = json.dumps(data, ensure_ascii=False)
    st.download_button("下載備份", backup, f"備份_{date.today()}.json")
    uploaded = st.file_uploader("上載備份", type="json")
    if uploaded:
        newdata = json.load(uploaded)
        st.session_state.data = newdata
        save()
        st.success("還原成功")
        st.rerun()

    # 同步 link
    sync_link = f"{st.experimental_get_url()}?d={st.query_params.get('d','')[0] if st.query_params.get('d') else ''}"
    st.text_input("同步 link（抄低換手機用）", sync_link)
    st.info("換手機打開呢條 link 就自動同步資料！")

# 登出
if st.sidebar.button("登出"):
    st.session_state.auth = False
    st.rerun()

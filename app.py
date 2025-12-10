import streamlit as st
import random
import base64
import json
from datetime import date

# 密碼（改呢度）
PASSWORD = "123456"

if st.session_state.get("ok") != True:
    pwd = st.text_input("輸入密碼", type="password")
    if st.button("登入") or pwd == PASSWORD:
        if pwd == PASSWORD:
            st.session_state.ok = True
            st.rerun()
        else:
            st.error("錯")
    st.stop()

# 高對比美化
st.markdown("<style>.stApp{background:#fffbeb;color:#1e293b;font-family:Arial}</style>", unsafe_allow_html=True)

# 數據
if "data" not in st.session_state:
    saved = st.query_params.get("s")
    if saved:
        try: st.session_state.data = json.loads(saved)
        except: st.session_state.data = {"items":[],"drawn":[],"used":[]}
    else:
        st.session_state.data = {"items":[],"drawn":[],"used":[]}

items = st.session_state.data["items"]
drawn = set(st.session_state.data["drawn"])
used = set(st.session_state.data["used"])

def save():
    st.query_params["s"] = json.dumps(st.session_state.data, ensure_ascii=False)

# 分頁
page = st.radio("頁面", ["抽籤", "管理", "同步/備份"], horizontal=True)

if page == "抽籤":
    st.title("今日用邊個？")
    if items:
        avail = [x for x in items if x["name"] not in drawn]
        if avail and st.button("抽！", use_container_width=True):
            w = random.choice(avail)
            drawn.add(w["name"])
            save()
            st.balloons()
            st.success(w["name"])
            if w["image"]: st.image(f"data:image/png;base64,{w['image']}", width=200)

if page == "管理":
    st.title("管理鎖匙扣")
    name = st.text_input("名稱")
    pic = st.file_uploader("圖片")
    if st.button("加入") and name:
        img64 = base64.b64encode(pic.read()).decode() if pic else None
        items.append({"name":name.strip(),"image":img64})
        save()
        st.rerun()

    for i, x in enumerate(items):
        c1,c2,c3,c4 = st.columns([3,2,1,3])
        c1.write(f"**{x['name']}**")
        if x["image"]: c2.image(f"data:image/png;base64,{x['image']}", width=80)
        c3.write("Check" if x["name"] in used else "—")
        if c4.button("用過/取消", key=f"u{i}"):
            used.symmetric_difference_update([x["name"]])
            save()
            st.rerun()
        if st.button("刪除", key=f"d{i}"):
            items.pop(i)
            save()
            st.rerun()

if page == "同步/備份":
    st.title("同步與備份")
    current_link = st.text_input("你嘅專屬同步 link（抄低發俾自己）", value=st.experimental_get_url() + f"?s={st.query_params.get('s','')}")
    st.code(current_link)
    st.info("下次用任何手機/電腦打開呢條 link 就即刻有返晒你嘅鎖匙扣！")
    st.download_button("下載備份檔", json.dumps(st.session_state.data), "backup.json")

if st.sidebar.button("登出"):
    st.session_state.ok = False
    st.rerun()

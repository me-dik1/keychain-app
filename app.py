import streamlit as st
import random
import base64
import json
from datetime import date

# ============ 1. 密碼（改這行）============
PASSWORD = "123456"   # ← 改你想要嘅密碼

# ============ 簡單登入（無怪 UI）============
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("我的鎖匙扣 App")
    pwd = st.text_input("請輸入密碼", type="password")
    if st.button("登入"):
        if pwd == PASSWORD:
            st.session_state.logged_in = True
            st.success("登入成功！")
            st.rerun()
        else:
            st.error("密碼錯誤")
    st.stop()

# ============ 2. 超簡單高對比美化（淺底 + 深字）============
st.markdown("""
<style>
    .stApp {background: #f0f2f6; color: #1e293b; font-family: Arial, sans-serif;}
    h1, h2, h3 {color: #1e40af;}
    .stButton>button {background: #3b82f6; color: white; border-radius: 12px; padding: 12px 24px; font-size: 18px;}
    .stTextInput > div > div > input {border-radius: 10px; border: 2px solid #93c5fd;}
    .stFileUploader {border: 2px dashed #93c5fd; border-radius: 12px; padding: 20px;}
</style>
""", unsafe_allow_html=True)

# ============ 側邊欄分頁（簡單大按鈕）============
st.sidebar.title("導航")
page = st.sidebar.radio("去邊頁？", ["抽籤主頁", "檔案庫管理", "備份"])

# ============ 數據儲存（關閉不丟）============
if "data" not in st.session_state:
    saved = st.query_params.get("d")
    if saved:
        try:
            st.session_state.data = json.loads(saved)
        except:
            st.session_state.data = {"items": [], "drawn": [], "used": []}
    else:
        st.session_state.data = {"items": [], "drawn": [], "used": []}

items = st.session_state.data["items"]        # [{"name":"香蕉", "image":base64}]
drawn = set(st.session_state.data["drawn"])   # 已抽過
used = set(st.session_state.data["used"])     # 已用過

def save():
    st.session_state.data = {"items": items, "drawn": list(drawn), "used": list(used)}
    st.query_params["d"] = json.dumps(st.session_state.data, ensure_ascii=False)

# ============ 抽籤主頁 ============
if page == "抽籤主頁":
    st.title("今日用邊個鎖匙扣？")
    
    if not items:
        st.info("你仲未加鎖匙扣，快啲去「檔案庫管理」加啦！")
    else:
        available = [x for x in items if x["name"] not in drawn]
        if available:
            if st.button("抽籤！", use_container_width=True):
                win = random.choice(available)
                drawn.add(win["name"])
                save()
                st.balloons()
                st.success(f"抽中：{win['name']}")
                if win["image"]:
                    st.image(f"data:image/png;base64,{win['image']}", width=250)
        else:
            st.warning("全部都抽過晒！")
            if st.button("重置抽籤記錄"):
                drawn.clear()
                save()
                st.rerun()

# ============ 檔案庫管理（重點：完全解決 Enter 跳頁）============
elif page == "檔案庫管理":
    st.title("檔案庫管理")
    
    # 獨立區塊，完全唔會影響分頁
    st.header("新增鎖匙扣")
    with st.container():
        name = st.text_input("名稱", key="add_name")
        pic = st.file_uploader("圖片（可選）", type=["png","jpg","jpeg","webp","gif"], key="add_pic")
        if st.button("加入", key="add_btn"):
            if name.strip():
                img64 = base64.b64encode(pic.read()).decode() if pic else None
                items.append({"name": name.strip(), "image": img64})
                save()
                st.success(f"已加入：{name.strip()}")
                st.rerun()
            else:
                st.error("請輸入名稱")

    st.divider()
    st.subheader(f"現有 {len(items)} 個（抽過 {len(drawn)} ⋅ 用過 {len(used)}）")

    # 每行獨立 key，絕不重複
    for i in range(len(items)):
        item = items[i]
        cols = st.columns([3, 2, 1, 1, 2])
        cols[0].write(f"**{i+1}. {item['name']}**")
        if item["image"]:
            cols[1].image(f"data:image/png;base64,{item['image']}", width=80)
        cols[2].write("Check" if item["name"] in drawn else "—")
        cols[3].write("Check" if item["name"] in used else "—")
        if cols[4].button("用過/取消", key=f"use_{i}"):
            if item["name"] in used:
                used.remove(item["name"])
            else:
                used.add(item["name"])
            save()
            st.rerun()
        if st.button("刪除", key=f"del_{i}"):
            items.pop(i)
            save()
            st.rerun()

# ============ 備份 ============
else:
    st.title("備份與還原")
    backup = json.dumps(st.session_state.data, ensure_ascii=False)
    st.download_button("下載備份", backup, f"鎖匙扣備份_{date.today()}.json")
    uploaded = st.file_uploader("上載備份還原", type=["json"])
    if uploaded:
        try:
            newdata = json.load(uploaded)
            st.session_state.data = newdata
            save()
            st.success("還原成功")
            st.rerun()
        except:
            st.error("檔案錯誤")

# ============ 登出 ============
if st.sidebar.button("登出"):
    st.session_state.logged_in = False
    st.rerun()

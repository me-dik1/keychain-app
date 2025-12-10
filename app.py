import streamlit as st
import random
import base64
import json
from datetime import date

# ============ 密碼保護（改這行）============
PASSWORD = "123456"  # ← 改成你自己的密碼

if st.session_state.get("authenticated") != True:
    st.markdown("""
    <style>
        body {background: linear-gradient(135deg, #667eea, #764ba2);}
        .login-container {max-width: 400px; margin: 150px auto; padding: 40px; background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); text-align: center;}
        .login-container input {width: 100%; padding: 15px; margin: 10px 0; border-radius: 12px; border: 1px solid #ddd; font-size: 18px;}
        .login-container button {width: 100%; padding: 15px; background: #e74c3c; border: none; border-radius: 12px; color: white; font-size: 18px;}
    </style>
    <div class="login-container">
        <h1>我的鎖匙扣</h1>
        <p>請輸入密碼</p>
    </div>
    """, unsafe_allow_html=True)
    
    pwd = st.text_input("密碼", type="password", label_visibility="collapsed")
    if st.button("登入") or st.session_state.get("enter_pressed", False):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.session_state.enter_pressed = False
            st.rerun()
        else:
            st.error("密碼錯誤")
    st.stop()

# ============ 全站美化（深紫高對比 + 靚字體）============
st.set_page_config(page_title="鎖匙扣神器", layout="centered", page_icon="key")

st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #2c3e50, #8e44ad); color: #ecf0f1; font-family: 'Segoe UI', sans-serif;}
    .header {background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 20px; padding: 20px; text-align: center; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.5);}
    .card {background: rgba(255,255,255,0.1); border-radius: 20px; padding: 25px; margin: 20px 0; backdrop-filter: blur(10px);}
    .stButton>button {background: linear-gradient(45deg, #e74c3c, #f39c12); color: white; border-radius: 18px; font-size: 18px; padding: 15px; border: none; box-shadow: 0 5px 15px rgba(0,0,0,0.4);}
    .stButton>button:hover {transform: translateY(-3px);}
    .green {color: #2ecc71; font-size: 2.2em; font-weight: bold;}
    .gray {color: #95a5a6; font-size: 2.2em;}
    .sidebar .stButton>button {background: #34495e; margin: 15px 0; border-radius: 15px;}
</style>
""", unsafe_allow_html=True)

# ============ 靚分頁按鈕（收在側邊欄）============
st.sidebar.markdown("### 頁面導航")
page1 = st.sidebar.button("抽籤主頁", use_container_width=True)
page2 = st.sidebar.button("檔案庫管理", use_container_width=True)
page3 = st.sidebar.button("備份與還原", use_container_width=True)

if page1 or (not page1 and not page2 and not page3):
    current_page = "抽籤主頁"
elif page2:
    current_page = "檔案庫管理"
else:
    current_page = "備份與還原"

# ============ 數據儲存（關閉不丟）============
DATA_KEY = "keychain_data"
if DATA_KEY not in st.session_state:
    saved = st.query_params.get("data")
    if saved:
        try:
            st.session_state[DATA_KEY] = json.loads(saved)
        except:
            pass
    if DATA_KEY not in st.session_state:
        st.session_state[DATA_KEY] = {"keychains": [], "drawn": [], "used": []}

data = st.session_state[DATA_KEY]
keychains = data["keychains"]
drawn = set(data["drawn"])
used = set(data["used"])

def save():
    st.session_state[DATA_KEY] = {"keychains": keychains, "drawn": list(drawn), "used": list(used)}
    st.query_params["data"] = json.dumps(st.session_state[DATA_KEY], ensure_ascii=False)

# ============ 主頁 ============
if current_page == "抽籤主頁":
    st.markdown('<div class="header"><h1>今日用邊個鎖匙扣？</h1></div>', unsafe_allow_html=True)
    
    if keychains:
        avail = [k for k in keychains if k["name"] not in drawn]
        if avail:
            if st.button("抽！", use_container_width=True, type="primary"):
                win = random.choice(avail)
                drawn.add(win["name"])
                save()
                st.balloons()
                st.success(f"抽中：{win['name']} 🎉")
                if win["image"]:
                    st.image(f"data:image/png;base64,{win['image']}", width=300)
        else:
            st.warning("全部都抽過晒！")
            if st.button("重置抽籤記錄"):
                drawn.clear()
                save()
                st.rerun()
    else:
        st.info("快啲去「檔案庫管理」加鎖匙扣啦～")

# ============ 檔案庫管理 ============
elif current_page == "檔案庫管理":
    st.markdown('<div class="header"><h1>檔案庫管理</h1></div>', unsafe_allow_html=True)
    
    # 添加
    with st.expander("➕ 添加新鎖匙扣", expanded=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("名稱", key="new_name")
        pic = c2.file_uploader("圖片", type=["png","jpg","jpeg","webp","gif"], key="new_pic")
        if st.button("加入", use_container_width=True):
            if name.strip():
                img64 = base64.b64encode(pic.read()).decode() if pic else None
                keychains.append({"name": name.strip(), "image": img64})
                save()
                st.success("已加入！")
                st.rerun()

    st.markdown(f"**總共 {len(keychains)} 個 ⋅ 抽過 {len(drawn)} ⋅ 用過 {len(used)}**", unsafe_allow_html=True)

    # 列表（每行獨立 container，避免 key 重複）
    for i, k in enumerate(keychains[:]):
        with st.container():
            cols = st.columns([1, 3, 2, 1, 1, 2, 2])
            cols[0].write(i+1)
            cols[1].write(f"**{k['name']}**")
            if k['image']:
                cols[2].image(f"data:image/png;base64,{k['image']}", width=80)
            cols[3].markdown(f"<div class='green'>✓</div>" if k['name'] in drawn else "<div class='gray'>—</div>", unsafe_allow_html=True)
            cols[4].markdown(f"<div class='green'>✓</div>" if k['name'] in used else "<div class='gray'>—</div>", unsafe_allow_html=True)
            
            if cols[5].button("用過", key=f"use_{i}"):
                if k['name'] in used:
                    used.remove(k['name'])
                else:
                    used.add(k['name'])
                save()
                st.rerun()
            if cols[6].button("刪除", key=f"del_{i}"):
                keychains.remove(k)
                save()
                st.rerun()

# ============ 備份 ============
else:
    st.markdown('<div class="header"><h1>備份與還原</h1></div>', unsafe_allow_html=True)
    backup = json.dumps({"keychains": keychains, "drawn": list(drawn), "used": list(used)}, ensure_ascii=False)
    st.download_button("下載備份", backup, f"鎖匙扣備份_{date.today()}.json")
    uploaded = st.file_uploader("上載備份還原", type=["json"])
    if uploaded:
        try:
            newdata = json.load(uploaded)
            keychains[:] = newdata.get("keychains", [])
            drawn.clear(); drawn.update(newdata.get("drawn", []))
            used.clear(); used.update(newdata.get("used", []))
            save()
            st.success("還原成功！")
            st.rerun()
        except:
            st.error("檔案錯誤")

# ============ 登出 ============
if st.sidebar.button("重新登入／換密碼"):
    st.session_state.authenticated = False
    st.rerun()

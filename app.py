import streamlit as st
import random
import base64
import json
from datetime import date

# ============ 密碼（改這行）============
PASSWORD = "123456"  # ← 改成你想要的密碼

# ============ 超靚登入頁 + Enter 登入 ============
if st.session_state.get("auth") != True:
    st.markdown("""
    <style>
        body {background: linear-gradient(135deg, #667eea, #764ba2);}
        .login-box {max-width:420px; margin:120px auto; padding:50px 40px; 
                    background: rgba(255,255,255,0.95); border-radius:25px; 
                    box-shadow:0 25px 50px rgba(0,0,0,0.4); text-align:center;
                    backdrop-filter: blur(10px);}
        .login-title {font-size:42px; color:#2c3e50; margin-bottom:10px;}
        .login-subtitle {color:#7f8c8d; margin-bottom:30px;}
        .stTextInput > div > div > input {padding:18px; font-size:20px; border-radius:15px; border:2px solid #3498db;}
        .stButton>button {padding:18px; font-size:20px; background:#e74c3c; border-radius:15px;}
    </style>
    <div class="login-box">
        <h1 class="login-title">我的鎖匙扣</h1>
        <p class="login-subtitle">請輸入密碼進入你的專屬空間</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("密碼", type="password", label_visibility="collapsed")
        if st.button("登入") or st.session_state.get("enter_login", False):
            if pwd == PASSWORD:
                st.session_state.auth = True
                st.session_state.enter_login = False
                st.rerun()
            else:
                st.error("密碼錯誤")
    st.markdown('<script>document.addEventListener("keydown",e=>{if(e.key==="Enter") Streamlit.setComponentValue("enter_login",true)})</script>', 
                unsafe_allow_html=True)
    st.stop()

# ============ 全站超靚美化 ============
st.set_page_config(page_title="鎖匙扣神器", layout="centered", page_icon="key")

st.markdown("""
<style>
    .stApp {background:#1a1a2e; color:#eee; font-family:'Segoe UI',sans-serif; min-height:100vh; position:relative; overflow:hidden;}
    .bg-deco {position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; opacity:0.08; z-index:-1;}
    .bg-deco span {position:absolute; font-size:80px; animation:float 20s infinite linear;}
    @keyframes float {0%{transform:translateY(100vh) rotate(0deg);} 100%{transform:translateY(-100px) rotate(360deg);}}
    .header {background:rgba(255,255,255,0.1); backdrop-filter:blur(10px); border-radius:20px; padding:25px; text-align:center; margin:20px 0; box-shadow:0 10px 30px rgba(0,0,0,0.5);}
    .card {background:rgba(255,255,255,0.08); border-radius:20px; padding:25px; margin:20px 0; backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.1);}
    .stButton>button {background:linear-gradient(45deg,#ff6b6b,#feca57); color:white; border:none; border-radius:18px; padding:15px; font-size:18px; box-shadow:0 8px 20px rgba(0,0,0,0.4);}
    .stButton>button:hover {transform:translateY(-4px); box-shadow:0 15px 30px rgba(0,0,0,0.5);}
    .green {color:#51cf66; font-size:2.5em;}
    .gray {color:#868e96; font-size:2.5em;}
    .sidebar .stButton>button {background:#34495e; margin:10px 0;}
</style>
<div class="bg-deco">
    <span style="top:10%;left:10%;animation-delay:0s;">key</span>
    <span style="top:20%;left:70%;animation-delay:5s;">key</span>
    <span style="top:60%;left:20%;animation-delay:10s;">key</span>
    <span style="top:80%;left:80%;animation-delay:15s;">key</span>
</div>
""", unsafe_allow_html=True)

# ============ 側邊欄分頁 ============
st.sidebar.markdown("### 頁面")
p1 = st.sidebar.button("抽籤主頁", use_container_width=True)
p2 = st.sidebar.button("檔案庫管理", use_container_width=True)
p3 = st.sidebar.button("備份與還原", use_container_width=True)

page = "抽籤主頁" if p1 else "檔案庫管理" if p2 else "備份與還原" if p3 else "抽籤主頁"

# ============ 數據儲存 ============
if "data" not in st.session_state:
    saved = st.query_params.get("d")
    if saved:
        try: st.session_state.data = json.loads(saved)
        except: st.session_state.data = {"keychains":[],"drawn":[],"used":[]}
    else:
        st.session_state.data = {"keychains":[],"drawn":[],"used":[]}

keychains = st.session_state.data["keychains"]
drawn = set(st.session_state.data["drawn"])
used = set(st.session_state.data["used"])

def save():
    st.session_state.data = {"keychains":keychains, "drawn":list(drawn), "used":list(used)}
    st.query_params["d"] = json.dumps(st.session_state.data, ensure_ascii=False)

# ============ 抽籤主頁 ============
if page == "抽籤主頁":
    st.markdown('<div class="header"><h1>今日用邊個鎖匙扣？</h1></div>', unsafe_allow_html=True)
    
    if keychains:
        avail = [k for k in keychains if k["name"] not in drawn]
        if avail:
            if st.button("抽！", use_container_width=True, type="primary"):
                win = random.choice(avail)
                drawn.add(win["name"])
                save()
                st.balloons()
                st.success(f"抽中：{win['name']} 恭喜")
                if win["image"]:
                    st.image(f"data:image/png;base64,{win['image']}", width=300)
        else:
            st.warning("全部都抽過晒！")
            if st.button("重置抽籤記錄"): drawn.clear(); save(); st.rerun()
    else:
        st.info("快啲去「檔案庫管理」加鎖匙扣啦～")

# ============ 檔案庫管理（重點：用 form 解決 Enter 跳頁）============
elif page == "檔案庫管理":
    st.markdown('<div class="header"><h1>檔案庫管理</h1></div>', unsafe_allow_html=True)
    
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("名稱")
        pic = c2.file_uploader("圖片", type=["png","jpg","jpeg","webp","gif"])
        submitted = st.form_submit_button("加入新鎖匙扣", use_container_width=True)
        if submitted and name.strip():
            img64 = base64.b64encode(pic.read()).decode() if pic else None
            keychains.append({"name": name.strip(), "image": img64})
            save()
            st.success("已成功加入！")
            st.rerun()

    st.markdown(f"<h2 style='text-align:center; color:#fff;'>總共 {len(keychains)} 個 ⋅ 抽過 {len(drawn)} ⋅ 用過 {len(used)}</h2>", unsafe_allow_html=True)

    for i, k in enumerate(keychains[:]):
        with st.container():
            cols = st.columns([1, 3, 2, 1, 1, 2, 2])
            cols[0].write(f"**{i+1}**")
            cols[1].write(f"**{k['name']}**")
            if k['image']:
                cols[2].image(f"data:image/png;base64,{k['image']}", width=80)
            cols[3].markdown(f"<div class='green'>Check</div>" if k['name'] in drawn else "<div class='gray'>—</div>", unsafe_allow_html=True)
            cols[4].markdown(f"<div class='green'>Check</div>" if k['name'] in used else "<div class='gray'>—</div>", unsafe_allow_html=True)
            if cols[5].button("用過", key=f"use_{i}"):
                used.symmetric_difference_update([k['name']])
                save()
                st.rerun()
            if cols[6].button("刪除", key=f"del_{i}"):
                keychains.remove(k)
                save()
                st.rerun()

# ============ 備份與還原 ============
else:
    st.markdown('<div class="header"><h1>備份與還原</h1></div>', unsafe_allow_html=True)
    backup = json.dumps({"keychains": keychains, "drawn": list(drawn), "used": list(used)}, ensure_ascii=False)
    st.download_button("下載完整備份", backup, f"鎖匙扣備份_{date.today()}.json", "application/json")
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
            st.error("檔案錯誤或損壞")

# ============ 登出 ============
if st.sidebar.button("重新登入／換密碼"):
    st.session_state.auth = False
    st.rerun()

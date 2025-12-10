import streamlit as st
import random
import base64
import json
from datetime import date

# ============ 密碼（改這行）============
PASSWORD = "123456"  # ← 改成你想要的密碼

# ============ 超靚登入頁 + Enter 即登入 ============
if st.session_state.get("logged_in") != True:
    st.markdown("""
    <style>
        .login-bg {background: linear-gradient(135deg, #1e3c72, #2a5298); min-height: 100vh; display: flex; align-items: center; justify-content: center;}
        .login-box {background: rgba(255,255,255,0.95); padding: 50px 40px; border-radius: 25px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); text-align: center; max-width: 420px;}
        .login-title {font-size: 48px; color: #2c3e50; margin: 0;}
        .login-subtitle {color: #7f8c8d; margin: 20px 0;}
        .stTextInput > div > div > input {padding: 18px; font-size: 20px; border-radius: 15px; border: 3px solid #3498db;}
        .login-btn {background: #e74c3c; padding: 18px; font-size: 20px; border-radius: 15px;}
    </style>
    <div class="login-bg">
        <div class="login-box">
            <h1 class="login-title">我的鎖匙扣</h1>
            <p class="login-subtitle">請輸入密碼進入</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("密碼", type="password", label_visibility="collapsed", key="pwd_input")
        login_clicked = st.button("登入", key="login_btn")
        # 真正實現 Enter 登入
        if login_clicked or st.session_state.get("enter_trigger", False):
            if pwd == PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("密碼錯誤")
    # 監聽 Enter 鍵
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            Streamlit.setComponentValue("enter_trigger", true);
        }
    });
    </script>
    """, unsafe_allow_html=True)
    st.stop()

# ============ 全站超靚高對比美化 ============
st.set_page_config(page_title="鎖匙扣神器", layout="centered", page_icon="key")

st.markdown("""
<style>
    .stApp {background: #0f172a; color: #f8fafc; font-family: 'Segoe UI', sans-serif; min-height: 100vh;}
    .deco {position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; opacity: 0.05; z-index: -1;}
    .deco span {position: absolute; font-size: 100px; animation: float 25s infinite linear;}
    @keyframes float {0% {transform: translateY(100vh) rotate(0deg);} 100% {transform: translateY(-100px) rotate(360deg);}}
    .header {background: rgba(30,58,138,0.4); border-radius: 20px; padding: 25px; text-align: center; margin: 20px 0; backdrop-filter: blur(10px);}
    .card {background: rgba(255,255,255,0.08); border-radius: 20px; padding: 25px; margin: 20px 0; border: 1px solid rgba(255,255,255,0.1);}
    .stButton>button {background: linear-gradient(45deg, #00d2ff, #3a7bd5); color: white; border: none; border-radius: 18px; padding: 16px; font-size: 18px; box-shadow: 0 8px 25px rgba(0,210,255,0.4);}
    .stButton>button:hover {transform: translateY(-4px); box-shadow: 0 15px 35px rgba(0,210,255,0.6);}
    .green {color: #10b981; font-size: 2.5em; font-weight: bold;}
    .gray {color: #64748b; font-size: 2.5em;}
    .stTextInput label, .stFileUploader label {color: #e2e8f0 !important;}
</style>
<div class="deco">
    <span style="top:10%; left:10%; animation-delay:0s;">key</span>
    <span style="top:30%; left:75%; animation-delay:7s;">key</span>
    <span style="top:70%; left:15%; animation-delay:14s;">key</span>
    <span style="top:50%; left:80%; animation-delay:21s;">key</span>
</div>
""", unsafe_allow_html=True)

# ============ 側邊欄靚分頁 ============
st.sidebar.markdown("### 導航")
page1 = st.sidebar.button("抽籤主頁", use_container_width=True)
page2 = st.sidebar.button("檔案庫管理", use_container_width=True)
page3 = st.sidebar.button("備份與還原", use_container_width=True)

current_page = "抽籤主頁" if page1 else "檔案庫管理" if page2 else "備份與還原" if page3 else "抽籤主頁"

# ============ 數據儲存（關閉不丟）============
DATA_KEY = "keychain_data_final"
if DATA_KEY not in st.session_state:
    saved = st.query_params.get("data")
    if saved:
        try:
            st.session_state[DATA_KEY] = json.loads(saved)
        except:
            st.session_state[DATA_KEY] = {"keychains": [], "drawn": [], "used": []}
    else:
        st.session_state[DATA_KEY] = {"keychains": [], "drawn": [], "used": []}

data = st.session_state[DATA_KEY]
keychains = data["keychains"]
drawn = set(data["drawn"])
used = set(data["used"])

def save():
    st.session_state[DATA_KEY] = {"keychains": keychains, "drawn": list(drawn), "used": list(used)}
    st.query_params["data"] = json.dumps(st.session_state[DATA_KEY], ensure_ascii=False)

# ============ 抽籤主頁 ============
if current_page == "抽籤主頁":
    st.markdown('<div class="header"><h1>今日用邊個鎖匙扣？</h1></div>', unsafe_allow_html=True)
    
    if keychains:
        available = [k for k in keychains if k["name"] not in drawn]
        if available:
            if st.button("抽籤！", use_container_width=True, type="primary"):
                winner = random.choice(available)
                drawn.add(winner["name"])
                save()
                st.balloons()
                st.success(f"抽中：{winner['name']} 恭喜！")
                if winner["image"]:
                    st.image(f"data:image/png;base64,{winner['image']}", width=320)
        else:
            st.warning("全部都抽過晒！")
            if st.button("重置抽籤記錄"): 
                drawn.clear(); save(); st.rerun()
    else:
        st.info("快啲去「檔案庫管理」加鎖匙扣啦～")

# ============ 檔案庫管理（重點：用 form + 獨立 key 解決 Enter 跳頁）============
elif current_page == "檔案庫管理":
    st.markdown('<div class="header"><h1>檔案庫管理</h1></div>', unsafe_allow_html=True)
    
    # 完全獨立 form，Enter 只會提交表單，絕不跳頁
    with st.form(key="add_keychain_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name_input = col1.text_input("鎖匙扣名稱", key="name_input_unique")
        pic_input = col2.file_uploader("上傳圖片", type=["png","jpg","jpeg","webp","gif"], key="pic_input_unique")
        submit_btn = st.form_submit_button("加入新鎖匙扣", use_container_width=True)
        
        if submit_btn and name_input.strip():
            img64 = base64.b64encode(pic_input.read()).decode() if pic_input else None
            keychains.append({"name": name_input.strip(), "image": img64})
            save()
            st.success(f"成功加入：{name_input.strip()} ")
            st.rerun()

    st.markdown(f"<h2 style='text-align:center; color:#fff;'>總共 {len(keychains)} 個 ⋅ 抽過 {len(drawn)} ⋅ 用過 {len(used)}</h2>", unsafe_allow_html=True)

    # 每行獨立 container + 獨一無二 key
    for idx, item in enumerate(keychains[:]):
        with st.container():
            cols = st.columns([1, 3, 2, 1, 1, 2, 2])
            cols[0].write(f"**{idx+1}**")
            cols[1].write(f"**{item['name']}**")
            if item["image"]:
                cols[2].image(f"data:image/png;base64,{item['image']}", width=80)
            cols[3].markdown(f"<div class='green'>Check</div>" if item["name"] in drawn else "<div class='gray'>—</div>", unsafe_allow_html=True)
            cols[4].markdown(f"<div class='green'>Check</div>" if item["name"] in used else "<div class='gray'>—</div>", unsafe_allow_html=True)
            
            if cols[5].button("用過", key=f"used_btn_{idx}_{item['name'][:10]}"):
                used.symmetric_difference_update([item["name"]])
                save()
                st.rerun()
            if cols[6].button("刪除", key=f"delete_btn_{idx}_{item['name'][:10]}"):
                keychains.remove(item)
                save()
                st.rerun()

# ============ 備份頁 ============
else:
    st.markdown('<div class="header"><h1>備份與還原</h1></div>', unsafe_allow_html=True)
    backup_data = json.dumps({"keychains": keychains, "drawn": list(drawn), "used": list(used)}, ensure_ascii=False)
    st.download_button("下載完整備份", backup_data, f"鎖匙扣備份_{date.today()}.json", "application/json")
    uploaded = st.file_uploader("上載備份還原", type=["json"])
    if uploaded:
        try:
            new_data = json.load(uploaded)
            keychains[:] = new_data.get("keychains", [])
            drawn.clear(); drawn.update(new_data.get("drawn", []))
            used.clear(); used.update(new_data.get("used", []))
            save()
            st.success("還原成功！")
            st.rerun()
        except:
            st.error("備份檔案損壞")

# ============ 登出 ============
if st.sidebar.button("重新登入 / 換密碼"):
    st.session_state.logged_in = False
    st.rerun()

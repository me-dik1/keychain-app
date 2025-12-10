import streamlit as st
import random
import base64
import json
from datetime import date

# ============ 密碼（改呢度）============
PASSWORD = "123456"   # ← 改成你鍾意嘅密碼

if st.session_state.get("auth") != True:
    st.title("請輸入密碼")
    pwd = st.text_input("密碼", type="password")
    if st.button("登入"):
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("密碼錯誤")
    st.stop()

# ============ 美化 + 靚分頁按鈕 ============
st.set_page_config(page_title="我的鎖匙扣", layout="wide", page_icon="key")

st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family:'Segoe UI',sans-serif; min-height:100vh;}
    .header {background:rgba(255,255,255,0.95); border-radius:20px; padding:20px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.3); margin:20px;}
    .tab-btn {background:linear-gradient(45deg,#ff6b6b,#feca57); color:white; border:none; padding:15px; margin:5px; border-radius:15px; font-size:18px; flex:1;}
    .tab-btn:hover {transform:scale(1.05); transition:0.3s;}
    .card {background:white; border-radius:20px; padding:25px; margin:15px 0; box-shadow:0 10px 30px rgba(0,0,0,0.2);}
    .stButton>button {background:linear-gradient(45deg,#1dd1a1,#10ac84); color:white; border-radius:15px; font-size:16px; padding:12px;}
    .green {color:#2ecc71; font-size:2em;}
    .gray {color:#bdc3c7; font-size:2em;}
</style>
""", unsafe_allow_html=True)

# 靚分頁按鈕
col1, col2, col3 = st.columns(3)
with col1:
    page1 = st.button("抽籤主頁", use_container_width=True, type="primary")
with col2:
    page2 = st.button("檔案庫管理", use_container_width=True, type="primary")
with col3:
    page3 = st.button("備份", use_container_width=True, type="primary")

page = "抽籤主頁" if page1 else "檔案庫管理" if page2 else "備份" if page3 else "抽籤主頁"

# 數據自動儲存（用 query_params + session）
DATA_KEY = "kc_data"
if DATA_KEY not in st.session_state:
    saved = st.query_params.get("d")
    if saved:
        try: st.session_state[DATA_KEY] = json.loads(saved)
        except: pass
    if DATA_KEY not in st.session_state:
        st.session_state[DATA_KEY] = {"keychains":[],"drawn":[],"used":[]}

data = st.session_state[DATA_KEY]
keychains = data["keychains"]
drawn = set(data["drawn"])
used = set(data["used"])

def save():
    st.session_state[DATA_KEY] = {"keychains":keychains, "drawn":list(drawn), "used":list(used)}
    st.query_params["d"] = json.dumps(st.session_state[DATA_KEY], ensure_ascii=False)

# ========================= 抽籤主頁 =========================
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
                st.success(f"抽中：{win['name']} 🎉")
                if win["image"]:
                    st.image(f"data:image/png;base64,{win['image']}", width=300)
        else:
            st.warning("全部都抽過晒！")
            if st.button("重置抽籤記錄"): drawn.clear(); save(); st.rerun()
    else:
        st.info("快啲去「檔案庫管理」加鎖匙扣啦～")

# ========================= 檔案庫管理 =========================
elif page == "檔案庫管理":
    st.markdown('<div class="header"><h1>檔案庫管理</h1></div>', unsafe_allow_html=True)
    
    # 添加
    with st.expander("➕ 添加新鎖匙扣", expanded=True):
        c1,c2 = st.columns(2)
        name = c1.text_input("名稱")
        pic = c2.file_uploader("圖片", type=["png","jpg","jpeg","webp","gif"])
        if st.button("加入", use_container_width=True):
            if name.strip():
                img64 = base64.b64encode(pic.read()).decode() if pic else None
                keychains.append({"name":name.strip(),"image":img64})
                save(); st.rerun()

    st.markdown(f"<h2 style='text-align:center;'>總共 {len(keychains)} 個 ⋅ 抽過 {len(drawn)} ⋅ 用過 {len(used)}</h2>", unsafe_allow_html=True)

    # 每行獨立 container，避免 key 重複
    for i, k in enumerate(keychains[:]):  # [:] 複製避免修改時出錯
        with st.container():
            cols = st.columns([1, 3, 2, 1, 1, 2, 2])
            cols[0].write(i+1)
            cols[1].write(f"**{k['name']}**")
            if k['image']:
                cols[2].image(f"data:image/png;base64,{k['image']}", width=80)
            else:
                cols[2].write("—")
            cols[3].markdown(f"<div class='green'>✓</div>" if k['name'] in drawn else "<div class='gray'>—</div>", unsafe_allow_html=True)
            cols[4].markdown(f"<div class='green'>✓</div>" if k['name'] in used else "<div class='gray'>—</div>", unsafe_allow_html=True)
            
            if cols[5].button("用過", key=f"use_{i}_{k['name']}"):
                if k['name'] in used: used.remove(k['name'])
                else: used.add(k['name'])
                save(); st.rerun()
            if cols[6].button("刪除", key=f"del_{i}_{k['name']}"):
                keychains.remove(k)
                save(); st.rerun()

# ========================= 備份 =========================
else:
    st.markdown('<div class="header"><h1>備份與還原</h1></div>', unsafe_allow_html=True)
    backup = json.dumps({"keychains":keychains,"drawn":list(drawn),"used":list(used)}, ensure_ascii=False)
    st.download_button("下載備份", backup, f"鎖匙扣備份_{date.today()}.json", "application/json")
    uploaded = st.file_uploader("上載備份還原", type=["json"])
    if uploaded:
        try:
            newdata = json.load(uploaded)
            keychains[:] = newdata.get("keychains",[])
            drawn.clear(); drawn.update(newdata.get("drawn",[]))
            used.clear(); used.update(newdata.get("used",[]))
            save(); st.success("還原成功！"); st.rerun()
        except:
            st.error("檔案錯誤")

# 登出
if st.sidebar.button("重新登入／換密碼"):
    st.session_state.auth = False
    st.rerun()

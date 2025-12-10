import streamlit as st
import random
import base64
import json
from datetime import date

# ============ 密碼保護（改呢度就係你個密碼）============
PASSWORD = "812317"   # ← 改成你鍾意嘅密碼（例如 mykeychain2025）

if st.session_state.get("authenticated") != True:
    st.title("🔒 請輸入密碼")
    pwd = st.text_input("密碼", type="password")
    if st.button("登入"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("密碼錯晒")
    st.stop()
# =================================================

st.set_page_config(page_title="我的鎖匙扣", layout="wide", page_icon="🔑")

# 美化（漸變藍綠 + 靚字體）
st.markdown("""
<style>
    .stApp {background: linear-gradient(to bottom right, #e0f7fa, #f0f8ff); font-family: 'Georgia', serif;}
    .card {background:white; border:2px solid #4CAF50; border-radius:18px; padding:20px; margin:15px 0; box-shadow:0 8px 20px rgba(0,0,0,0.15);}
    .stButton>button {background:linear-gradient(45deg,#4CAF50,#2196F3); color:white; border-radius:15px; font-size:18px; padding:12px;}
    .green {color:green; font-weight:bold; font-size:1.5em;}
    .gray {color:#aaa;}
</style>
""", unsafe_allow_html=True)

# 自動載入／儲存（用 st.session_state + 本地備份）
DATA_KEY = "keychain_data_v3"
if DATA_KEY not in st.session_state:
    saved = st.query_params.get("saved")
    if saved:
        try:
            st.session_state[DATA_KEY] = json.loads(saved)
        except:
            pass
    if DATA_KEY not in st.session_state:
        st.session_state[DATA_KEY] = {"keychains":[],"drawn":[],"used":[]}

data = st.session_state[DATA_KEY]
keychains = data["keychains"]
drawn = set(data["drawn"])
used = set(data["used"])

def save():
    st.session_state[DATA_KEY] = {"keychains":keychains, "drawn":list(drawn), "used":list(used)}
    st.query_params["saved"] = json.dumps(st.session_state[DATA_KEY])

# Sidebar 靚按鈕分頁
page = st.sidebar.radio("📱 頁面", ["抽籤主頁", "檔案庫管理", "備份"])

# ========================= 抽籤主頁 =========================
if page == "抽籤主頁":
    st.title("🎲 今日用邊個鎖匙扣？")
    if keychains:
        avail = [k for k in keychains if k["name"] not in drawn]
        if avail:
            if st.button("抽！", use_container_width=True, type="primary"):
                win = random.choice(avail)
                drawn.add(win["name"])
                save()
                st.balloons()
                st.success(f"抽中：{win['name']} 🎉")
                if win["image"]: st.image(f"data:image/png;base64,{win['image']}", width=250)
        else:
            st.warning("全部都抽過晒啦！")
            if st.button("重置抽籤記錄"): drawn.clear(); save(); st.rerun()
    else:
        st.info("快啲去「檔案庫管理」加鎖匙扣啦～")

# ========================= 檔案庫管理 =========================
elif page == "檔案庫管理":
    st.title("📂 檔案庫管理 + 狀態")
    
    # 添加
    with st.expander("➕ 添加新鎖匙扣", expanded=True):
        c1,c2 = st.columns(2)
        name = c1.text_input("名稱")
        pic = c2.file_uploader("圖片", type=["png","jpg","jpeg","webp"])
        if st.button("加入", use_container_width=True):
            if name.strip():
                img64 = base64.b64encode(pic.read()).decode() if pic else None
                keychains.append({"name":name.strip(), "image":img64})
                save(); st.rerun()

    # 總統計
    st.markdown(f"**總數 {len(keychains)} ⋅ 抽過 {len(drawn)} ⋅ 用過 {len(used)}**")

    # 表格
    rows = []
    for i,k in enumerate(keychains):
        rows.append({
            "編號": i+1,
            "名稱": k["name"],
            "預覽": f'<img src="data:image/png;base64,{k["image"]}" width=80>' if k["image"] else "",
            "抽過": '<span class="green">✓</span>' if k["name"] in drawn else '<span class="gray">-</span>',
            "用過": '<span class="green">✓</span>' if k["name"] in used else '<span class="gray">-</span>',
            "操作": k["name"]
        })

    for row in rows:
        col1,col2,col3,col4,col5,col6 = st.columns([1,2,2,1,1,2])
        col1.write(row["編號"])
        col2.write(row["名稱"])
        if row["預覽"]: col3.markdown(row["預覽"], unsafe_allow_html=True)
        col4.markdown(row["抽過"], unsafe_allow_html=True)
        col5.markdown(row["用過"], unsafe_allow_html=True)
        with col6:
            if st.button("用過", key=f"use{i}"):
                if row["操作"] in used: used.remove(row["操作"])
                else: used.add(row["操作"])
                save(); st.rerun()
            if st.button("刪除", key=f"del{i}"):
                keychains.remove(next(x for x in keychains if x["name"]==row["操作"]))
                save(); st.rerun()

# ========================= 備份 =========================
elif page == "備份":
    st.title("💾 備份與還原")
    backup = json.dumps({"keychains":keychains,"drawn":list(drawn),"used":list(used)}, ensure_ascii=False)
    st.download_button("下載備份", backup, f"鎖匙扣備份_{date.today()}.json")
    uploaded = st.file_uploader("上載備份", type="json")
    if uploaded:
        newdata = json.load(uploaded)
        keychains[:] = newdata.get("keychains",[])
        drawn.clear(); drawn.update(newdata.get("drawn",[]))
        used.clear(); used.update(newdata.get("used",[]))
        save(); st.success("還原成功"); st.rerun()

# 登出／換密碼
if st.sidebar.button("換密碼／重新登入"):
    st.session_state.authenticated = False
    st.rerun()

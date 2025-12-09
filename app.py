import streamlit as st
import random
import base64
import json
from datetime import date

# ==================== 超靚藍綠玻璃風格 CSS ====================
st.set_page_config(page_title="我的鎖匙扣", layout="wide", page_icon="🔑")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');
    
    body, .stApp { font-family: 'Noto Sans TC', sans-serif; }
    .stApp { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 25px;
        margin: 20px auto;
        max-width: 1400px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        backdrop-filter: blur(10px);
    }
    h1, h2, h3 { color: #2c3e50; font-weight: 700; }
    .nav-button button {
        background: linear-gradient(45deg, #4CAF50, #2196F3);
        background: linear-gradient(45deg, #4CAF50, #2196F3);
        color: white !important;
        border: none;
        border-radius: 50px;
        padding: 12px 25px;
        font-size: 1.1em;
        font-weight: 600;
        margin: 5px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s;
    }
    .nav-button button:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.3); }
    .status-badge { padding: 6px 12px; border-radius: 20px; font-size: 0.9em; font-weight: bold; }
    .drawn { background: #e3f2fd; color: #1976d2; }
    .used { background: #e8f5e9; color: #388e3c; }
    .card { 
        background: white; 
        border-radius: 16px; 
        padding: 20px; 
        margin: 15px 0; 
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        transition: transform 0.3s;
    }
    .card:hover { transform: translateY(-5px); }
    .stButton>button { border-radius: 12px !important; height: 3em; }
</style>
""", unsafe_allow_html=True)

# ==================== 永久儲存（解決第5點：關掉不見、手機同步） ====================
def save_data():
    data = {
        "keychains": st.session_state.keychains,
        "drawn": list(st.session_state.drawn),
        "used": st.session_state.used,
        "currently_using": st.session_state.currently_using
    }
    st.session_state.backup_json = json.dumps(data, ensure_ascii=False)

def load_data():
    if backup := st.session_state.get("backup_json"):
        try:
            data = json.loads(backup)
            st.session_state.keychains = data.get("keychains", [])
            st.session_state.drawn = set(data.get("drawn", []))
            st.session_state.used = data.get("used", {})
            st.session_state.currently_using = data.get("currently_using", "")
        except:
            pass

# 初始化
if "keychains" not in st.session_state:
    st.session_state.keychains = []
    st.session_state.drawn = set()
    st.session_state.used = {}           # {日期: 名稱}
    st.session_state.currently_using = "" # 目前正在用的（第4點）
    load_data()

# 每次有變動就自動儲存
def auto_save():
    save_data()
    st.rerun()

# ==================== 頁面導航（改成靚靚按鈕） ====================
st.markdown("<div class='main-container'>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:white; text-shadow: 0 4px 10px rgba(0,0,0,0.4);'>🔑 我的鎖匙扣</h1>", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns(3)
with col_btn1:
    if st.button("抽籤 + 使用", use_container_width=True, type="primary"):
        st.session_state.page = "main"
with col_btn2:
    if st.button("鎖匙扣檔案庫", use_container_width=True):
        st.session_state.page = "library"
with col_btn3:
    if st.button("備份與匯入", use_container_width=True):
        st.session_state.page = "backup"

if "page" not in st.session_state:
    st.session_state.page = "main"

# ============================== 主頁 ==============================
if st.session_state.page == "main":
    st.markdown("<h2>今日抽籤</h2>", unsafe_allow_html=True)
    
    if not st.session_state.keychains:
        st.info("你仲未有鎖匙扣呀～快啲去「鎖匙扣檔案庫」加啦！")
    else:
        avail = [k for k in st.session_state.keychains if k['name'] not in st.session_state.drawn]
        
        if avail:
            if st.button("抽籤！", use_container_width=True, type="primary"):
                win = random.choice(avail)
                st.session_state.drawn.add(win['name'])
                auto_save()
                st.balloons()
                st.success(f"抽中：{win['name']}！")
                if win['image']:
                    st.image(f"data:image/png;base64,{win['image']}", width=250)
        else:
            st.warning("全部都抽晒啦！")
            if st.button("重置抽籤記錄"):
                st.session_state.drawn.clear()
                auto_save()
    
    # 目前正在使用（第4點）
    st.markdown("### 目前使用緊")
    if st.session_state.currently_using:
        cur = next((x for x in st.session_state.keychains if x['name']==st.session_state.currently_using), None)
        if cur:
            c1, c2 = st.columns([1,3])
            with c1:
                if cur['image']:
                    st.image(f"data:image/png;base64,{cur['image']}", width=100)
            with c2:
                st.markdown(f"**{cur['name']}**")
            if st.button("用完・收回", type="secondary"):
                st.session_state.currently_using = ""
                auto_save()
    else:
        st.info("未有使用緊嘅鎖匙扣")

# ============================== 檔案庫（合併統計＋狀態＋一鍵切換使用中） ==============================
elif st.session_state.page == "library":
    st.markdown("<h2>鎖匙扣檔案庫</h2>", unsafe_allow_html=True)
    
    # 新增
    with st.expander("➕ 添加新鎖匙扣", expanded=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("名稱", key="new_name")
        pic = c2.file_uploader("圖片（可選）", type=["png","jpg","jpeg","webp"], key="new_pic")
        if st.button("加入檔案庫", type="primary", use_container_width=True):
            if name.strip():
                img64 = None
                if pic:
                    img64 = base64.b64encode(pic.read()).decode()
                st.session_state.keychains.append({"name": name.strip(), "image": img64})
                auto_save()
                st.success("已加入！")
                st.rerun()
    
    st.markdown(f"**總共 {len(st.session_state.keychains)} 個鎖匙扣**　｜　隨機排序")
    if st.button("隨機排序", use_container_width=False):
        random.shuffle(st.session_state.keychains)
        auto_save()
    
    # 顯示所有卡片（含狀態＋一鍵切換使用中）
    for i, k in enumerate(st.session_state.keychains):
        is_drawn = k['name'] in st.session_state.drawn
        is_used = k['name'] in set(st.session_state.used.values())
        is_current = k['name'] == st.session_state.currently_using
        
        with st.container():
            cols = st.columns([1, 4, 2])
            with cols[0]:
                if k['image']:
                    st.image(f"data:image/png;base64,{k['image']}", use_column_width=True)
                else:
                    st.markdown("<div style='height:120px;background:#eee;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#999;'>無圖</div>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"### {k['name']}")
                status = []
                if is_drawn: status.append("<span class='status-badge drawn'>已抽過</span>")
                if is_used: status.append("<span class='status-badge used'>已用過</span>")
                if is_current: status.append("<span class='status-badge' style='background:#fff3e0;color:#ef6c00;'>使用中</span>")
                st.markdown("　".join(status), unsafe_allow_html=True)
            with cols[2]:
                if is_current:
                    if st.button("收回", key=f"off_{i}", use_container_width=True):
                        st.session_state.currently_using = ""
                        auto_save()
                else:
                    if st.button("使用緊", key=f"on_{i}", type="primary", use_container_width=True):
                        st.session_state.currently_using = k['name']
                        # 自動記錄今日使用
                        today = date.today().isoformat()
                        st.session_state.used[today] = k['name']
                        auto_save()
                if st.button("刪除", key=f"del_{i}", type="secondary", use_container_width=True):
                    del st.session_state.keychains[i]
                    auto_save()
    
    # 編輯名稱（可選）
    with st.expander("編輯名稱"):
        options = [""] + [k['name'] for k in st.session_state.keychains]
        sel = st.selectbox("選擇要改名", options, key="edit_sel")
        if sel:
            idx = next(i for i,k in enumerate(st.session_state.keychains) if k['name']==sel)
            new = st.text_input("新名稱", value=sel)
            if st.button("儲存"):
                st.session_state.keychains[idx]['name'] = new.strip()
                auto_save()

# ============================== 備份頁 ==============================
else:
    st.markdown("<h2>備份與匯入</h2>", unsafe_allow_html=True)
    
    backup_data = {
        "keychains": st.session_state.keychains,
        "drawn": list(st.session_state.drawn),
        "used": st.session_state.used,
        "currently_using": st.session_state.currently_using
    }
    st.download_button(
        label="下載完整備份",
        data=json.dumps(backup_data, ensure_ascii=False, indent=2),
        file_name=f"我的鎖匙扣備份_{date.today()}.json",
        mime="application/json"
    )
    
    uploaded = st.file_uploader("匯入備份檔案", type="json")
    if uploaded:
        try:
            data = json.load(uploaded)
            st.session_state.keychains = data.get("keychains", [])
            st.session_state.drawn = set(data.get("drawn", []))
            st.session_state.used = data.get("used", {})
            st.session_state.currently_using = data.get("currently_using", "")
            save_data()
            st.success("匯入成功！")
            st.rerun()
        except:
            st.error("檔案格式錯誤")

st.markdown("</div>", unsafe_allow_html=True)

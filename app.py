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

# ============ 美化（高對比 + 裝飾）============
st.markdown("""
<style>
    .stApp {background: #f0f7ff; color: #1e3a8a; font-family: 'Arial', sans-serif;}
    .header {text-align: center; color: #1d4ed8;}
    .stButton>button {background: #3b82f6; color: white; border-radius: 12px; padding: 12px 24px; font-size: 18px;}
    .stTextInput > div > div > input {border-radius: 10px; border: 2px solid #93c5fd;}
    .stFileUploader {border: 2px dashed #93c5fd; border-radius: 12px; padding: 20px;}
    .green {color: #15803d;}
    .gray {color: #6b7280;}
</style>
""", unsafe_allow_html=True)

# ============ 數據儲存（修復同步問題）============
DATA_KEY = "keychain_data"
if DATA_KEY not in st.session_state:
    saved = st.query_params.get("d")
    if saved:
        try:
            # 修復問題1：安全處理 query_params
            data_str = saved[0] if isinstance(saved, list) else saved
            st.session_state[DATA_KEY] = json.loads(data_str)
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
            if st.button("抽籤！", use_container_width=True):
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
    
    # 新增（正常）
    with st.expander("新增鎖匙扣", expanded=True):
        name = st.text_input("名稱", key="new_name")
        pic = st.file_uploader("圖片（可選）", type=["png","jpg","jpeg","webp","gif"], key="new_pic")
        if st.button("加入", key="add_btn"):
            if name.strip():
                img64 = base64.b64encode(pic.read()).decode() if pic else None
                items.append({"name": name.strip(), "image": img64})
                save()
                st.success("加入成功！")
                st.rerun()

    st.subheader(f"總 {len(items)} 個 | 抽過 {len(drawn)} | 用過 {len(used)}")
    
    # 顯示 + 編輯 + 後加圖片（修復問題2）
    for i, k in enumerate(items[:]):
        cols = st.columns([3, 2, 1, 1, 2, 2])
        cols[0].write(f"**{k['name']}**")
        if k["image"]:
            cols[1].image(f"data:image/png;base64,{k['image']}", width=80)
        else:
            cols[1].write("—")
        cols[2].write("Check" if k["name"] in drawn else "—")
        cols[3].write("Check" if k["name"] in used else "—")
        
        if cols[4].button("用過", key=f"use_{i}"):
            if k["name"] in used:
                used.remove(k["name"])
            else:
                used.add(k["name"])
            save()
            st.rerun()
            
        if cols[5].button("刪除", key=f"del_{i}"):
            items.pop(i)
            save()
            st.rerun()
    
    # 後加圖片（獨立區塊，修復問題2）
    st.divider()
    st.subheader("後加/換圖片")
    edit_name = st.selectbox("選擇鎖匙扣", [k["name"] for k in items])
    if edit_name:
        idx = next(i for i, k in enumerate(items) if k["name"] == edit_name)
        new_pic = st.file_uploader("上傳新圖片", type=["png","jpg","jpeg","webp","gif"], key=f"edit_pic_{idx}")
        if st.button("更新圖片", key=f"update_pic_{idx}"):
            if new_pic:
                items[idx]["image"] = base64.b64encode(new_pic.read()).decode()
                save()
                st.success("圖片更新成功！")
                st.rerun()

with tab3:
    st.title("備份與同步")
    backup = json.dumps(data, ensure_ascii=False)
    st.download_button("下載備份", backup, f"備份_{date.today()}.json")
    
    uploaded = st.file_uploader("上載備份還原", type="json")
    if uploaded:
        try:
            newdata = json.load(uploaded)
            st.session_state.data = newdata
            save()
            st.success("還原成功！")
            st.rerun()
        except:
            st.error("檔案錯誤")
    
    # 同步 link（已修復問題1）
    current_url = st.experimental_get_url() if hasattr(st, "experimental_get_url") else "https://ahl1-key.streamlit.app"
    data_param = st.query_params.get("d", "")
    data_str = data_param[0] if isinstance(data_param, list) else data_param
    sync_link = f"{current_url}?d={data_str}" if data_str else current_url
    st.text_input("同步 link（抄低換手機用）", sync_link)
    st.info("換手機打開呢條 link 就自動同步晒所有資料（包括圖片）！")

# 登出
if st.sidebar.button("登出"):
    st.session_state.auth = False
    st.rerun()

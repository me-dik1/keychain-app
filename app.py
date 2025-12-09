import streamlit as st
import random
import base64
import json
from datetime import date

st.set_page_config(page_title="我的鎖匙扣", layout="wide", page_icon="🔑")

# 美化 CSS（藍綠主題）
st.markdown("""
<style>
    .stApp { background-color: #f0f8ff; }
    .card { background: #ffffff; border: 1px solid #4CAF50; border-radius: 12px; padding: 15px; margin: 10px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .stButton > button { background: linear-gradient(to right, #4CAF50, #2196F3); color: white; border-radius: 10px; }
    .big-stat { font-size: 1.4em; text-align: center; padding: 15px; background: #E8F5E9; border-radius: 12px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# 初始化
if 'keychains' not in st.session_state: st.session_state.keychains = []
if 'drawn' not in st.session_state: st.session_state.drawn = set()
if 'used' not in st.session_state: st.session_state.used = {}

# Sidebar 導航
page = st.sidebar.selectbox("頁面", ["主頁（抽籤+使用）", "管理檔案庫", "歷史與統計", "備份與匯入"])

# ============================== 主頁 ==============================
if page == "主頁（抽籤+使用）":
    st.title("我的鎖匙扣抽籤 + 使用記錄")
    # （同之前一樣，省略以節省篇幅）

    if st.session_state.keychains:
        avail = [k for k in st.session_state.keychains if k['name'] not in st.session_state.drawn]
        if avail:
            if st.button("今日抽籤！", use_container_width=True, type="primary"):
                win = random.choice(avail)
                st.session_state.drawn.add(win['name'])
                st.balloons()
                st.success(f"抽中：**{win['name']}**")
                if win['image']: st.image(f"data:image/png;base64,{win['image']}", width=200)
        else:
            st.warning("全部抽晒！")
            if st.button("重置抽籤歷史"): st.session_state.drawn.clear(); st.rerun()

    today = date.today().isoformat()
    if today in st.session_state.used:
        n = st.session_state.used[today]
        kc = next((x for x in st.session_state.keychains if x['name']==n), None)
        st.success(f"今日已記錄使用：**{n}**")
        if kc and kc['image']: st.image(f"data:image/png;base64,{kc['image']}", width=150)

    sel = st.selectbox("手動記錄今日使用", [""] + [k['name'] for k in st.session_state.keychains])
    c1, c2 = st.columns(2)
    if c1.button("記錄今日使用", use_container_width=True):
        if sel: st.session_state.used[today] = sel; st.rerun()
    if c2.button("清除今日記錄", use_container_width=True):
        st.session_state.used.pop(today, None); st.rerun()

# ============================== 管理檔案庫（同之前一樣）==============================
elif page == "管理檔案庫":
    st.title("鎖匙扣檔案庫管理")
    # （添加、編輯、刪除、排序功能，同上一個版本，完全保留）

    with st.expander("➕ 添加新鎖匙扣", expanded=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("名稱")
        pic = c2.file_uploader("圖片", type=["png","jpg","jpeg","webp"])
        a1, a2 = st.columns(2)
        if a1.button("添加", use_container_width=True):
            if name.strip():
                img64 = None if not pic else base64.b64encode(pic.read()).decode()
                st.session_state.keychains.append({"name": name.strip(), "image": img64})
                st.success("已加入"); st.rerun()
        if a2.button("隨機排序", use_container_width=True):
            random.shuffle(st.session_state.keychains); st.rerun()

    st.subheader(f"目前擁有 {len(st.session_state.keychains)} 個")
    for i, k in enumerate(st.session_state.keychains):
        with st.expander(f"{i+1}. {k['name']}"):
            if k['image']: st.image(f"data:image/png;base64,{k['image']}", width=100)

    with st.expander("編輯或刪除"):
        sel_edit = st.selectbox("選擇要編輯", [""] + [k['name'] for k in st.session_state.keychains])
        if sel_edit:
            idx = next(i for i,k in enumerate(st.session_state.keychains) if k['name']==sel_edit)
            new_name = st.text_input("新名稱", value=st.session_state.keychains[idx]['name'])
            new_pic = st.file_uploader("加/換圖片")
            c1,c2 = st.columns(2)
            if c1.button("保存"):
                if new_name.strip(): st.session_state.keychains[idx]['name'] = new_name.strip()
                if new_pic: st.session_state.keychains[idx]['image'] = base64.b64encode(new_pic.read()).decode()
                st.rerun()
            if c2.button("刪除", use_container_width=True):
                del st.session_state.keychains[idx]; st.rerun()

# ============================== 歷史與統計（已修正）==============================
elif page == "歷史與統計":
    st.title("歷史與統計")

    total = len(st.session_state.keychains)
    drawn_count = len([k for k in st.session_state.keychains if k['name'] in st.session_state.drawn])
    used_set = set(st.session_state.used.values())  # 去重
    used_count = len([k for k in st.session_state.keychains if k['name'] in used_set])

    col1, col2, col3 = st.columns(3)
    col1.metric("總數", total)
    col2.metric("抽過", drawn_count)
    col3.metric("用過", used_count)

    st.markdown("---")
    st.subheader("所有鎖匙扣狀態")

    if total == 0:
        st.info("還沒有鎖匙扣")
    else:
        table_data = []
        for k in st.session_state.keychains:
            drawn_mark = "✓" if k['name'] in st.session_state.drawn else ""
            used_mark  = "✓" if k['name'] in used_set else ""
            table_data.append({
                "名稱": k['name'],
                "抽過": drawn_mark,
                "用過": used_mark
            })
            if k['image']:
                table_data[-1]["預覽"] = f"![圖片](data:image/png;base64,{k['image']})"

        st.write(table_data, use_container_width=True)  # Streamlit 自動轉成表格

    # 詳細歷史
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("抽籤歷史"):
            st.write("\n".join(f"• {x}" for x in st.session_state.drawn) or "無")
    with c2:
        with st.expander("實際使用日曆"):
            for d in sorted(st.session_state.used, reverse=True):
                st.write(f"**{d}** → {st.session_state.used[d]}")

# ============================== 備份頁（同之前）==============================
elif page == "備份與匯入":
    st.title("備份與匯入")
    backup = {"keychains": st.session_state.keychains, "drawn": list(st.session_state.drawn), "used": st.session_state.used}
    st.download_button("下載備份", json.dumps(backup, ensure_ascii=False), f"鎖匙扣備份_{date.today()}.json")
    up = st.file_uploader("上載備份", type="json")
    if up:
        try:
            data = json.load(up)
            st.session_state.keychains = data.get("keychains", [])
            st.session_state.drawn = set(data.get("drawn", []))
            st.session_state.used = data.get("used", {})
            st.success("匯入成功"); st.rerun()
        except:
            st.error("檔案錯誤")

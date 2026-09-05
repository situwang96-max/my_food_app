import streamlit as st

# 初始化网页设置
st.set_page_config(page_title="Wallace 的美食评价空间", page_icon="🍔", layout="wide")

# ==================== 初始化点赞数据 ====================
# 如果是第一次打开网页，初始化默认的点赞数
if "likes_dish5" not in st.session_state:
    st.session_state.likes_dish5 = 18  # 蒜蓉大虾
if "likes_dish3" not in st.session_state:
    st.session_state.likes_dish3 = 12  # 中式套餐
if "likes_dish2" not in st.session_state:
    st.session_state.likes_dish2 = 25  # 伊比利亚火腿
if "likes_dish4" not in st.session_state:
    st.session_state.likes_dish4 = 15  # 火腿包装
if "likes_dish1" not in st.session_state:
    st.session_state.likes_dish1 = 30  # 天妇罗

# 顶部标题
st.title("🍔 Wallace 的美食评价空间")
st.markdown("欢迎来到我的美食世界！这里记录了我亲自制作或品尝的真实美食体验。")

# 分类导航
tab1, tab2, tab3 = st.tabs(["中餐 🇨🇳", "西餐 🥩", "日本料理 🍣"])

# ==================== 中餐模块 ====================
with tab1:
    st.subheader("🍜 家常美味与中式套餐")
    
    # 菜品：大虾炒时蔬 (my_dish5.jpg)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("my_dish5.jpg", caption="蒜蓉大虾炒时蔬")
    with col2:
        st.markdown("### 🥇 蒜蓉大虾炒时蔬")
        st.write("大虾鲜甜弹牙，油菜吸收了虾汁和蒜蓉的香气，翠绿爽口。这是一道营养均衡、色香味俱全的家常硬菜！")
        st.markdown("**推荐指数：** ⭐⭐⭐⭐⭐")
        
        # 实时点赞按钮逻辑
        if st.button(f"点赞 👍 ({st.session_state.likes_dish5})", key="btn_dish5"):
            st.session_state.likes_dish5 += 1
            st.rerun() # 重新运行网页以刷新数字

    st.divider()

    # 菜品：中式套餐 (my_dish3.jpg)
    col3, col4 = st.columns([1, 2])
    with col3:
        st.image("my_dish3.jpg", caption="丰盛中式能量套餐")
    with col4:
        st.markdown("### 🥈 丰盛中式能量套餐")
        st.write("辣椒炒肉超级下饭，炸时蔬香脆可口，面包香甜。再配上一碗红豆沙，这一顿饭营养和能量直接拉满，简直是治愈系天花板！")
        st.markdown("**推荐指数：** ⭐⭐⭐⭐")
        
        if st.button(f"点赞 👍 ({st.session_state.likes_dish3})", key="btn_dish3"):
            st.session_state.likes_dish3 += 1
            st.rerun()


# ==================== 西餐模块 ====================
with tab2:
    st.subheader("🥩 西班牙火腿专题")
    
    # 菜品：火腿切片 (这里调换为了 my_dish2.jpg)
    col5, col6 = st.columns([1, 2])
    with col5:
        st.image("my_dish2.jpg", caption="伊比利亚火腿切片展示")
    with col6:
        st.markdown("### 🥇 50% 伊比利亚火腿（现切片）")
        st.write("脂肪如雪花般均匀分布，入口温润，由于体温让油脂微微融化，带着淡淡的橡果香气和咸鲜。无论是单吃还是搭配红酒、奶酪，都是极致的享受。")
        st.markdown("**推荐指数：** ⭐⭐⭐⭐⭐")
        
        if st.button(f"点赞 👍 ({st.session_state.likes_dish2})", key="btn_dish2"):
            st.session_state.likes_dish2 += 1
            st.rerun()

    st.divider()

    # 菜品：火腿包装 (my_dish4.jpg)
    col7, col8 = st.columns([1, 2])
    with col7:
        st.image("my_dish4.jpg", caption="Legado Ibérico 火腿包装")
    with col8:
        st.markdown("### 🥈 Legado Ibérico 火腿（24个月窖藏）")
        st.write("50% 纯种伊比利亚黑猪。这款开袋即食的火腿性价比极高，咸度适中，油脂丰盈。作为日常解馋和备用餐盘，品质非常稳定。")
        st.markdown("**推荐指数：** ⭐⭐⭐⭐")
        
        if st.button(f"点赞 👍 ({st.session_state.likes_dish4})", key="btn_dish4"):
            st.session_state.likes_dish4 += 1
            st.rerun()


# ==================== 日本料理模块 ====================
with tab3:
    st.subheader("🍣 精致日料体验")
    
    # 菜品：天妇罗 (这里调换为了 my_dish1.jpg)
    col9, col10 = st.columns([1, 2])
    with col9:
        st.image("my_dish1.jpg", caption="大虾天妇罗拼盘")
    with col10:
        st.markdown("### 🥇 什锦大虾天妇罗")
        st.write("天妇罗的面衣金黄轻薄、酥脆无比，大虾保留了饱满的汁水，外酥里嫩。搭配特制天妇罗蘸汁和大根泥，完美地带出了食材本身的鲜甜。")
        st.markdown("**推荐指数：** ⭐⭐⭐⭐⭐")
        
        if st.button(f"点赞 👍 ({st.session_state.likes_dish1})", key="btn_dish1"):
            st.session_state.likes_dish1 += 1
            st.rerun()
import streamlit as st
import sqlite3

# ==================== 1. 初始化数据库设置 ====================
def init_db():
    conn = sqlite3.connect("comments.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dish_id TEXT,
            username TEXT,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_comment(dish_id, username, content):
    conn = sqlite3.connect("comments.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (dish_id, username, content) VALUES (?, ?, ?)", (dish_id, username, content))
    conn.commit()
    conn.close()

def get_comments(dish_id):
    conn = sqlite3.connect("comments.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, content, datetime(created_at, 'localtime') FROM comments WHERE dish_id = ? ORDER BY created_at DESC", (dish_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

init_db()


# ==================== 2. 网页初始化与背景美化 ====================
st.set_page_config(page_title="Wallace 的美食评价空间", page_icon="🍔", layout="wide")

# 🎨 注入自定义 CSS，将网页背景改为柔和、温馨的浅米色（更像美食博主的网站）
st.markdown("""
<style>
.stApp {
    background-color: #FAF8F6;
}
</style>
""", unsafe_allow_html=True)


# 初始化页面跳转状态
if "selected_dish" not in st.session_state:
    st.session_state.selected_dish = None  # None 代表在主页

# 初始化点赞数据
if "likes_dish5" not in st.session_state: st.session_state.likes_dish5 = 18
if "likes_dish3" not in st.session_state: st.session_state.likes_dish3 = 12
if "likes_dish2" not in st.session_state: st.session_state.likes_dish2 = 25
if "likes_dish4" not in st.session_state: st.session_state.likes_dish4 = 15
if "likes_dish1" not in st.session_state: st.session_state.likes_dish1 = 30


# 定义每个菜品的详细数据（用于详情页展示）
DISH_DATA = {
    "dish5": {
        "title": "🥇 蒜蓉大虾炒时蔬",
        "image": "my_dish5.jpg",
        "desc": "大虾鲜甜弹牙，油菜吸收了虾汁和蒜蓉的香气，翠绿爽口。",
        "detail": "### 👨‍🍳 主厨秘籍与步骤\n1. **食材准备**：新鲜对虾去虾线，青口油菜洗净切段。\n2. **爆香大蒜**：热锅冷油，下入大量蒜蓉，慢火煸炒至金黄色流油。\n3. **大虾下锅**：转大火，下入大虾翻炒至变红变弯曲，逼出鲜美虾油。\n4. **合体出锅**：最后加入油菜，快速翻炒30秒，撒入少许食盐即可出锅。保持油菜的翠绿与爽脆！"
    },
    "dish3": {
        "title": "🥈 丰盛中式能量套餐",
        "image": "my_dish3.jpg",
        "desc": "有荤有素，辣椒炒肉超级下饭，炸时蔬香脆可口。",
        "detail": "### 🍚 套餐配置详解\n* **主食**：肉松沙拉面包，外皮松软，肉松分量扎实。\n* **主菜**：经典辣椒炒肉，精选五花肉大火爆炒，辣味过瘾，极为下饭。\n* **副菜**：香炸椒盐时蔬，裹上薄浆炸至金黄，外酥里嫩。\n* **甜品与汤**：暖胃红豆沙搭配清汤丸子，一冷一热，解腻舒心。"
    },
    "dish2": {
        "title": "🥇 50% 伊比利亚火腿（现切片）",
        "image": "my_dish2.jpg",
        "desc": "脂肪如雪花般均匀分布，入口温润，带着淡淡的橡果香气与细腻的咸鲜。",
        "detail": "### 🍷 品鉴与搭配建议\n* **切片艺术**：火腿切片需保持极薄，用指尖温度使其油脂微微融化时，口感最佳。\n* **佐餐搭配**：强烈推荐搭配陈年红葡萄酒（如Rioja）或桃红香槟。\n* **美味吃法**：尝试搭配成熟度高的哈密瓜，咸甜交织，是经典的西班牙吃法。"
    },
    "dish4": {
        "title": "🥈 Legado Ibérico 火腿（24个月）",
        "image": "my_dish4.jpg",
        "desc": "50% 纯种伊比利亚黑猪，咸度适中，油脂丰盈。",
        "detail": "### 🛒 购买与保存指南\n* **品牌故事**：Legado Ibérico 是西班牙家喻户晓的优质火腿品牌，控温窖藏24个月以上。\n* **开袋指南**：从冰箱取出后，切勿直接食用。建议室温静置20分钟，让火腿油脂苏醒。\n* **储存方法**：开封后用保鲜膜严密封口，放入冰箱冷藏，并在3天内食用完毕以保持最佳风味。"
    },
    "dish1": {
        "title": "🥇 什锦大虾天妇罗",
        "image": "my_dish1.jpg",
        "desc": "面衣金黄轻薄、酥脆无比，大虾保留了饱满的汁水，外酥里嫩。",
        "detail": "### 🍤 酥脆面衣的秘密\n1. **面糊秘诀**：使用冰水调和低筋面粉，千万不能过度搅拌，保留小面疙瘩才是酥脆的关键。\n2. **油温控制**：油温必须保持在 170°C - 180°C。滴入面糊能立刻浮起并发出沙沙声。\n3. **黄金蘸汁**：出汁（昆布柴鱼汤）、酱油、味醂按 4:1:1 调制，加入白萝卜泥，清爽解腻。"
    }
}


# ==================== 3. 逻辑分流：详情页 VS 主页 ====================

if st.session_state.selected_dish is not None:
    # ---------------- 页面 A：菜品详情页 ----------------
    dish_id = st.session_state.selected_dish
    data = DISH_DATA[dish_id]
    
    # 返回按钮
    if st.button("⬅️ 返回主页", key="back_to_main"):
        st.session_state.selected_dish = None
        st.rerun()
        
    st.divider()
    
    # 详情展示（左右分栏）
    col_img, col_txt = st.columns([1, 1.2])
    with col_img:
        st.image(data["image"], use_container_width=True)
    with col_txt:
        st.title(data["title"])
        st.caption(data["desc"])
        st.markdown(data["detail"])
        
    st.divider()
    
    # 💬 专属评论区
    st.subheader(f"💬 {data['title']} 的食客留言板")
    
    # 评论输入表单
    with st.form(key=f"form_{dish_id}", clear_on_submit=True):
        user_name = st.text_input("您的昵称：", placeholder="例如：好吃爱吃")
        user_comment = st.text_area("您的评价：", placeholder="写下你的真实食评吧...")
        submit_button = st.form_submit_button(label="提交评价 🚀")
        
        if submit_button:
            if user_name.strip() == "" or user_comment.strip() == "":
                st.warning("⚠️ 昵称和评价内容都不能为空哦！")
            else:
                add_comment(dish_id, user_name, user_comment)
                st.success("🎉 评价发表成功！")
                st.rerun()
    
    # 展示历史评论
    comments_list = get_comments(dish_id)
    if len(comments_list) == 0:
        st.caption("暂无评论，快来抢沙发吧！🛋️")
    else:
        for username, content, created_at in comments_list:
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #FF4B4B;">
                <strong style="color: #FF4B4B;">👤 {username}</strong> 
                <span style="color: #888; font-size: 0.8em; float: right;">🕒 {created_at}</span>
                <p style="margin-top: 10px; margin-bottom: 0px; color: #333;">{content}</p>
            </div>
            """, unsafe_allow_html=True)

else:
    # ---------------- 页面 B：主页目录 ----------------
    st.title("🍔 Wallace 的美食评价空间")
    st.markdown("欢迎来到我的美食世界！这里记录了我亲自制作或品尝的真实美食体验。")
    
    tab1, tab2, tab3 = st.tabs(["中餐 🇨🇳", "西餐 🥩", "日本料理 🍣"])
    
    # --- 中餐模块 ---
    with tab1:
        st.subheader("🍜 家常美味与中式套餐")
        
        # 菜品：大虾炒时蔬
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("my_dish5.jpg")
        with col2:
            st.markdown("### 🥇 蒜蓉大虾炒时蔬")
            st.write(DISH_DATA["dish5"]["desc"])
            st.markdown("**推荐指数：** ⭐⭐⭐⭐⭐")
            
            # 点击按钮，切换到对应菜品的详情页状态
            if st.button("查看详情 📖", key="view_dish5"):
                st.session_state.selected_dish = "dish5"
                st.rerun()
                
            if st.button(f"点赞 👍 ({st.session_state.likes_dish5})", key="btn_dish5"):
                st.session_state.likes_dish5 += 1
                st.rerun()

        st.divider()

        # 菜品：中式套餐
        col3, col4 = st.columns([1, 2])
        with col3:
            st.image("my_dish3.jpg")
        with col4:
            st.markdown("### 🥈 丰盛中式能量套餐")
            st.write(DISH_DATA["dish3"]["desc"])
            st.markdown("**推荐指数：** ⭐⭐⭐⭐")
            
            if st.button("查看详情 📖", key="view_dish3"):
                st.session_state.selected_dish = "dish3"
                st.rerun()
                
            if st.button(f"点赞 👍 ({st.session_state.likes_dish3})", key="btn_dish3"):
                st.session_state.likes_dish3 += 1
                st.rerun()

    # --- 西餐模块 ---
    with tab2:
        st.subheader("🥩 西班牙火腿专题")
        
        # 菜品：火腿切片
        col5, col6 = st.columns([1, 2])
        with col5:
            st.image("my_dish2.jpg")
        with col6:
            st.markdown("### 🥇 50% 伊比利亚火腿（现切片）")
            st.write(DISH_DATA["dish2"]["desc"])
            st.markdown("**推荐指数：** ⭐⭐⭐⭐⭐")
            
            if st.button("查看详情 📖", key="view_dish2"):
                st.session_state.selected_dish = "dish2"
                st.rerun()
                
            if st.button(f"点赞 👍 ({st.session_state.likes_dish2})", key="btn_dish2"):
                st.session_state.likes_dish2 += 1
                st.rerun()

        st.divider()

        # 菜品：火腿包装
        col7, col8 = st.columns([1, 2])
        with col7:
            st.image("my_dish4.jpg")
        with col8:
            st.markdown("### 🥈 Legado Ibérico 火腿（24个月）")
            st.write(DISH_DATA["dish4"]["desc"])
            st.markdown("**推荐指数：** ⭐⭐⭐⭐")
            
            if st.button("查看详情 📖", key="view_dish4"):
                st.session_state.selected_dish = "dish4"
                st.rerun()
                
            if st.button(f"点赞 👍 ({st.session_state.likes_dish4})", key="btn_dish4"):
                st.session_state.likes_dish4 += 1
                st.rerun()

    # --- 日本料理模块 ---
    with tab3:
        st.subheader("🍣 精致日料体验")
        
        # 菜品：天妇罗
        col9, col10 = st.columns([1, 2])
        with col9:
            st.image("my_dish1.jpg")
        with col10:
            st.markdown("### 🥇 什锦大虾天妇罗")
            st.write(DISH_DATA["dish1"]["desc"])
            st.markdown("**推荐指数：** ⭐⭐⭐⭐⭐")
            
            if st.button("查看详情 📖", key="view_dish1"):
                st.session_state.selected_dish = "dish1"
                st.rerun()
                
            if st.button(f"点赞 👍 ({st.session_state.likes_dish1})", key="btn_dish1"):
                st.session_state.likes_dish1 += 1
                st.rerun()
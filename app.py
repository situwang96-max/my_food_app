import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import os  # 新增：用于检测文件是否存在

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


# ==================== 2. 安全图片加载器（防崩溃核心） ====================
# 这个函数会自动尝试各种大小写后缀，如果文件不存在，会显示温馨提示而绝对不红屏崩溃！
def safe_image(img_path, caption=None, use_container_width=True):
    # 1. 尝试原文件名
    if os.path.exists(img_path):
        st.image(img_path, caption=caption, use_container_width=use_container_width)
        return
    
    # 2. 如果不存在，自动尝试其他常见后缀（大写 JPG、PNG 等）
    base, ext = os.path.splitext(img_path)
    for alt_ext in [ext.upper(), ext.lower(), '.jpg', '.JPG', '.png', '.PNG', '.jpeg', '.JPEG']:
        alt_path = base + alt_ext
        if os.path.exists(alt_path):
            st.image(alt_path, caption=caption, use_container_width=use_container_width)
            return
            
    # 3. 实在没有找到，显示友好提示，不破坏网页结构
    st.info(f"📷 图片正在云端同步中: {img_path} (请确保它已分批上传至 GitHub 仓库)")


# ==================== 3. 网页初始化与背景美化 ====================
st.set_page_config(page_title="Wallace 的个人精神空间", page_icon="📓", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #FAF8F6;
}
</style>
""", unsafe_allow_html=True)

# ✨ 鼠标点击漂浮粒子特效 JavaScript
components.html("""
<script>
const parentDoc = window.parent.document;
if (!parentDoc.getElementById('click-effect-handler')) {
    const style = parentDoc.createElement('style');
    style.innerHTML = `
        .click-sparkle {
            position: absolute;
            pointer-events: none;
            font-size: 24px;
            transition: all 0.8s cubic-bezier(0.25, 1, 0.5, 1);
            opacity: 1;
            z-index: 999999;
            user-select: none;
            font-weight: bold;
        }
    `;
    parentDoc.head.appendChild(style);

    const handler = parentDoc.createElement('div');
    handler.id = 'click-effect-handler';
    parentDoc.body.appendChild(handler);

    parentDoc.addEventListener('click', function(e) {
        const sparkle = parentDoc.createElement('span');
        sparkle.className = 'click-sparkle';
        const emojis = ["✨", "🍔", "🍣", "❤️", "🌸", "🍕", "🍤", "📓"];
        sparkle.textContent = emojis[Math.floor(Math.random() * emojis.length)];
        sparkle.style.left = (e.pageX - 12) + 'px';
        sparkle.style.top = (e.pageY - 12) + 'px';
        parentDoc.body.appendChild(sparkle);

        setTimeout(() => {
            sparkle.style.transform = 'translateY(-80px) scale(1.6) rotate(' + (Math.random() * 360) + 'deg)';
            sparkle.style.opacity = '0';
        }, 50);

        setTimeout(() => {
            sparkle.remove();
        }, 800);
    });
}
</script>
""", height=0)


# ==================== 4. 导航与页面状态管理 ====================
if "likes_dish5" not in st.session_state: st.session_state.likes_dish5 = 18
if "likes_dish3" not in st.session_state: st.session_state.likes_dish3 = 12
if "likes_dish2" not in st.session_state: st.session_state.likes_dish2 = 25
if "likes_dish4" not in st.session_state: st.session_state.likes_dish4 = 15
if "likes_dish1" not in st.session_state: st.session_state.likes_dish1 = 30

if "selected_dish" not in st.session_state: st.session_state.selected_dish = None
if "selected_diary" not in st.session_state: st.session_state.selected_diary = None
if "selected_daily" not in st.session_state: st.session_state.selected_daily = None

menu = st.sidebar.radio(
    "🧭 导航菜单",
    ["🍔 经典美食评测", "📓 个人私密日记", "🛒 Wallace 的日常生活"]
)


# ==================== 页面一：经典美食评测 ====================
if menu == "🍔 经典美食评测":
    DISH_DATA = {
        "dish5": {
            "title": "🥇 蒜蓉大虾炒时蔬", "image": "my_dish5.jpg", "desc": "大虾鲜甜弹牙，油菜吸收了虾汁和蒜蓉的香气，翠绿爽口。",
            "detail": "### 👨‍🍳 主厨秘籍与步骤\n1. **食材准备**：新鲜对虾去虾线，青口油菜洗净切段。\n2. **爆香大蒜**：热锅冷油，下入大量蒜蓉，慢火sauté至金黄色流油。\n3. **大虾下锅**：转大火，下入大虾翻炒至变红变弯曲，逼出鲜美虾油。\n4. **合体出锅**：最后加入油菜，快速翻炒30秒，撒入少许食盐即可出锅。保持油菜的翠绿与爽脆！"
        },
        "dish3": {
            "title": "🥈 丰盛中式能量套餐", "image": "my_dish3.jpg", "desc": "有荤有素，辣椒炒肉超级下饭，炸时蔬香脆可口。",
            "detail": "### 🍚 套餐配置详解\n* **主食**：肉松沙拉面包，外皮松软，肉松分量扎实。\n* **主菜**：经典辣椒炒肉，精选五花肉大火爆炒，辣味过瘾，极为下饭。\n* **副菜**：香炸椒盐时蔬，裹上薄浆炸至金黄，外酥里嫩。\n* **甜品与汤**：暖胃红豆沙搭配清汤丸子，一冷一热，解腻舒心。"
        },
        "dish2": {
            "title": "🥇 50% 伊比利亚火腿（现切片）", "image": "my_dish2.jpg", "desc": "脂肪如雪花般均匀分布，入口温润，带着淡淡的橡果香气与细腻的咸鲜。",
            "detail": "### 🍷 品鉴与搭配建议\n* **切片艺术**：火腿切片需保持极薄，用指尖温度使其油脂微微融化时，口感最佳。\n* **佐餐搭配**：强烈推荐搭配陈年红葡萄酒（如Rioja）或桃红香槟。\n* **美味吃法**：尝试搭配成熟度高的哈密瓜，咸甜交织，是经典的西班牙吃法。"
        },
        "dish4": {
            "title": "🥈 Legado Ibérico 火腿（24个月）", "image": "my_dish4.jpg", "desc": "50% 纯种伊比利亚黑猪，咸度适中，油脂丰盈。",
            "detail": "### 🛒 购买与保存指南\n* **品牌故事**：Legado Ibérico 是西班牙家喻户晓的优质火腿品牌，控温窖藏24个月以上。\n* **开袋指南**：从冰箱取出后，切勿直接食用。建议室温静置20分钟，让火腿油脂苏醒。\n* **储存方法**：开封后用保鲜膜封口，放入冰箱冷藏，并在3天内食用完毕以保持最佳风味。"
        },
        "dish1": {
            "title": "🥇 什锦大虾天妇罗", "image": "my_dish1.jpg", "desc": "面衣金黄轻薄、酥脆无比，大虾保留了饱满的汁水，外酥里嫩。",
            "detail": "### 🍤 酥脆面衣的秘密\n1. **面糊秘诀**：使用冰水调和低筋面粉，千万不能过度搅拌，保留小面疙瘩才是酥脆的关键。\n2. **油温控制**：油温必须保持在 170°C - 180°C。滴入面糊能立刻浮起并发出沙沙声。\n3. **黄金蘸汁**：出汁、酱油、味醂按 4:1:1 调制，加入白萝卜泥，清爽解腻。"
        }
    }

    if st.session_state.selected_dish is not None:
        dish_id = st.session_state.selected_dish
        data = DISH_DATA[dish_id]
        if st.button("⬅️ 返回主页", key="back_to_main"):
            st.session_state.selected_dish = None
            st.rerun()
        st.divider()
        col_img, col_txt = st.columns([1, 1.2])
        with col_img: 
            # 使用安全加载器
            safe_image(data["image"])
        with col_txt:
            st.title(data["title"])
            st.caption(data["desc"])
            st.markdown(data["detail"])
        st.divider()
        st.subheader(f"💬 {data['title']} 的食客留言板")
        with st.form(key=f"form_{dish_id}", clear_on_submit=True):
            user_name = st.text_input("您的昵称：", placeholder="例如：好吃爱吃")
            user_comment = st.text_area("您的评价：", placeholder="写下你的真实食评吧...")
            if st.form_submit_button(label="提交评价 🚀"):
                if user_name.strip() == "" or user_comment.strip() == "":
                    st.warning("⚠️ 昵称和评价内容都不能为空哦！")
                else:
                    add_comment(dish_id, user_name, user_comment)
                    st.success("🎉 评价发表成功！")
                    st.rerun()
        comments_list = get_comments(dish_id)
        if len(comments_list) == 0: st.caption("暂无评论，快来抢沙发吧！🛋️")
        else:
            for username, content, created_at in comments_list:
                st.markdown(f'<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #FF4B4B;"><strong style="color: #FF4B4B;">👤 {username}</strong><span style="color: #888; font-size: 0.8em; float: right;">🕒 {created_at}</span><p style="margin-top: 10px; margin-bottom: 0px; color: #333;">{content}</p></div>', unsafe_allow_html=True)
    else:
        st.title("🍔 经典美食评测")
        st.markdown("这里记录了我品尝和制作的各种经典美食。点击“查看详情”了解更多。")
        tab1, tab2, tab3 = st.tabs(["中餐 🇨🇳", "西餐 🥩", "日本料理 🍣"])
        with tab1:
            st.subheader("🍜 家常美味与中式套餐")
            col1, col2 = st.columns([1, 2])
            with col1: safe_image("my_dish5.jpg")
            with col2:
                st.markdown("### 🥇 蒜蓉大虾炒时蔬")
                st.write(DISH_DATA["dish5"]["desc"])
                if st.button("查看详情 📖", key="view_dish5"): st.session_state.selected_dish = "dish5"; st.rerun()
                if st.button(f"点赞 👍 ({st.session_state.likes_dish5})", key="btn_dish5"): st.session_state.likes_dish5 += 1; st.rerun()
            st.divider()
            col3, col4 = st.columns([1, 2])
            with col3: safe_image("my_dish3.jpg")
            with col4:
                st.markdown("### 🥈 丰盛中式能量套餐")
                st.write(DISH_DATA["dish3"]["desc"])
                if st.button("查看详情 📖", key="view_dish3"): st.session_state.selected_dish = "dish3"; st.rerun()
                if st.button(f"点赞 👍 ({st.session_state.likes_dish3})", key="btn_dish3"): st.session_state.likes_dish3 += 1; st.rerun()
        with tab2:
            st.subheader("🥩 西班牙火腿专题")
            col1, col2 = st.columns([1, 2])
            with col1: safe_image("my_dish2.jpg")
            with col2:
                st.markdown("### 🥇 50% 伊比利亚火腿（现切片）")
                st.write(DISH_DATA["dish2"]["desc"])
                if st.button("查看详情 📖", key="view_dish2"): st.session_state.selected_dish = "dish2"; st.rerun()
                if st.button(f"点赞 👍 ({st.session_state.likes_dish2})", key="btn_dish2"): st.session_state.likes_dish2 += 1; st.rerun()
            st.divider()
            col3, col4 = st.columns([1, 2])
            with col3: safe_image("my_dish4.jpg")
            with col4:
                st.markdown("### 🥈 Legado Ibérico 火腿（24个月）")
                st.write(DISH_DATA["dish4"]["desc"])
                if st.button("查看详情 📖", key="view_dish4"): st.session_state.selected_dish = "dish4"; st.rerun()
                if st.button(f"点赞 👍 ({st.session_state.likes_dish4})", key="btn_dish4"): st.session_state.likes_dish4 += 1; st.rerun()
        with tab3:
            st.subheader("🍣 精致日料体验")
            col1, col2 = st.columns([1, 2])
            with col1: safe_image("my_dish1.jpg")
            with col2:
                st.markdown("### 🥇 什锦大虾天妇罗")
                st.write(DISH_DATA["dish1"]["desc"])
                if st.button("查看详情 📖", key="view_dish1"): st.session_state.selected_dish = "dish1"; st.rerun()
                if st.button(f"点赞 👍 ({st.session_state.likes_dish1})", key="btn_dish1"): st.session_state.likes_dish1 += 1; st.rerun()


# ==================== 页面二：个人私密日记 ====================
elif menu == "📓 个人私密日记":
    DIARY_POSTS = {
        "road": {
            "title": "《路》—— 顺河高架与三克的温度",
            "date": "2026-09-05",
            "excerpt": "凌晨三点的济南，顺河高架上很空。没有一辆车在等。但我知道，什么都会发生。",
            "content": """
            一套欧舒丹三支装手霜礼盒的重量，九十克。
            一条我自己买的金项链的重量，三克。
            三克，并不多。
            路医生把后者退给我的时候，是在我的车里。
            她说：
            “现在还不是时候。”
            她抵押给我的，是下一次见面。

            济南第三人民医院在工业北路，旁边是顺河高架。
            她在那里的消化科，值班，查房，看那些坏掉的胃。
            她天天很忙，待遇降了不少，她觉得绝望，甚至开玩笑说想去跑外卖。
            我没有劝她坚持。
            我是唯一一个劝她辞职的人。

            七月，二十六国外的世界杯决赛还没踢。
            她猜阿根廷夺冠，我猜西班牙。
            后来西班牙赢了，我猜对了。

            下一次见面，隔了整整一个月。她连着上了一个月的班，没有私人时间。
            I didn't rush her.
            送出那套三支装手霜礼盒的时候，我也把那条三克的金项链给了她。
            我觉得我们接触了快两个月，也是时候了。
            路医生没有生气，她把项链收下，又温和地推回来：
            “下次见面，我给你送回来。”
            她没有说下次是什么时候。
            我也没有问。

            那天她刚烫了头发。
            新发型有些蓬松，显得比平时成熟，甚至有些老气。她没化妆，皮肤在下午车里的光线里，不如上次见面时雪白。
            我看着她的侧脸。
            我的心跳很稳。
            一分钟六十几下，和在银行上班、看复核姐姐哭泣时没有区别。

            我每周去五次健身房，自己做健康餐。
            她不知道我曾经有过多么混乱的深夜，我从没让她发现过，以后她也不会知道了。

            今晚，我买了山姆的大鱿鱼、罗氏虾和肥肠。
            我今天去外面的健身房练了力量，感觉力气变大了，手臂上的肌肉绷得很紧。
            路医生的那套手霜礼盒，还在她的抽屉里。
            下周，她要来还那条项链。
            那是我们的第五次见面。

            我想：
            原来是这样。
            凌晨三点的济南，顺河高架上很空。
            没有一辆车在等。
            但这一次。
            我知道，什么都会发生。
            """
        }
    }

    if st.session_state.selected_diary is not None:
        post_id = st.session_state.selected_diary
        post = DIARY_POSTS[post_id]
        if st.button("⬅️ 返回日记列表", key="back_to_diary"):
            st.session_state.selected_diary = None
            st.rerun()
        
        st.divider()
        st.title(post["title"])
        st.caption(f"🕒 发表于 {post['date']} | 独立创作")
        
        st.markdown(f"""
        <div style="font-family: 'Georgia', serif; font-size: 1.15em; line-height: 2; color: #2c3e50; padding: 20px; background-color: #fff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); max-width: 800px; margin: 0 auto;">
            {post['content'].replace('\\n', '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("💬 读后感与私密回应")
        with st.form(key=f"form_diary_{post_id}", clear_on_submit=True):
            user_name = st.text_input("昵称：", placeholder="留下一个代号...")
            user_comment = st.text_area("寄语：", placeholder="说你想说的话...")
            if st.form_submit_button("发送 📮"):
                if user_name.strip() and user_comment.strip():
                    add_comment(f"diary_{post_id}", user_name, user_comment)
                    st.success("🎉 发送成功！")
                    st.rerun()
        comments_list = get_comments(f"diary_{post_id}")
        for username, content, created_at in comments_list:
            st.markdown(f'<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #FF4B4B;"><strong style="color: #FF4B4B;">👤 {username}</strong><span style="color: #888; font-size: 0.8em; float: right;">🕒 {created_at}</span><p style="margin-top: 10px; margin-bottom: 0px; color: #333;">{content}</p></div>', unsafe_allow_html=True)

    else:
        st.title("📓 Wallace 的个人私密日记")
        st.markdown("一些在寂静深夜、高架桥上，或银行复核机器轰鸣声中的个人随笔。")
        
        for k, v in DIARY_POSTS.items():
            st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 6px solid #2c3e50; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px;">
                <h3 style="margin-top:0px; color: #2c3e50;">{v['title']}</h3>
                <span style="color: #888; font-size: 0.9em;">🕒 {v['date']}</span>
                <p style="color: #555; margin-top: 15px; font-style: italic; font-family: 'Georgia', serif;">“{v['excerpt']}”</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("点击阅读完整篇章 📖", key=f"read_{k}"):
                st.session_state.selected_diary = k
                st.rerun()


# ==================== 页面三：Wallace 的日常生活 ====================
elif menu == "🛒 Wallace 的日常生活":
    DAILY_STORIES = {
        "sams": {
            "title": "《山姆的日光灯与冻肉之美》",
            "date": "2026-09-05",
            "excerpt": "176块1毛6的加拿大牛腱子，裹在坚硬的塑料膜里，呈现出一种近乎死寂的暗红色。在这里，生命被切割、冷冻、明码标价。",
            "images": ["daily_sams_cart.jpg", "daily_sams_shank.jpg", "daily_frozen_beef.jpg", "daily_lunch.jpg"],
            "content": """
            白炽日光灯像冰冷的刀子，无情地剖开山姆会员店巨大的、挑高的、充斥着冷气的空间。
            我推着笨重的购物车，不锈钢车轮在干净得有些虚无的地面上发出轻微、神经质的摩擦声。
            
            176块1毛6的加拿大牛腱子，裹在紧绷、反光的塑料收缩膜里，呈现出一种近乎死寂的暗红色。
            旁边是布满人工白霜的雪花肥牛，那脂肪的花纹在低温中冷酷而精确。
            在这里，往昔狂奔的生命被切割、冷冻、明码标价。
            
            我冷漠地往铁网车里扔了一箱无糖希腊酸奶和一颗巨大的、布满斑纹的西瓜。它们沉重地坠落，像墓碑和炮弹一样压弯了不锈钢铁网。
            
            回到银行，正午。
            食堂白瓷盘里那个木讷的南瓜、缠绕多汁的粉丝，以及泛着温热油光的肉丸，在复核姐姐细微、沉闷的啜泣声中，被我一口口机械地咽下喉咙。
            我的心跳依旧是一分钟六十几下，稳定、迟闷得像一架没有灵魂的工业测谎仪。
            混乱的深夜早已远去，我只是用哑铃、冰冷的重铁和这大块的生牛肉，将它们生生压进废墟的底层，筑起一道理性的高墙。
            """
        },
        "kitchen": {
            "title": "《黄油、烈火与虎皮青椒的余温》",
            "date": "2026-09-05",
            "excerpt": "粗砺的青椒在铸铁锅的干烧下绽开焦黑的斑点，像垂死挣扎时留下的虎皮斑纹。这就是食物的解剖。",
            "images": ["daily_butter_prawns.jpg", "daily_prep_board.jpg", "daily_tofu_beef_pot.jpg", "daily_beef_wok.jpg", "daily_boiled_beef.jpg", "daily_stewed_beef.jpg"],
            "content": """
            案板上，苍白、坚硬的北豆腐被利刃切成绝对完美的几何方块。
            旁边，粗砺的青椒在铸铁锅烈火的干烧下急剧收缩，绽开焦黑、碳化的斑点，像野兽垂死挣扎时留下的虎皮斑纹。
            
            在我眼里，烹饪不是艺术，而是一场对自然生命精密的解剖。
            
            金黄色的黄油在高温的煎锅中发出滋滋的、绝望的哀鸣，随即化为一摊滚烫的油脂，将那些罗氏大虾那艳丽、坚硬的红壳无情地吞噬。
            铁锅里大火翻炒，热油的甜香混杂着大蒜被拍碎后释放的辛辣，在一瞬间将狭窄的厨房填满。
            这些曾经在水底游动的生灵，在我的铁锅里完成了它们最后一次壮烈、香气四溢的合唱。
            
            当红亮的虾肉、冒着滚烫气泡的牛肉豆腐煲以及泼满芝麻的水煮牛肉端上木桌时，我独自坐在阴影里，看着浓白的热气在空气中徐徐上升，又在数秒内迅速、寂静地消散。
            
            食物不过是维持肉体运动的卡路里。
            而在每一个无人的深夜，我正是用这些精妙、算计好的热量，维持着我与这个荒诞世界最虚妄的连接。
            """
        }
    }

    if st.session_state.selected_daily is not None:
        story_id = st.session_state.selected_daily
        story = DAILY_STORIES[story_id]
        if st.button("⬅️ 返回日常生活", key="back_to_daily_list"):
            st.session_state.selected_daily = None
            st.rerun()
        
        st.divider()
        st.title(story["title"])
        st.caption(f"🕒 记录时间：{story['date']} | 摄影与撰文：Wallace")
        
        st.markdown(f"""
        <div style="font-family: 'Kaiti', 'STKaiti', serif; font-size: 1.2em; line-height: 2.1; color: #1a1a1a; padding: 25px; background-color: #FDFCF7; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); max-width: 850px; margin: 0 auto; border-left: 4px solid #8e8e8e;">
            {story['content'].replace('\\n', '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("📷 故事背后的真实快照")
        
        # 使用安全图片加载器，防止因为部分图片大写或未上传完毕导致崩溃
        for i in range(0, len(story["images"]), 2):
            cols = st.columns(2)
            with cols[0]:
                safe_image(story["images"][i])
            if i + 1 < len(story["images"]):
                with cols[1]:
                    safe_image(story["images"][i+1])
                    
        st.write("---")
        st.subheader("💬 朋友的碎碎念")
        with st.form(key=f"form_daily_{story_id}", clear_on_submit=True):
            user_name = st.text_input("昵称：", placeholder="过客...")
            user_comment = st.text_area("留言：", placeholder="留下你的脚印...")
            if st.form_submit_button("提交留言 📪"):
                if user_name.strip() and user_comment.strip():
                    add_comment(f"daily_{story_id}", user_name, user_comment)
                    st.success("🎉 留言成功！")
                    st.rerun()
        comments_list = get_comments(f"daily_{story_id}")
        for username, content, created_at in comments_list:
            st.markdown(f'<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #8e8e8e;"><strong style="color: #555;">👤 {username}</strong><span style="color: #888; font-size: 0.8em; float: right;">🕒 {created_at}</span><p style="margin-top: 10px; margin-bottom: 0px; color: #333;">{content}</p></div>', unsafe_allow_html=True)

    else:
        st.title("🛒 Wallace 的日常生活分享")
        st.markdown("将枯燥、麻木、冷硬的日常生活，用锋利的文字与真实的快照进行解剖。")
        
        for k, v in DAILY_STORIES.items():
            st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 6px solid #8e8e8e; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px;">
                <h3 style="margin-top:0px; color: #333;">{v['title']}</h3>
                <span style="color: #888; font-size: 0.9em;">🕒 {v['date']}</span>
                <p style="color: #666; margin-top: 15px; font-style: italic; font-family: 'Georgia', serif;">“{v['excerpt']}”</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("阅读此篇日常与看照片 📖", key=f"read_daily_{k}"):
                st.session_state.selected_daily = k
                st.rerun()


# ==================== 5. 🎵 底部 B 站背景音乐播放器（回归主宽屏，解决精简版音量被隐藏的问题） ====================
# 这里把它从左侧窄边栏移回主宽页面最下方，B站播放器会自动识别并显示完整版，包含音量调节滑块！
st.write("---")
st.markdown("#### 🎵 顺河高架电台")
st.write("点击下方播放按钮，一边听着温暖的 Lo-Fi 音乐，一边开启阅读之旅吧：")
components.html("""
<iframe src="//player.bilibili.com/player.html?bvid=BV1Aa411C7EJ&page=1&high_quality=1" 
        scrolling="no" 
        border="0" 
        frameborder="no" 
        framespacing="0" 
        allowfullscreen="true" 
        width="100%" 
        height="320">
</iframe>
""", height=340)
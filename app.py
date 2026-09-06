import html
import os
import sqlite3

import streamlit as st
import streamlit.components.v1 as components


# ==================== 1. 基础配置 ====================
st.set_page_config(
    page_title="Wallace 的个人精神空间",
    page_icon="📓",
    layout="wide",
)

DB_PATH = "comments.db"


# ==================== 2. 数据库 ====================
def get_connection():
    """打开数据库连接。"""
    return sqlite3.connect(DB_PATH)


def init_db():
    """创建评论表和点赞表；如果已经存在，则保留原数据。"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dish_id TEXT NOT NULL,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS likes (
            item_id TEXT PRIMARY KEY,
            like_count INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    conn.commit()
    conn.close()


def add_comment(item_id, username, content):
    """保存一条评论。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO comments (dish_id, username, content) VALUES (?, ?, ?)",
        (item_id, username, content),
    )
    conn.commit()
    conn.close()


def get_comments(item_id):
    """按照最新时间倒序读取评论。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT username, content, datetime(created_at, 'localtime')
        FROM comments
        WHERE dish_id = ?
        ORDER BY created_at DESC
        """,
        (item_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def init_like_counts(default_counts):
    """第一次运行时，把原来的点赞初始值写进数据库。"""
    conn = get_connection()
    cursor = conn.cursor()

    for item_id, count in default_counts.items():
        cursor.execute(
            "INSERT OR IGNORE INTO likes (item_id, like_count) VALUES (?, ?)",
            (item_id, count),
        )

    conn.commit()
    conn.close()


def get_like_count(item_id):
    """读取点赞数量。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT like_count FROM likes WHERE item_id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


def add_like(item_id):
    """把指定内容的点赞数加 1。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE likes SET like_count = like_count + 1 WHERE item_id = ?",
        (item_id,),
    )
    conn.commit()
    conn.close()


LIKE_DEFAULTS = {
    "dish5": 18,
    "dish3": 12,
    "dish2": 25,
    "dish4": 15,
    "dish1": 30,
}

init_db()
init_like_counts(LIKE_DEFAULTS)


# ==================== 3. 图片加载 ====================
def safe_image(img_path, caption=None, width="stretch"):
    """图片存在就显示；不存在时尝试常见扩展名，最后给出友好提示。"""
    if os.path.exists(img_path):
        st.image(img_path, caption=caption, use_container_width=True)
        return

    base, ext = os.path.splitext(img_path)
    alt_suffixes = [
        ext.upper(),
        ext.lower(),
        ".jpg",
        ".JPG",
        ".png",
        ".PNG",
        ".jpeg",
        ".JPEG",
        ".jpg.jpg",
        ".jpg.JPG",
        ".JPG.jpg",
        ".JPG.JPG",
    ]

    checked = set()
    for alt_ext in alt_suffixes:
        alt_path = base + alt_ext
        if alt_path in checked:
            continue
        checked.add(alt_path)

        if os.path.exists(alt_path):
            st.image(alt_path, caption=caption, use_container_width=True)
            return

    st.info(f"📷 图片正在云端同步中：`{img_path}`")


# ==================== 4. 页面状态 ====================
def init_session_state():
    """集中初始化所有页面状态。"""
    defaults = {
        "selected_dish": None,
        "selected_diary": None,
        "selected_daily": None,
        "diary_unlocked": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ==================== 5. 数据 ====================
DISH_DATA = {
    "dish5": {
        "category": "中餐",
        "title": "🥇 蒜蓉大虾炒时蔬",
        "image": "my_dish5.jpg",
        "desc": "大虾鲜甜弹牙，油菜吸收了虾汁和蒜蓉的香气，翠绿爽口。",
        "detail": "### 👨‍🍳 主厨秘籍与步骤\n1. **食材准备**：新鲜对虾去虾线，青口油菜洗净切段。\n2. **爆香大蒜**：热锅冷油，下入大量蒜蓉，慢火 sauté 至金黄色流油。\n3. **大虾下锅**：转大火，下入大虾翻炒至变红变弯曲，逼出鲜美虾油。\n4. **合体出锅**：最后加入油菜，快速翻炒 30 秒，撒入少许食盐即可出锅。保持油菜的翠绿与爽脆！",
    },
    "dish3": {
        "category": "中餐",
        "title": "🥈 丰盛中式能量套餐",
        "image": "my_dish3.jpg",
        "desc": "有荤有素，辣椒炒肉超级下饭，炸时蔬香脆可口。",
        "detail": "### 🍚 套餐配置详解\n* **主食**：肉松沙拉面包，外皮松软，肉松分量扎实。\n* **主菜**：经典辣椒炒肉，精选五花肉大火爆炒，辣味过瘾，极为下饭。\n* **副菜**：香炸椒盐时蔬，裹上薄浆炸至金黄，外酥里嫩。\n* **甜品与汤**：暖胃红豆沙搭配清汤丸子，一冷一热，解腻舒心。",
    },
    "dish2": {
        "category": "西餐",
        "title": "🥇 50% 伊比利亚火腿（现切片）",
        "image": "my_dish2.jpg",
        "desc": "脂肪如雪花般均匀分布，入口温润，带着淡淡的橡果香气与细腻的咸鲜。",
        "detail": "### 🍷 品鉴与搭配建议\n* **切片艺术**：火腿切片需保持极薄，用指尖温度使其油脂微微融化时，口感最佳。\n* **佐餐搭配**：强烈推荐搭配陈年红葡萄酒（如 Rioja）或桃红香槟。\n* **美味吃法**：尝试搭配成熟度高的哈密瓜，咸甜交织，是经典的西班牙吃法。",
    },
    "dish4": {
        "category": "西餐",
        "title": "🥈 Legado Ibérico 火腿（24个月）",
        "image": "my_dish4.jpg",
        "desc": "50% 纯种伊比利亚黑猪，咸度适中，油脂丰盈。",
        "detail": "### 🛒 购买与保存指南\n* **品牌故事**：Legado Ibérico 是西班牙家喻户晓的优质火腿品牌，控温窖藏 24 个月以上。\n* **开袋指南**：从冰箱取出后，切勿直接食用。建议室温静置 20 分钟，让火腿油脂苏醒。\n* **储存方法**：开封后用保鲜膜封口，放入冰箱冷藏，并在 3 天内食用完毕以保持最佳风味。",
    },
    "dish1": {
        "category": "日本料理",
        "title": "🥇 什锦大虾天妇罗",
        "image": "my_dish1.jpg",
        "desc": "面衣金黄轻薄、酥脆无比，大虾保留了饱满的汁水，外酥里嫩。",
        "detail": "### 🍤 酥脆面衣的秘密\n1. **面糊秘诀**：使用冰水调和低筋面粉，千万不能过度搅拌，保留小面疙瘩才是酥脆的关键。\n2. **油温控制**：油温必须保持在 170°C - 180°C。滴入面糊能立刻浮起并发出沙沙声。\n3. **黄金蘸汁**：出汁、酱油、味醂按 4:1:1 调制，加入白萝卜泥，清爽解腻。",
    },
}


DIARY_POSTS = {
    "road": {
        "title": "《路》—— 顺河高架与三克的温度",
        "date": "2026-09-05",
        "excerpt": "凌晨三点的济南，顺河高架上很空。没有一辆车在等。但我知道，什么都会发生。",
        "content": """一套欧舒丹三支装手霜礼盒的重量，九十克。
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
我没有催她。
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
But this time.
I know, everything will happen.""",
    }
}


DAILY_STORIES = {
    "sams": {
        "title": "《山姆的日光灯与冻肉之美》",
        "date": "2026-09-05",
        "excerpt": "176块1毛6的加拿大牛腱子，裹在坚硬的塑料膜里，呈现出一种近乎死寂的暗红色。在这里，生命被切割、冷冻、明码标价。",
        "images": [
            "daily_sams_cart.jpg",
            "daily_sams_shank.jpg",
            "daily_frozen_beef.jpg",
            "daily_lunch.jpg",
        ],
        "content": """白炽日光灯像冰冷的刀子，无情地剖开山姆会员店巨大的、挑高的、充斥着冷气的空间。
我推着笨重的购物车，不锈钢车轮在干净得有些虚无的地面上发出轻微、神经质的摩擦声。

176块1毛6的加拿大牛腱子，裹在紧绷、反光的塑料收缩膜里，呈现出一种近乎死寂的暗红色。
旁边是布满人工白霜的雪花肥牛，那脂肪的花纹在低温中冷酷而精确。
在这里，往昔狂奔的生命被切割、冷冻、明码标价。

我冷漠地往铁网车里扔了一箱无糖希腊酸奶和一颗巨大的、布满斑纹的西瓜。它们沉重地坠落，像墓碑和炮弹一样压弯了不锈钢铁网。

回到银行，正午。
食堂白瓷盘里那个木讷的南瓜、缠绕多汁的粉丝，以及泛着温热油光的肉丸，在复核姐姐细微、沉闷的啜泣声中，被我一口口机械地咽下喉咙。
我的心跳依旧是一分钟六十几下，稳定、迟闷得像一架没有灵魂的工业测谎仪。
混乱的深夜早已远去，我只是用哑铃、冰冷的重铁和这大块的生牛肉，将它们生生压进废墟的底层，筑起一道理性的高墙。""",
    },
    "kitchen": {
        "title": "《黄油、烈火与虎皮青椒的余温》",
        "date": "2026-09-05",
        "excerpt": "粗砺的青椒在铸铁锅的干烧下绽开焦黑的斑点，像垂死挣扎时留下的虎皮斑纹。这就是食物的解剖。",
        "images": [
            "daily_butter_prawns.jpg",
            "daily_prep_board.jpg",
            "daily_tofu_beef_pot.jpg",
            "daily_beef_wok.jpg",
            "daily_boiled_beef.jpg",
            "daily_stewed_beef.jpg",
        ],
        "content": """案板上，苍白、坚硬的北豆腐被利刃切成绝对完美的几何方块。
旁边，粗砺的青椒在铸铁锅烈火的干烧下急剧收缩，绽开焦黑、碳化的斑点，像野兽垂死挣扎时留下的虎皮斑纹。

在我眼里，烹饪不是艺术，而是一场对自然生命精密的解剖。

金黄色的黄油在高温的煎锅中发出滋滋的、绝望的哀鸣，随即化为一摊滚烫的油脂，将那些罗氏大虾那艳丽、坚硬的红壳无情地吞噬。
铁锅里大火翻炒，热油的甜香混杂着大蒜被拍碎后释放的辛辣，在一瞬间将狭窄的厨房填满。
这些曾经在水底游动的生灵，在我的铁锅里完成了它们最后一次壮烈、香气四溢的合唱。

当红亮的虾肉、冒着滚烫气泡的牛肉豆腐煲以及泼满芝麻的水煮牛肉端上木桌时，我独自坐在阴影里，看着浓白的热气在空气中徐徐上升，又在数秒内迅速、寂静地消散。

食物不过是维持肉体运动的卡路里。
而在每一个无人的深夜，我正是用这些精妙、算计好的热量，维持着我与这个荒诞世界最虚妄的连接。""",
    },
}


# ==================== 6. 通用显示函数 ====================
def render_comments(item_id, empty_text="暂无评论，快来抢沙发吧！🛋️"):
    """统一显示评论，避免把用户输入直接插入 HTML。"""
    comments_list = get_comments(item_id)

    if not comments_list:
        st.caption(empty_text)
        return

    for username, content, created_at in comments_list:
        with st.container(border=True):
            top_left, top_right = st.columns([3, 1])
            with top_left:
                st.markdown(f"**👤 {html.escape(username)}**")
            with top_right:
                st.caption(f"🕒 {created_at}")
            st.write(content)


def render_comment_form(item_id, button_label="提交评价 🚀", name_placeholder="例如：好吃爱吃", comment_placeholder="写下你的真实食评吧..."):
    """统一处理评论表单。"""
    with st.form(key=f"form_{item_id}", clear_on_submit=True):
        user_name = st.text_input("昵称：", placeholder=name_placeholder)
        user_comment = st.text_area("留言：", placeholder=comment_placeholder)

        if st.form_submit_button(button_label):
            user_name = user_name.strip()
            user_comment = user_comment.strip()

            if not user_name or not user_comment:
                st.warning("⚠️ 昵称和内容都不能为空哦！")
                return

            add_comment(item_id, user_name, user_comment)
            st.success("🎉 发表成功！")
            st.rerun()


def render_dish_card(dish_id):
    """统一生成一张菜品卡片。"""
    data = DISH_DATA[dish_id]
    col_img, col_txt = st.columns([1, 2])

    with col_img:
        safe_image(data["image"])

    with col_txt:
        st.markdown(f"### {data['title']}")
        st.write(data["desc"])

        btn_detail, btn_like = st.columns(2)

        with btn_detail:
            if st.button("查看详情 📖", key=f"view_{dish_id}", use_container_width=True):
                st.session_state.selected_dish = dish_id
                st.rerun()

        with btn_like:
            like_count = get_like_count(dish_id)
            if st.button(f"点赞 👍 ({like_count})", key=f"like_{dish_id}", use_container_width=True):
                add_like(dish_id)
                st.rerun()


def render_dish_detail(dish_id):
    """显示菜品详情页。"""
    data = DISH_DATA[dish_id]

    if st.button("⬅️ 返回主页", key="back_to_main"):
        st.session_state.selected_dish = None
        st.rerun()

    st.divider()
    col_img, col_txt = st.columns([1, 1.2])

    with col_img:
        safe_image(data["image"])

    with col_txt:
        st.title(data["title"])
        st.caption(data["desc"])
        st.markdown(data["detail"])

    st.divider()
    st.subheader(f"💬 {data['title']} 的食客留言板")
    render_comment_form(dish_id)
    render_comments(dish_id)


# ==================== 7. 页面样式 ====================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FAF8F6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================== 8. 点击漂浮粒子 ====================
components.html(
    """
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
    """,
    height=0,
)


# ==================== 9. 导航 ====================
menu = st.sidebar.radio(
    "🧭 导航菜单",
    ["🍔 经典美食评测", "📓 个人私密日记", "🛒 Wallace 的日常生活"],
)


# ==================== 页面一：经典美食评测 ====================
if menu == "🍔 经典美食评测":
    if st.session_state.selected_dish is not None:
        render_dish_detail(st.session_state.selected_dish)
    else:
        st.title("🍔 经典美食评测")
        st.markdown("这里记录了我品尝和制作的各种经典美食。点击“查看详情”了解更多。")

        tab1, tab2, tab3 = st.tabs(["中餐 🇨🇳", "西餐 🥩", "日本料理 🍣"])

        with tab1:
            st.subheader("🍜 家常美味与中式套餐")
            render_dish_card("dish5")
            st.divider()
            render_dish_card("dish3")

        with tab2:
            st.subheader("🥩 西班牙火腿专题")
            render_dish_card("dish2")
            st.divider()
            render_dish_card("dish4")

        with tab3:
            st.subheader("🍣 精致日料体验")
            render_dish_card("dish1")


# ==================== 页面二：个人私密日记 ====================
elif menu == "📓 个人私密日记":
    if not st.session_state.diary_unlocked:
        st.title("🔒 访问受限")
        st.markdown("这里是 Wallace 的私人空间，需要输入密码才能查阅。")

        # 🚀 兼顾安全与便利：优先读取云端加密 Secrets，本地未配置时，自动使用默认密码 wallace1996 登录，无需繁琐配置！
        try:
            diary_password = st.secrets.get("diary_password", "wallace1996")
        except Exception:
            diary_password = "wallace1996"

        pwd_input = st.text_input(
            "请输入访问密码：",
            type="password",
            placeholder="请输入密码...",
        )

        if st.button("解锁空间 🔑", use_container_width=True):
            if pwd_input == diary_password:
                st.session_state.diary_unlocked = True
                st.success("🎉 密码正确，正在进入空间...")
                st.rerun()
            else:
                st.error("❌ 密码错误，请重新输入！")

    else:
        if st.session_state.selected_diary is not None:
            post_id = st.session_state.selected_diary
            post = DIARY_POSTS[post_id]

            if st.button("⬅️ 返回日记列表", key="back_to_diary"):
                st.session_state.selected_diary = None
                st.rerun()

            st.divider()
            st.title(post["title"])
            st.caption(f"🕒 发表于 {post['date']} | 独立创作")

            st.markdown(
                f"""
                <div style="font-family: 'Georgia', serif; font-size: 1.15em; line-height: 2; color: #2c3e50; padding: 25px; background-color: #fff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); max-width: 800px; margin: 0 auto; white-space: pre-wrap;">{html.escape(post['content'])}</div>
                """,
                unsafe_allow_html=True,
            )

            st.write("---")
            st.subheader("💬 读后感与私密回应")
            render_comment_form(
                f"diary_{post_id}",
                button_label="发送 📮",
                name_placeholder="留下一个代号...",
                comment_placeholder="说你想说的话...",
            )
            render_comments(f"diary_{post_id}", "暂无回应，写下第一句吧。🌙")

        else:
            st.title("📓 Wallace 的个人私密日记")
            st.markdown("一些在寂静深夜、高架桥上，或银行复核机器轰鸣声中的个人随笔。")

            for post_id, post in DIARY_POSTS.items():
                st.markdown(
                    f"""
                    <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 6px solid #2c3e50; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px;">
                        <h3 style="margin-top:0px; color: #2c3e50;">{html.escape(post['title'])}</h3>
                        <span style="color: #888; font-size: 0.9em;">🕒 {html.escape(post['date'])}</span>
                        <p style="color: #555; margin-top: 15px; font-style: italic; font-family: 'Georgia', serif;">“{html.escape(post['excerpt'])}”</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "点击阅读完整篇章 📖",
                    key=f"read_{post_id}",
                    use_container_width=True,
                ):
                    st.session_state.selected_diary = post_id
                    st.rerun()


# ==================== 页面三：Wallace 的日常生活 ====================
elif menu == "🛒 Wallace 的日常生活":
    if st.session_state.selected_daily is not None:
        story_id = st.session_state.selected_daily
        story = DAILY_STORIES[story_id]

        if st.button("⬅️ 返回日常生活", key="back_to_daily_list"):
            st.session_state.selected_daily = None
            st.rerun()

        st.divider()
        st.title(story["title"])
        st.caption(f"🕒 记录时间：{story['date']} | 摄影与撰文：Wallace")

        st.markdown(
            f"""
            <div style="font-family: 'Kaiti', 'STKaiti', serif; font-size: 1.2em; line-height: 2.1; color: #1a1a1a; padding: 25px; background-color: #FDFCF7; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); max-width: 850px; margin: 0 auto; border-left: 4px solid #8e8e8e; white-space: pre-wrap;">{html.escape(story['content'])}</div>
            """,
            unsafe_allow_html=True,
        )

        st.write("---")
        st.subheader("📷 故事背后的真实快照")

        for i in range(0, len(story["images"]), 2):
            cols = st.columns(2)
            with cols[0]:
                safe_image(story["images"][i])
            if i + 1 < len(story["images"]):
                with cols[1]:
                    safe_image(story["images"][i + 1])

        st.write("---")
        st.subheader("💬 朋友的碎碎念")
        render_comment_form(
            f"daily_{story_id}",
            button_label="提交留言 📪",
            name_placeholder="过客...",
            comment_placeholder="留下你的脚印...",
        )
        render_comments(f"daily_{story_id}", "还没有留言，留下第一个脚印吧。👣")

    else:
        st.title("🛒 Wallace 的日常生活分享")
        st.markdown("将枯燥、麻木、冷硬的日常生活，用锋利的文字与真实的快照进行解剖。")

        for story_id, story in DAILY_STORIES.items():
            st.markdown(
                f"""
                <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 6px solid #8e8e8e; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px;">
                    <h3 style="margin-top:0px; color: #333;">{html.escape(story['title'])}</h3>
                    <span style="color: #888; font-size: 0.9em;">🕒 {html.escape(story['date'])}</span>
                    <p style="color: #666; margin-top: 15px; font-style: italic; font-family: 'Georgia', serif;">“{html.escape(story['excerpt'])}”</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "阅读此篇日常与看照片 📖",
                key=f"read_daily_{story_id}",
                use_container_width=True,
            ):
                st.session_state.selected_daily = story_id
                st.rerun()


# ==================== 10. 侧边栏辅助功能 ====================
if st.session_state.diary_unlocked:
    st.sidebar.write("---")
    st.sidebar.subheader("🔒 隐私保护")
    if st.sidebar.button("锁定日记空间", use_container_width=True):
        st.session_state.diary_unlocked = False
        st.session_state.selected_diary = None
        st.rerun()


# ==================== 11. 全局背景音乐播放器（主页面最下方，解决手机端隐藏与电脑端音量调节问题） ====================
# 这里已经完美将电台放回主页面底部，彻底解决了手机端折叠和电脑端音量条丢失的终极体验问题！
st.write("---")
st.markdown("#### 🎵 顺河高架电台")
st.write("点击下方播放按钮，一边听着温暖的 Lo-Fi 音乐，一边开启阅读之旅吧：")

components.html(
    """
    <iframe src="//player.bilibili.com/player.html?bvid=BV1Aa411C7EJ&page=1&high_quality=1"
            scrolling="no"
            border="0"
            frameborder="no"
            framespacing="0"
            allowfullscreen="true"
            width="100%"
            height="320">
    </iframe>
    """,
    height=340,
)
--- END OF FILE app_v2.py ---
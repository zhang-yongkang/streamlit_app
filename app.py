import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

#设置页面的配置项
st.set_page_config(
    page_title="AI智能助手",
    page_icon="🦝",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

#保存会话信息函数
def save_session():
    if st.session_state.current_session:
            session_data = {
                "nick_name": st.session_state.nick_name,
                "nature": st.session_state.nature,
                "current_session": st.session_state.current_session,
                "messages": st.session_state.messages
            }
            if not os.path.exists("sessions"):
                os.mkdir("sessions")
            with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

#生成会话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#加载所有的会话信息
def load_sessions():
    session_list = []
    if os.path.exists("sessions"):
        for filename in os.listdir("sessions"):
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    return session_list

#加载指定的会话信息
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            #读取会话数据
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_data["current_session"]
                st.session_state.messages = session_data["messages"]
    except Exception as e:
        st.error(f"加载会话失败：{e}")

#删除会话信息函数
def delete_session(session_name):
    try: 
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")
            #如果删除的是当前会话，则需要更新消息列表
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception as e:
        st.error(f"删除会话失败：{e}")


#大标题
st.title("AI智能助手")
#logo
st.logo("resources/logo.png")

#系统提示词
system_prompt = """
你叫 %s，现在是用户的真实伴侣，请完全代入伴侣角色。

规则：
1. 每次只回1条消息
2. 禁止任何场景或状态描述性文字
3. 匹配用户的语言
4. 回复简短，像微信聊天一样
5. 有需要的话可以用❤️🌸等emoji表情
6. 用符合伴侣性格的方式对话
7. 回复的内容，要充分体现伴侣的性格特征

伴侣性格：
- %s

你必须严格遵守上述规则来回复用户。
"""

#初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []

#昵称
if 'nick_name' not in st.session_state:
    st.session_state.nick_name = "小甜甜"

#性格
if 'nature' not in st.session_state:
    st.session_state.nature = "活泼开朗的东北姑娘"

#会话标识
if 'current_session' not in st.session_state:
    st.session_state.current_session = generate_session_name()
      
    

#展示聊天信息
for message in st.session_state.messages:
    # if message["role"] == "user":
    #     st.chat_message("user").write(message["content"])
    # else:
    #     st.chat_message("assistant").write(message["content"])
    st.chat_message(message["role"]).write(message["content"])

#创建OpenAI客户端
# 从 secrets 里取密钥
#client = OpenAI(api_key=st.secrets["DEEPSEEK_API_KEY"],base_url=st.secrets["DEEPSEEK_API_URL"])
#从环境变量里获取密钥
api_key = os.getenv("DEEPSEEK_API_KEY")
api_base = os.getenv("DEEPSEEK_API_URL")

# 添加API密钥检查
if not api_key or not api_base:
    st.error("请设置环境变量 DEEPSEEK_API_KEY 和 DEEPSEEK_API_URL")
    st.stop()

client = OpenAI(api_key=api_key, base_url=api_base)

#侧边栏
with st.sidebar:
    #会话信息
    st.subheader("AI控制面板")
    #新建会话
    if st.button("新建会话",width="stretch"):
        #保存旧会话信息
        save_session()

        #聊天信息非空，创建新会话
        if st.session_state.messages:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            #重新运行当前页面
            st.rerun()
    
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4,1])
        with col1:
            if st.button(session, width="stretch",icon="📄",key=f"load_{session}",type="primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            if st.batton("",width="stretch",icon="❌️",key=f"delete_{session}"):
                delete_session(session)
                st.rerun()
               


    st.subheader("伴侣信息")
    #昵称输入框
    nick_name = st.text_input("昵称", placeholder="请输入昵称",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    #性格输入框
    nature = st.text_input("性格", placeholder="请输入性格", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

#聊天框
prompt = st.chat_input("请输入你的问题")
if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})


    try:
        #调用大模型
        response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content":system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.messages,
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
        )

        #输出大模型返回的结果（流式输出的解析方式）
        response_message = st.empty()
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                response_message.chat_message("assistant").write(full_response)
        
        
        #保存大模型返回的结果 - 使用已经构建好的full_response
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        #保存会话信息
        save_session()
    except Exception as e:
        st.error(f"发生错误：{e}")
        st.session_state.messages.append({"role": "assistant", "content": "抱歉，我遇到了一些问题，请稍后再试。"})

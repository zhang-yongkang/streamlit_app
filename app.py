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
st.text(f"会话名称：{st.session_state.current_session}")
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
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),base_url=os.getenv("DEEPSEEK_API_URL"))

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

    #输出大模型返回的结果（非流式输出的解析方式）
    # st.chat_message("assistant").write(response.choices[0].message.content)
    
    #输出大模型返回的结果（流式输出的解析方式）
    response_message = st.empty()
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)
    
    
    #保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})

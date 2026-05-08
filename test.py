import streamlit as st
import os
from openai import OpenAI

#设置页面的配置项
st.set_page_config(
    page_title="AI智能助手",
    page_icon="🦝",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

#大标题
st.title("AI智能助手")
#logo
st.logo("resources/banner.png")

#系统提示词
system_prompt = "You are a helpful assistant"

#初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []

#展示聊天信息
for message in st.session_state.messages:
    # if message["role"] == "user":
    #     st.chat_message("user").write(message["content"])
    # else:
    #     st.chat_message("assistant").write(message["content"])
    st.chat_message(message["role"]).write(message["content"])


# 从 secrets 里取密钥
#client = OpenAI(api_key=st.secrets["DEEPSEEK_API_KEY"],base_url=st.secrets["DEEPSEEK_API_URL"])
#从环境变量里获取密钥
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),base_url=os.getenv("DEEPSEEK_API_URL"))

#聊天框
prompt = st.chat_input("请输入你的问题")
if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.message.append({"role": "user", "content": prompt})


    #调用大模型
    response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content":system_prompt},
        *st.session_state.messages,
    ],
    stream=False,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}}
    )

    st.chat_message("assistant").write(response.choices[0].message.content)
    #保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})

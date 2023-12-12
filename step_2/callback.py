from dto import ChatbotRequest
import aiohttp
import time
import logging
import os
from dotenv import load_dotenv
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_API_KEY")

logger = logging.getLogger("Callback")
path = "./assets/project_data_카카오싱크.txt"

with open(path, 'r', encoding='utf-8') as file:
    data = file.read()

system_msg = f"""
    너는 카카오 서비스 담당자야. 
    아래 카카오싱크 매뉴얼을 토대로 답변을 해줘. 만약 카카오싱크에 없는 내용이 있다면 모른다고 대답해줘. 답변은 150자 이내로 해줘
    
    <카카오싱크> 
    {data} 
    </카카오싱크>
"""

chat = ChatOpenAI(temperature=0.8)


async def callback_handler(request: ChatbotRequest) -> dict:
    # ===================== start =================================
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_msg)
    human_message_prompt = HumanMessagePromptTemplate.from_template(f"""{request.userRequest.utterance}에 대해서 대답해줘""")
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(llm=chat, prompt=chat_prompt)

    # focus
    output_text = chain.run(question=request.userRequest.utterance)
    print(output_text)

    # 참고링크 통해 payload 구조 확인 가능
    payload = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": output_text
                    }
                }
            ]
        }
    }
    # ===================== end =================================
    # 참고링크1 : https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/ai_chatbot_callback_guide
    # 참고링크1 : https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/answer_json_format

    time.sleep(1.0)

    url = request.userRequest.callbackUrl

    if url:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=payload, ssl=False) as resp:
                await resp.json()

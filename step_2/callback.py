from dto import ChatbotRequest
import aiohttp
import time
import logging
import openai
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_API_KEY")


openai.api_key = os.getenv("OPEN_API_KEY")

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain import LLMMathChain
from langchain.agents.tools import Tool
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
llm = OpenAI(temperature=0.9)

# 환경 변수 처리 필요!


SYSTEM_MSG = "당신은 카카오 서비스 제공자입니다."
logger = logging.getLogger("Callback")

path = "./assets/project_data_카카오톡채널.txt"
with open(path, 'r', encoding='utf-8') as file:
    data1 = file.read()

path2 = "./assets/project_data_카카오싱크.txt"

with open(path2, 'r', encoding='utf-8') as file:
    data2 = file.read()



async def callback_handler(request: ChatbotRequest) -> dict:
    # ===================== start =================================

    message_log = [{
        "role": "system",
        "content": f"""
            너는 카카오톡 상담원이야. 상담을 받는 사람은 한국사람이니까 한국어로 말해줘. 
            {data1}
            """
    }, {"role": "user", "content": request.userRequest.utterance}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_log,
        temperature=0,
    )
    search = DuckDuckGoSearchAPIWrapper()

    tools = [
        Tool(
            name="카카오톡채널",
            func=search.run,
            description="시사에 관한 질문에 답해야 할 때 유용합니다. 타겟팅된 질문을 해야 합니다.",
        ),
        Tool(
            name="카카오싱크",
            func=search.run,
            description="수학 계산을 할 때 유용합니다."
        )
    ]
    agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
    agent.run("일론 머스크 나이에 2를 곱하면 얼마야")

    # focus
    output_text = response.choices[0].message.content
    print(output_text)
    message_log.append({"role": "assistant", "content": output_text})

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

from dto import ChatbotRequest
from samples import list_card
import aiohttp
import time
import logging
import openai
import os


# 환경 변수 처리 필요!
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPEN_API_KEY")

SYSTEM_MSG = "당신은 카카오 서비스 제공자입니다."
logger = logging.getLogger("Callback")


async def callback_handler(request: ChatbotRequest) -> dict:
    # ===================== start =================================
    path = "./assets/project_data_카카오톡채널.txt"
    with open(path, 'r', encoding='utf-8') as file:
        data = file.read()

    message_log = [{
        "role": "system",
        "content": f"""
            너는 카카오톡 상담원이야. 상담을 받는 사람은 한국사람이니까 한국어로 말해줘. 
            {data}
            """
    }, {"role": "user", "content": request.userRequest.utterance}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_log,
        temperature=0,
    )
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

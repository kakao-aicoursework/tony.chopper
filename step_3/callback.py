from dto import ChatbotRequest
import aiohttp
import time
import logging
import os
from dotenv import load_dotenv
from langchain.chains import ConversationChain, LLMChain, LLMRouterChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_API_KEY")

logger = logging.getLogger("Callback")


syncPath = "./assets/project_data_카카오싱크.txt"
socialPath = "./assets/project_data_카카오소셜.txt"
channelPath = "./assets/project_data_카카오톡채널.txt"

intentPath = "./prompt/intent.txt"

def getFileData(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()


llm = ChatOpenAI(temperature=0.8)

sync_chain = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        template=getFileData(syncPath)
    ),
    output_key="sync"
)
social_chain = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        template=getFileData(socialPath)
    ),
    output_key="social"
)
channel_chain = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        template=getFileData(channelPath)
    ),
    output_key="channel"
)

intent_chain = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        template=getFileData(intentPath)
    ),
    output_key="intent"
)

chains = ConversationChain(llm=llm, output_key="text")



async def callback_handler(request: ChatbotRequest) -> dict:
    # ===================== start =================================
    context = dict(user_message=request.userRequest.utterance)
    context["input"] = context["user_message"]

    output_text = intent_chain.run(context)
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

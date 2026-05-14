from typing_extensions import TypedDict, Annotated

import operator
import os

from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langchain_upstage import ChatUpstage  # Upstage

from dotenv import load_dotenv
load_dotenv()


# OpenAI API는 아래 주석을 풀고 쓰세요.
model = init_chat_model("gpt-5-nano", temperature=0)

# Upstage API는 아래 주석을 풀고 쓰세요.
# model = ChatUpstage(model="solar-pro", upstage_api_key=os.getenv("UPSTAGE_API_KEY"), temperature=0)


# 랭그래프에서 State는 전역변수처럼 모든 Node들이 데이터를 저장할 수 있는 공간입니다.
class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


def BBQ(state: State):
    return {"messages": [model.invoke(state["messages"])]}


graph = StateGraph(State)
graph.add_node("BBQ", BBQ)
graph.add_edge(START, "BBQ")
graph.add_edge("BBQ", END)

agent = graph.compile()


result = agent.invoke({
    "messages": [HumanMessage(content="KFC랑 맥도날드 치킨 중 뭐가 더 맛있지? 한줄 요약")]
})

for m in result["messages"]:
    m.pretty_print()
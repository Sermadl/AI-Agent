import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from prompts.trend_prediction_prompt import prompt
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import re

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o", 
    temperature=0.2
    )

response_schemas = [
    ResponseSchema(name="keyword", description="기술에 대한 미래 트렌드 키워드(5개, 리스트 형태)"),
    ResponseSchema(name="summary", description="각 기술 트렌드 요약(5개, 리스트 형태)"),
    ResponseSchema(name="reason", description="해당 트렌드가 왜 중요해질지에 대한 근거(5개, 리스트 형태)"),
    ResponseSchema(name="confidence", description="신뢰도(0~100, 5개, 리스트 형태)")
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

chain = prompt | llm | output_parser

# --- 1. 상태 정의 ---
class AgentState(TypedDict):
    trend_result: dict
    trend_predict: dict
    retry_count: int

# --- 2. 노드: 트렌드 생성 ---
def trend_prediction(state: AgentState) -> AgentState:
    print("3. 미래 기술 트렌드를 예측하는 중입니다...\n")
    print("재시도 횟수: ", state.get("retry_count", 0))

    trend_result = state["trend_result"]

    response = chain.invoke({
        "format_instructions": format_instructions,
        "trend": state["trend_result"]
    })

    print("\n기술 트렌드 예측 완료!\n")

    return {
        "trend_result": trend_result,
        "trend_predict": response,
        "retry_count": state.get("retry_count", 0)
    }

# --- 3. 노드: 신뢰도 검사 ---
def check_reliability(state: AgentState) -> dict:
    result = state["trend_predict"]
    
    # 신뢰도 점수 추출
    scores = [int(item) for item in result['confidence']]
    low_scores = [s for s in scores if s <= 79]
    
    if len(low_scores) >= 3 and state["retry_count"] < 2:
        print("신뢰도 검사 통과 못함\n")
        return {**state, "next": "retry", "retry_count": state["retry_count"] + 1}
    else:
        print("신뢰도 검사 통과\n")
        return {**state, "next": "done"}
    
# --- 3-1. 신뢰도 검사: 재시도 경로 ---
def reliability_route(output: dict) -> str:
    return output["next"]


# --- 4. 그래프 구성 ---
graph = StateGraph(AgentState)

STEP1 = "trend_prediction"
STEP2 = "check_reliability"

graph.add_node(STEP1, trend_prediction)
graph.add_node(STEP2, check_reliability)

graph.add_edge(START, STEP1)

graph.add_edge(STEP1, STEP2)
graph.add_conditional_edges(STEP2, reliability_route, {
    "retry": STEP1,
    "done": END
})

prediction = graph.compile()


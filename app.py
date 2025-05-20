from langgraph.graph import StateGraph, START, END
from typing import Annotated, TypedDict
from agents.collect_info import search_patents_by_keyword
from agents.trend_summary import summarize_trend
from agents.trend_prediction import prediction, STEP1, STEP2
from agents.report_generator import generate_report
from langchain_core.runnables.graph_mermaid import draw_mermaid_png

# 초기 상태 스키마 정의
class State(TypedDict):
    keyword: Annotated[str, "검색할 키워드"]
    patents: Annotated[list, "특허 정보"]
    scholarly: Annotated[list, "학술 정보"]
    tavily: Annotated[list, "뉴스 정보"]
    trend_summary: Annotated[dict, "트렌드 요약"]
    trend_prediction: Annotated[dict, "트렌드 예측"]
    retry_count: Annotated[int, "재시도 횟수"]
    done: Annotated[bool, "예측 완료 여부"]

# 1. 정보 수집 노드
def collect_info(state: State) -> State:
    keyword = state["keyword"]
    patents, scholarly, tavily = search_patents_by_keyword(keyword)
    return State({
        **state,
        "patents": patents,
        "scholarly": scholarly,
        "tavily": tavily
    })

# 2. 트렌드 요약 노드
def summarize(state: State) -> State:
    summary = summarize_trend(state["scholarly"], state["patents"], state["tavily"])
    return State({
        **state,
        "trend_summary": summary
    })

# 3. 트렌드 예측 노드 (LangGraph 내부 반복 포함)
def predict(state: State) -> State:
    result = prediction.invoke({
        "trend_result": state["trend_summary"],
        "retry_count": state.get("retry_count", 0)
    })
    
    return State({
        **state,
        "trend_prediction": result["trend_predict"],
        "done": True
    })

# 4. 보고서 생성 노드
def report(state: State) -> State:
    generate_report(
        state["keyword"],
        state["trend_summary"],
        state["trend_prediction"]
    )
    return state

# mermaid 코드 생성 및 그래프 시각화
def save_graph(app):
    print("프로그램 시작 전 그래프를 시각화하는 중입니다...\n")

    NODE_LABELS = {
        AGENT1: "최신 연구/뉴스 수집",
        AGENT2: "현재 트렌드 요약",
        AGENT3: "미래 트렌드 예측",
        AGENT4: "보고서 생성",
        STEP1: "미래 트렌드 예측",
        STEP2: "신뢰도 검사",
        "retry": "재시도",
        "done": "예측 완료"
    }

    graph_obj = app.get_graph(xray=1)
    mermaid_code = graph_obj.draw_mermaid()

    for node_id, label in NODE_LABELS.items():
        mermaid_code = mermaid_code.replace(f"{node_id}({node_id})", f"{node_id}({label})")
    
    mermaid_code = mermaid_code.replace(f"subgraph predict", f"subgraph predict [{NODE_LABELS[AGENT3]}]")
    mermaid_code = mermaid_code.replace("&nbsp;done&nbsp;", "&nbsp;완료&nbsp;")
    mermaid_code = mermaid_code.replace("&nbsp;retry&nbsp;", "&nbsp;재시도&nbsp;")

    draw_mermaid_png(mermaid_code, max_retries=5, retry_delay=2.0, output_file_path="graph.png")

    print("그래프 시각화 완료!\n")
    print("그래프를 확인하세요: ./graph.png\n")    


# 그래프 생성
builder = StateGraph(State)

AGENT1 = "collect_info"
AGENT2 = "summarize"
AGENT3 = "predict"
AGENT4 = "report"

builder.add_node(AGENT1, collect_info)
builder.add_node(AGENT2, summarize)
builder.add_node(AGENT3, predict)
builder.add_node(AGENT4, report)

# 경로 연결
builder.add_edge(START, AGENT1)
builder.add_edge(AGENT1, AGENT2)
builder.add_edge(AGENT2, AGENT3)

# 예측 반복 조건부 흐름
def should_repeat(state: State):
    return AGENT3 if not state.get("done") else AGENT4

builder.add_conditional_edges(AGENT3, should_repeat)

builder.add_edge(AGENT3, AGENT4)
builder.add_edge(AGENT4, END)

# 그래프 실행
app = builder.compile()

if __name__ == "__main__":
    # 그래프 시각화
    save_graph(app)
    
    # 그래프 실행
    print("이 프로그램은 사용자가 입력한 키워드에 대한 정보를 바탕으로 기술 트렌드를 예측하고 보고서를 생성합니다.")
    keyword = input("검색할 키워드를 영어로 입력하세요: ")
    initial_state = State({"keyword": keyword})
    app.invoke(initial_state)

from agents.collect_info import search_patents_by_keyword
from agents.trend_summary import summarize_trend
from agents.trend_prediction import app
from agents.report_generator import generate_report

if __name__ == "__main__":
    # 사용자로부터 검색할 키워드를 입력받습니다.
    print("이 프로그램은 사용자가 입력한 키워드에 대한 논문, 특허, 뉴스 정보를 수집하여 해당 분야의 기술 트렌드를 예측합니다.")
    keyword = input('검색할 키워드를 영어로 입력하세요: ')

    # 키워드에 대한 정보를 수집합니다.
    print(f"1. '{keyword}'에 대한 정보를 수집하는 중입니다...\n")
    patents, scholarly, tavily = search_patents_by_keyword(keyword)
    print("정보 수집 완료!\n")

    # 수집된 정보를 요약하여 현재 기술 트렌드를 분석합니다.
    print("2. 수집된 정보를 바탕으로 기술 트렌드를 분석하는 중입니다...\n")
    trend_summary = summarize_trend(scholarly, patents, tavily)
    print(trend_summary)
    print("수집된 정보 요약 완료!\n")

    # 수집된 정보를 바탕으로 기술 트렌드를 예측합니다.
    print("3. 기술 트렌드를 예측하는 중입니다...\n")

    initial_state = {
        "trend_result": trend_summary,
        "retry_count": 0
    }

    trend_prediction = app.invoke(initial_state) # LangGraph를 통해 신뢰도 검사 및 재시도 로직을 처리합니다.
    trend_prediction = trend_prediction['trend_predict']
    print(trend_prediction)
    print("기술 트렌드 예측 완료!\n")

    # 보고서를 생성합니다.
    print("4. 보고서를 생성하는 중입니다...\n")
    generate_report(keyword, trend_summary, trend_prediction)


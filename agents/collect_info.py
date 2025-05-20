import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
from langchain_community.tools.tavily_search.tool import TavilySearchResults

import re
import os

load_dotenv()

scholar_url = "https://api.lens.org/scholarly/search"
patent_url = "https://api.lens.org/patent/search"

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LENS_API_KEY = os.getenv("LENS_API_KEY")

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + LENS_API_KEY  # 본인 API 키로 교체
}

end_date = datetime.today()
start_date = end_date - timedelta(days=30)
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

def search_patents_by_keyword(keyword):
    """
    키워드만 입력받아 최근 30일간 논문/특허를 검색하는 함수

    Parameters:
        keyword (str): 검색할 키워드

    Returns:
        dict: 검색 결과(JSON)
    """
    payload = {
        "query": {
            "bool": {
                "must": [
                    {
                        "query_string": {
                            "query": keyword,
                            "fields": ["title", "abstract", "claims", "description"],
                            "default_operator": "or"
                        }
                    },
                    {
                        "range": {
                            "date_published": {
                                "gte": start_date_str,
                                "lte": end_date_str
                            }
                        }
                    }
                ]
            }
        }
    }

    patents = requests.post(patent_url, headers=headers, data=json.dumps(payload))
    scholarly = requests.post(scholar_url, headers=headers, data=json.dumps(payload))

    if patents.status_code == 200 and scholarly.status_code == 200:
        patents = patents.json()
        scholarly = scholarly.json()
        
        patent_result = parse_patent_data(patents['data'])
        scholar_result = parse_scholar_data(scholarly['data'])
        tavily_result = search_tavily(keyword)

        return patent_result, scholar_result, tavily_result
    else:
        print("에러(patents):", patents.status_code, patents.text)
        print("에러(scholarly):", scholarly.status_code, scholarly.text)
        return None
    

def parse_patent_data(patent_data):
    # 특허 데이터에서 필요한 정보만 추출합니다.
    patent_result = []

    for data in patent_data:
        tmp = data['biblio']['invention_title']
        titles = [title['text'] for title in tmp if title.get('lang') == 'en']
        title_text = titles[0] if titles else None

        tmp = data.get('abstract', '')
        
        abstracts = [abstract['text'] for abstract in tmp if abstract.get('lang') == 'en']
        abstract_text = abstracts[0] if abstracts else None

        patent_result.append([title_text, abstract_text])

    return patent_result


def parse_scholar_data(scholar_data):
    # 학술 데이터에서 필요한 정보만 추출합니다.
    scholar_result = []

    for data in scholar_data:
        title = data['title']

        abstract = data.get('abstract', '')
        abstract = re.sub('<[^<]+?>', '', abstract).strip() if abstract else None

        scholar_result.append([title, abstract])
    
    return scholar_result

def search_tavily(keyword):
    # Tavily 검색 도구 인스턴스 생성
    tavily_tool = TavilySearchResults(max_results=10, search_depth="advanced", topic="news")

    # 검색 실행
    tavily_result = tavily_tool.invoke({"query": keyword + ' technic trend news' + start_date_str + '~' + end_date_str})

    return tavily_result
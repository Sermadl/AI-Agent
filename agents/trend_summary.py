import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from prompts.trend_summary_prompt import prompt

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o", 
    temperature=0.2
    )

response_schemas = [
    ResponseSchema(name="keyword", description="기술에 대한 트렌드 키워드(5개, 리스트 형태)"),
    ResponseSchema(name="summary", description="각 기술 트렌드 요약(5개, 리스트 형태)"),
    ResponseSchema(name="source", description="해당 트렌드가 언급된 논문, 특허, 뉴스(5개, 리스트 형태)")
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

chain = prompt | llm | output_parser

def summarize_trend(scholar_result, patent_result, tavily_result):
    print("2. 수집된 정보를 바탕으로 기술 트렌드를 분석하는 중입니다...\n")

    trend_summary = chain.invoke({
        "format_instructions": format_instructions,
        "scholarly": scholar_result,
        "patents": patent_result,
        "tavily": tavily_result
    })

    print(trend_summary)
    print("\n수집된 정보 요약 완료!\n")

    return trend_summary
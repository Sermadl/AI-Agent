from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template('''당신은 기술 트렌드 분석 전문가입니다.
아래 논문, 특허, 뉴스 정보를 참고해서  
아래 논문, 특허, 뉴스 정보를 참고해서  
“AI 산업에서 현재 주목받고 있는 기술 트렌드”의 **핵심 키워드**와  
각 키워드별로 “기술적 내용 중심”의 요약, 그리고 해당 트렌드와 관련된 **모든 주요 출처(논문, 특허, 뉴스의 제목 또는 URL)**를 함께 작성해 주세요.

※ 시장 동향, 비즈니스 모델, 투자, 기업 전략 등 “산업적 관점”이 아니라
“기술 자체의 발전, 원리, 구현 방식, 연구 동향”에 집중해서 답변해 주세요.

# 답변은 한글로 해주세요.

제시 정보 예시:
[{{'제목', 'abstract'}}, {{'제목', 'abstract'}}, ...]

{format_instructions}

[논문]
{scholarly}

[특허]
{patents}

[뉴스]
{tavily}
''')
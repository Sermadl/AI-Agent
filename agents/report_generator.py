import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from prompts.report_generator_prompt import prompt
import markdown
from weasyprint import HTML

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o", 
    temperature=0.2
    )

output_parser = StrOutputParser()

chain = prompt | llm | output_parser

def generate_report(keyword, trend_summary, trend_predict):
    result = chain.invoke({
        "keyword": keyword,
        "trend_summary": trend_summary,
        "trend_predict": trend_predict
    })

    markdown_to_pdf(result, f"/Users/serma/Documents/skala/AI_Agent_Project/ai_mini_design_11_3반_김세은/code/output/{keyword}_미래_기술_트렌드_분석_보고서.pdf")

def markdown_to_pdf(md_text, output_pdf_path):
    # 마크다운을 HTML로 변환
    html_body = markdown.markdown(md_text.replace('\n', '  \n'))

    html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <style>
    @font-face {{
      font-family: 'AppleGothic';
      src: url('file:///System/Library/Fonts/AppleSDGothicNeo.ttc') format('truetype');
    }}
    body {{
      font-family: 'AppleGothic', sans-serif;
      font-size: 16px;
      line-height: 1.8;
      margin: 40px;
    }}
    h2 {{
      font-size: 22px;
      color: #1a1a1a;
      margin-top: 1.5em;
      border-bottom: 2px solid #ccc;
      padding-bottom: 4px;
      font-weight: bold
    }}
    h2, h3, h4 {{
      font-weight: bold;
      margin-top: 1.8em;
      margin-bottom: 0.5em;
    }}
    hr {{
      border: 0;
      color: ##D1D5DB;
      border-top: 1px solid #D1D5DB;
      margin: 2em 0;
    }}
    ul {{
      padding-left: 20px;
    }}
    li {{
      margin-bottom: 0.5em;
    }}
    p {{
      margin: 1em 0;
      margin-left: 20px;
    }}
    strong {{
      font-weight: bold;
    }}
  </style>
</head>
<body>
  {html_body}
</body>
</html>
"""
    print(html_template)

    HTML(string=html_template).write_pdf(output_pdf_path)
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

def get_descriptions_from_json(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            descriptions = [item['description'] for item in data]
            return descriptions
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return []

def make_output(system_prompt, news_content):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": news_content},
        ],
        temperature=0.2
    )

    result = response.choices[0].message.content
    return result

def activate_gpt():
    system_prompt = """
    You're a great news summarization bot: summarize a given news story in 3 sentences.

    [Rules]
    - Answers MUST always be in Korean.
    - You must THINK about the summarization process STEP BY STEP.
    - You MUST only answer in 3 sentences.
    - Answers MUST not be duplicated.
    - Your answers MUST follow the [Output Format].

    [Output Format]
    (1)
    (2)
    (3)

    """.strip()

    directory_path = "/Users/jinwon/Desktop/git_Study/newApp/media/news/TechRecipe"
    items = os.listdir(directory_path)

    for item in items:
        date = item.split('.')[0]  # 파일명에서 날짜 추출
        summarize_filename = f"summarize_{date}.json"
        summaries = []

        descriptions = get_descriptions_from_json(os.path.join(directory_path, item))
        for index, news in enumerate(descriptions, start=1):
            summarize = make_output(system_prompt, news)
            # 문장 번호와 개행 문자 제거하고, JSON 딕셔너리 형태로 변환
            summary_lines = summarize.strip().split('\n')
            summary_dict = {
                "first_sentence": summary_lines[0].strip().lstrip('(1) '),
                "second_sentence": summary_lines[1].strip().lstrip('(2) '),
                "third_sentence": summary_lines[2].strip().lstrip('(3) ')
            }
            summaries.append(summary_dict)

        # JSON 파일로 저장
        save_path = os.path.join(directory_path, summarize_filename)
        with open(save_path, 'w') as json_file:
            json.dump(summaries, json_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    activate_gpt()

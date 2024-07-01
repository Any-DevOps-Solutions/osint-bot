import os
from googleapiclient.discovery import build
import openai
if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    from bot_lambda.config import OPENAI_API_KEY, YOUR_API_KEY as api_key, YOUR_SEARCH_ENGINE_ID as search_engine_id, DOMAINS as domains
else:
    from config import OPENAI_API_KEY, YOUR_API_KEY as api_key, YOUR_SEARCH_ENGINE_ID as search_engine_id, DOMAINS as domains

openai.api_key = OPENAI_API_KEY

def google_search(search_term, domain, api_key=api_key, search_engine_id=search_engine_id):
    service = build("customsearch", "v1", developerKey=api_key)
    result = service.cse().list(
        q=search_term,
        cx=search_engine_id,
        siteSearch=domain,
        siteSearchFilter="i",  # 'i' означает "включить" указанный домен
        num=10  # Увеличиваем количество результатов до 10
    ).execute()
    return result.get('items', [])

def check_snippet_with_openai(company, job_title, snippet, api_key=api_key):
    combined_prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Translate the following job title to Russian and English: '{job_title}'."},
        {"role": "assistant", "content": "Russian: '...'\nEnglish: '...'"},
        {"role": "user", "content": "Check if the following snippet mentions a job opening with the job title in any of the given languages (original, Russian, or English). Respond only with 'True' or 'False'.\n\nSnippet: ...\n"},
        {"role": "assistant", "content": "True"},
        {"role": "user", "content": "Check if the following snippet mentions a job opening with the job title in any of the given languages (original, Russian, or English). Respond only with 'True' or 'False'.\n\nSnippet: ...\n"},
        {"role": "assistant", "content": "False"},
        {"role": "user", "content": f"Check if the following snippet mentions a job opening for the company '{company}' with the job title '{job_title}' (original), the translated Russian job title, or the translated English job title. Respond only with 'True' or 'False'.\n\nSnippet: {snippet}\n"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=combined_prompt,
        max_tokens=200
    )
    
    result = response.choices[0].message["content"].strip()
    return result

def filter_urls_by_domain(results, domains=domains):
    filtered_results = []
    for result in results:
        url = result.get('link', '')
        for domain in domains:
            if domain in url:
                filtered_results.append(result)
                break
    return filtered_results

def fetch_and_filter_results(company, job_title, domains=domains):
    results_ru = google_search(f"{company} {job_title}", ".ru")
    results_by = google_search(f"{company} {job_title}", ".by")

    all_results = results_ru + results_by
    filtered_results = filter_urls_by_domain(all_results)
    
    return filtered_results

def process_results(filtered_results, company, job_title, domains=domains):
    response_text = ""
    for result in filtered_results:
        snippet = result.get('snippet', 'No snippet available')
        is_relevant = check_snippet_with_openai(company, job_title, snippet)
        if is_relevant.lower() == 'true':
            response_text += f"Title: {result['title']}\nLink: {result['link']}\nSnippet: {snippet}\n---\n"
    return response_text

def nice_process_results(filtered_results, company, job_title, domains=domains):
    relevant_results = [
        result for result in filtered_results
        if check_snippet_with_openai(company, job_title, result.get('snippet', 'No snippet available')).lower() == 'true'
    ]

    if not relevant_results:
        return (
            "🟢🟢🟢🟢🟢\nОзнак зв'язку зі країнами-ворогами не виявлено.\n\n"
            "Щоб покращити результат аналізу, вводьте назву компанії повністю, "
            "наприклад, не Pin-Up, а Pin-Up Global, а позицію одним словом, наприклад - оператор.\n"
            "Приклад: /check \"Pin-Up Global\",\"оператор\""
        )

    risk_level = min(len(relevant_results), 5)
    risk_indicators = "🔴" * risk_level + "🟢" * (5 - risk_level)
    
    if risk_level == 1:
        risk_comment = "Ця компанія ретельно приховує зв'язки або намагається піти з токсичної країни. Настійно не рекомендується зв'язуватися з нею без додаткової перевірки."
    elif risk_level == 2:
        risk_comment = "Ця компанія намагається приховати свою токсичність, але не дуже успішно. Уникайте цю компанію."
    elif risk_level == 3:
        risk_comment = "Ця компанія навіть не намагається приховати токсичність, дуже небезпечно, не зв'язуйтеся з нею будь-якою ціною."
    elif risk_level == 4:
        risk_comment = "Це токсичність компанія! Дуже небезпечно, обходьте стороною!"
    else:
        risk_comment = "Це стовідсотково токсична компанія, уникайте будь-якою ціною!"

    return f"{risk_indicators}\n{risk_comment}"

def osint_process_result(processed_results):
    if not processed_results.strip():
        return "No relevant results found."

    prompt = f"""
Проаналізуй дані. Виведь у (шаблону):

(Аналіз показує, що [компанія] активно шукає [посада] через публікації вакансій у [країнах].
Ось посилання з доказами їх діяльності по залученню співробітників:
[посилання у mardown style]
)

Ось дані до аналізу

{processed_results}


"""

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response['choices'][0]['message']['content']


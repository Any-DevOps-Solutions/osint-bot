import os
import argparse
from functions import load_domains, google_search, check_snippet_with_openai, filter_urls_by_domain

def main():
    parser = argparse.ArgumentParser(description='Google Search API script.')
    parser.add_argument('company', type=str, help='Company name to look up.')
    parser.add_argument('job_title', type=str, help='Job title to look up.')
    parser.add_argument('--domains_file', type=str, default='domains.txt', help='Path to the domains file.')
    args = parser.parse_args()

    api_key = os.environ.get('YOUR_API_KEY')
    search_engine_id = os.environ.get('YOUR_SEARCH_ENGINE_ID')

    if not api_key or not search_engine_id:
        print("Please set your API_KEY and SEARCH_ENGINE_ID as environment variables.")
        return

    domains = load_domains(args.domains_file)
    
    results_ru = google_search(f"{args.company} {args.job_title}", api_key, search_engine_id, ".ru")
    results_by = google_search(f"{args.company} {args.job_title}", api_key, search_engine_id, ".by")

    all_results = results_ru + results_by
    filtered_results = filter_urls_by_domain(all_results, domains)

    for result in filtered_results:
        snippet = result.get('snippet', 'No snippet available')
        is_relevant = check_snippet_with_openai(args.company, args.job_title, snippet)
        if is_relevant.lower() == 'true':
            print(f"Title: {result['title']}")
            print(f"Link: {result['link']}")
            print(f"Snippet: {snippet}")
            print("---")

if __name__ == '__main__':
    main()

import unittest
import os
from functions import process_results, load_domains, fetch_and_filter_results

class TestFunctions(unittest.TestCase):
    def setUp(self):
        # Загружаем домены из файла
        self.domains = load_domains('domains.txt')
        self.api_key = os.getenv('YOUR_API_KEY')  # API ключ из переменной окружения
        self.search_engine_id = os.getenv('YOUR_SEARCH_ENGINE_ID')  # Идентификатор поисковой системы из переменной окружения

    def test_process_results(self):
        # Используем fetch_and_filter_results для получения результатов
        results = fetch_and_filter_results('Globallogic', 'Java Developer', self.api_key, self.search_engine_id, self.domains)
        
        # Обрабатываем результаты
        processed_results = process_results(results, 'Java Developer', self.domains)
        
        # Проверяем, что все ссылки в результатах содержат один из доменов
        for result in processed_results:
            url = result.get('link', '')
            self.assertTrue(any(domain in url for domain in self.domains))
        
        # Выводим итоговый список ссылок, если он не пустой
        final_urls = [result.get('link', '') for result in processed_results]
        if final_urls:
            print("Итоговый список ссылок:", final_urls)
        else:
            print("Итоговый список ссылок пустой, что ожидаемо для данного теста.")

if __name__ == '__main__':
    unittest.main()

import unittest
from functions import fetch_and_filter_results, process_results, osint_process_result  # Убедитесь, что импорты корректны

class TestWorkflowIntegration(unittest.TestCase):
    def test_integration_of_functions(self):
        # Подготовка данных для запроса
        company = "Adsneton"
        job_title = "DevOps"

        # Реальный вызов функции для получения и фильтрации результатов
        filtered_results = fetch_and_filter_results(company, job_title)

        # Обработка фильтрованных результатов
        processed_data = process_results(filtered_results, company, job_title)

        # Реальный вызов функции обработки результатов
        processed_results = osint_process_result(processed_data)  # Передаем обработанные данные

        # Реальный вызов функции для экранирования Markdown
        escaped_output = processed_results

        # Вывод результатов теста (можно также использовать assert для сравнения с ожидаемым результатом)
        print("Final output:", escaped_output)

        # Проверка на корректность форматирования (это условный пример, настройте под ваши требования)
        #self.assertTrue(escaped_output.startswith("Аналіз показує"), "Output does not start with expected text.")

if __name__ == '__main__':
    unittest.main()

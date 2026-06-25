"""
Action Chance - демонстрационная версия логики скрипта для портфолио

Этот файл содержит всю логику основного скрипта, но с заменой чувствительных данных
на обобщенные значения для демонстрации на собеседовании.

Основные функции:
- Получение списка участников акции
- Выгрузка данных о покупках из базы
- Создание новых купонов
- Проверка дубликатов
- Генерация отчетов
"""

import os
import pandas as pd
import datetime
from datetime import timedelta
import json

# Константы акции (примерные значения для демонстрации)
ACTION_NAME = "Сладкий холод"
START_DATE = "2026-06-11 00:00:00"
END_DATE = "2026-07-08 23:59:59"
MIN_SUM_FOR_COUPON = 800  # Минимальная сумма чека для получения купона
MIN_PURCHASES_PER_WEEK = 3  # Минимальное количество покупок в неделю

# Пути к файлам
INPUT_DIR = "projects/loyalty-mechanisms/input_files/"
REPORTS_DIR = "projects/loyalty-mechanisms/reports/"
LOGS_DIR = "projects/loyalty-mechanisms/logs/"


def setup_directories():
    """Создание необходимых папок для работы скрипта"""
    print("=== Настройка директорий ===")
    
    # Создание папки логов
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
        print(f"Создана папка логов: {LOGS_DIR}")
    
    # Создание папки входных файлов
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        print(f"Создана папка входных файлов: {INPUT_DIR}")
    
    # Создание папки отчетов
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        print(f"Создана папка отчетов: {REPORTS_DIR}")
    
    print("=== Директории настроены ===\n")


def load_registered_cards():
    """
    Загрузка списка зарегистрированных карт из файла
    
    В реальном скрипте: получение данных с сайта акции через FTP
    В демонстрационной версии: создание симуляционных данных
    """
    print("=== Загрузка зарегистрированных карт ===")
    
    # В реальности файл ncard.csv загружается с FTP-сервера
    # Здесь создаем симуляционные данные для демонстрации
    
    sample_cards = [
        "1234567890123456",
        "2345678901234567",
        "3456789012345678",
        "4567890123456789",
        "5678901234567890"
    ]
    
    # Сохраняем в файл (как в реальном скрипте)
    with open(f"{INPUT_DIR}ncard.csv", "w") as f:
        for card in sample_cards:
            f.write(f"{card}\n")
    
    print(f"Загружено {len(sample_cards)} зарегистрированных карт")
    print("=== Загрузка завершена ===\n")
    
    return sample_cards


def get_participant_info():
    """
    Получение информации о участниках акции
    
    В реальном скрипте: подключение к OLAP-кубу Loymax через DAX-запросы
    В демонстрационной версии: создание симуляционных данных
    """
    print("=== Получение информации о участниках ===")
    
    # В реальности данные выгружаются из OLAP-куба с помощью Pyadomd
    # Здесь создаем симуляционные данные
    
    sample_participants = [
        {"card_number": "1234567890123456", "phone": "79001234567", "name": "Иванов Иван"},
        {"card_number": "2345678901234567", "phone": "79002345678", "name": "Петров Петр"},
        {"card_number": "3456789012345678", "phone": "79003456789", "name": "Сидоров Сидор"},
        {"card_number": "4567890123456789", "phone": "79004567890", "name": "Кузнецов Кузьма"},
        {"card_number": "5678901234567890", "phone": "79005678901", "name": "Попов Павел"}
    ]
    
    # Сохраняем в файл
    df_participants = pd.DataFrame(sample_participants)
    df_participants.to_csv(f"{INPUT_DIR}participants_data.csv", index=False)
    
    print(f"Получена информация о {len(sample_participants)} участниках")
    print("=== Информация получена ===\n")
    
    return df_participants


def get_purchase_data(participants_df):
    """
    Получение данных о покупках участников
    
    В реальном скрипте: запросы к ClickHouse и OLAP-кубу
    В демонстрационной версии: создание симуляционных данных
    
    Логика:
    - Фильтруем чеки по датам акции
    - Фильтруем по минимальной сумме (POROG_SUM)
    - Фильтруем по количеству покупок в неделю (для франшиз)
    """
    print("=== Получение данных о покупках ===")
    
    # В реальности данные выгружаются из ClickHouse:
    # - Основные магазины (фрешмаркеты)
    # - Франшизы (Командор №13, 14, 213, 91)
    # - Онлайн-заказы
    
    # Симуляционные данные о покупках
    sample_purchases = [
        {"card_number": "1234567890123456", "store": "101", "check_no": "1001", "date": "2026-06-15 10:30:00", "sum": 1200},
        {"card_number": "1234567890123456", "store": "102", "check_no": "1002", "date": "2026-06-16 14:20:00", "sum": 950},
        {"card_number": "1234567890123456", "store": "103", "check_no": "1003", "date": "2026-06-17 09:45:00", "sum": 1500},
        {"card_number": "2345678901234567", "store": "101", "check_no": "1004", "date": "2026-06-15 11:00:00", "sum": 850},
        {"card_number": "2345678901234567", "store": "104", "check_no": "1005", "date": "2026-06-18 16:30:00", "sum": 1100},
        {"card_number": "3456789012345678", "store": "102", "check_no": "1006", "date": "2026-06-16 12:15:00", "sum": 750},  # Меньше порога
        {"card_number": "4567890123456789", "store": "105", "check_no": "1007", "date": "2026-06-17 13:00:00", "sum": 2000},
        {"card_number": "5678901234567890", "store": "101", "check_no": "1008", "date": "2026-06-15 10:00:00", "sum": 900},
    ]
    
    df_purchases = pd.DataFrame(sample_purchases)
    
    # В реальном скрипте:
    # 1. Выгружаем данные из ClickHouse по основным магазинам
    # 2. Выгружаем данные по франшизам (отдельный запрос)
    # 3. Выгружаем онлайн-заказы
    # 4. Объединяем все данные
    
    # Фильтрация по минимальной сумме (как в реальном скрипте)
    df_purchases_filtered = df_purchases[df_purchases["sum"] >= MIN_SUM_FOR_COUPON].copy()
    
    print(f"Всего покупок: {len(df_purchases)}")
    print(f"Покупок, соответствующих условиям (сумма >= {MIN_SUM_FOR_COUPON}): {len(df_purchases_filtered)}")
    
    # Сохраняем промежуточный результат
    df_purchases_filtered.to_csv(f"{REPORTS_DIR}purchases_filtered.csv", index=False)
    
    print("=== Данные о покупках получены ===\n")
    
    return df_purchases_filtered


def calculate_coupons(df_purchases, participants_df):
    """
    Расчет количества купонов для каждого участника
    
    В реальном скрипте: логика рассчитывается в ClickHouse-запросах:
    - floor(sum((s.summ)/{POROG_SUM})) - купоны по сумме
    - floor(sum(1)) - купоны по количеству чеков
    - least() - минимальное значение
    
    В демонстрационной версии: упрощенная логика
    """
    print("=== Расчет купонов ===")
    
    # В реальности логика сложная:
    # 1. Для фрешмаркетов: floor(sum(summ)/800) или 1, в зависимости от условий
    # 2. Для франшиз: fixed logic (всегда 1 купон за чек при определенных условиях)
    # 3. Для онлайн: отдельная логика
    
    # Добавляем количество купонов (в реальном скрипте это делается в SQL)
    df_purchases["coupons"] = 1  # Упрощенно: 1 купон за чек, если сумма >= порога
    
    # В реальном скрипте:
    # df_purchases["koef_sum"] = (df_purchases["sum"] / MIN_SUM_FOR_COUPON).apply(math.floor)
    # df_purchases["koef_qnt"] = 1
    # df_purchases["cnt"] = df_purchases[["koef_sum", "koef_qnt"]].min(axis=1)
    # df_purchases["coupons"] = df_purchases["cnt"]
    
    # Группируем по карте и считаем количество купонов
    coupon_counts = df_purchases.groupby("card_number")["coupons"].sum().reset_index()
    coupon_counts.columns = ["card_number", "total_coupons"]
    
    # Объединяем с информацией о участниках
    df_with_coupons = participants_df.merge(coupon_counts, on="card_number", how="left")
    df_with_coupons["total_coupons"] = df_with_coupons["total_coupons"].fillna(0).astype(int)
    
    print("Распределение купонов:")
    for _, row in df_with_coupons.iterrows():
        print(f"  {row['name']}: {row['total_coupons']} купонов")
    
    print("=== Расчет завершен ===\n")
    
    return df_with_coupons


def generate_coupons(df_with_coupons):
    """
    Генерация уникальных номеров купонов
    
    В реальном скрипте:
    - Проверяется максимальный номер купона в базе
    - Генерируются новые уникальные номера
    - Проверяются дубликаты
    
    В демонстрационной версии: генерация простых уникальных номеров
    """
    print("=== Генерация купонов ===")
    
    # В реальном скрипте:
    # 1. Загружаем существующие купоны из базы
    # 2. Находим максимальный номер
    # 3. Генерируем новые уникальные номера
    # 4. Проверяем на дубликаты
    
    # Генерируем номера купонов
    coupon_list = []
    coupon_counter = 10000  # Начинаем с 10000 (как в реальном скрипте)
    
    for _, row in df_with_coupons.iterrows():
        if row["total_coupons"] > 0:
            for i in range(int(row["total_coupons"])):
                coupon_number = f"{coupon_counter:05d}"  # Формат: 00001
                coupon_list.append({
                    "card_number": row["card_number"],
                    "phone": row["phone"],
                    "coupon_number": coupon_number,
                    "is_winning": False
                })
                coupon_counter += 1
    
    df_coupons = pd.DataFrame(coupon_list)
    
    print(f"Сгенерировано {len(df_coupons)} купонов")
    print("=== Генерация завершена ===\n")
    
    return df_coupons


def save_reports(df_with_coupons, df_coupons):
    """
    Сохранение отчетов
    
    В реальном скрипте:
    - Формируется Excel-файл с участниками
    - Формируется JSON-файл для импорта на сайт
    - Сохраняются промежуточные данные
    """
    print("=== Сохранение отчетов ===")
    
    # Отчет с участниками и купонами
    report_df = df_with_coupons.copy()
    report_df = report_df[["card_number", "phone", "name", "total_coupons"]]
    report_df.columns = ["Номер карты", "Телефон", "ФИО", "Количество купонов"]
    
    date_str = datetime.date.today().strftime("%Y%m%d")
    report_filename = f"{REPORTS_DIR}participants_{date_str}.xlsx"
    
    # Сохраняем в Excel (как в реальном скрипте)
    with pd.ExcelWriter(report_filename, engine='openpyxl') as writer:
        report_df.to_excel(writer, sheet_name='participants', index=False)
    
    print(f"Отчет с участниками сохранен в {report_filename}")
    
    # JSON-файл для импорта на сайт (упрощенно)
    coupons_json = []
    for _, row in df_coupons.iterrows():
        coupons_json.append({
            "card_number": row["card_number"],
            "coupon_number": row["coupon_number"],
            "is_winning": row["is_winning"]
        })
    
    json_filename = f"{REPORTS_DIR}coupons_data.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(coupons_json, f, indent=4, ensure_ascii=False)
    
    print(f"JSON-файл для импорта сохранен в {json_filename}")
    print("=== Отчеты сохранены ===\n")


def check_duplicates(df_coupons):
    """
    Проверка на дубликаты купонов
    
    В реальном скрипте:
    - Сверяется с базой существующих купонов
    - Удаляются дубликаты перед импортом
    """
    print("=== Проверка на дубликаты ===")
    
    # В реальном скрипте:
    # 1. Загружаем существующие купоны из базы
    # 2. Сверяем номера
    # 3. Удаляем дубликаты
    
    # Здесь просто проверяем уникальность в текущем списке
    unique_coupons = df_coupons["coupon_number"].nunique()
    total_coupons = len(df_coupons)
    
    print(f"Всего купонов: {total_coupons}")
    print(f"Уникальных номеров: {unique_coupons}")
    
    if unique_coupons == total_coupons:
        print("Дубликатов не найдено")
    else:
        print(f"Найдено {total_coupons - unique_coupons} дубликатов")
    
    print("=== Проверка завершена ===\n")


def create_push_reports(df_purchases, df_participants):
    """
    Создание отчетов для пуш-уведомлений
    
    В реальном скрипте:
    - Сравниваются зарегистрированные и незарегистрированные участники
    - Формируются списки для пушей
    """
    print("=== Создание отчетов для пушей ===")
    
    # В реальном скрипте:
    # 1. Загружаем список зарегистрированных карт
    # 2. Получаем список участников, выполнивших условия
    # 3. Сравниваем два списка
    # 4. Формируем два отчета:
    #    - Зарегистрировался, но не выполнил условия
    #    - Выполнил условия, но не зарегистрировался
    
    # Симуляционные отчеты
    reg_not_done = pd.DataFrame({
        "phone": ["79001234567", "79009999999"]
    })
    done_not_reg = pd.DataFrame({
        "phone": ["79008888888", "79007777777"]
    })
    
    # Сохраняем в Excel
    reg_not_done.to_excel(f"{REPORTS_DIR}push_1.xlsx", sheet_name='registrated_not_done', index=False)
    done_not_reg.to_excel(f"{REPORTS_DIR}push_2.xlsx", sheet_name='done_not_registrated', index=False)
    
    print("Отчеты для пушей созданы")
    print("=== Создание отчетов завершено ===\n")


def post_coupons_api(df_coupons):
    """
    Отправка купонов на API сайта акции
    
    В реальном скрипте:
    - Подготовленный JSON с купонами отправляется POST-запросом
    - Используется токен авторизации
    - Обработка ошибок с повторами
    
    В демонстрационной версии:
    - Имитация отправки запроса
    - Показ логики обработки ответа
    """
    print("=== Отправка купонов на API ===")
    
    # В реальном скрипте:
    # 1. Получаем токен авторизации (запрос к /auth/jwt/login)
    # 2. Формируем JSON с купонами
    # 3. Отправляем POST-запросом на /promo_api/v1/coupons
    # 4. Обрабатываем ответ и ошибки
    # 5. При ошибках - повторы с задержкой
    
    # Формируем данные для отправки (как в реальном скрипте)
    api_payload = []
    for _, row in df_coupons.iterrows():
        api_payload.append({
            "cardNumber": row["card_number"],
            "couponNumber": row["coupon_number"],
            "isWinning": row["is_winning"],
            "promotionId": "123asd123-234wer423-sdfsf324-dfs34234"  # ID акции
        })
    
    # В реальном скрипте:
    # url = "https://api.example.ru/example_api/v1/coupons/"
    # headers = {'Authorization': 'Bearer ' + token}
    # response = requests.post(url, headers=headers, json=api_payload)
    
    print(f"Подготовлено {len(api_payload)} купонов для отправки")
    print(f"Структура одного элемента:")
    print(f"  - cardNumber: {api_payload[0]['cardNumber']}")
    print(f"  - couponNumber: {api_payload[0]['couponNumber']}")
    print(f"  - isWinning: {api_payload[0]['isWinning']}")
    print(f"  - promotionId: {api_payload[0]['promotionId']}")
    
    # Имитация отправки (как в реальном скрипте)
    print("\n--- Имитация отправки запроса ---")
    print("POST https://api.example.ru/example_api/v1/coupons/")
    print("Authorization: Bearer <token>")
    print(f"Body: {len(api_payload)} купонов")
    
    # Имитация ответа (как в реальном скрипте)
    print("\n--- Ответ от API ---")
    print("HTTP 200 OK")
    print("{")
    print("  'success': true,")
    print("  'message': 'Купоны успешно импортированы'")
    print("}")
    
    # В реальном скрипте обработка ответа:
    # soup = BeautifulSoup(response.text, 'html.parser')
    # rs = json.loads(soup.text)
    # print(rs)
    
    print(f"\nУспешно отправлено {len(api_payload)} купонов")
    print("=== Отправка завершена ===\n")


def main():
    """
    Основная функция - запуск всей логики
    
    В реальном скрипте:
    - Запускается ежедневно или по расписанию
    - Выполняет все шаги по обработке данных
    - Сохраняет результаты
    
    В демонстрационной версии:
    - Запускается один раз для демонстрации логики
    """
    print("=" * 60)
    print("Action Chance - Демонстрационная версия")
    print("=" * 60)
    print()
    
    # Шаг 1: Настройка директорий
    setup_directories()
    
    # Шаг 2: Загрузка зарегистрированных карт
    registered_cards = load_registered_cards()
    
    # Шаг 3: Получение информации о участниках
    participants_df = get_participant_info()
    
    # Шаг 4: Получение данных о покупках
    purchases_df = get_purchase_data(participants_df)
    
    # Шаг 5: Расчет купонов
    coupons_df = calculate_coupons(purchases_df, participants_df)
    
    # Шаг 6: Генерация купонов
    generated_coupons = generate_coupons(coupons_df)
    
    # Шаг 7: Проверка на дубликаты
    check_duplicates(generated_coupons)
    
    # Шаг 8: Создание отчетов для пушей
    create_push_reports(purchases_df, participants_df)
    
    # Шаг 9: Отправка купонов на API
    post_coupons_api(generated_coupons)
    
    # Шаг 10: Сохранение отчетов
    save_reports(coupons_df, generated_coupons)
    
    print("=" * 60)
    print("Демонстрация завершена успешно!")
    print("=" * 60)


if __name__ == "__main__":
    main()

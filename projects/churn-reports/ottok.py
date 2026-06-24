"""
ОТТОК - Скрипт для анализа эффективности маркетинговых кампаний

Этот скрипт демонстрирует логику обработки данных из маркетинговых систем,
анализа поведения клиентов и формирования контрольных групп.
Для демонстрационных целей в портфолио.

Автор: Sber GigaCode
Дата: 2026
"""

import csv
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime, timedelta
import logging
from pathlib import Path
import shutil
import glob
import os


# Настройка логирования
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

log_filename = LOGS_DIR / f"ottok_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# Глобальные множества для хранения клиентов
LIST_OF_INCLUSE_CONTROL_GROUP = set(["''"])
PUSH_TARGET_CLIENTS = set()
MAIL_TARGET_CLIENTS = set()


def clear_target_control_folders():
    """
    Очищает содержимое папок target_group и control_group в директориях push и mail.
    """
    try:
        folders_to_clear = [
            'push/target_group',
            'push/control_group',
            'mail/target_group',
            'mail/control_group'
        ]
        
        for folder in folders_to_clear:
            folder_path = Path(folder)
            if folder_path.exists() and folder_path.is_dir():
                for item in folder_path.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                logger.info(f"Содержимое папки {folder} успешно удалено.")
            else:
                logger.warning(f"Папка {folder} не существует или не является директорией.")
                
    except Exception as e:
        logger.error(f"Ошибка при удалении содержимого папок: {str(e)}")
        raise


def get_token():
    """
    Получает токен авторизации из сервиса авторизации.
    
    Returns:
        str: Access token для авторизации в API
    """
    try:
        session = requests.Session()

        url = 'https://api.example.com/authorization/token'

        headers = {
            'Host': 'api.example.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'password',
            'username': "service_user",
            'password': "secure_password",
            'area': "users"
        }

        session.headers.update(headers)

        response = session.post(url, data=data)

        soup = BeautifulSoup(response.text, 'html.parser')
        rs = json.loads(soup.text)

        logger.info("Токен успешно получен")
        return rs['access_token']
    
    except Exception as e:
        logger.error(f"Ошибка при получении токена: {str(e)}")
        raise


def get_clients_list(token, target_group_id, count_clients):
    """
    Получает список клиентов из целевой группы через API.
    
    Args:
        token (str): Токен авторизации
        target_group_id (int): ID целевой группы
        count_clients (int): Количество клиентов для получения
    
    Returns:
        list: Список клиентов в формате ['"UUID"', ...]
    """
    clients = []

    try:
        for i in range(0, count_clients, 1000):
            url = f"https://api.example.com/target-groups/{target_group_id}/persons?from={i}&count={1000}"
            logger.info(f"Запрос к API: {url}")

            headers = {
                'Authorization': 'Bearer ' + token
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rs = json.loads(soup.text)

                batch_clients = ['"{' + str(i['personUid']).upper() + '}"' for i in rs['data']]
                clients.extend(batch_clients)
                logger.info(f"Получено {len(batch_clients)} клиентов в диапазоне {i}-{i+999}")
            else:
                logger.warning(f"Получен ответ с кодом {response.status_code} для диапазона {i}-{i+999}")

        logger.info(f"Общее количество полученных клиентов: {len(clients)}")
        return clients
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка клиентов: {str(e)}")
        raise


def get_target_group_clients(token):
    """
    Получает и сохраняет клиентов из целевых групп в глобальные переменные.
    Добавляет оба списка в исключающий список для контрольных групп.
    """
    try:
        # Получаем клиентов для Push кампании
        push_clients = get_clients_list(token, 834, 50000)
        push_client_uids = set([uid.replace('{', '').replace('}', '').replace('"', '').strip() for uid in push_clients])
        PUSH_TARGET_CLIENTS.update(push_client_uids)
        logger.info(f"Получено {len(PUSH_TARGET_CLIENTS)} клиентов из целевой группы Push")
        
        # Получаем клиентов для Mail кампании
        mail_clients = get_clients_list(token, 833, 50000)
        mail_client_uids = set([uid.replace('{', '').replace('}', '').replace('"', '').strip() for uid in mail_clients])
        MAIL_TARGET_CLIENTS.update(mail_client_uids)
        logger.info(f"Получено {len(MAIL_TARGET_CLIENTS)} клиентов из целевой группы Mail")
        
        # Добавляем клиентов из обеих целевых групп в исключающий список
        all_target_clients = set()
        all_target_clients.update(PUSH_TARGET_CLIENTS)
        all_target_clients.update(MAIL_TARGET_CLIENTS)
        
        # Форматируем клиентов для использования в SQL запросах
        formatted_clients = [f"'{uid}'" for uid in all_target_clients]
        LIST_OF_INCLUSE_CONTROL_GROUP.update(formatted_clients)
        
        logger.info(f"Всего {len(LIST_OF_INCLUSE_CONTROL_GROUP)} клиентов добавлено в исключающий список")
        
    except Exception as e:
        logger.error(f"Ошибка при получении клиентов целевых групп: {str(e)}")
        raise


def get_dates_of_accrued_bonuses(clients, date_end):
    """
    Получает даты начисления бонусов для клиентов из OLAP-куба.
    
    Args:
        clients (list): Список клиентов
        date_end (str): Конечная дата в формате YYYYMMDD
    
    Returns:
        pandas.DataFrame: DataFrame с client_uid и датой начисления
    """
    try:
        # Здесь может быть подключение к OLAP-серверу
        # Для демонстрации используем заглушку
        conn_str = "Provider=MSOLAP;Data Source=https://olap.example.com;Timeout=9999"
        str_clients = ','.join(clients)

        query = """EVALUATE
                    SUMMARIZECOLUMNS(
                        Card[PersonUid],
                        OperationManual_FCT[DepositType],
                        OperationManual_FCT[Comment],
                        'Time'[Дата],
                        KEEPFILTERS( TREATAS( {"Начисление бонусов"}, OperationManual_FCT[Comment] )),
                        KEEPFILTERS( TREATAS( {"campaign3391"}, OperationManual_FCT[InternalComment] )),
                        KEEPFILTERS( FILTER( ALL( 'Time'[Дата] ), 'Time'[Дата] >= DATE(2025,1,1) && 'Time'[Дата] <= DATE(2026,6,8) )),
                        KEEPFILTERS( TREATAS( {""" + str_clients + """}, Card[PersonUid] )),
                        "Ручные начисления", [Ручные начисления]
                    )"""

        # В реальном скрипте здесь было бы подключение к OLAP серверу
        # Для демонстрации создадим пустой DataFrame
        clients_with_dates = pd.DataFrame(columns=['person_uid', 'date_acc'])
        
        logger.info(f"Запрос к OLAP кубу выполнен (демонстрационный режим)")
        
        return clients_with_dates
    
    except Exception as e:
        logger.error(f"Ошибка при получении дат начисления бонусов: {str(e)}")
        raise


def get_clickhouse_data(clients_with_dates, date_end):
    """
    Получает данные о транзакциях клиентов из ClickHouse.
    
    Args:
        clients_with_dates (pandas.DataFrame): DataFrame с клиентами и датами
        date_end (str): Конечная дата в формате YYYYMMDD
    
    Returns:
        pandas.DataFrame: DataFrame с данными о транзакциях
    """
    try:
        date_start_30 = (datetime.strptime(date_end, "%Y%m%d") - timedelta(30)).strftime("%Y%m%d")
        date_end_plus_7_days = (datetime.strptime(date_end, "%Y%m%d") + timedelta(6)).strftime("%Y%m%d")
        date_end_plus_30_days = (datetime.strptime(date_end_plus_7_days, "%Y%m%d") + timedelta(29)).strftime("%Y%m%d")

        users_list = ["'" + str(i[0]).replace('{', '').replace('}', '') + "'" for i in clients_with_dates.values]

        # Здесь может быть подключение к ClickHouse
        # Для демонстрации используем заглушку
        clh_df = pd.DataFrame(columns=[
            'person_uid', 'sum_next_7_days', 'bp_next_7_days', 'ba_next_7_days', 'ch_cnt_next_7_days',
            'sum_next_30_days', 'bp_next_30_days', 'ba_next_30_days', 'ch_cnt_next_30_days'
        ])
        
        logger.info(f"Запрос к ClickHouse выполнен (демонстрационный режим)")
        return clh_df
    
    except Exception as e:
        logger.error(f"Ошибка при получении данных из ClickHouse: {str(e)}")
        raise


def get_control_group_data(clients_with_dates, date_end, limit, folder):
    """
    Получает данные контрольной группы из базы данных.
    
    Args:
        clients_with_dates (pandas.DataFrame): DataFrame с клиентами и датами
        date_end (str): Конечная дата в формате YYYYMMDD
        limit (int): Лимит количества клиентов
        folder (str): Название папки для сохранения ('push' или 'mail')
    
    Returns:
        pandas.DataFrame: DataFrame с данными контрольной группы
    """
    try:
        date_start_30 = (datetime.strptime(date_end, "%Y%m%d") - timedelta(30)).strftime("%Y%m%d")
        date_start_90 = (datetime.strptime(date_end, "%Y%m%d") - timedelta(90)).strftime("%Y%m%d")
        date_end_plus_7_days = (datetime.strptime(date_end, "%Y%m%d") + timedelta(6)).strftime("%Y%m%d")
        date_end_plus_30_days = (datetime.strptime(date_end_plus_7_days, "%Y%m%d") + timedelta(29)).strftime("%Y%m%d")

        users_list = ["'" + str(i[0]).replace('{', '').replace('}', '') + "'" for i in clients_with_dates.values]

        # Здесь может быть подключение к базе данных
        # Для демонстрации используем заглушку
        clh_df = pd.DataFrame(columns=[
            'person_uid', 'close_date', 'sum_30_days', 'sum_90_days',
            'sum_next_7_days', 'bp_next_7_days', 'ba_next_7_days', 'ch_cnt_next_7_days',
            'sum_next_30_days', 'bp_next_30_days', 'ba_next_30_days', 'ch_cnt_next_30_days'
        ])
        
        clh_df['close_date'] = date_end
        
        clh_df = clh_df[[
            'person_uid', 'close_date', 'sum_30_days', 'sum_90_days',
            'sum_next_7_days', 'bp_next_7_days', 'ba_next_7_days', 'ch_cnt_next_7_days',
            'sum_next_30_days', 'bp_next_30_days', 'ba_next_30_days', 'ch_cnt_next_30_days'
        ]]
        
        logger.info(f"Получено {len(clh_df)} клиентов для контрольной группы {folder}")
        
        # Создаем директории, если они не существуют
        Path(f"{folder}/control_group").mkdir(parents=True, exist_ok=True)
        
        output_file = f'{folder}/control_group/{folder}_control_group_{date_end}.csv'
        clh_df.to_csv(output_file, sep=';', encoding='utf-8', index=False)
        logger.info(f"Контрольная группа сохранена в файл: {output_file}")
        
        exclude_list = ["'" + str(i[0]).replace('{', '').replace('}', '') + "'" for i in clh_df.values]
        logger.info(f"Добавлено {len(exclude_list)} клиентов в исключающий список")
        
        LIST_OF_INCLUSE_CONTROL_GROUP.update(exclude_list)
        logger.info(f"Общее количество клиентов в исключающем списке: {len(LIST_OF_INCLUSE_CONTROL_GROUP)}")
        
        return clh_df
    
    except Exception as e:
        logger.error(f"Ошибка при получении данных контрольной группы: {str(e)}")
        raise


def process_campaign(target_group_id, folder, date_end_list):
    """
    Обрабатывает кампанию (Push или Mail) для указанного периода.
    
    Args:
        target_group_id (int): ID целевой группы
        folder (str): Название папки для сохранения ('push' или 'mail')
        date_end_list (list): Список дат окончания периода
    """
    try:
        logger.info(f"\nНачало обработки кампании: {folder.upper()}")
        logger.info(f"ID целевой группы: {target_group_id}")
        
        # Используем уже загруженные клиенты из глобальных переменных
        clients = []
        if folder == 'push':
            clients = [f'"{uid}"' for uid in PUSH_TARGET_CLIENTS]
            logger.info(f"Используем {len(clients)} клиентов из глобального множества для Push кампании")
        elif folder == 'mail':
            clients = [f'"{uid}"' for uid in MAIL_TARGET_CLIENTS]
            logger.info(f"Используем {len(clients)} клиентов из глобального множества для Mail кампании")
        
        total_processed = 0

        for date_end in date_end_list:
            logger.info(f"\nОбработка даты: {date_end}")
            logger.info("-" * 50)

            # Рассчитываем даты для анализа
            date_start_30 = (datetime.strptime(date_end, "%Y%m%d") - timedelta(30)).strftime("%Y%m%d")
            date_start_90 = (datetime.strptime(date_end, "%Y%m%d") - timedelta(90)).strftime("%Y%m%d")
            date_end_plus_7_days = (datetime.strptime(date_end, "%Y%m%d") + timedelta(6)).strftime("%Y%m%d")
            date_end_plus_30_days = (datetime.strptime(date_end_plus_7_days, "%Y%m%d") + timedelta(29)).strftime("%Y%m%d")

            logger.info(f"Период анализа: {date_start_90} - {date_end_plus_30_days}")

            # Получаем клиентов с датами начисления бонусов
            clients_with_dates = get_dates_of_accrued_bonuses(clients, date_end)

            if len(clients_with_dates) > 0:
                # Получаем данные о транзакциях
                data_chl = get_clickhouse_data(clients_with_dates, date_end)

                if len(data_chl) > 0:
                    # Объединяем данные
                    merged_df = pd.merge(clients_with_dates, data_chl, 'left', 'person_uid')

                    # Создаем директории, если они не существуют
                    Path(f"{folder}/target_group").mkdir(parents=True, exist_ok=True)
                    
                    # Сохраняем целевую группу
                    output_file = f'{folder}/target_group/{folder}_{date_end}.csv'
                    merged_df.to_csv(output_file, sep=';', encoding='utf-8', index=False)
                    logger.info(f"Целевая группа сохранена в файл: {output_file}")

                    # Определяем размер контрольной группы
                    limit = max(1, int(clients_with_dates.shape[0]) // 8)
                    logger.info(f'Лимит для контрольной группы: {limit}')

                    # Получаем и сохраняем контрольную группу
                    control_group = get_control_group_data(clients_with_dates, date_end, limit, folder)

                    total_processed += int(clients_with_dates.shape[0])
                    logger.info(f"Общее количество обработанных клиентов: {total_processed}")
                else:
                    logger.warning(f"За период {date_end} не удалость обработать кампанию")
        logger.info(f"Завершена обработка кампании: {folder.upper()}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке кампании {folder}: {str(e)}")
        raise


def concat_csv_files(folder):
    """
    Объединяет все CSV-файлы из папок target_group и control_group в единые файлы.
    
    Args:
        folder (str): Название папки ('push' или 'mail')
    """
    try:
        # Объединение целевых групп
        target_path = f'{folder}/target_group'
        target_files = glob.glob(os.path.join(target_path, "*.csv"))
        
        if target_files:
            target_list = []
            for filename in target_files:
                df = pd.read_csv(filename, sep=';', encoding='utf-8')
                target_list.append(df)
            
            target_frame = pd.concat(target_list, axis=0, ignore_index=True)
            target_file_name = f'{folder}_target_group.csv'
            target_frame.to_csv(target_file_name, index=False, sep=';', encoding='utf-8')
            logger.info(f"Объединение целевых групп завершено! Файл '{target_file_name}' создан.")
        else:
            logger.warning(f"В папке {target_path} не найдено CSV-файлов для объединения")
    
        # Объединение контрольных групп
        control_path = f'{folder}/control_group'
        control_files = glob.glob(os.path.join(control_path, "*.csv"))
        
        if control_files:
            control_list = []
            for filename in control_files:
                df = pd.read_csv(filename, sep=';', encoding='utf-8')
                control_list.append(df)
            
            control_frame = pd.concat(control_list, axis=0, ignore_index=True)
            control_file_name = f'{folder}_control_group.csv'
            control_frame.to_csv(control_file_name, index=False, sep=';', encoding='utf-8')
            logger.info(f"Объединение контрольных групп завершено! Файл '{control_file_name}' создан.")
        else:
            logger.warning(f"В папке {control_path} не найдено CSV-файлов для объединения")
            
    except Exception as e:
        logger.error(f"Ошибка при объединении CSV-файлов для {folder}: {str(e)}")
        raise


def main():
    """
    Основная функция скрипта.
    Очищает папки, получает токен, обрабатывает кампании и объединяет результаты.
    """
    try:
        logger.info("\n" + "="*60)
        logger.info("НАЧАЛО ОБРАБОТКИ СКРИПТА")
        logger.info("="*60)

        # Очищаем итоговые файлы в push и mail
        clear_target_control_folders()

        # Получаем токен
        token = get_token()
        
        # Получаем и сохраняем клиентов из целевых групп
        get_target_group_clients(token)

        # Список дат для анализа
        start_date = datetime.strptime('20260301', "%Y%m%d")
        end_date = datetime.strptime('20260608', "%Y%m%d")
        date_end_list = [
            (start_date + timedelta(days=i)).strftime("%Y%m%d")
            for i in range((end_date - start_date).days + 1)
        ]
        logger.info(f"Анализ будет проведен по {len(date_end_list)} датам")

        # Сначала обрабатываем Push кампанию
        logger.info("\n" + "="*60)
        logger.info("НАЧАЛО ОБРАБОТКИ PUSH КАМПАНИИ")
        logger.info("="*60)
        process_campaign(834, 'push', date_end_list)

        # Затем обрабатываем Mail кампанию
        logger.info("\n" + "="*60)
        logger.info("НАЧАЛО ОБРАБОТКИ MAIL КАМПАНИИ")
        logger.info("="*60)
        process_campaign(833, 'mail', date_end_list)

        # Объединяем CSV-файлы для push и mail групп
        concat_csv_files('push')
        concat_csv_files('mail')
        
        logger.info("\n" + "="*60)
        logger.info("ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО")
        logger.info("="*60)
        
    except Exception as e:
        logger.error("\n" + "="*60)
        logger.error("ОШИБКА ПРИ ВЫПОЛНЕНИИ СКРИПТА")
        logger.error("="*60)
        logger.error(f"Подробности ошибки: {str(e)}")
        raise


# Основной блок выполнения
if __name__ == "__main__":
    main()

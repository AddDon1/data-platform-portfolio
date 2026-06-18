"""Скрипт для сверки чеков с витриной данных."""
import pandas as pd

LIST_OF_STORE_IRKUTSK = [
    173, 175, 176, 177, 180, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192,
    193, 194, 195, 197, 198, 199, 202, 203, 204, 205, 206, 207, 210, 212, 214,
    216, 222, 260, 287, 311, 321, 331, 332, 333, 341, 345, 347, 352, 358, 362,
    371, 373, 377, 378, 380, 381, 394, 396, 398, 407, 413, 414, 435, 441, 443,
]

FORMAT_DICT = {
    'ALLEYA': 'Суперстор',
    'ALLEYA PRODUKTY': 'Суперстор',
    'BUFET': 'Суперстор',
    'DISKAUNTER KHOROSHIJ': 'Дискаунтер',
    'KHOROSHI PRODUKTY': 'Дискаунтер',
    'KHOROSHII': 'Дискаунтер',
    'KHOROSHIJ': 'Дискаунтер',
    'KOMANDOR': 'Фрешмаркет',
    'KOMANDOR PRODUKTY': 'Фрешмаркет',
    'KOMANDOR_': 'Фрешмаркет',
    'MAGAZIN KHOROSHIJ': 'Дискаунтер',
    'MAGAZIN KOMANDOR': 'Фрешмаркет',
    'MERCHANT': 'Фрешмаркет',
    'ALLEJA': 'Суперстор',
    'ALLEYA PRODUKTY': 'Суперстор',
    'DISKAUNTER KHOROSHIJ': 'Дискаунтер',
    'FRESHMARKET 43': 'Фрешмаркет',
    'FRESHMARKET 87': 'Фрешмаркет',
    'KHOROSHI PRODUKTY': 'Дискаунтер',
    'KHOROSHII': 'Дискаунтер',
    'KHOROSHIJ': 'Дискаунтер',
    'KHOROSHIY': 'Дискаунтер',
    'KOMANDOR': 'Фрешмаркет',
    'KOMANDOR PRODUKTY': 'Фрешмаркет',
    'KOMANDOR_': 'Фрешмаркет',
    'MAGAKHIN KHOROSHIJ': 'Дискаунтер',
    'MAGAZIN  KOMANDOR': 'Фрешмаркет',
    'MAGAZIN KHOROSHIJ': 'Дискаунтер',
    'MAGAZIN KOMANDOR': 'Фрешмаркет',
    'K 10': 'Фрешмаркет',
    'K 2': 'Фрешмаркет',
    'K 4': 'Фрешмаркет',
    'MAGAZIN 23': 'Фрешмаркет',
    'Komandor': 'Фрешмаркет'
}


def refresh_format(format_name: str) -> str:
    """Возвращает обновленный формат магазина по словарю."""
    return FORMAT_DICT[format_name.upper()]


def load_vitrina_data(file_path: str) -> pd.DataFrame:
    """Загружает данные витрины из Excel-файла."""
    df = pd.read_excel(file_path, sheet_name='Лист1')
    df['MRC_NAME'] = df['MRC_NAME'].astype('str').apply(refresh_format)
    df = df.rename(columns={
        'MRC_NAME': 'format_name',
        'SUMMA_RUR': 'payed_money_bank',
        'OP_DATE': 'close_date',
    })
    df['RRN'] = df['RRN'].astype('int64')
    return df


def load_checks_data(file_path: str) -> pd.DataFrame:
    """Загружает данные чеков из CSV-файла."""
    df = pd.read_csv(file_path, sep=';')
    df['close_date'] = pd.to_datetime(df['close_date'])
    return df


def merge_data(
    checks_df: pd.DataFrame,
    vitrina_df: pd.DataFrame,
    on_columns: list,
) -> pd.DataFrame:
    """Выполняет слияние чеков и витрины по указанным колонкам."""
    merged = pd.merge(checks_df, vitrina_df, on=on_columns)
    merged['diff_date'] = merged['close_date_x'] - merged['close_date_y']
    merged['diff_date'] = merged['diff_date'].apply(
        lambda x: abs(x.total_seconds() / 60),
    )
    merged = merged.sort_values(by='diff_date')
    merged = merged.drop_duplicates(subset=['RRN'])
    return merged


def main():
    """Основная функция для выполнения сверки данных."""
    vitrina_df = load_vitrina_data('reports/vitrina_2026_without_store.xlsx')
    checks_df = load_checks_data('reports/checks_df.csv')

    print(vitrina_df['RRN'].head())
    print(vitrina_df.info())
    print(vitrina_df.shape[0])

    print(checks_df['close_date'].head())
    print(vitrina_df['close_date'].head())

    vitrina_df['close_date'] = pd.to_datetime(
        vitrina_df['close_date'], dayfirst=True,
    )

    merged_df = merge_data(
        checks_df,
        vitrina_df,
        on_columns=['format_name', 'payed_money_bank'],
    )

    print(merged_df.head())
    print(merged_df.info())
    print(merged_df.shape[0])

    merged_df.to_csv(
        'result/sverka_without_store_2026.csv',
        sep=';',
        encoding='utf-8',
    )


if __name__ == '__main__':
    main()

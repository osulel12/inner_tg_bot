import typing
from datetime import datetime

# Доступные значеения для каждого из параметров DAG
params_dag_list = {'eac': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
                   'nnnn': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
                   'mptrg': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
                   'chat_id': ['👻', '🎃'],
                   'field': ['day', 'hour', 'minute'],
                   'timeout': [str(i) for i in range(1, 101)],
                   'all_cleare': ['all cleare', 'no all cleare'],
                   'name_table_by_sql': ['ref_country', 'ref_flow', 'ref_flow_usda', 'ref_mirror', 'ref_name_group_tnved', 'ref_source', 'all'],
                   'name_table_by_run_func': ['ref_years', 'ref_month', 'all'],
                   'year_lower_border': [str(i) for i in range(2010, 2041)],
                   'year_upper_border': [str(i) for i in range(2010, 2041)],
                   'is_shown_lower_border': [str(i) for i in range(2010, 2041)],
                   'is_shown_upper_border': [str(i) for i in range(2010, 2041)],
                   'flag_truncate': ['True', 'False']}

# Доступные значеения для каждого из параметров DAG, вязанные со временем
params_dag_list_from_date = {'date_start': [], 'date_end': []}

# Количество элементов на странице для каждого параметра
element_on_page_value = {'eac': 12,
                         'nnnn': 12,
                         'mptrg': 12,
                         'date_end': 12,
                         'date_start': 12,
                         'field': 10,
                         'timeout': 25,
                         'chat_id': 2,
                         'all_cleare': 2,
                         'name_table_by_sql': 10,
                         'name_table_by_run_func': 10,
                         'year_lower_border': 10,
                         'year_upper_border': 10,
                         'is_shown_lower_border': 10,
                         'is_shown_upper_border': 10,
                         'flag_truncate': 5}


def get_twin_param_name(operation_name: str, param_choos: str) -> str:
    dct_operation = {'Отчет-Количество Справок': ['date_end', 'date_start']}
    return [param for param in dct_operation[operation_name] if param != param_choos][0]


def get_month_starts() -> list:
    """
    :return: список из дат начала каждого месяца в заданном интервале
    """
    start_year = 2020
    end_year = 2030
    month_starts = []

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            month_starts.append(datetime(year, month, 1))
    return month_starts


def get_need_value_list(key: str, current_value: str, current_value_twin: typing.Optional[str] = None) -> list:
    """
    :param key: название параметра, который мы редактируем

    :param current_value: текущее значение этого параметра

    :param current_value_twin: текущее значение парного параметра (используется для интервала дат)

    :return: преобразованный к нужному виду список с доступными значениями для переданного парамера(key)
    """
    if key in params_dag_list:
        return [value for value in params_dag_list[key] if value != current_value]
    elif key in params_dag_list_from_date:
        current_value = datetime.strptime(current_value, '%Y.%m.%d')
        current_value_twin = datetime.strptime(current_value_twin, '%Y.%m.%d')
        if key == 'date_start':
            return [date.strftime('%Y.%m.%d') for date in get_month_starts() if
                    date != current_value and date < current_value_twin]
        else:
            return [date.strftime('%Y.%m.%d') for date in get_month_starts() if
                    date != current_value and date > current_value_twin]

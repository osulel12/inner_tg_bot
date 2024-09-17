from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
import os
from dotenv import load_dotenv
import asyncpg
from asyncpg.pool import Pool
from datetime import datetime, timedelta
import pandas as pd
import requests
import logging
import io
import typing
import json

if os.path.exists('.env'):
    load_dotenv('.env')


class Hepl_work_by_postgre:
    """
    Класс риализующий дополнительную логику работы с базой данных пользователей ТГ бота

    :param alch_pg: не асинхронное соединение с БД Postgres
    :type alch_pg: Engine

    :param dct_user_state: словарь собираемый в момент инициализации экземпляра класса
                           и необходимый для проверки состояния пользователей
    :type dct_user_state: dict

    :param pool_aeforecast: пул асинхронных соединений для работы с бд Postgre Агроэкспорт
    :type pool_aeforecast: Pool | null

    """

    def __init__(self):
        self.alch_pg = create_engine(
            f"postgresql://{os.getenv('USER_NAME_PG')}:{os.getenv('PASSWORD_PG')}@{os.getenv('HOST_PG')}:{os.getenv('PORT_PG')}/{os.getenv('DATABASE_PG')}")
        self.dct_user_state = self.create_dct()
        self.pool_aeforecast = None
        self.dict_dag_state = {'success': '✅',
                               'running': '▶️',
                               'failed': '⛔️'}

    def create_dct(self) -> dict:
        """
        Возвращает словарь состояний каждого из пользователей роли admin
        необходимо для валидации состояния в callback_query_handler

        :return: словарь состояний пользователей
        """
        df_state = pd.read_sql("""SELECT * 
                                      FROM bot.state_user_etl_bot 
                                      WHERE chat_id in (SELECT chat_id FROM bot.user_tg_bot WHERE role_id IN (2, 4))""",
                               con=self.alch_pg)
        return {k: v for k, v in zip(df_state.chat_id.tolist(), df_state.current_state.tolist())}

    async def create_pool(self):
        """
        Создает асинхронный пул соединений для баз данных.
        Если такие еще не были созданы
        """
        if self.pool_aeforecast is None:
            self.pool_aeforecast = await asyncpg.create_pool(user=os.getenv('USER_NAME_PG'),
                                                             password=os.getenv('PASSWORD_PG'),
                                                             host=os.getenv('HOST_PG'),
                                                             port=os.getenv('PORT_PG'),
                                                             database=os.getenv('DATABASE_PG'), max_size=2, min_size=1)
        else:
            pass

    @staticmethod
    async def write_hello_func() -> str:
        """
        Рассчитывает приветственную фразу в зависимости от текущего времени
        :return: строку приветствия
        """
        hour = datetime.now().hour
        if 1 < hour <= 9:
            return 'Доброе утро'
        elif 9 < hour <= 13:
            return 'Добрый день'
        elif 13 < hour <= 20:
            return 'Добрый вечер'
        elif 20 <= hour <= 1:
            return 'Доброй ночи'

    async def check_user(self, user_id: int) -> bool:
        """
        Проверяет есть ли такой пользователь и является ли он администратором/пользователем-администратором

        :param user_id: chat_id пользователя

        :return: True or False
        """
        await self.create_pool()

        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval(
                """SELECT EXISTS(SELECT 1 FROM bot.user_tg_bot 
                   WHERE chat_id = $1 
                   AND uu_user_id IS NOT NULL 
                   AND role_id IN (2, 4)
                   AND active_user)""",
                user_id)

    async def update_state_user(self, user_id: int, state: str, update_dag_tag_func: typing.Optional[bool] = False):
        """
        Обновляет состояние пользователя(администратора) в БД и словаре
        для каждого бота используется своя таблица состояний

        :param user_id: chat_id администратора

        :param state: состояние в котором будет находиться администратора

        :param update_dag_tag_func: переменная необходимая для обновления dag_tag_func_state,
                                    параметра отвечающего за информацию о состоянии tag dag
        """
        await self.create_pool()

        async with self.pool_aeforecast.acquire() as conn:
            if update_dag_tag_func:
                await conn.execute(
                    """UPDATE bot.state_user_etl_bot SET dag_tag_func_state = current_state, current_state = $1 WHERE chat_id = $2""",
                    state, user_id)
            else:
                await conn.execute(
                    """UPDATE bot.state_user_etl_bot SET current_state = $1 WHERE chat_id = $2""",
                    state, user_id)
        self.dct_user_state[user_id] = state

    async def get_dag_tag_func_state(self, user_id: int) -> str:
        """
        :param user_id: chat_id пользователя

        :return: значение из столбца dag_tag_func_state, т.е. значение state
                 из какой функции было вызвано меню управления DAG
        """
        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval("""SELECT dag_tag_func_state 
                                    FROM bot.state_user_etl_bot
                                    WHERE chat_id = $1""", user_id)

    async def get_access_section(self, user_id: int, message_text: str) -> bool:
        """
        Провермяем есть указанные раздел в доступе у роли, которой наделен пользователь

        :param user_id: chat_id пользователя

        :param message_text: текст сообщения пользователя (наименование раздела в боте)

        :return: True or False
        """
        if len(message_text) == 0:
            return False
        await self.create_pool()
        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval("""SELECT EXISTS(SELECT 1 FROM bot.role_table 
                    WHERE role_id = (SELECT role_id FROM bot.user_tg_bot WHERE chat_id = $1) AND button_names LIKE('%' || $2 || '%'))""",
                                       user_id, message_text)

    async def get_pagination_status(self, user_id: int, status: str = 'default') -> int:
        """
        Возвращает пагинацию клавиатуры для указанного пользователя в зависимости от переданного статуса
        - default: пользователь на первой страницу
        - next: итерируется дальше по списку страниц
        - back: итерируется к началу по списку страниц

        :param user_id: chat_id пользователя

        :param status: положение, куда двигается пользователь или только начинает работу с клавитатурой
                       (default)

        :return: номер страницы
        """
        await self.create_pool()
        if status == 'default':
            async with self.pool_aeforecast.acquire() as conn:
                await conn.execute(
                    """UPDATE bot.pagination_status SET status_user_etl_bot = 0 WHERE chat_id = $1""", user_id)
                return 0
        elif status == 'next':
            async with self.pool_aeforecast.acquire() as conn:
                pagen = await conn.fetchval(
                    """SELECT status_user_etl_bot FROM bot.pagination_status WHERE chat_id = $1""", user_id)
                pagen += 1
                await conn.execute(
                    """UPDATE bot.pagination_status SET status_user_etl_bot = $2 WHERE chat_id = $1""", user_id,
                    pagen)
                return pagen
        elif status == 'back':
            async with self.pool_aeforecast.acquire() as conn:
                pagen = await conn.fetchval(
                    """SELECT status_user_etl_bot FROM bot.pagination_status WHERE chat_id = $1""", user_id)
                pagen = 0 if pagen == 0 else pagen - 1
                await conn.execute(
                    """UPDATE bot.pagination_status SET status_user_etl_bot = $2 WHERE chat_id = $1""", user_id,
                    pagen)
                return pagen

    async def check_timeout_operation(self, operation_name: str, field: str, timeout: int) -> bool:
        """
        Проверяем, прошел ли тайм-аут на переданной операции

        :param operation_name: наименоване операции (пример, Проверка_Сертификатов)

        :param field: какую часть из времени мы вытаскиваем (day, hour, minute и тд.)

        :param timeout: сколько должно было пройти времени с момента последнего запуска операции

        :return: True or False
        """

        async with self.pool_aeforecast.acquire() as conn:
            value = await conn.fetchval("""SELECT CASE 
                                        WHEN $2 = 'day' 
                                            THEN DATE_PART($2, NOW() - timeout_operation) >= $3
                                        WHEN $2 = 'hour'
                                            THEN (DATE_PART($2, NOW() - timeout_operation) + DATE_PART('day', NOW() - timeout_operation) * 24) >= $3
                                        WHEN $2 = 'minute'
                                            THEN (DATE_PART($2, NOW() - timeout_operation) + DATE_PART('hour', NOW() - timeout_operation) * 60 + DATE_PART('day', NOW() - timeout_operation) * 1440) >= $3
                                        END
                                        FROM bot.status_operation 
                                        WHERE operation_name = $1""", operation_name, field, timeout)
            return True if value is None else value

    @staticmethod
    async def trigger_dag(dag_id: str, json_conf: dict) -> list[str | int]:
        """
        Триггер DAG, id которого был передан

        :param dag_id: id DAG, который будет запускать в ручную

        :param json_conf: набор параметров для конкретного DAG

        :return: список с состоянием, удачно был запущен DAG или что-то пошло не так
        """

        head = {'Content-Type': 'application/json'}
        json_conf = {'conf': json_conf}
        response_json = requests.post(os.getenv('TRIGGER_URL_DAG').format(dag_id=dag_id),
                                      auth=(os.getenv('AIRFLOW_USER'), os.getenv('AIRFLOW_PASSWORD')), headers=head,
                                      json=json_conf).json()

        if 'status' in response_json:
            return [response_json['detail'], response_json['status']]
        else:
            return [response_json['run_type']]

    async def get_alert_description(self, user_id: int) -> list[dict]:
        """
        Пример возвращаемых данных:
            [{'alert_id': 2, 'type_alert': 'Обновление данных в БД', 'status_alert': True},
             {'alert_id': 1, 'type_alert': 'Ветеринарные сертификаты', 'status_alert': True}]

        :param user_id: chat_id пользователя

        :return: список словарей с необходимой информацией для каждого пользователя
        """
        await self.create_pool()
        async with self.pool_aeforecast.acquire() as conn:
            query_result = await conn.fetch("""SELECT alert_id, type_alert, status_alert 
                                          FROM bot.alert_status_etl_bot 
                                          JOIN bot.alert_type_table_etl_bot USING(alert_id)
                                          WHERE chat_id = $1""", user_id)

        return [dict(row) for row in query_result]

    async def alert_status_update(self, user_id: int, alert_id: int):
        """
        Меняет статус алерта на противположные:
        Пользователь был подписан на алерт(True), выбрал соответствующую кнопку и изменил свой статус на отписан(False)

        :param user_id: chat_id пользователя

        :param alert_id: идентификатор нужного алерта

        :return:
        """
        async with self.pool_aeforecast.acquire() as conn:
            await conn.execute(
                f"""UPDATE bot.alert_status_etl_bot 
                   SET status_alert = CASE WHEN status_alert = True THEN False ELSE True END 
                   WHERE alert_id = $1 AND chat_id = $2""", alert_id, user_id)

    async def get_missing_countries(self, bytes_path: bytes) -> str:
        """
        Находит страны, которые есть в ITC, но которых нет в БД в конкретном году

        :param bytes_path: скаченный фалй в telegram ботом

        :return: название файла, куда был сохранен результат
        """
        txt_bytes = io.BytesIO(bytes_path)

        # Данные из ITC
        df_itc = pd.read_table(txt_bytes).iloc[:, :13].rename(columns=lambda x: str(x).replace(' ', '_'))

        # Данные из БД
        df_countrys_in_db = pd.read_sql("""SELECT year, name_itc 
                                           FROM ss.sources_updates l
                                           LEFT JOIN (SELECT code, name_itc 
                                           FROM gf.ref_country_add 
                                           WHERE length(name_itc) > 0
                                           GROUP BY code, name_itc ) r ON l.reporter_code = r.code""",
                                        con=self.alch_pg, dtype={'year': str})

        # Итерируемся по колонкам датафрейма itc и просматриваем каждую страну
        # если такой нет в списке, до добавляем в словарь
        dct_need_country = {'year': [], 'country': []}
        for column in list(df_itc.columns)[1:]:
            list_country_by_year = list(df_countrys_in_db.query('year == @column').name_itc)
            for country in list(df_itc[df_itc[f'{column}'] == 1].Countries_and_Territories):
                try:
                    if country not in list_country_by_year and country not in dct_need_country['country']:
                        dct_need_country['year'].append(column)
                        dct_need_country['country'].append(country)
                except KeyError:
                    continue

        # Сохраняем результат в файл
        exlsx_df = pd.DataFrame(dct_need_country)
        with pd.ExcelWriter('new_country_itc.xlsx') as writer:
            exlsx_df.to_excel(writer, sheet_name='Перечень стран', index=False, na_rep='NaN')
            for column in exlsx_df:
                column_width = max(exlsx_df[column].astype(str).map(len).max(), len(column))
                col_idx = exlsx_df.columns.get_loc(column)
                writer.sheets['Перечень стран'].set_column(col_idx, col_idx, column_width)
            writer.sheets['Перечень стран'].set_default_row(30)
        return 'new_country_itc.xlsx'

    async def update_etl_choose_dag(self, user_id: int, choose_operation_name: str, dag_id: str):
        """
        Обновляем название DAG и его id в сервисной таблице

        :param user_id: chat_id пользователя

        :param choose_operation_name: название операции, как она записана в БД

        :param dag_id: id DAG в airflow

        :return:
        """
        async with self.pool_aeforecast.acquire() as conn:
            await conn.execute("""UPDATE bot.etl_choose 
                            SET choose_operation_name = $1,
                            dag_id = $2
                            WHERE chat_id = $3""", choose_operation_name, dag_id, user_id)

    async def update_etl_choose_variable(self, user_id: int, variable_name: typing.Optional[str] = None,
                                         variable_value: typing.Optional[str] = None):
        """
        Обновление параметров DAG в зависимости от переданных значений

        :param user_id: chat_id пользователя

        :param variable_name: необязательная переменная - имя меняемого параметра

        :param variable_value: необязательная переменная - новое значение выбранного параметра

        :return:
        """
        async with self.pool_aeforecast.acquire() as conn:
            # Обновляем имя параметра
            if variable_name:
                await conn.execute("""UPDATE bot.etl_choose 
                            SET variable_name = $1
                            WHERE chat_id = $2""", variable_name, user_id)
            # Обновляем значение параметра
            else:
                await conn.execute("""UPDATE bot.etl_choose 
                                            SET variable_value = $1
                                            WHERE chat_id = $2""", variable_value, user_id)

    async def get_choose_operation_name(self, user_id: int) -> str:
        """
        :param user_id: chat_id пользователя

        :return: выбранный пользователем DAG
        """
        await self.create_pool()

        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval("""SELECT choose_operation_name 
                                          FROM bot.etl_choose 
                                          WHERE chat_id = $1""", user_id)

    async def get_dag_id(self, user_id: int) -> str:
        """
        :param user_id: chat_id пользователя

        :return: id DAG, который указан в airflow
        """
        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval("""SELECT dag_id 
                                          FROM bot.etl_choose 
                                          WHERE chat_id = $1""", user_id)

    async def get_variables_dag(self, operation_name: str, user_id: int) -> dict:
        """
        :param operation_name: выбранный пользователем DAG

        :param user_id: chat_id пользователя

        :return: сформированный словарь параметров для запуска DAG
        """
        async with self.pool_aeforecast.acquire() as conn:
            await conn.set_type_codec(
                'json',
                encoder=json.dumps,
                decoder=json.loads,
                schema='pg_catalog'
            )

            dict_variables = await conn.fetchval("""SELECT variables_dag::json 
                                          FROM bot.status_operation 
                                          WHERE operation_name = $1""", operation_name)

        # Для отправки сообщения конкретному пользователю
        if 'chat_id' in dict_variables:
            dict_variables['chat_id'] = user_id
        return dict_variables

    async def get_timeout_operation_value(self, operation_name: str) -> dict:
        """
        :param operation_name: выбранный пользователем DAG

        :return: словарь с параметрами timeout триггера DAG
        """
        async with self.pool_aeforecast.acquire() as conn:
            await conn.set_type_codec(
                'json',
                encoder=json.dumps,
                decoder=json.loads,
                schema='pg_catalog'
            )

            return await conn.fetchval("""SELECT timeout_operation_value::json
                                          FROM bot.status_operation 
                                          WHERE operation_name = $1""", operation_name)

    async def get_list_variables_dag(self, operation_name: str) -> list:
        """
        :param operation_name: выбранный пользователем DAG

        :return: список параметов запуска DAG
        """
        async with self.pool_aeforecast.acquire() as conn:
            await conn.set_type_codec(
                'json',
                encoder=json.dumps,
                decoder=json.loads,
                schema='pg_catalog'
            )

            variables_dag = await conn.fetchval("""SELECT variables_dag::json
                                          FROM bot.status_operation 
                                          WHERE operation_name = $1""", operation_name)
        return [i for i in variables_dag]

    async def get_variable_name(self, user_id: int) -> str:
        """
        :param user_id: chat_id пользователя

        :return: значение параметра, который выбрал пользователь
        """
        await self.create_pool()

        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval("""SELECT variable_name 
                                          FROM bot.etl_choose 
                                          WHERE chat_id = $1""", user_id)

    async def get_variable_value(self, user_id: int) -> str:
        """
        :param user_id: chat_id пользователя

        :return: новое значение выбранного параметра
        """
        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval("""SELECT variable_value 
                                          FROM bot.etl_choose 
                                          WHERE chat_id = $1""", user_id)

    async def update_variables_dag(self, user_id: int, flag_update: str):
        """
        Функция обновляет значения выбранных параметров в зависимости от переданного flag_update

        :param user_id: chat_id пользователя

        :param flag_update: значение какого столбца мы обновляем (variables_dag/timeout_operation_value)

        :return:
        """
        variable_name = await self.get_variable_name(user_id)
        variable_value = await self.get_variable_value(user_id)
        operation_name = await self.get_choose_operation_name(user_id)
        json_path = [variable_name]

        # Тернарный оператор для обработки строкового значения
        # так как asyncpg требует преобразовать его к типу json
        json_value = variable_value if variable_value.isdigit() else json.dumps(variable_value)

        async with self.pool_aeforecast.acquire() as conn:
            if flag_update == 'variables_dag':
                await conn.execute("""UPDATE bot.status_operation
                                SET
                                 variables_dag = jsonb_set(
                                                            variables_dag,
                                                            $2,
                                                            $3
                                                           )
                                WHERE operation_name = $1""", operation_name, json_path, json_value)
            else:
                await conn.execute("""UPDATE bot.status_operation
                                                SET
                                                 timeout_operation_value = jsonb_set(
                                                                            timeout_operation_value,
                                                                            $2,
                                                                            $3
                                                                           )
                                                WHERE operation_name = $1""", operation_name, json_path, json_value)

    async def get_current_variable_value(self, user_id: int, name_columns: str) -> str | int:
        """
        :param user_id: chat_id пользователя

        :param name_columns: имя столбца откуда мы будем брать значение

        :return: текущее значение переменной
        """
        variable_name = await self.get_variable_name(user_id)
        operation_name = await self.get_choose_operation_name(user_id)

        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval(f"""SELECT {name_columns} ->> $1
                                       FROM bot.status_operation WHERE operation_name = $2""", variable_name,
                                       operation_name)

    async def get_current_twin_variable_value(self, user_id: int, name_columns: str, variable_name: str) -> str | int:
        """
        :param user_id: chat_id пользователя

        :param name_columns: имя столбца откуда мы будем брать значение

        :param variable_name: название парной переменной

        :return: текущее значение парной переменной
        """
        operation_name = await self.get_choose_operation_name(user_id)

        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval(f"""SELECT {name_columns} ->> $1
                                       FROM bot.status_operation WHERE operation_name = $2""", variable_name,
                                       operation_name)

    async def get_list_timeout_operation_value(self, operation_name: str) -> list:
        """
        :param operation_name: выбранный пользователем DAG

        :return: список параметов интервала запусков DAG
        """
        async with self.pool_aeforecast.acquire() as conn:
            await conn.set_type_codec(
                'json',
                encoder=json.dumps,
                decoder=json.loads,
                schema='pg_catalog'
            )

            timeout_operation_value_dag = await conn.fetchval("""SELECT timeout_operation_value::json
                                          FROM bot.status_operation 
                                          WHERE operation_name = $1""", operation_name)
        return [i for i in timeout_operation_value_dag]

    async def get_status_dag(self) -> str:
        """
        Функция проходится по каждому DAG и получает его текущий статус

        :return: итоговое сообщение со статусом всех DAG
        """
        need_datetime = (datetime.now() - timedelta(days=10)).isoformat() + "Z"
        message = ''
        head = {'Content-Type': 'application/json'}
        # Получаем список dag_id
        responce_dags = requests.get(os.getenv('URL_DAG_LIST'),
                                     auth=(os.getenv('AIRFLOW_USER'), os.getenv('AIRFLOW_PASSWORD')),
                                     headers=head).json()['dags']
        list_dag_id = [dag['dag_id'] for dag in responce_dags if dag['is_paused'] == False]

        # Составляем сообщение со статусами каждого dag в данный момент
        for dag_id in list_dag_id:
            try:
                rez = requests.get(os.getenv('TRIGGER_URL_DAG').format(dag_id=dag_id),
                                   auth=(os.getenv('AIRFLOW_USER'), os.getenv('AIRFLOW_PASSWORD')),
                                   headers=head,
                                   params={'start_date_gte': need_datetime}).json()['dag_runs'][-1]
                message += f"{self.dict_dag_state[rez['state']]} {dag_id}\n\n"
            except IndexError:
                logging.info(f'Пустой список по dag = {dag_id}')
        return message



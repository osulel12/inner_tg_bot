from telebot.async_telebot import AsyncTeleBot
from telebot import types
import dotenv
import os
import asyncio
import logging
from class_bd_work import Hepl_work_by_postgre
from create_keyboard import create_replay_markup, create_inline_markup
import aiofiles
from help_variable import get_need_value_list, element_on_page_value, get_twin_param_name

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

if os.path.exists('.env'):
    dotenv.load_dotenv('.env')

bot = AsyncTeleBot(os.getenv('TOKEN'), colorful_logs=True)

need_example_class = Hepl_work_by_postgre()


@bot.message_handler(commands=['start'])
async def start_command(message: types.Message):
    """
    Функция отвечающая за ввод команды start

    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id
    hello_text = await need_example_class.write_hello_func()

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, commands = start")

    # Проверка авторизации пользователя
    if await need_example_class.check_user(chat_id):
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, f'{hello_text}, выберите интересующий вас функционал 👇',
                               reply_markup=create_replay_markup('', 'main'))

    # Если пользователь не зарегистрирован
    else:
        await bot.send_message(chat_id, f'{hello_text}, Функционал не доступен')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'main')
async def main_bot_menue(message: types.Message):
    """
    Функция срабатывающая, когда пользователь находится в состоянии main

    :param message: сообщение пользователя
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    if await need_example_class.get_access_section(chat_id, message_text[
                                                            2:]) and message_text == '📩 Управление рассылкой':
        list_user_alert = await need_example_class.get_alert_description(chat_id)
        if len(list_user_alert) > 0:
            await need_example_class.update_state_user(chat_id, 'get_subscribe_user')
            pagination_status = await need_example_class.get_pagination_status(chat_id)
            await bot.send_message(chat_id, 'Выберите рассылку, статус которой хотите изменить 📨',
                                   reply_markup=create_inline_markup(state='get_subscribe_user',
                                                                     list_itemns=list_user_alert,
                                                                     pagen=pagination_status,
                                                                     element_on_page=7))
        else:
            await bot.send_message(chat_id,
                                   'Нет доступных рассылок',
                                   reply_markup=create_replay_markup('', 'main')
                                   )
    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🗺 Блок ITC':
        await need_example_class.update_state_user(chat_id, 'bloc_ITC')
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup(message_text, 'bloc_ITC'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '📺 Витрины данных':
        await need_example_class.update_state_user(chat_id, 'datamart_menue')
        await bot.send_message(chat_id, 'Выберите витрину данных 👇',
                               reply_markup=create_replay_markup('', 'datamart_menue'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🗂 Отчеты по справкам':
        await need_example_class.update_state_user(chat_id, 'certificates_menue')
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'certificates_menue'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '📡 Парсеры':
        await need_example_class.update_state_user(chat_id, 'Parser_menue')
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'Parser_menue'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🍃 Блок USDA':
        await need_example_class.update_state_user(chat_id, 'bloc_USDA')
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'bloc_USDA'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🌾 Блок FAO':
        await need_example_class.update_state_user(chat_id, 'bloc_FAO')
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'bloc_FAO'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🔬 Тестовые витрины данных':
        await need_example_class.update_state_user(chat_id, 'test_datamart_menue')
        await bot.send_message(chat_id, 'Выберите витрину данных 👇',
                               reply_markup=create_replay_markup('', 'test_datamart_menue'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🖥 Bash commands':
        await need_example_class.update_state_user(chat_id, 'bash_menue')
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'bash_menue'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == 'ℹ️ Статусы DAG`s':
        await bot.send_message(chat_id,
                               text=await need_example_class.get_status_dag(),
                               reply_markup=create_replay_markup('', 'main'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🐘 Postgres':
        await need_example_class.update_state_user(chat_id, 'postgres_menue')
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'postgres_menue'))
    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа')


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'get_subscribe_user')
async def get_subscribe_user(call: types.CallbackQuery):
    """
    Функция отрабатывает, когда состояние пользователя равно 'get_subscribe_user'
    Отвечает за управление алертами (подписка на них или отписка)

    :param call: callback с инлайновой клавиатуры
    :return:
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}")

    if await need_example_class.check_user(chat_id):
        # Навигация по доступным алертам
        if call_text in ['next', 'back']:
            pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text='Выберите рассылку, статус которой хотите изменить 📨',
                                        reply_markup=create_inline_markup(state='get_subscribe_user',
                                                                          list_itemns=await need_example_class.get_alert_description(
                                                                              chat_id),
                                                                          pagen=pagination_status,
                                                                          element_on_page=7))

        # Если пользователь выбирает изменение состояния алерта
        elif call_text.isdigit():
            btn_text = [j['text'] for i in call.message.json['reply_markup']['inline_keyboard'] for j in i if
                        j['callback_data'] == call_text][0]
            await bot.delete_message(chat_id, message_id)
            await need_example_class.update_state_user(chat_id, 'main')
            await need_example_class.alert_status_update(chat_id, int(call_text))
            await bot.send_message(chat_id,
                                   f"""Вы успешно {'<b>отписались</b> от рассылки' if '✅' in btn_text else '<b>подписались</b> на рассылку'}
                                            \n"<b>{btn_text[2:]}</b>\"""",
                                   reply_markup=create_replay_markup('', 'main'),
                                   parse_mode='html')

        # Если пользователь ничего не выбрал, то может без изменений перейти в главное меню
        elif call_text == 'main':
            await bot.delete_message(chat_id, message_id)
            await need_example_class.update_state_user(chat_id, 'main')
            await bot.send_message(chat_id, 'Вы вернулись в главное меню!',
                                   reply_markup=create_replay_markup('', 'main'))
    else:
        await bot.send_message(chat_id=chat_id, text='👻')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'bloc_ITC')
async def bloc_ITC(message: types.Message):
    """
    Функция отвечающая за функционал связанный с itc
    - 📖 Перечень отсутствующих стран: Пользователь загружает файл и если он проходит валидацию, то получает в ответ
                                       файл со странами, которые есть в itc, но нет в БД

    :param message: сообщение с клавиатуры

    :return:
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    if await need_example_class.get_access_section(chat_id, message_text[
                                                            2:]) and message_text == '📖 Перечень отсутствующих стран':
        await need_example_class.update_state_user(chat_id, 'itc_load_file')
        await bot.send_message(chat_id, 'Отправьте файл, который хотите загрузить',
                               reply_markup=create_replay_markup(message_text, 'bloc_ITC'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🚪 В главное меню':
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы вернулись в главное меню!',
                               reply_markup=create_replay_markup('', 'main'))
    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа')


@bot.message_handler(content_types='document',
                     func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'itc_load_file')
async def itc_load_file(message: types.Message):
    """
    Функция проверяет отправленный пользователем файл и отправляет отчет
    файл со странами, которые есть в itc, но нет в БД

    :param message: файл отправленный пользователем

    :return:
    """
    chat_id = message.chat.id

    # Информация о файле
    file_info = await bot.get_file(message.document.file_id)
    # Скачивайт файл в формате bytes
    bytes_file_download = await bot.download_file(file_info.file_path)

    # Получаем первую строку файла для валидации, предварительно декодировов его в нужной кодировке
    first_line_file = bytes_file_download.decode('utf-8').splitlines()[0]
    # Патер по которому идет валидация
    patern = 'Countries and Territories'

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {file_info}")

    if patern in first_line_file and await need_example_class.check_user(chat_id):
        # Обрабатываем файл и присылаем ответ - назване файла, куда сохранены данные
        file_name_from_user = await need_example_class.get_missing_countries(bytes_file_download)
        await need_example_class.update_state_user(chat_id, 'bloc_ITC')

        async with aiofiles.open(file_name_from_user, 'rb') as f_itc:
            await bot.send_document(chat_id, f_itc, caption=f'Новые данные в ITC')
        os.remove(file_name_from_user)

    # Если пользователь отправил не подходящий файл
    elif patern not in first_line_file and await need_example_class.check_user(chat_id):
        await need_example_class.update_state_user(chat_id, 'bloc_ITC')
        await bot.send_message(chat_id, 'Не корректный файл, попробуйте еще раз!',
                               reply_markup=create_replay_markup('', 'bloc_ITC'))
    # Если у пользователя нет доступа
    else:
        await bot.send_message(chat_id, '👻')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'datamart_menue')
async def datamart_menue(message: types.Message):
    """
    Функция реализующая меню, где собраны все DAG с тэгом DATAMART
    - "Витрина Регионов РФ": название витрины (как пример), которую мы выбираем и тд.

    :param message: сообщение с клавиатуры отправленное пользователем

    :return:
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    # Блок с витринами данных
    if await need_example_class.check_user(chat_id) and message_text == 'Витрина Регионов РФ':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'etl_region_update_datamart')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.check_user(chat_id) and message_text == 'Витрина Year_Data':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'etl_web_app_datamart')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.check_user(chat_id) and message_text == 'Витрина Балансов':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'etl_balance_datamart_update')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.check_user(chat_id) and message_text == 'Витрина Month_Data':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'etl_ref_table_update')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.check_user(chat_id) and message_text == 'Витрина World Trade':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'etl_world_trade_update')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.check_user(chat_id) and message_text == 'Статические справочники':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'update_ref_table_static')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.check_user(chat_id) and message_text == 'Витрина outer_tg_bot':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'update_outer_tg_bot_datamart')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🚪 В главное меню':
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы вернулись в главное меню!',
                               reply_markup=create_replay_markup('', 'main'))
    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'certificates_menue')
async def certificates_menue(message: types.Message):
    """
    Функция реализующая меню, где собраны все DAG с тэгом certificates
    - "Актуальные Даты Справок": название DAG (как пример), которое мы выбираем и тд.

    :param message: сообщение с клавиатуры отправленное пользователем

    :return:
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    # Блок с витринами данных
    if await need_example_class.check_user(chat_id) and message_text == 'Актуальные Даты Справок':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'update_certificates_date')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.check_user(chat_id) and message_text == 'Отчет-Количество Справок':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'count_certificates_in_folder')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.check_user(chat_id) and message_text == 'Новые справки с момента последнего запуска':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'checking_the_previous_day_certificates')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🚪 В главное меню':
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы вернулись в главное меню!',
                               reply_markup=create_replay_markup('', 'main'))
    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'Parser_menue')
async def Parser_menue(message: types.Message):
    """
    Функция реализующая меню, где собраны все DAG с тэгом Parser
    - "Парсинг MOEX": название DAG (как пример), которое мы выбираем и тд.

    :param message: сообщение с клавиатуры отправленное пользователем

    :return:
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    # Блок с витринами данных
    if await need_example_class.check_user(chat_id) and message_text == 'Парсинг MOEX':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'moex_etl_proces')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🚪 В главное меню':
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы вернулись в главное меню!',
                               reply_markup=create_replay_markup('', 'main'))
    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'bloc_USDA')
async def bloc_USDA(message: types.Message):
    """
    Функция реализующая меню, где собраны все DAG с тэгом USDA
    - "Обновление таблицы psd": название DAG (как пример), которое мы выбираем и тд.

    :param message: сообщение с клавиатуры отправленное пользователем

    :return:
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    # Блок с витринами данных
    if await need_example_class.check_user(chat_id) and message_text == 'Обновление таблицы psd':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'usda_update_table')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.check_user(chat_id) and message_text == 'Обновление таблицы reference_data':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'usda_update_reference_data')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🚪 В главное меню':
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы вернулись в главное меню!',
                               reply_markup=create_replay_markup('', 'main'))
    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'bloc_FAO')
async def bloc_FAO(message: types.Message):
    """
    Функция реализующая меню, где собраны все DAG с тэгом FAO
    - "Обновление таблиц FAO": название DAG (как пример), которое мы выбираем и тд.

    :param message: сообщение с клавиатуры отправленное пользователем

    :return:
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    # Блок с витринами данных
    if await need_example_class.check_user(chat_id) and message_text == 'Обновление таблиц FAO':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'fao_update_table')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🚪 В главное меню':
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы вернулись в главное меню!',
                               reply_markup=create_replay_markup('', 'main'))
    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'test_datamart_menue')
async def test_datamart_menue(message: types.Message):
    """
    Функция реализующая меню, где собраны все DAG с тэгом TEST
    - "Тест Витрина Year_Data": название DAG (как пример), которое мы выбираем и тд.

    :param message: сообщение с клавиатуры отправленное пользователем

    :return:
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    # Блок с витринами данных
    if await need_example_class.check_user(chat_id) and message_text == 'Тест Витрина Year_Data':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'test_web_app_datamart')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.check_user(chat_id) and message_text == 'Тест Витрина Month_Data':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'test_etl_ref_table_update')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.check_user(chat_id) and message_text == 'Тест Статические Справочники':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'test_update_ref_table_static')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.check_user(chat_id) and message_text == 'Тест Витрина Регионов РФ':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'test_etl_region_update_datamart')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🚪 В главное меню':
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы вернулись в главное меню!',
                               reply_markup=create_replay_markup('', 'main'))
    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'bash_menue')
async def bash_menue(message: types.Message):
    """
    Функция реализующая меню, где собраны все DAG с тэгом VM
    - "Перезапуск VM": название DAG (как пример), которое мы выбираем и тд.

    :param message: сообщение с клавиатуры отправленное пользователем

    :return:
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    # Блок с витринами данных
    if await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == 'Перезапуск VM':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'reboot_vm')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🚪 В главное меню':
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы вернулись в главное меню!',
                               reply_markup=create_replay_markup('', 'main'))
    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'postgres_menue')
async def postgres_menue(message: types.Message):
    """
    Функция реализующая меню, где собраны все DAG с тэгом POSTGRES
    - "Представление Годовых данных": название DAG (как пример), которое мы выбираем и тд.

    :param message: сообщение с клавиатуры отправленное пользователем

    :return:
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    # Блок с витринами данных
    if await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == 'Представление Годовых данных':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'sources_updates')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == 'Представление Месячных данных':
        await need_example_class.update_etl_choose_dag(chat_id, message_text, 'sources_updates_month')
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag', True)
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🚪 В главное меню':
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы вернулись в главное меню!',
                               reply_markup=create_replay_markup('', 'main'))
    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'interaction_with_dag')
async def interaction_with_dag(message: types.Message):
    """
    Функция реализует инструменты позволяющие запускать и редактировать параметры DAG

    - ▶️ Запуск DAG: запускаем обновление выбранного ранее DAG
    - 🔄 Редактирование параметров запуска: меню редактирования параметров необходимых при запуске DAG
    - ⏳ Редактирование параметров timeout: редактирование параметров timeout для интервала триггеров DAG

    :param message: сообщение с клавиатуры отправленное пользователем
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    # Функция запуска обновления
    if await need_example_class.check_user(chat_id) and message_text == '▶️ Запуск DAG':
        # Название dag, которое мы дали ему в БД
        operation_name = await need_example_class.get_choose_operation_name(chat_id)
        dag_id = await need_example_class.get_dag_id(chat_id)
        # Параметры запуска DAG
        dag_variables = await need_example_class.get_variables_dag(operation_name, chat_id)
        # Параметры интервала запуска для проверки
        timeout_value = await need_example_class.get_timeout_operation_value(operation_name)

        if await need_example_class.check_timeout_operation(operation_name, timeout_value['field'],
                                                            timeout_value['timeout']):
            # Триггерим DAG
            response_dag_run = await need_example_class.trigger_dag(dag_id, dag_variables)

            if 400 in response_dag_run:
                await bot.send_message(chat_id, response_dag_run[
                    0] + f'\n<b>{operation_name}</b> запуск не прошел. Попробуйте запустить позже')
            else:
                await bot.send_message(chat_id, f'▶️ Процесс <b>"{operation_name}"</b> запущен',
                                       parse_mode='html')
        else:
            await bot.send_message(chat_id, f'🕒 Время повторного запуска <b>"{operation_name}"</b> еще не пришло',
                                   parse_mode='html')

    # Меню редактирования параметров запуска
    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🔄 Редактирование параметров запуска':
        # Название dag, которое мы дали ему в БД
        operation_name = await need_example_class.get_choose_operation_name(chat_id)
        # Список параметров DAG
        list_variables_dag = await need_example_class.get_list_variables_dag(operation_name)

        if len(list_variables_dag) > 0:
            await need_example_class.update_state_user(chat_id, 'choos_value_dag')
            pagination_status = await need_example_class.get_pagination_status(chat_id)
            await bot.send_message(chat_id, 'Выберите параметр DAG для редактирования ⚙️',
                                   reply_markup=create_inline_markup(state='choos_value_dag',
                                                                     list_itemns=list_variables_dag,
                                                                     pagen=pagination_status,
                                                                     element_on_page=10))
        else:
            await bot.send_message(chat_id, f'Параметры запуска <b>"{operation_name}"</b> отсутствуют',
                                   parse_mode='html')

    # Меню редактирования параметров интервалов запуска DAG
    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '⏳ Редактирование параметров timeout':
        # Название dag, которое мы дали ему в БД
        operation_name = await need_example_class.get_choose_operation_name(chat_id)
        # Список параметров интервалов запуска DAG
        list_timeout_variables_dag = await need_example_class.get_list_timeout_operation_value(operation_name)

        if len(list_timeout_variables_dag) > 0:
            await need_example_class.update_state_user(chat_id, 'choos_timeout_dag')
            pagination_status = await need_example_class.get_pagination_status(chat_id)
            await bot.send_message(chat_id, 'Выберите параметр timeout DAG для редактирования ⚙️',
                                   reply_markup=create_inline_markup(state='choos_timeout_dag',
                                                                     list_itemns=list_timeout_variables_dag,
                                                                     pagen=pagination_status,
                                                                     element_on_page=10))
        else:
            await bot.send_message(chat_id, f'Параметры timeout <b>"{operation_name}"</b> отсутствуют')

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🔙 Назад':
        await need_example_class.update_state_user(chat_id, await need_example_class.get_dag_tag_func_state(chat_id))
        await bot.send_message(chat_id, 'Выберите витрину данных 👇',
                               reply_markup=create_replay_markup('', await need_example_class.get_dag_tag_func_state(
                                   chat_id)))
    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа')


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'choos_value_dag')
async def choos_value_dag(call: types.CallbackQuery):
    """
    Функция отвечает за меню выбора параметров запуска DAG

    :param call: callback с инлайн клавиатуры

    :return:
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Название dag, которое мы дали ему в БД
    operation_name = await need_example_class.get_choose_operation_name(chat_id)
    # Список параметров DAG
    list_variables_dag = await need_example_class.get_list_variables_dag(operation_name)

    logging.info(
        f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}, operation_name = {operation_name}")

    # Функционал итерирования по списку параметров
    if call_text in ['next', 'back'] and await need_example_class.check_user(chat_id):
        pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text='Выберите параметр DAG для редактирования ⚙️',
                                    parse_mode="markdown",
                                    reply_markup=create_inline_markup(state='choos_value_dag',
                                                                      list_itemns=list_variables_dag,
                                                                      pagen=pagination_status,
                                                                      element_on_page=10))

    # Если пользователь решил вернуться в меню работы с dag state = 'interaction_with_dag'
    elif call_text == 'back_menue' and await need_example_class.check_user(chat_id):
        await bot.delete_message(chat_id, message_id)
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag')
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    # Если пользователь выбрал один из параметров
    elif call_text in list_variables_dag and await need_example_class.check_user(chat_id):
        # Записываем название выбранного параметр в БД
        await need_example_class.update_etl_choose_variable(user_id=chat_id, variable_name=call_text)
        await need_example_class.update_state_user(chat_id, 'update_new_value_dag')

        # Для Dag у которого параметры зависят друг от друга
        # К примеру дата начала и дата окончания интервала
        if operation_name in ['Отчет-Количество Справок']:
            current_value_twin = await need_example_class.get_current_twin_variable_value(chat_id, 'variables_dag',
                                                                                          get_twin_param_name(
                                                                                              operation_name,
                                                                                              call_text))
        else:
            current_value_twin = None

        # Получаем текущее значение параметра
        current_variable_value = await need_example_class.get_current_variable_value(chat_id, 'variables_dag')
        pagination_status = await need_example_class.get_pagination_status(chat_id)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=f'Текущее значение <b>{call_text}</b> = <b>{current_variable_value}</b> \nВыберите новое значение:',
                                    parse_mode="html",
                                    reply_markup=create_inline_markup(state='update_new_value_dag',
                                                                      # Возвращаем список доступных значений параметров из функции
                                                                      list_itemns=get_need_value_list(call_text,
                                                                                                      current_variable_value,
                                                                                                      current_value_twin),
                                                                      pagen=pagination_status,
                                                                      # Возвращаем значение пагинации для каждого из параметров
                                                                      element_on_page=element_on_page_value[call_text]))


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'update_new_value_dag')
async def update_new_value_dag(call: types.CallbackQuery):
    """
    Функция отвечает за обновление значения выбранного параметра запуска DAG

    :param call: callback с инлайн клавиатуры - новое значение параметра

    :return:
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Параметр, который мы изменяем
    variable_name = await need_example_class.get_variable_name(chat_id)
    # Текущее значение параметра
    current_variable_value = await need_example_class.get_current_variable_value(chat_id, 'variables_dag')
    # Название dag, которое мы дали ему в БД
    operation_name = await need_example_class.get_choose_operation_name(chat_id)

    # Для Dag у которого параметры зависят друг от друга
    # К примеру дата начала и дата окончания интервала
    if variable_name in ['date_end', 'date_start']:
        current_value_twin = await need_example_class.get_current_twin_variable_value(chat_id, 'variables_dag',
                                                                                      get_twin_param_name(operation_name, variable_name))
    else:
        current_value_twin = None

    logging.info(
        f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}, variable_name = {variable_name}")

    # Функционал итерирования по списку доступных значений
    if call_text in ['next', 'back'] and await need_example_class.check_user(chat_id):
        pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=f'Текущее значение <b>{variable_name}</b> = <b>{current_variable_value}</b> \nВыберите новое значение:',
                                    parse_mode="html",
                                    reply_markup=create_inline_markup(state='update_new_value_dag',
                                                                      # Возвращаем список доступных значений параметров из функции
                                                                      list_itemns=get_need_value_list(variable_name,
                                                                                                      current_variable_value,
                                                                                                      current_value_twin),
                                                                      pagen=pagination_status,
                                                                      # Возвращаем значение пагинации для каждого из параметров
                                                                      element_on_page=element_on_page_value[
                                                                          variable_name]))

    # Если пользователь решил вернуться в предыдущее меню state = 'choos_value_dag'
    elif call_text == 'back_menue' and await need_example_class.check_user(chat_id):
        await need_example_class.update_state_user(chat_id, 'choos_value_dag')
        operation_name = await need_example_class.get_choose_operation_name(chat_id)
        list_variables_dag = await need_example_class.get_list_variables_dag(operation_name)
        pagination_status = await need_example_class.get_pagination_status(chat_id)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text='Выберите параметр DAG для редактирования ⚙️',
                                    parse_mode="markdown",
                                    reply_markup=create_inline_markup(state='choos_value_dag',
                                                                      list_itemns=list_variables_dag,
                                                                      pagen=pagination_status,
                                                                      element_on_page=10))

    # Если пользователь выбрал новое значение параметра
    elif call_text in get_need_value_list(variable_name, current_variable_value,
                                          current_value_twin) and await need_example_class.check_user(chat_id):
        await bot.delete_message(chat_id, message_id)
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag')

        # Записываем значение параметра в сервисную таблицу
        await need_example_class.update_etl_choose_variable(user_id=chat_id, variable_value=call_text)
        # Обновляем значение параметра в основной таблице
        await need_example_class.update_variables_dag(chat_id, 'variables_dag')

        await bot.send_message(chat_id,
                               f'Новое значение параметра <b>{variable_name}</b> = <b>{call_text}</b> \nВыберите действие 👇',
                               parse_mode='html',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'choos_timeout_dag')
async def choos_timeout_dag(call: types.CallbackQuery):
    """
    Функция отвечает за меню выбора параметров интервалов запуска DAG

    :param call: callback с инлайн клавиатуры

    :return:
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Название dag, которое мы дали ему в БД
    operation_name = await need_example_class.get_choose_operation_name(chat_id)
    # Список параметров интервалов запуска DAG
    list_timeout_variables_dag = await need_example_class.get_list_timeout_operation_value(operation_name)

    logging.info(
        f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}, operation_name = {operation_name}")

    # Функционал итерирования по списку параметров
    if call_text in ['next', 'back'] and await need_example_class.check_user(chat_id):
        pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text='Выберите параметр timeout DAG для редактирования ⚙️',
                                    parse_mode="markdown",
                                    reply_markup=create_inline_markup(state='choos_timeout_dag',
                                                                      list_itemns=list_timeout_variables_dag,
                                                                      pagen=pagination_status,
                                                                      element_on_page=10))

    # Если пользователь решил вернуться в меню работы с dag state = 'interaction_with_dag'
    elif call_text == 'back_menue' and await need_example_class.check_user(chat_id):
        await bot.delete_message(chat_id, message_id)
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag')
        await bot.send_message(chat_id, 'Выберите действие 👇',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))

    # Получаем текущее значение параметра
    elif call_text in list_timeout_variables_dag and await need_example_class.check_user(chat_id):
        # Записываем название выбранного параметр в БД
        await need_example_class.update_etl_choose_variable(user_id=chat_id, variable_name=call_text)
        await need_example_class.update_state_user(chat_id, 'update_new_timeout_value')

        # Получаем текущее значение параметра
        current_variable_value = await need_example_class.get_current_variable_value(chat_id, 'timeout_operation_value')
        pagination_status = await need_example_class.get_pagination_status(chat_id)

        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=f'Текущее значение <b>{call_text}</b> = <b>{current_variable_value}</b> \nВыберите новое значение:',
                                    parse_mode="html",
                                    reply_markup=create_inline_markup(state='update_new_timeout_value',
                                                                      # Возвращаем список доступных значений параметров из функции
                                                                      list_itemns=get_need_value_list(call_text,
                                                                                                      current_variable_value),
                                                                      pagen=pagination_status,
                                                                      # Возвращаем значение пагинации для каждого из параметров
                                                                      element_on_page=element_on_page_value[call_text]))


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'update_new_timeout_value')
async def update_new_timeout_value(call: types.CallbackQuery):
    """
    Функция отвечает за обновление значения выбранного параметра интервала запуска DAG

    :param call: callback с инлайн клавиатуры - новое значение параметра

    :return:
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Параметр, который мы изменяем
    variable_name = await need_example_class.get_variable_name(chat_id)
    # Текущее значение параметра
    current_variable_value = await need_example_class.get_current_variable_value(chat_id, 'timeout_operation_value')

    logging.info(
        f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}, variable_name = {variable_name}")

    # Функционал итерирования по списку доступных значений
    if call_text in ['next', 'back'] and await need_example_class.check_user(chat_id):
        pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=f'Текущее значение <b>{variable_name}</b> = <b>{current_variable_value}</b> \nВыберите новое значение:',
                                    parse_mode="html",
                                    reply_markup=create_inline_markup(state='update_new_timeout_value',
                                                                      # Возвращаем список доступных значений параметров из функции
                                                                      list_itemns=get_need_value_list(variable_name,
                                                                                                      current_variable_value),
                                                                      pagen=pagination_status,
                                                                      # Возвращаем значение пагинации для каждого из параметров
                                                                      element_on_page=element_on_page_value[
                                                                          variable_name]))

    # Если пользователь решил вернуться в предыдущее меню state = 'choos_timeout_dag'
    elif call_text == 'back_menue' and await need_example_class.check_user(chat_id):
        await need_example_class.update_state_user(chat_id, 'choos_timeout_dag')
        operation_name = await need_example_class.get_choose_operation_name(chat_id)
        list_timeout_variables_dag = await need_example_class.get_list_timeout_operation_value(operation_name)
        pagination_status = await need_example_class.get_pagination_status(chat_id)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text='Выберите параметр timeout DAG для редактирования ⚙️',
                                    parse_mode="markdown",
                                    reply_markup=create_inline_markup(state='choos_timeout_dag',
                                                                      list_itemns=list_timeout_variables_dag,
                                                                      pagen=pagination_status,
                                                                      element_on_page=10))

    # Если пользователь выбрал новое значение параметра
    elif call_text in get_need_value_list(variable_name,
                                          current_variable_value) and await need_example_class.check_user(chat_id):
        await bot.delete_message(chat_id, message_id)
        await need_example_class.update_state_user(chat_id, 'interaction_with_dag')

        # Записываем значение параметра в сервисную таблицу
        await need_example_class.update_etl_choose_variable(user_id=chat_id, variable_value=call_text)
        # Обновляем значение параметра в основной таблице
        await need_example_class.update_variables_dag(chat_id, 'timeout_operation_value')

        await bot.send_message(chat_id,
                               f'Новое значение параметра <b>{variable_name}</b> = <b>{call_text}</b> \nВыберите действие 👇',
                               parse_mode='html',
                               reply_markup=create_replay_markup('', 'interaction_with_dag'))


if __name__ == '__main__':
    asyncio.run(bot.infinity_polling())

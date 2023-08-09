import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from contextlib import closing
from datetime import datetime
import io
import time
import valutes_project_settings as prset
import matplotlib
matplotlib.use('Agg')

def get_data_from_db(button_first: str, button_second: str):
    '''
    по нажатию кнопок получаем таблицу из базы по запросу
    запихиваем табилцу в pandas.DataFrame
    '''

    def format_data(df, button_first: str = button_first):
        '''
        форматируем таблицу по выбраной валюте
        соотносим валюты
        '''

        table_columns_names = [
            'dt',
            'rate',
            'name_first_val',
            'name_second_val'
        ]

        # если соотносим USD с иной валютой
        if 'USD' == button_first.split('/')[0]:
            df = df.drop(columns=['id_source', 'id_val']).rename(columns={ \
                'name_source': table_columns_names[2], 'name_val': table_columns_names[3]})
            df = df.reindex(columns=table_columns_names)
        # если соотносим иную валюту с USD
        elif 'USD' == button_first.split('/')[1]:
            df = df.drop(columns=['id_source', 'id_val']).rename(columns={ \
                'name_source': table_columns_names[3], 'name_val': table_columns_names[2]})
            df.rate = 1 / df.rate
            df = df.reindex(columns=table_columns_names)
        # если в соотношение валют не встречается USD
        else:
            # преобразуем таблицу валюты, которую будем соотносить
            df_first_val = df.query(f"name_val == '{button_first.split('/')[0]}'")

            col_df_first_val = []
            for i in df_first_val.columns:
                if '_' + button_first.split('/')[0] not in i:
                    col_df_first_val.append(i + '_' + button_first.split('/')[0])
            df_first_val.columns = col_df_first_val
            # преобразуем таблицу валюты, к которой будем соотносить
            df_second_val = df.query(f"name_val == '{button_first.split('/')[1]}'")

            col_df_second_val = []
            for i in df_second_val.columns:
                if '_' + button_first.split('/')[1] not in i:
                    col_df_second_val.append(i + '_' + button_first.split('/')[1])
            df_second_val.columns = col_df_second_val

            # сбрасываем индексы
            df_first_val = df_first_val.reset_index().drop(columns='index')
            df_second_val = df_second_val.reset_index().drop(columns='index')

            # объединяем таблицы по дате
            df = df_second_val.merge(df_first_val, \
                                     left_on=df_second_val.columns[0], right_on=df_first_val.columns[0], how='inner')
            # добавляем столбцы с вычисленной разницей между валютами
            df.insert(loc=1, column=table_columns_names[1],
                      value=df[df.columns[1]] / df[df.columns[len(df_first_val.columns) + 1]])
            df.insert(loc=2, column=table_columns_names[2], value=df_first_val[df_first_val.columns[-1]])
            df.insert(loc=3, column=table_columns_names[3], value=df_second_val[df_second_val.columns[-1]])
            # удаляем ненужные столбцы
            df = df.drop(columns=df.columns[4:])
            # переименовываем столбцы
            df.columns = table_columns_names

        return df

    # параметры для отбора из БД
    params = str(button_first + '/-' + button_second).split('/')

    with closing(sqlite3.connect('main_db.db')) as connection:
        with closing(connection.cursor()) as cursor:
            df = pd.read_sql_query("""
            SELECT datetime(r.timestamp,'unixepoch') as dt,
            r.rate,r.id_source,cn_source.name as name_source,cn.id as id_val,cn.name as name_val
            FROM rates as r, currency_name as cn, currency_name as cn_source
            WHERE r.id_currency_name = cn.id AND r.id_source = cn_source.id AND cn.name in (?,?)

            AND dt between datetime('now',?) and datetime('now')

            """, params=params, con=connection)

    df = format_data(df)

    return df


def draw_plot(df, x_count, y_count, button_first: str, button_second: str, \
              show_min_max_plot: bool, \
              night_theme_on: bool) -> bytes:
    # устанавливаем формат даты, отображающийся на графике
    if int(str(pd.to_datetime(df.dt).max() - pd.to_datetime(df.dt).min()).split(' ')[0]) >= (x_count - 1):
        dt_format = '%d.%m'
    else:
        dt_format = '%d.%m\n%H:%M'

    fig = plt.figure(figsize=(15, 9), dpi=200,layout='constrained')
    axes = plt.axes()
    x = pd.to_datetime(df.dt)
    y = round(df.rate, 2)

    def get_axis_X(df=df, x_count=x_count, dt_format=dt_format) -> tuple:
        # подготовка шкалы и подписей для оси X

        def get_xticks_new(df=df, x_count=x_count) -> list:
            # получение данных шкалы xticks

            def round_time(timestamp: int):
                # функция округления до часа
                hour_in_seconds = 60 * 60
                half_hour_in_seconds = 60 * 30
                if timestamp % hour_in_seconds > half_hour_in_seconds:
                    return ((timestamp // hour_in_seconds) + 1) * hour_in_seconds
                else:
                    return (timestamp // hour_in_seconds) * hour_in_seconds

            xticks_timestamp = []
            # конвертим все даты в timestamp
            dt_timestamp = []
            for i in df.dt:
                d = datetime.strptime(i, "%Y-%m-%d %H:%M:%S")
                ts = round(time.mktime(d.timetuple()))
                dt_timestamp.append(ts)
            # временной шаг между датами на шкале X
            step = round_time(round((round_time(max(dt_timestamp)) - round_time(min(dt_timestamp))) / (x_count - 1)))

            # собираем список с timestamp и округляем до часов
            for i in range(x_count):
                xticks_timestamp.append(round_time(min(dt_timestamp)) + i * step)
            # xticks_timestamp.append(round_time(max(dt_timestamp)))

            xticks_timestamp.sort()

            # Возвращаем прежний формат
            xticks = []
            for i in xticks_timestamp:
                xticks.append(datetime.fromtimestamp(i))
            return xticks

        xticks = get_xticks_new(df, x_count)
        xlabels = []
        for i in xticks:
            xlabels.append(i.strftime(dt_format))
        return (xticks, xlabels)

    def get_axis_Y(df=df, y_count=y_count) -> tuple:
        # подготовка шкалы и подписей для оси Y

        yticks = []
        value_min = round(df.rate.min(), 2)

        step = round(round(df.rate.max(), 2) - round(df.rate.min(), 2), 2) / (y_count - 1)
        for i in range(y_count):
            yticks.append(round(value_min + i * step, 2))
        ylabels = yticks

        return (yticks, ylabels)

    def show_min_max_plot(activate=show_min_max_plot, x=x, y=y, night_theme_on=night_theme_on):
        if activate:
            if night_theme_on == False:
                color_line = 'blue'
                facecolor_legend = None
                labelcolor_legend = None
            else:
                color_line = '#26ff00'  # ядовито зелёный
                facecolor_legend = '#303030'
                labelcolor_legend = 'white'
            # отображает минимальные и максимальные значения
            plt.axhline(y.min()).set(linestyle='-.', color=color_line, label='min value', linewidth=0.7)
            plt.axhline(y.max()).set(linestyle='-', color=color_line, label='max value', linewidth=0.7)
            plt.axvline(x[y.idxmin()]).set(linestyle='--', color=color_line, linewidth=1)
            plt.axvline(x[y.idxmax()]).set(linestyle='-', color=color_line, linewidth=1)
            plt.legend(facecolor=facecolor_legend, labelcolor=labelcolor_legend)
        else:
            pass

    def night_theme(activate=night_theme_on, button_first=button_first, button_second=button_second):
        if activate:
            plt.tick_params(colors='white')
            fig.set_facecolor('#1b191a')
            axes.set_facecolor('#1b191a')
            plt.grid(color='#706b6b')
            plt.title(button_first, color='white')
            plt.xlabel(button_second, color='white').set_fontweight('bold')
        else:
            pass

    # рисуем график
    if night_theme_on == True:
        plt.plot(x, y, color='red', linewidth=2)
    else:
        plt.plot(x, y, color='red')
    plt.title(button_first)
    plt.xlabel(button_second).set_fontweight('bold')

    x_ticks, x_label = get_axis_X(df, x_count, dt_format)
    y_ticks, y_label = get_axis_Y(df, y_count)
    plt.xticks(ticks=x_ticks, labels=x_label)
    plt.yticks(ticks=y_ticks, labels=y_label)

    # выключает каждую вторую подпись по оси X
    xax = axes.xaxis
    counter = 0
    for label in xax.get_ticklabels():
        if counter % 2 != 0:
            label.set_visible(False)
        counter += 1


    show_min_max_plot()
    plt.grid()
    night_theme()

    # получение данных картинки
    with io.BytesIO() as buf:
        plt.savefig(buf)
        buf.seek(0)
        pic = buf.read()
        buf.close()

    #plt.savefig('file_name.png')
    #plt.show()

    plt.close()
    return pic


def send_to_tg(bot, chat_id: str, caption: str = None, pic: bytes = None):
    bot = bot
    if pic is not None:
        bot.send_photo(chat_id=chat_id, photo=pic, caption=caption)
    else:
        bot.send_message(chat_id=chat_id, text=caption)


def get_analys_text(df, button_first: str, button_second: str) -> str:
    # Возвращает краткий анализ графика в текстовом виде для отправки в подпись к графику
    x = pd.to_datetime(df.dt)
    y = round(df.rate, 2)

    return 'valutes {}\nperiod {}\n{} | {} - minimum \n{} | {} - maximum \n{} | {} - last value'.format( \
        button_first, button_second, y.min(), x[y.idxmin()], y.max(), x[y.idxmax()], y.tail(1).min(), x.tail(1).min())

def drawing_to_tg(message, bot, valutes, \
                  period, \
                  show_min_max_plot, \
                  night_theme):

    #получаем DataFrame
    df = get_data_from_db(button_first=valutes ,button_second=period)
    # проверка на пустой датафрейм
    if (df.empty):
        print('DataFrame is Empty!')
        send_to_tg(chat_id=message.chat.id,bot=bot,caption= 'valutes {}\nperiod {}\nDataFrame is Empty!'. \
                   format(valutes,period))
    else:
        # получаем картинку
        picture = draw_plot(df=df, x_count=prset.params_default['x_count'], y_count=prset.params_default['y_count'], \
                            show_min_max_plot=show_min_max_plot, \
                            night_theme_on=night_theme, \
                            button_first=valutes, \
                            button_second=period)
        # получаем подпись к картинке
        caption = get_analys_text(df,valutes,period)
        # отправляем
        send_to_tg(pic=picture,bot=bot,chat_id=message.chat.id,caption=caption)

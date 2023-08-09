buttons_first_valutes: tuple = (
    'GEL/RUB',
    'USD/GEL',
    'USD/RUB',
    'EUR/GEL',
    'EUR/RUB'
)

buttons_second_times: tuple = (
    '1 day',
    '7 day',
    '14 day',
    '1 month',
    '3 month',
    '6 month',
    '1 year'
)

params_default:dict = {'button_valutes':buttons_first_valutes[0], \
              'button_period':buttons_second_times[2], \
              'night_theme':False, \
              'show_min_max':True, \
              'x_count':24, \
              'y_count':10}

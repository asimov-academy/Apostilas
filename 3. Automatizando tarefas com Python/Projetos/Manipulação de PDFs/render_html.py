from flask import Flask, render_template
app = Flask(__name__)

import calendar

full_months = ["Janeiro", 
            "Fevereiro", 
            "Março", 
            "Abril", 
            "Maio", 
            "Junho", 
            "Julho", 
            "Agosto", 
            "Setembro", 
            "Outubro", 
            "Novembro",
            "Dezembro"]
s_months = [i[:3] for i in full_months]
wk_list = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", 
            "Sexta-feira", "Sábado", "Domingo"]

sem_day = [i[0] for i in wk_list]
hours = ["{:02d}:00".format(i) for i in range(7, 22)]

def get_calendar(mm, yy):
    cal = calendar.month(yy, mm).split("\n")[2:-1]

    pos_primeiro_dia = (cal[0].find('1'))
    dict_position_to_days = {i*3 + 1: i for i in range(7)}
    first_day = dict_position_to_days[pos_primeiro_dia]
    last_day = int(cal[-1].split(" ")[-1])

    day_check = 0
    list_cal = [[]]
    pair_day = []
    day = 1
    i =0
    while day < last_day + 1:
        if day_check == 0 and i < first_day:
            list_cal[-1].append({'day': ' '})
            i += 1
        else:
            day_check = 1
            pair_day += [{
                'wkd': sem_day[len(list_cal[-1])], 
                "day": str(day),
                'full_wkd': wk_list[len(list_cal[-1])], 
                'month': mm
                }]
            list_cal[-1].append({'day': day, 'link': '{}-{}'.format(day, mm)})
            day += 1

        if len(list_cal[-1]) >= 7:
            list_cal.append([])
    
    return [s_months[mm - 1], list_cal, pair_day, sem_day]


def get_full_year():    
    full_year = []
    for i in range(1, 13):
        full_year += get_calendar(i, 2022)[2]
    
    first_day = full_year[0] 
    wk = 1
    for day in full_year:
        if day["full_wkd"] == 'Segunda-feira':
            first_day = day.copy()
            wk += 1
        day["week"] = "{}-{}".format(first_day["day"], first_day["month"])
        day["week_n"] = wk
    return full_year


def render_calendar(year):       
    template = render_template('spreads/yearly.html', main_m="{}".format(year),
        cal=[get_calendar(i, year) for i in range(1, 13)], zip=zip)
    return template


def render_days():
    template_out = ''
    full_days = get_full_year()

    dict_week_data = {i: [] for i in list(set([i["week"] for i in full_days]))}
    for dict_day in full_days[:]:
        info_week_day = [('{:02d}'.format(int(dict_day["day"])), dict_day["full_wkd"][:3].upper(), "{}-{}".format(dict_day['day'], dict_day['month']))]
        dict_week_data[dict_day["week"]] += info_week_day
    
    dict_day = full_days[0]
    for dict_day in full_days[:]: 
        day = dict_day["day"]
        month = dict_day["month"]
                
        month_days = [i for i in full_days if i["month"] == dict_day['month']]
        template_out += render_template('spreads/daily.html', dia='{:02d}'.format(int(day)),
        wkd= dict_day["full_wkd"], month=month, anchor='{}-{}'.format(day, month), m_days=month_days,
        main_m=full_months[month-1], hours=hours, zip=zip, week=dict_day["week"])
    return template_out

# ==================
# Specif Renders
def render_rodrigo(year):
    template_out = ''
    template_out += render_calendar(year)
    template_out += render_days()

    return template_out


# ========================
# Auxiliar functions
@app.route('/')
def home():
    year = 2022

    with open('planner_template.html', 'w') as f:
        del_pattern = open('remove_pattern.html').read()
        template_out = render_rodrigo(year)
        template_out = template_out.replace(del_pattern, '')
        f.write(template_out)    

    return template_out

if __name__ == '__main__':
    # DEBUG MODE: FLASK_APP=render_html.py FLASK_ENV=development flask run
   app.run()

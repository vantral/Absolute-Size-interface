from flask import Flask, render_template, request
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)


# Читаем ключи из файла
scope = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    '/home/sizematters/mysite/creds.json', scope
)

gc = gspread.authorize(credentials)

spreadsheet = gc.open('Rita\'s new results')
worksheet = spreadsheet.sheet1


@app.route('/')
def main_page():
    data = get_as_dataframe(worksheet)

    data = data.dropna(how='all')

    if data.empty:
        first = 1
    else:
        big = data.type.to_list().count('big')
        small = data.type.to_list().count('small')
        if big > small:
            first = 0
        else:
            first = 1
    if first:
        link = 'big'
    else:
        link = 'small'
    return(render_template('index.html', link=link, stop=0, type=link))


@app.route('/small', methods=['GET'])
def small():
    data = get_as_dataframe(worksheet)
    data = data.dropna(how='all')
    if data.empty:
        person_id = 0
    else:
        person_id = len(data)

    tp = request.args.get('type')
    gender = request.args.get('gender')
    language = request.args.get('language')
    duration = 0

    if request.args.get('age'):
        age = request.args.get('age')
    else:
        age = 0
    if request.args.get('stop') == '1':
        person_id = request.args.get('id')
        big = request.args.get('big')
        duration = int(request.args.get('duration_big'))
        link = 'finish'
        stop = 0
        table = get_as_dataframe(worksheet).dropna(how='all').iloc[:,:9]
        print(table[table['id'] == int(person_id)])
        table[table['id'] == int(person_id)] = [person_id, age, language, tp, big, '', duration / 1000, 0, gender]
        set_with_dataframe(worksheet, table)
    else:
        big = ''
        link = 'big'
        stop = 1
        data = {
            'id': person_id,
            'age': age,
            'language': language,
            'type': tp,
            'big': big,
            'small': '',
            'gender': gender
        }
        print(data)
        df = pd.DataFrame([data])
        table = get_as_dataframe(worksheet).dropna(how='all').iloc[:,:9]
        df = pd.concat([table, df])
        set_with_dataframe(worksheet, df)

    return(render_template(
        'small.html',
        link=link,
        stop=stop,
        age=age,
        big=big,
        type=tp,
        person_id=person_id,
        duration_big=duration,
        duration_small=request.args.get('duration_small'),
        gender=gender,
        language=language
    ))

@app.route('/big')
def big():
    data = get_as_dataframe(worksheet)
    data = data.dropna(how='all')
    if data.empty:
        person_id = 0
    else:
        person_id = len(data)

    tp = request.args.get('type')
    gender = request.args.get('gender')
    language = request.args.get('language')
    duration = 0

    if request.args.get('age'):
        age = request.args.get('age')
    else:
        age = 0
    if request.args.get('stop') == '1':
        person_id = request.args.get('id')
        small = request.args.get('small')
        duration = int(request.args.get('duration_small'))
        link = 'finish'
        stop = 0
        table = get_as_dataframe(worksheet).dropna(how='all').iloc[:,:9]
        table[table['id'] == int(person_id)] = [person_id, age, language, tp, '', small, 0, duration / 1000, gender]
        set_with_dataframe(worksheet, table)
    else:
        small = ''
        link = 'small'
        stop = 1
        data = {
            'id': person_id,
            'age': age,
            'language': language,
            'type': tp,
            'big': '',
            'small': small,
            'gender': gender
        }
        df = pd.DataFrame([data])
        table = get_as_dataframe(worksheet).dropna(how='all').iloc[:,:9]
        df = pd.concat([table, df])
        set_with_dataframe(worksheet, df)
    return(render_template(
        'big.html', link=link, stop=stop, age=age,
        small=small, type=tp, person_id=person_id,
        duration_small=duration, duration_big=request.args.get('duration_big'),
        gender=gender, language=language))


@app.route('/finish')
def finish():
    # data = {
    #     'age': request.args.get('age'),
    #     'type': request.args.get('type'),
    #     'big': request.args.get('big'),
    #     'small': request.args.get('small')
    # }
    table = get_as_dataframe(worksheet).dropna(how='all').iloc[:,:9]
    duration_big = request.args.get('duration_big')
    duration_small = request.args.get('duration_small')


    table[table['id'] == int(request.args.get('id'))] = [
        request.args.get('id'),
        request.args.get('age'),
        request.args.get('language'),
        request.args.get('type'),
        request.args.get('big'),
        request.args.get('small'),
        duration_big if isinstance(duration_big, float) else int(duration_big) / 1000,
        duration_small if isinstance(duration_small, float) else int(duration_small) / 1000,
        request.args.get('gender')]
    set_with_dataframe(worksheet, table)

    # df = pd.DataFrame([data])
    # table = get_as_dataframe(worksheet).dropna(how='all').iloc[:,:7]
    # df = pd.concat([table, df])
    # set_with_dataframe(worksheet, df)
    return(render_template('finish.html'))

if __name__ == '__main__':
    app.run()
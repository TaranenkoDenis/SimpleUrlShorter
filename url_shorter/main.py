from flask import Flask, request, render_template, redirect
from math import floor
from sqlite3 import OperationalError
import string
import sqlite3

try:
    from urllib.parse import urlparse  # Python 3
    str_encode = str.encode
except ImportError:
    from urlparse import urlparse  # Python 2
    str_encode = str
try:
    from string import ascii_lowercase  # Python 3
    from string import ascii_uppercase
except ImportError:
    from string import lowercase as ascii_lowercase  # Python 2
    from string import uppercase as ascii_uppercase
import base64

# Assuming urls.db is in your app root folder
app = Flask(__name__)
host = 'http://localhost:5000/'
tab = '-'*20


def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        URL TEXT NOT NULL
        );
        """
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError as e:
            print("{} OperationalError: {}".format(tab, str(e)))


@app.route('/', methods=['POST','GET'])
def home():

    print('{} Hello from redirect_short_url: method {}'.format(tab, request.method))

    if request.method == 'POST':

        original_url = str_encode(request.form.get('url'))
        if urlparse(original_url).scheme == '':
            url = 'http://' + original_url
        else:
            url = original_url
        
        print('{} url: {}'.format(tab, url))
        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()

            encoded_url = base64.urlsafe_b64encode(url)

            res = cursor.execute(
                'SELECT ID FROM WEB_URL WHERE URL = (?)', 
                [encoded_url]
            )

            id = None
            if len(res.fetchall()) != 0:
                id = str(res.lastrowid)
            else:
                res = cursor.execute(
                    'INSERT INTO WEB_URL (URL) VALUES (?)',
                    [encoded_url]
                )
                id = str(res.lastrowid)

        return render_template('main.html', short_url=host + id)

    return render_template('main.html')


@app.route('/<short_url>')
def redirect_short_url(short_url):
    print('{} Hello from redirect_short_url'.format(tab))
    url = host  # fallback if no URL is found
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        res = cursor.execute('SELECT URL FROM WEB_URL WHERE ID=?', [short_url])
        try:
            short = res.fetchone()
            if short is not None:
                url = base64.urlsafe_b64decode(short[0])
        except Exception as e:
            print(e)
    return redirect(url)


if __name__ == '__main__':
    # This code checks whether database table is created or not
    table_check()
    app.run(debug=True)
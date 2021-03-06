from flask import Flask, render_template, redirect, request
from random import randrange
from datetime import datetime
import os

from lib.feed import post, add_post
from lib.story import Story
from lib.database import Database


app = Flask(__name__)
app.config.from_pyfile('settings.py')

conn = Database(app.config["DATABASE_URL"])
conn.init_databases()

stories = [
    Story(0, 'Отдыхаю на природе', '31.03.2021'),
    Story(1, 'Выбираю ноутбук', '15.03.2021'),
    Story(2, 'Весна пришла', '01.03.2021')
]
feed = [post(*el) for el in conn.get_all('Feed', 'id, title, text, tags, link, img, timestamp, type')[::-1]]

@app.route('/')
def index():
    return render_template('index.html', stories=stories, feed=feed)

@app.route('/article')
def rand_article():
    rnd = randrange(len(conn.get('Feed', 'id', f'type="article"'))) + 1
    return redirect(f'article/{rnd}')

@app.route('/article/<int:idx>')
def article(idx):
    if len(conn.get('Feed', 'id', f'type="article"')) < idx:
        return render_template('404.html', location=f'article/{idx}')
    return render_template('article.html', post=post(*conn.get('Feed', 'id, title, text, tags, link, img, timestamp, type', f'type="article" and id={idx}')))


@app.route('/addpost', methods=['post'])
def addpost():
    if request.form:
        type = request.form.get('type')
        # enum = len(conn.get_all('Feed', 'id')) + 1
        idx = len(conn.get_all('Feed', 'id', f'type="{type}"')) + 1
        title = request.form.get('title')
        text = request.form.get('text').replace('\\r', '\\n')
        tags = request.form.get('tags').replace(' ', ';')
        link = request.form.get('link')
        timestamp = datetime.now().strftime('%d.%m.%Y')
        img = ''

        if request.files:
            image = request.files['image']
            image_format_ind = image.filename[::-1].find('.')
            image_format = image.filename[-image_format_ind:]
            image.filename = f'{type}{idx}.{image_format}'
            img = image.filename
            image.save(f'{os.getcwd()}{app.config["UPLOAD_IMAGE"]}{image.filename}')

        feed.insert(0, add_post(conn, idx, title, text, tags, link, img, timestamp, type))
    return redirect('/')


@app.route('/<path:path>')
def undefined_page(path):
    return render_template('404.html', location=path)
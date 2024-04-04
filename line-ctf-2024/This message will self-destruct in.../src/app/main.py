from flask import Flask, render_template, request, jsonify
from uuid import uuid4
from threading import Timer, Thread
import os
import io
import time
import secrets
from urllib.parse import urljoin
from werkzeug.datastructures import FileStorage
from mysql.connector.errors import DatabaseError
import requests

from config import (
    FILE_SAVE_PATH,
    URLBASE,
    TRIAL_IMAGE,
    DESTRUCTION_SECONDS
)
import db
import util
from forms import AddImageForm

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init():
    db.init()
    if not os.path.exists(FILE_SAVE_PATH):
        os.mkdir(FILE_SAVE_PATH)
    print(os.listdir(FILE_SAVE_PATH))
    for filename in os.listdir(FILE_SAVE_PATH):
        filepath = os.path.join(FILE_SAVE_PATH, filename)
        if not filename.endswith('.gitignore') and os.path.isfile(filepath):
            os.remove(filepath)

init()

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 #1mb
app.config['WTF_CSRF_ENABLED'] = False

@app.get('/')
def get_index():
    return render_template('index.html')

@app.post('/')
def add_image():
    form = AddImageForm()

    print(form)

    if form.validate_on_submit():
        file = form.image.data
        password = form.password.data
        id_ = form.id.data or uuid4().hex
        image_url = form.image_url.data

        url = __add_image(password, id_, file=file, image_url=image_url)

        return render_template('image_added.html', url=url, form=form)
    else:
        logger.info(f'validation error: {form.errors}')
        return render_template('index.html', form=form)


def __add_image(password, id_, file=None, image_url=None, admin=False):
    t = Thread(target=convert_and_save, args=(id_, file, image_url))
    t.start()

    # no need, but time to waiting heavy response makes me excited!!
    if not admin:
        time.sleep(5)

    if file:
        mimetype = file.content_type
    elif image_url.endswith('.jpg'):
        mimetype = 'image/jpg'
    else:
        mimetype = 'image/png'

    db.add_image(id_, mimetype, password)

    return urljoin(URLBASE, id_)


def convert_and_save(id, file=None, url=None):
    try:
        if url:
            res = requests.get(url, timeout=3)
            image_bytes = res.content
        elif file:
            image_bytes = io.BytesIO()
            file.save(image_bytes)
            image_bytes = image_bytes.getvalue()

        if len(image_bytes) > app.config['MAX_CONTENT_LENGTH']:
            raise Exception('image too large')

        obfs_image_bytes = util.mosaic(image_bytes)

        with open(os.path.join(FILE_SAVE_PATH, id), 'wb') as f:
            f.write(image_bytes)
        with open(os.path.join(FILE_SAVE_PATH, id+'-mosaic'), 'wb') as f:
            f.write(obfs_image_bytes)
    except Exception as e:
        logger.error(f'convert_and_save: rollback: {e}')
        db.delete_image(id)
        try:
            os.remove(os.path.join(FILE_SAVE_PATH, id))
        except:
            pass
        try:
            os.remove(os.path.join(FILE_SAVE_PATH+'-mosaic', id))
        except:
            pass


@app.get('/trial')
def trial():
    with open(TRIAL_IMAGE, 'rb') as f:
        file = FileStorage(stream=f, content_type='image/png')
        url = __add_image(
            secrets.token_urlsafe(32),
            uuid4().hex,
            file=file,
            admin=True
        )
    return jsonify({'url': url})


@app.get('/<id>')
def hidden_image(id:str):
    result = db.get_image(id)
    if result:
        with open(os.path.join(FILE_SAVE_PATH, id+'-mosaic'), 'rb') as f:
            data = f.read()

        image_data_url = util.image_data2url(result[1], data)
        Timer(DESTRUCTION_SECONDS, db.delete_image, args=(id,)).start()
        return render_template('hidden_image.html', data_url=image_data_url, destruction_seconds=DESTRUCTION_SECONDS)
    else:
        logger.info(f'image not found: {id}')
        return render_template('imposter.html')


@app.post('/<id>')
def reveal_image(id:str):
    result = db.get_image(id)
    if result:
        password = request.form['password']
        if password == result[2]:
            with open(os.path.join(FILE_SAVE_PATH, id), 'rb') as f:
                data = f.read()
            image_data_url = util.image_data2url(result[1], data)
            return render_template('reveal_image.html', data_url=image_data_url)
        else:
            logger.info(f'wrong password: {id}')
            return render_template('imposter.html')
    else:
        logger.info(f'image not found: {id}')
        return render_template('imposter.html')


@app.errorhandler(FileNotFoundError)
def handle_FileNotFoundError(e):
    logger.info('file not found')
    return render_template('imposter.html')

@app.errorhandler(DatabaseError)
def handle_DatabaseError(e):
    logger.info(f'database error: {e}')
    return render_template('imposter.html')

if __name__ == '__main__':
    app.run('0.0.0.0', 8888, debug=True, threaded=True)
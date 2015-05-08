import os
from flask import Flask, send_file, send_from_directory

BUILD_PATH = './frontend/build/'
TEST_FOLDER = './frontend/src/static/'

app = Flask(__name__, instance_path=os.path.dirname(__file__), static_folder=BUILD_PATH, instance_relative_config=True)
app.debug = True


@app.route('/')
def hello_word():
    return send_file(app.static_folder + '/index.html')


@app.route('/media/build/<path:path>')
def send_js(path):
    return send_from_directory(app.static_folder, path)


@app.route('/test/<path:path>')
def send_from_test(path):
    return send_from_directory(TEST_FOLDER, path)


def main():
    app.run()


if __name__ == "__main__":
    main()
from flask import Flask, render_template, json

STATIC_FOLDER = 'frontend/src/static'

app = Flask(__name__, template_folder='frontend/build/')
app.debug = True


@app.route('/')
def hello_word():
    return render_template('index.html')


def main():
    app.run()

if __name__ == "__main__":
    main()
from flask import render_template
from Website import create_app

app = create_app()

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
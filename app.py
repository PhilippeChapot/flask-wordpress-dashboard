from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('dashboard.html')  # Assurez-vous que cette ligne est bien là

if __name__ == '__main__':
    app.run(debug=True)

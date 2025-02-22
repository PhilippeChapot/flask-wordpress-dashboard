from flask import Flask, render_template

app = Flask(__name__)
import requests
import os
from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder='templates')

# Paramètres WordPress
WORDPRESS_API_URL = "https://podcastmagazine.fr/wp-json/wp/v2/posts"
WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME", "PODCAST_MAGAZINE")
WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD", "VOTRE_MOT_DE_PASSE")

@app.route('/articles')
def articles():
    try:
        response = requests.get(WORDPRESS_API_URL, auth=(WORDPRESS_USERNAME, WORDPRESS_PASSWORD))
        articles = response.json()
        return render_template("articles.html", articles=articles)
    except Exception as e:
        return f"Erreur lors de la récupération des articles: {str(e)}"


@app.route('/')
def home():
    return render_template('dashboard.html')  # Assurez-vous que cette ligne est bien là

if __name__ == '__main__':
    app.run(debug=True)

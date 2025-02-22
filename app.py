from flask import Flask, render_template

app = Flask(__name__)
import requests
import os
from flask import Flask, request, render_template, redirect, url_for
import requests  # Assure-toi que 'requests' est bien importé

app = Flask(__name__, template_folder='templates')

# Paramètres WordPress
WORDPRESS_API_URL = "https://podcastmagazine.fr/wp-json/wp/v2/posts"
# URL de l'API WordPress pour envoyer des images
MEDIA_API_URL = "https://podcastmagazine.fr/wp-json/wp/v2/media"
WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME", "PODCAST_MAGAZINE")
WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD", "S4Gs 0u6c 1zbJ kHUw 1kFz kUOM")

@app.route('/articles')
def articles():
    try:
        response = requests.get(WORDPRESS_API_URL, auth=(WORDPRESS_USERNAME, WORDPRESS_PASSWORD))
        articles = response.json()

        print("Réponse API WordPress :", articles)  # Affiche la réponse API dans la console

        if not isinstance(articles, list):  # Vérifier si la réponse est bien une liste
            return f"Erreur : WordPress ne renvoie pas une liste d'articles. Réponse : {articles}"

        return render_template("articles.html", articles=articles)

    except Exception as e:
        return f"Erreur lors de la récupération des articles: {str(e)}"


@app.route('/publier', methods=['GET', 'POST'])
def publier():
    if request.method == 'POST':
        titre = request.form['titre'].encode("utf-8")  # Encodage UTF-8
        contenu = request.form['contenu'].encode("utf-8")  # Encodage UTF-8

        # Vérifier si un fichier a bien été envoyé
        if 'image' not in request.files:
            return "Erreur : Aucun fichier image reçu"

        image_file = request.files['image']

        # Vérifier si le fichier a un nom (c'est-à-dire qu'il a bien été téléversé)
        if image_file.filename == '':
            return "Erreur : Aucun fichier sélectionné"

        # 1️⃣ Envoyer l'image à WordPress
        image_id = None
        if image_file and image_file.filename:
            files = {'file': (image_file.filename, image_file.stream, 'image/jpeg')}
            response = requests.post(
                MEDIA_API_URL,
                auth=(WORDPRESS_USERNAME, WORDPRESS_PASSWORD),
                files=files,
                headers={'Content-Disposition': f'attachment; filename="{image_file.filename}"'}
            )
            if response.status_code == 201:
                image_id = response.json().get("id")

        # 2️⃣ Publier l'article avec l'image associée
        data = {
            "title": titre,
            "content": contenu,
            "status": "publish",
            "featured_media": image_id  # Associer l'image à l'article
        }

        response = requests.post(WORDPRESS_API_URL, json=data, auth=(WORDPRESS_USERNAME, WORDPRESS_PASSWORD))

        if response.status_code == 201:
            return redirect(url_for('articles'))
        else:
            return f"Erreur lors de la publication : {response.text}"

    return render_template("publier.html")



@app.route('/modifier/<int:article_id>', methods=['GET', 'POST'])
def modifier(article_id):
    if request.method == 'POST':
        titre = request.form['titre']
        contenu = request.form['contenu']

        # Mettre à jour l'article WordPress
        data = {
            "title": titre,
            "content": contenu,
        }

        response = requests.post(f"{WORDPRESS_API_URL}/{article_id}", json=data, auth=(WORDPRESS_USERNAME, WORDPRESS_PASSWORD))

        if response.status_code == 200:
            return redirect(url_for('articles'))
        else:
            return f"Erreur lors de la modification : {response.text}"

    # Récupérer les détails de l'article à modifier
    response = requests.get(f"{WORDPRESS_API_URL}/{article_id}", auth=(WORDPRESS_USERNAME, WORDPRESS_PASSWORD))
    article = response.json()
    
    return render_template("modifier.html", article=article)

@app.route('/supprimer/<int:article_id>', methods=['POST'])
def supprimer(article_id):
    response = requests.delete(f"{WORDPRESS_API_URL}/{article_id}", auth=(WORDPRESS_USERNAME, WORDPRESS_PASSWORD))

    if response.status_code == 200:
        return redirect(url_for('articles'))
    else:
        return f"Erreur lors de la suppression : {response.text}"


@app.route('/')
def home():
    return render_template('dashboard.html')  # Assurez-vous que cette ligne est bien là

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)


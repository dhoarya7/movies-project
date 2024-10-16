import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/movie", methods=["POST"])
def movie_post():
   
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']

    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    # Mendapatkan elemen gambar, judul, dan deskripsi
    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('meta[property="og:title"]')

    # Seleksi deskripsi dari elemen yang sesuai
    description_elem = soup.select_one('div.sc-70a366cc-2.bscNnP')
    if description_elem:
        description = description_elem.get_text(strip=True)
    else:
        description = "No description available"

    image = og_image['content'] if og_image else "No image available"
    title = og_title['content'] if og_title else "No title available"
    
    doc = {
        'image': image,
        'title': title,
        'description': description,
        'star': star_receive,
        'comment': comment_receive,
    }

    db.movies.insert_one(doc)

    return jsonify({'msg': 'POST request!'})

@app.route("/movie", methods=["GET"])
def movie_get():
    movie_list = list(db.movies.find({}, {'_id': False}))
    return jsonify({'movies': movie_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

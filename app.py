# OS
import json
import os
import random
from datetime import datetime

# Mongo database
import pymongo
from bson import ObjectId
# Flask
from flask import Flask, Response, request
from flask_cors import CORS
from slug import slug

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database
MONGODB_URI = os.getenv('MONGODB_URL')
client = pymongo.MongoClient(MONGODB_URI)
db = client.playwithsongs

""" Function """


def all_songs():
    return [{
        '_id': str(ele['_id']),
        'title': ele['title'],
        'artist': ele['artist'],
        'emotion': ele['emotion'],
        'lyric': ele['lyric'],
        'created_at': ele['created_at']
    } for ele in db.song.find()]


def check_title(new_title):
    new = slug(new_title)
    arr = [slug(val['title']) for val in all_songs()]
    return new in arr


def res_message(message, status):
    response_message = {
        'message': message
    }
    return Response(json.dumps(response_message), status=status, mimetype='application/json')


""" Flask Route """


@app.route('/')
def home():
    return "from tinhtute with love"


@app.route('/api/songs', methods=['GET', 'POST'])
def songs():
    if request.method == 'GET':
        song_list = all_songs()
        return Response(json.dumps(song_list), status=200, mimetype='application/json')

    if request.method == 'POST':
        request_data = json.loads(request.data)
        if check_title(request_data['title']):
            return res_message("This song had been existed.", 400)
        data = {
            'title': request_data['title'],
            'artist': request_data['artist'],
            'emotion': request_data['emotion'],
            'lyric': request_data['lyric'],
            'created_at': str(datetime.now().timestamp() * 1000)
        }
        db.song.insert_one(data)
        print(data)
        response_message = {
            'message': "A song has been created successfully!"
        }
        return Response(json.dumps(response_message), status=201, mimetype='application/json')


@app.route('/api/songs/random', methods=['GET'])
def song_random():
    song_list = all_songs()
    random_song = random.choice(song_list)
    return Response(json.dumps(random_song), status=200, mimetype='application/json')


@app.route('/api/songs/<song_id>', methods=['GET'])
def get_a_song(song_id):
    result = db.song.find_one({'_id': ObjectId(song_id)})
    data = {
        '_id': str(result['_id']),
        'title': result['title'],
        'artist': result['artist'],
        'emotion': result['emotion'],
        'lyric': result['lyric'],
        'created_at': result['created_at']
    }
    return Response(json.dumps(data), status=200, mimetype='application/json')


@app.route('/api/songs/<song_id>', methods=['PUT'])
def update_a_song(song_id):
    query = {'_id': ObjectId(song_id)}
    request_data = json.loads(request.data)
    data = {
        'title': request_data['title'],
        'artist': request_data['artist'],
        'emotion': request_data['emotion'],
        'lyric': request_data['lyric'],
        'created_at': str(datetime.now().timestamp() * 1000)
    }
    db.song.update_one(query, {"$set": data}, upsert=True)
    response_message = {
        'message': "A song has been updated successfully!"
    }
    return Response(json.dumps(response_message), status=200, mimetype='application/json')


@app.route('/api/songs/<song_id>', methods=['DELETE'])
def delete_a_song(song_id):
    db.song.delete_one({'_id': ObjectId(song_id)})
    response_message = {
        'message': "A song has been deleted successfully!"
    }
    return Response(json.dumps(response_message), status=200, mimetype='application/json')

'''
Main
'''
if __name__ == '__main__':
    # for deployment
    # to make it work for both production and development
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

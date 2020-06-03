from flask import Flask, jsonify, request


app = Flask(__name__)
app.users = {}
app.id_count = 1


@app.route('/ping', methods=['GET'])
def ping():
    return "pong"


@app.route('/sign-up', methods=['POST'])
def sign_up():
    new_user = request.json
    new_user['id'] = app.id_count
    app.users[app.id_count] = new_user
    app.id_count = app.id_count + 1

    return jsonify(new_user)


app.tweets = []


@app.route('/tweet', methods=['POST'])
def tweet():
    payload = request.json
    user_id = int(payload['id'])
    tweet = payload['tweet']

    if user_id not in app.users:
        return '사용자가 존재하지 않습니다', 400

    if len(tweet) > 300:
        return '300자를 초과하였습니다', 400

    user_id = int(payload['id'])

    app.tweets.append({
        'user_id' : user_id,
        'tweet' : tweet
    })

    return '', 200


if __name__ == '__main__':
    app.run(debug=True)
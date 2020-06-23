from flask import Flask, jsonify, request, current_app
from sqlalchemy import create_engine, text
from flask_sqlalchemy import SQLAlchemy


def create_app(test_config=None):
    # create_app 함수 정의, test_config 인자는 uni test 를 위해
    app = Flask(__name__)

    if test_config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.update(test_config)

    database = create_engine(app.config['DB_URL'], encoding='utf-8',
                             max_overflow=0)
    # create_engine 함수를 통한 DB 연결
    app.database = database
    # 외부에서도 DB 사용할 수 있게

    @app.route('/sign-up', methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user_id = app.database.execute(text("""
            INSERT INTO users (
                name,
                email,
                profile,
                hashed_password
            ) VALUES (
                :name,
                :email,
                :profile,
                :password
            )
        """), new_user).lastrowid

        row = current_app.database.execute(text("""
            SELECT
                id,
                name,
                email,
                profile
            FROM users
            WHERE id = :user_id
        """), {
            'user_id': new_user_id
        }).fetchone()

        create_user = {
            'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'profile': row['profile']
        } if row else None

        return jsonify(create_user)

    @app.route('/tweet', methods=['POST'])
    def tweet():
        user_tweet = request.json
        tweet = user_tweet['tweet']

        if len(tweet) > 300:
            return '300자를 초과했습니다', 400

        app.database.execute(text("""
            INSERT INTO tweets (
                user_id,
                tweet
            ) VALUES (
                :id, 
                :tweet
            )
        """), user_tweet)

        return '', 200

    @app.route('/timeline/<int:user_id>', methods=['GET'])
    def timeline(user_id):
        rows = app.database.execute(text("""
            SELECT
                t.user_id,
                t.tweet
            FROM tweets t
            LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
            WHERE t.user_id = :user_id
            OR t.user_id = ufl.follow_user_id
        """), {
            'user_id' : user_id
        }).fetchall()

        timeline = [{
            'user_id': row['user_id'],
            'tweet': row['tweet']
        } for row in rows]

        return jsonify({
            'user_id': user_id,
            'timeline': timeline
        })

    return app




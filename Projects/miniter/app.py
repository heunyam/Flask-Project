from flask import Flask, jsonify, request, current_app
from sqlalchemy import create_engine, text


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

    return app


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
    """), new_user). lastrowid

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


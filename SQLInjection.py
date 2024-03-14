# Python (Flask)
from flask import Flask, request

app = Flask(__name__)

@app.route('/login')
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    # Vulnerable code
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    # Execute the query and process the result
    # ...

if __name__ == '__main__':
    app.run(debug=True)

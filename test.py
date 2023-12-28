from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/create_thread', methods=['GET'])
def create_thread():
    # Your existing logic to create a thread
    pass

if __name__ == '__main__':
    app.run(debug=True, port=8000)

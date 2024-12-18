import time
from flask import Flask, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Isso permite requisições de qualquer origem

@app.route('/events')
def sse():
    def event_stream():
        while True:
            yield f"data: {time.ctime()}\n\n"  # Envia a hora atual a cada 5 segundos
            time.sleep(5)
    
    return Response(event_stream(), content_type='text/event-stream', status=200)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)  # Rodar na porta 8000

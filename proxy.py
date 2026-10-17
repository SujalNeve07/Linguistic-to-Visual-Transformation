from flask import Flask, request, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
# Enable CORS for requests from http://localhost:8080
CORS(app, resources={r"/proxy": {"origins": "http://localhost:8080"}})

@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url')
    if not url:
        
        return Response("Missing 'url' parameter", status=400, mimetype='text/plain')
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        return Response(response.content, status=response.status_code, mimetype=content_type)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {str(e)}")
        return Response(f"Proxy error: {str(e)}", status=500, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
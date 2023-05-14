# views.py
import sys
sys.path.append('../')

from flask import Flask
from api.endpoints import extract

app = Flask(__name__)
app.register_blueprint(extract, url_prefix='/pdf_extract')



#if __name__ == '__main__':
#    app.run(debug=True, port=5001)

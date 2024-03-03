# Dependencies
from flask import Flask, request, jsonify
from recommendation_algo import print_recommendations
import traceback
import pandas as pd

# Your API definition
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Bundle Recommender</h1>
                <p>A REST api implementation for product-bundle recommendation   </p>'''

@app.route('/recommend', methods=['POST'])
def predict():
    print('inside predict')
    try:
        json_ = request.json
        print(json_)
        query = pd.DataFrame(json_)

        product, prediction = print_recommendations(list(query['product_id'])[0], data_pkl, rules_pkl, list(query['recommendation_count'])[0])
        print(prediction)
        return jsonify({'Product':product, 'Recommended products': prediction})

    except:

        return jsonify({'trace': traceback.format_exc()})

if __name__ == '__main__':
    try:
        port = int(sys.argv[1]) # This is for a command-line input
    except:
        port = 5000 # If you don't provide any port the port will be set to 5000

    data_pkl = pd.read_pickle("filtered_dt.pkl")
    rules_pkl = pd.read_pickle("rules.pkl")
    print ('Model loaded')

    app.run(host='0.0.0.0',port=port, debug=True)
from flask import Flask, request, render_template
from main import getZipcode, zipToCityState, getCongressionalDistrict, findPoliticianByDistrict, findPoliticianByState, googleCivicInfoKey, congressApiKey

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        zipcode = request.form['zipcode']
        city, state = zipToCityState(zipcode)
        district = getCongressionalDistrict(zipcode, googleCivicInfoKey)
        if district:
            politicians = findPoliticianByDistrict(district)
        else:
            politicians = findPoliticianByState(state)

        return render_template('results.html', city=city,
                               state=state,
                               district=district,
                               politicians=politicians)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5001)
from flask import Flask, render_template, request
import pickle

tokenizer = pickle.load(open("models/cv.pkl","rb"))
model = pickle.load(open("models/clf.pkl","rb"))

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    email = request.form.get('content')
    tokenized_email = tokenizer.transform([email])
    predictions = model.predict(tokenized_email)
    predictions =1 if predictions == 1 else -1
    return render_template("index.html", predictions = predictions, email = email)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)



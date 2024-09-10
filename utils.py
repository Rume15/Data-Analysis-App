import pickle
tokenizer = pickle.load(open("models/cv.pkl","rb"))
model = pickle.load(open("models/clf.pkl","rb"))

def make_prediction(email):
    tokenized_email = tokenizer.transform([email])
    predictions = model.predict(tokenized_email)
    predictions =1 if predictions == 1 else -1
    return predictions
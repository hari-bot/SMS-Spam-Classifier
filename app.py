import pickle
import string
from nltk.corpus import stopwords
import nltk
from nltk.stem.porter import PorterStemmer
from flask import Flask, request, render_template
import warnings
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

ps = PorterStemmer()
tfidf = pickle.load(open('vectorizer.pkl','rb'))
model = pickle.load(open('model.pkl','rb'))
app = Flask(__name__)

messages=[]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']
        result =process_input(user_input)
        messages.insert(0,{"message":user_input,"type":result})
        return render_template('index.html', result=result,messages=messages)
    return render_template('index.html',messages=messages)

@app.route('/delete', methods=['POST'])
def delete_message():
    task_index = int(request.form['task_index'])
    if task_index < len(messages):
        messages.pop(task_index)
    return render_template('index.html',messages=messages)


def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)

    y = []
    for i in text:
        if i.isalnum():
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        y.append(ps.stem(i))

    return " ".join(y)

def process_input(user_input):

    # 1. preprocess
    transformed_sms = transform_text(user_input)
    # 2. vectorize
    vector_input = tfidf.transform([transformed_sms])
    # 3. predict
    result = model.predict(vector_input)[0]
    # 4. Display
    if result == 1:
        return("This SMS is a spam.")
    else:
        return("This SMS is not spam.")



if __name__ == '__main__':
    app.run(debug=True)




from flask import Flask, render_template, url_for, request,session
import nltk
import json
import psycopg2
from bs4 import BeautifulSoup
import requests

Password='Pallavi'
app = Flask(__name__, static_folder="/var/data/")

conn = psycopg2.connect(
host="dpg-cnmu59a1hbls739ikbcg-a",database="pallavi",user='pallavi_user',password='0iaVGe9gNF9ozNxqnV8CrMw5Tj5WWH0O',port='5432')
cur=conn.cursor()

cur.execute('create table if not exists history(id SERIAL PRIMARY KEY, URL varchar, input_text TEXT, word_count INTEGER, sentence_count INTEGER, stop_word_count INTEGER, upos_frequency varchar(1000))')
conn.commit()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/submit',methods=['POST','GET'])
def page1():
    stop_wrd_count=0      # No of stop words
    upos_frequency={}   # Upos frequency
    words=0         # Total no of words
    sent=0          # Total no of sentences
    error_message=None
    text=''
    title=''
    if request.method=='POST':
        url=request.form['url']
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        One=soup.find( class_="_s30J clearfix")
        if One!=None:
            text=One.text
            title=soup.title.string
        else:
            error_message='Enter a valid URL'
            return render_template('home.html', error_message=error_message)
        
        stop_words=nltk.corpus.stopwords.words('english')      # List of total stop words in english
        tok_word=nltk.word_tokenize(text)                      # Total tokenize words in sentences (inc. punc).
        sent_list=nltk.sent_tokenize(text)                     # List of sentences 
        list_punc=[',','$','%',')','(','!',';','?','/','``',"''",'.',"'",'\\','{','}','[',']','=']

        # List of actual words without punctuations
        word_list=[ ]
        for x in tok_word:
            if x not in list_punc:
                word_list.append(x)

        # Total no of words
        for x in word_list:
            words=words+1

        # Total stop_words
        for x in word_list:
            if x in nltk.corpus.stopwords.words('english'):
                stop_wrd_count=stop_wrd_count+1

        # Total no of sentences.
        for x in sent_list:
            sent=sent+1

        # upos frequency appending in a dictionary.
        
        upos_tag_list = nltk.pos_tag(tok_word, tagset='universal')
        for _, pos in upos_tag_list:
            upos_frequency[pos] = upos_frequency.get(pos, 0) + 1
        upos_frequency_json = json.dumps(upos_frequency)

    # Inserting these values into created table
        cur.execute('insert into history(URL,input_text, word_count , sentence_count , stop_word_count, upos_frequency ) values(%s,%s,%s,%s,%s,%s)',(url, text, words, sent, stop_wrd_count, upos_frequency_json))
        conn.commit()
    return render_template('content.html', text_html=text, title_html=title, words=words, sent=sent, stop_wrd_count=stop_wrd_count, upos_frequency=upos_frequency)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/history', methods=['POST','GET'])
def history():
    if request.method=='POST':
        entered_password=request.form['password']
        if entered_password!=Password:
            error_message='Incorrect Password. Access Denied.'
            return render_template('login.html', error_message=error_message)
        else:
            cur.execute('select * from history')
            data=cur.fetchall()
            conn.commit()
    return render_template('history.html', data_html=data )
if __name__== "__main__":
    app.run(debug=True)

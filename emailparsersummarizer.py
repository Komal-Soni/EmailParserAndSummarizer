import warnings
warnings.filterwarnings("ignore")
import smtplib
import time
import imaplib
import email
import traceback 
import pandas as pd
# Importing the required Libraries
import numpy as np
import pandas as pd
import nltk
nltk.download('punkt') # one time execution
import re
nltk.download('stopwords') # one time execution
import matplotlib.pyplot as plt
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

def major(FROM_EMAIL, FROM_PWD):
    FROM_EMAIL=FROM_EMAIL
    FROM_PWD=FROM_PWD
    SMTP_SERVER = "imap.gmail.com" 
    SMTP_PORT = 993

    def read_email_from_gmail(FROM_EMAIL,FROM_PWD): 
        FROM=[]
        SUBJECT=[]
        BODY=[]
        SUMMARY=[]
        try:
            mail = imaplib.IMAP4_SSL(SMTP_SERVER)
            mail.login(FROM_EMAIL,FROM_PWD)
            mail.select('inbox')

            data = mail.search(None, 'ALL')
            mail_ids = data[1]
            id_list = mail_ids[0].split()   
            first_email_id = int(id_list[0])
            latest_email_id = int(id_list[-1])

            for i in range(latest_email_id,first_email_id, -1):
                data = mail.fetch(str(i), '(RFC822)' )
                for response_part in data:
                    arr = response_part[0]
                    if isinstance(arr, tuple):
                        msg = email.message_from_string(str(arr[1],'utf-8'))
                        email_subject = msg['subject']
                        email_from = msg['from']
                        body = ""

                        if msg.is_multipart():
                            for part in msg.walk():
                                ctype = part.get_content_type()
                                cdispo = str(part.get('Content-Disposition'))

                                # skip any text/plain (txt) attachments
                                if ctype == 'text/plain' and 'attachment' not in cdispo:
                                    body = part.get_payload(decode=True)  # decode
                                    break
                        else:
                            body = msg.get_payload(decode=True)
                        
                        FROM.append(email_from)
                        SUBJECT.append(email_subject)
                        BODY.append(str(body,encoding='latin1'))
                        SUMMARY.append("")
        except Exception as e:
            traceback.print_exc() 
            print(str(e))
        dict = {'From': FROM, 'Subject': SUBJECT, 'Body': BODY, 'Summary': SUMMARY } 
        df = pd.DataFrame(dict)
        #print(df.info())
        return df
    dataset=(read_email_from_gmail(FROM_EMAIL,FROM_PWD))

# Extract word vectors
#!wget http://nlp.stanford.edu/data/glove.6B.zip
    word_embeddings = {}
    file = open("C:/Users/sk26k/OneDrive/Desktop/major103/glove.6B.100d.txt", encoding='utf-8')
    for line in file:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        word_embeddings[word] = coefs
    file.close()
    import re
    def remove_tags(text):
        TAG_RE = re.compile(r'<[^>]+>')
        text=re.sub('\s+',' ',text)
        text=re.sub(r'http\S+', '', text)
        text=re.sub(r'\[image:\s+','',text)
        text=TAG_RE.sub('', text)
        text=text.lower()
        
        return text
    # Converting the DataFrame into a dictionary
    text_dictionary = {}
    for i in range(1,len(dataset['Body'])):
        text_dictionary[i] = remove_tags(dataset['Body'][i])
    # function to remove stopwords
    def remove_stopwords(sen):
        stop_words = stopwords.words('english')  
        sen_new = " ".join([i for i in sen if i not in stop_words])
        return sen_new
    # function to make vectors out of the sentences
    def sentence_vector_func (sentences_cleaned) : 
        sentence_vector = []
        for i in sentences_cleaned:
            if len(i) != 0:
                v = sum([word_embeddings.get(w, np.zeros((100,))) for w in i.split()])/(len(i.split())+0.001)
            else:
                v = np.zeros((100,))
            sentence_vector.append(v)
        
        return (sentence_vector)
    # function to get the summary of the articles
    def summary_text (test_text, n = 5):
        sentences = []
        
        # tokenising the text 
        sentences.append(sent_tokenize(test_text))
        # print(sentences)
        sentences = [y for x in sentences for y in x] # flatten list
        # print(sentences)
        
        # remove punctuations, numbers and special characters
        clean_sentences = pd.Series(sentences).str.replace("[^a-z A-Z 0-9]", " ")

        # make alphabets lowercase
        clean_sentences = [s.lower() for s in clean_sentences]
        #print(clean_sentences)

        
        # remove stopwords from the sentences
        clean_sentences = [remove_stopwords(r.split()) for r in clean_sentences]
        #print(clean_sentences)
        
        sentence_vectors = sentence_vector_func(clean_sentences)
        
        # similarity matrix
        sim_mat = np.zeros([len(sentences), len(sentences)])
        #print(sim_mat)
        
        # Finding the similarities between the sentences 
        for i in range(len(sentences)):
            for j in range(len(sentences)):
                if i != j:
                    sim_mat[i][j] = cosine_similarity(sentence_vectors[i].reshape(1,100), sentence_vectors[j].reshape(1,100))[0,0]
        
        
        nx_graph = nx.from_numpy_array(sim_mat)
        scores = nx.pagerank(nx_graph)
        #print(scores)
        
        ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(sentences)))
        # Extract sentences as the summary
        summarised_string = ''
        s=[]
        for i in range(n):
            
            try:
                summarised_string = summarised_string + str(ranked_sentences[i][1])            
            except IndexError:
                pass
                #s.append("Summary Not Available")
                #print ("Summary Not Available")
        
        return (summarised_string)
    x=2

    summary_dictionary = {}
    s=[]
    c=1
    for key in text_dictionary:
        
        para = text_dictionary[key]
        s.append(("Summary of the email - "+str(key)))
        summary = summary_text(para,x)
        summary_dictionary[key] = summary
        summary=re.sub("â© 2018 google llc,1600 amphitheatre parkway, mountain view, ca 94043, usa","",summary)
        summary=re.sub("â© 2022 google llc, 1600 amphitheatre parkway, mountain view, ca 94043, usa","",summary)
        summary=re.sub("hyderabad institute of technology and management gowdavelli(v), medchal dist - 501 401 /*accredited by naac a+ & nba (cse&ece)/* /*||hitam is the first green campus in india to be awarded a silver rating|/*","",summary)
        s.append(summary)
        s.append('='*120)
        smry=[]
        smry.append(summary)
        dataset['Summary'][c]=dataset['Summary'][c]+(summary)
        c+=1
        d={'From': dataset['From'], 'Subject': dataset['Subject'], 'Summary': dataset['Summary']} 
        data = pd.DataFrame(d)
    s.append("*"*40+"The process has been completed successfully"+"*"*40)
    return dataset





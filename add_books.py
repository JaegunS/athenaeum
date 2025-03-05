import sqlite3
import isbnlib
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm import tqdm

confident_threshold = 0.9

sql_db = sqlite3.connect('sql.db')
sql_cursor = sql_db.cursor()


# device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
model_name = 'MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)

label_entailment_idx = 0

hypothesis = "This book is about {label}."

sql_cursor.execute('SELECT id FROM models WHERE name = ?', (model_name,))
model_id = sql_cursor.fetchone()[0]

# get tags from database
sql_cursor.execute('SELECT * FROM tags')
tags = {}
for tag in sql_cursor.fetchall():
    # name -> id
    tags[tag[1]] = tag[0]

tag_list = list(tags.keys())

def add_book(isbnlike):
    isbn = isbnlib.canonical(isbnlike)
    book = isbnlib.meta(isbn)

    # check if book already exists
    if book is None:
        return None
    
    # check if book already exists in database
    sql_cursor.execute('SELECT * FROM books WHERE isbn = ?', (isbn,))
    if sql_cursor.fetchone() is not None:
        return None

    # add book to book table
    # id, title, author, year, isbn
    sql_cursor.execute('INSERT INTO books VALUES (NULL, ?, ?, ?, ?)',
                       (book['Title'], ', '.join(book['Authors']), book['Year'], isbn))

    last_id = sql_cursor.lastrowid

    # get description
    description = isbnlib.desc(isbn)

    # clean
    description = description.replace('\n', ' ')
    description = description.replace('\r', ' ')
    description = description.replace('\t', ' ')
    
    # add title and author to description
    premise = book['Title'] + ' by ' + ', '.join(book['Authors']) + '. Description: ' + description

    filtered_tags = []
    for tag_name in tqdm(tag_list):
        current_hypothesis = hypothesis.format(label=tag_name)
        
        # Tokenize with truncation to model's max length
        inputs = tokenizer(
            premise, 
            current_hypothesis, 
            truncation=True, 
            max_length=512,  # Set to model's max length
            return_tensors="pt"
        ).to(device)  # Move inputs to the same device as model
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)
        entailment_prob = probs[0][label_entailment_idx].item()
        
        if entailment_prob > confident_threshold:
            filtered_tags.append((tags[tag_name], entailment_prob))

    # add tags to book_tags table
    # book_tag table
    # book_id, tag_id, weight, model_id
    for tag, weight in filtered_tags:
        sql_cursor.execute('INSERT INTO book_tags VALUES (?, ?, ?, ?)',
                           (last_id, tag, weight, model_id)) 

    sql_db.commit()
    return (book, description)

# simple input loop
while True:
    isbn = input('Enter ISBN: ')
    if isbn == 'exit':
        break
    print(add_book(isbn))

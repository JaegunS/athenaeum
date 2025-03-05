import sqlite3
import json

conn = sqlite3.connect('sql.db')
cursor = conn.cursor()

models = [
    'facebook/bart-large-mnli',
    'MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli',
]

def add_tables():
    # book table
    # id, title, author, year, isbn
    cursor.execute('''
    CREATE TABLE books (
        id INTEGER PRIMARY KEY,
        title TEXT,
        author TEXT,
        year INTEGER,
        isbn INTEGER
    )
    ''')

    # tag table
    # id, name, frequency
    # this table should not be changed by the user
    cursor.execute('''
    CREATE TABLE tags (
        id INTEGER PRIMARY KEY,
        name TEXT,
        frequency INTEGER
    )
    ''')

    # model table
    # id, name
    cursor.execute('''
    CREATE TABLE models (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    ''')

    # book_tag table
    # book_id, tag_id, weight
    cursor.execute('''
    CREATE TABLE book_tags (
        book_id INTEGER,
        tag_id INTEGER,
        weight FLOAT,
        model_id INTEGER,
        PRIMARY KEY (book_id, tag_id),
        FOREIGN KEY (book_id) REFERENCES book(id),
        FOREIGN KEY (tag_id) REFERENCES tag(id),
        FOREIGN KEY (model_id) REFERENCES model(id)
    )
    ''')
    
def add_tags(threshold):
    with open('tags.json') as f:
        tags = json.load(f)

    # write tags to sql.db
    # schema: id, name, frequency
    for tag in tags.keys():
        # we only want tags with frequency > threshold
        if tags[tag] > threshold:
            cursor.execute("INSERT INTO tags (name, frequency) VALUES (?, ?)", (tag, tags[tag]))

def add_models():
    for model in models:
        cursor.execute("INSERT INTO models (name) VALUES (?)", (model,))

if __name__ == '__main__':
    add_tables()
    add_tags(25000)
    add_models()

conn.commit()
conn.close()
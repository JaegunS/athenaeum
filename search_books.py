import sqlite3
import isbnlib

sql_db = sqlite3.connect('sql.db')
cursor = sql_db.cursor()

def search_books(isbnlike):
    isbn = isbnlib.canonical(isbnlike)

    cursor.execute('SELECT * FROM books WHERE isbn = ?', (isbn,))
    book = cursor.fetchone()

    if book is None:
        return None
    
    return book

def get_tags(isbnlike):
    isbn = isbnlib.canonical(isbnlike)

    cursor.execute('''
        SELECT b.title, t.name, bt.weight
            FROM book_tags bt
            JOIN books b ON bt.book_id = b.id
            JOIN tags t ON bt.tag_id = t.id
            WHERE b.isbn = ? ORDER BY bt.weight DESC
                   ''', (isbn,))
    tags = cursor.fetchall()
    output = [(tag[1], tag[2]) for tag in tags]
    return output

if __name__ == '__main__':
    query = input("Enter ISBN: ")
    print(search_books(query))
    print(get_tags(query))
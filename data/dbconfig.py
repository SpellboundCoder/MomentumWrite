import sqlite3


class Story:
    __tablename__ = "stories" # noqa

    def __init__(self,
                 _id: int = None,
                 text: str = "",
                 date: str = ""):

        self.id = _id
        self.text = text
        self.date = date


conn = sqlite3.connect('data/database.db', check_same_thread=False)   #
c = conn.cursor()

conn.execute("""CREATE TABLE IF NOT EXISTS stories(
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                date TEXT NOT NULL
                )"""
             )


def get_all_stories():

    c.execute("SELECT * FROM stories")
    stories = c.fetchall()
    return [Story(
        _id=story[0],
        text=story[1],
        date=story[2],
    ) for story in stories]


def add_story(story: Story):
    with conn:
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("""INSERT INTO stories(text,date)
                  VALUES (:text, :date)""",
                  {
                      "text": story.text,
                      "date": story.date,
                  })


def delete_story(_id):
    with conn:
        c.execute("DELETE from stories WHERE  id = :id", {'id': _id})

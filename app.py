from flask import Flask, request, redirect, render_template_string
import sqlite3
import random
import string

app = Flask(__name__)

def setup_database():
    conn = sqlite3.connect("urls.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_code():
    characters = string.ascii_letters + string.digits

    while True:
        code = "".join(
            random.choice(characters)
            for _ in range(6)
        )

        conn = sqlite3.connect("urls.db")

        result = conn.execute(
            "SELECT * FROM urls WHERE short_code = ?",
            (code,)
        ).fetchone()

        conn.close()

        if result is None:
            return code


@app.route("/", methods=["GET", "POST"])
def home():

    short_url = None

    if request.method == "POST":

        original_url = request.form["url"]

        short_code = create_code()

        conn = sqlite3.connect("urls.db")

        conn.execute(
            """
            INSERT INTO urls (original_url, short_code)
            VALUES (?, ?)
            """,
            (original_url, short_code)
        )

        conn.commit()
        conn.close()

        short_url = request.host_url + short_code

    with open("index.html", "r", encoding="utf-8") as file:
        html = file.read()

    if short_url:
        html = html.replace(
            "{{SHORT_URL}}",
            f'<a href="{short_url}" target="_blank">{short_url}</a>'
        )
    else:
        html = html.replace(
            "{{SHORT_URL}}",
            ""
        )

    return render_template_string(html)


@app.route("/<short_code>")
def redirect_url(short_code):

    conn = sqlite3.connect("urls.db")

    result = conn.execute(
        """
        SELECT original_url
        FROM urls
        WHERE short_code = ?
        """,
        (short_code,)
    ).fetchone()

    conn.close()

    if result:
        return redirect(result[0])

    return "Short URL not found", 404


if __name__ == "__main__":

    setup_database()

    app.run(debug=True)

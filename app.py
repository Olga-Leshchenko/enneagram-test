from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = "enneagram-secret"  # для збереження даних у session

with open("pairs.json", "r", encoding="utf-8") as f:
    PAIRS = json.load(f)

SCALES = list("ABCDEFGHI")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        choices = [request.form.get(f"p_{i}", "") for i in range(len(PAIRS))]
        scores = {s: 0 for s in SCALES}
        for i, choice in enumerate(choices):
            pair = PAIRS[i]
            if choice == "L":
                sc = pair["left"]["scale"]
            elif choice == "R":
                sc = pair["right"]["scale"]
            else:
                sc = None
            if sc:
                scores[sc] += 1

        # Зберігаємо результати у сесії
        session["scores"] = scores
        return redirect(url_for("result"))

    return render_template("index.html")

@app.route('/test')
def test():
    return render_template('test.html', pairs=PAIRS)


@app.route("/result")
def result():
    scores = session.get("scores")
    if not scores:
        return redirect(url_for("test"))

    # знайти букву з найбільшим балом
    top_letter = max(scores, key=scores.get)
    top_score = scores[top_letter]

    # відповідність літера → тип
    mapping = {
        "A": {"num": 9, "name": "Миротворець"},
        "B": {"num": 6, "name": "Лояльний"},
        "C": {"num": 3, "name": "Досягатор"},
        "D": {"num": 1, "name": "Реформатор"},
        "E": {"num": 4, "name": "Індивідуаліст"},
        "F": {"num": 2, "name": "Помічник"},
        "G": {"num": 8, "name": "Лідер"},
        "H": {"num": 5, "name": "Дослідник"},
        "I": {"num": 7, "name": "Ентузіаст"},
    }

    top_type = mapping[top_letter]

    return render_template(
        "result.html",
        scores=scores,
        top_letter=top_letter,
        top_type=top_type,
        top_score=top_score,
    )


@app.route("/type/<letter>")
def type_page(letter):
    letter = letter.upper()
    if letter not in SCALES:
        return "Невідомий тип", 404
    return render_template(f"type_{letter}.html")

if __name__ == "__main__":
    app.run(debug=True, port=5050)

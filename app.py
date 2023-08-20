from flask import Flask

app = Flask()

@app.route("/")
def home():
    ...


if __name__ == "__main__":
    app.run(debug=True)


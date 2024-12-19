from flask import Flask, render_template

app = Flask(__name__)

@app.route("/home")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/preset")
def preset():
    return render_template("preset.html") 

@app.route("/custom")
def custom():
    return render_template("custom.html") 

@app.route("/custom1")
def custom1():
    return render_template("custom1.html") 

@app.route("/output")
def output():
    return render_template("output.html") 


if __name__ == "__main__":
    app.run(debug=True)
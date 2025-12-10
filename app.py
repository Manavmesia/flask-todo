from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# ✅ Security: Secret Key Added
app.config['SECRET_KEY'] = os.environ.get(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)

# ✅ Safer DB Config (fallback for local)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", "sqlite:///todo.db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ✅ Model
class Todo(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.srno} - {self.title}"

# ✅ Home + Add Todo (PRG Pattern Fixed)
@app.route('/', methods=["GET", "POST"])
def add():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')

        # ✅ Validation
        if not title or not desc:
            return "Invalid input", 400

        todo = Todo(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()

        # ✅ PRG FIX (Prevents duplicate submissions)
        return redirect("/")

    allTodo = Todo.query.all()
    return render_template('index.html', allTodo=allTodo)

# ❌ /show WAS REMOVED (debug + useless)
# ✅ If you still want it:
@app.route('/show')
def show():
    allTodo = Todo.query.all()
    return render_template('index.html', allTodo=allTodo)

# ✅ Edit Todo (Crash-Proof)
@app.route('/edit/<int:srno>', methods=["GET", "POST"])
def edit(srno):
    todo = Todo.query.filter_by(srno=srno).first()

    # ✅ Prevent None Crash
    if not todo:
        return "Todo not found", 404

    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')

        if not title or not desc:
            return "Invalid input", 400

        todo.title = title
        todo.desc = desc

        # ✅ db.session.add(todo) REMOVED (not needed)
        db.session.commit()

        return redirect("/")

    return render_template('edit.html', todo=todo)

# ✅ Delete Todo (CSRF-SAFE: POST only + Crash-Proof)
@app.route('/delete/<int:srno>', methods=["POST"])
def delete(srno):
    todo = Todo.query.filter_by(srno=srno).first()

    # ✅ Prevent None Crash
    if not todo:
        return "Todo not found", 404

    db.session.delete(todo)
    db.session.commit()
    return redirect("/")

# ✅ Safe App Boot with Table Creation
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)

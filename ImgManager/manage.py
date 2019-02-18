from main import app
from ImgManager.models import db, Person, Album, Picture


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Person=Person, Album=Album, Picture=Picture)

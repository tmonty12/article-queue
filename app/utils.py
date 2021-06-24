from functools import wraps
from flask import redirect, url_for
from flask_login import current_user
from app.models import Article

def is_current_user(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    author = Article.query.filter_by(id=kwargs['id']).first().author
    if current_user == author:
      return func(*args, **kwargs)
    return redirect(url_for('index'))
  return wrapper
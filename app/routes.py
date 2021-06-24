from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, ArticleForm, SearchForm
from app.models import User, Article
from app.utils import is_current_user

  
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = ArticleForm()
    filter = request.args.get('filter')
    articles = current_user.articles.order_by(Article.timestamp.desc()).all()
    if filter == 'read':
      article_query = current_user.articles.order_by(Article.timestamp.desc()).filter_by(has_read=True)
      articles = [ article for article in article_query ]
    elif filter == 'unread':
      article_query = current_user.articles.order_by(Article.timestamp.desc()).filter_by(has_read=False)
      articles = [ article for article in article_query ]
    if form.validate_on_submit():
      article = Article(title=form.title.data, topic=form.topic.data, url=form.url.data, author=current_user)
      db.session.add(article)
      db.session.commit()
      flash('You added a new article')
      return redirect(url_for('index'))
    return  render_template('index.html', form=form, articles=articles, filter=filter)

@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user is None or not user.check_password(form.password.data):
      flash('Invalid username or password')
      return redirect(url_for('login'))
    login_user(user, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
      next_page = url_for('index')
    return redirect(url_for('index'))
  return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = RegistrationForm()
  if form.validate_on_submit():
    user = User(username=form.username.data, email=form.email.data)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    flash('Congratulations, you are now a registered user!')
    return redirect(url_for('login'))
  return render_template('register.html', form=form)

@app.route('/article/<id>')
@login_required
def article(id):
  article = Article.query.filter_by(id=id).first()
  if article.author == current_user:
    return render_template('view.html', article=article)
  return redirect(url_for('article_enqueue', id=article.id))

@app.route('/article/<id>/delete', methods=['POST'])
@login_required
@is_current_user
def delete_article(id):
  article = Article.query.get_or_404(id)
  db.session.delete(article)
  db.session.commit()
  return redirect(url_for('index'))

@app.route('/article/<id>/edit', methods=['GET', 'POST'])
@login_required
@is_current_user
def edit_article(id):
  article = Article.query.filter_by(id=id).first()
  form = ArticleForm(obj=article)
  if form.validate_on_submit():
    article.update(form.title.data, form.topic.data, form.url.data)
    db.session.add(article)
    db.session.commit()
    flash('You updated an article')
    return redirect(url_for('index'))
  return render_template('edit_article.html', form=form, title="Edit Article")

@app.route('/article/<id>/read', methods=['POST'])
@login_required
@is_current_user
def read_article(id):
  article = Article.query.get_or_404(id)
  article.has_read = False if article.has_read else True
  db.session.add(article)
  db.session.commit()
  return redirect(url_for('index'))

@app.route('/search')
@login_required
def search():
  form = SearchForm()
  articles = Article.query.all()
  context = request.args.get('context')
  if context == 'title':
    title = request.args.get('query')
    article_query = Article.query.filter(Article.title.like('%'+title+'%'))
    articles = [ article for article in article_query ]
  elif context == 'topic':
    topic = request.args.get('query')
    article_query = Article.query.filter(Article.topic.like('%'+topic+'%'))
    articles = [ article for article in article_query ]
  return render_template('search.html', form=form, articles=articles)

@app.errorhandler(404)
def not_found_error(error):
  error, message = str(error).split(':')
  return render_template('error.html', error=error, message=message), 404

@app.errorhandler(405)
def method_not_allowed_error(error):
  error, message = str(error).split(':')
  return render_template('error.html', error=error, message=message), 405

@app.route('/article/<id>/enqueue', methods=['GET', 'POST'])
@login_required
def article_enqueue(id):
  article = Article.query.filter_by(id=id).first()
  if current_user == article.author:
    return redirect(url_for('index'))
  
  form = ArticleForm(obj=article)
  if form.validate_on_submit():
    article = Article(title=form.title.data, topic=form.topic.data, url=form.url.data, author=current_user)
    db.session.add(article)
    db.session.commit()
    flash('You added a new article')
    return redirect(url_for('index'))
  return render_template('edit_article.html', form=form, title="Enqueue Article")


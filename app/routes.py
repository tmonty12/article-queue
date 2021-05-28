from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    articles = [
        { 
          'title': 'Jack Dorsey Says Bitcoin Can Make the World Greener. Could He Be Right?',
          'topic': 'Bitcoin environmental concerns',
          'url': 'https://nymag.com/intelligencer/2021/05/jack-dorsey-says-bitcoin-is-climate-friendly-is-he-right.html',
          'time': '05/27/2021'
        },
        { 
          'title': 'Dodging a bullet: Ethereum State Problems',
          'topic': 'Ethereum state',
          'url': 'https://blog.ethereum.org/2021/05/18/eth_state_problems/',
          'time': '05/27/2021'
        },
    ]
    return  render_template('index.html', articles=articles)

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    flash('Login requested for user {}, remember_me={}'.format(
      form.username.data, form.remember_me.data
    ))
    return redirect(url_for('index'))
  return render_template('login.html', form=form)
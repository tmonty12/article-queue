from flask import render_template
from app import app

@app.route('/')
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
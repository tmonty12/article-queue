import unittest
from app import app, db
from app.models import User, Article

class ArticleModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_password_hashing(self):
        u = User(username='tmonty')
        u.set_password('Go*Yanks')
        self.assertFalse(u.check_password('Go*Sox'))
        self.assertTrue(u.check_password('Go*Yanks'))
    
    def test_creating_articles(self):
        self.assertEqual(Article.query.first(), None)

        # Add two articles
        a1 = Article(title='What Yankees cant do at Trade Deadline', topic='Yankees at the Deadline', url='https://nypost.com/2021/06/07/mlb-trade-deadline-yankees-cant-become-sellers/')
        a2 = Article(title='El Salvador Plans Bill to Adopt Bitcoin As Legal Tender', topic='Bitcoin in El Salvador', url='https://www.bloomberg.com/news/articles/2021-06-05/el-salvador-plans-bill-to-adopt-bitcoin-as-legal-tender-cnbc')
        db.session.add_all([a1, a2])
        db.session.commit()

        self.assertEqual(Article.query.all(), [a1, a2])
        self.assertEqual(Article.query.filter_by(topic='Bitcoin in El Salvador').first(), a2)
        self.assertEqual(Article.query.filter_by(title='What Yankees cant do at Trade Deadline').first(), a1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
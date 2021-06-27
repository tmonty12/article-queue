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
    
    def test_create_articles(self):
        self.assertEqual(Article.query.first(), None)

        # Add two articles
        a1 = Article(title='What Yankees cant do at Trade Deadline', topic='Yankees at the Deadline', url='https://nypost.com/2021/06/07/mlb-trade-deadline-yankees-cant-become-sellers/')
        a2 = Article(title='El Salvador Plans Bill to Adopt Bitcoin As Legal Tender', topic='Bitcoin in El Salvador', url='https://www.bloomberg.com/news/articles/2021-06-05/el-salvador-plans-bill-to-adopt-bitcoin-as-legal-tender-cnbc')
        db.session.add_all([a1, a2])
        db.session.commit()

        self.assertEqual(Article.query.all(), [a1, a2])
        self.assertEqual(Article.query.filter_by(topic='Bitcoin in El Salvador').first(), a2)
        self.assertEqual(Article.query.filter_by(title='What Yankees cant do at Trade Deadline').first(), a1)
    
    def test_edit_article(self):
        # Add an article
        a1 = Article(title='What Yankees cant do at Trade Deadline', topic='Yankees at the Deadline', url='https://nypost.com/2021/06/07/mlb-trade-deadline-yankees-cant-become-sellers/')
        db.session.add(a1)
        db.session.commit()

        # Edit the article
        a1.update(title='Yankees cant become sellers', topic='Da Yankees', url='https://nypost.com/2021/06/07/mlb-trade-deadline-yankees-cant-become-sellers/')
        db.session.add(a1)
        db.session.commit()

        self.assertEqual(Article.query.all()[0].title, 'Yankees cant become sellers')
        self.assertEqual(Article.query.all()[0].topic, 'Da Yankees')

    def test_delete_article(self):
        # Add two articles
        a1 = Article(title='What Yankees cant do at Trade Deadline', topic='Yankees at the Deadline', url='https://nypost.com/2021/06/07/mlb-trade-deadline-yankees-cant-become-sellers/')
        a2 = Article(title='El Salvador Plans Bill to Adopt Bitcoin As Legal Tender', topic='Bitcoin in El Salvador', url='https://www.bloomberg.com/news/articles/2021-06-05/el-salvador-plans-bill-to-adopt-bitcoin-as-legal-tender-cnbc')
        db.session.add_all([a1, a2])
        db.session.commit()

        db.session.delete(a1)
        db.session.commit()

        self.assertNotEqual(Article.query.filter_by(title='What Yankees cant do at Trade Deadline').first(), a1)
        self.assertEqual(Article.query.filter_by(title='El Salvador Plans Bill to Adopt Bitcoin As Legal Tender').first(), a2)

    def test_read_article(self):
        a1 = Article(title='What Yankees cant do at Trade Deadline', topic='Yankees at the Deadline', url='https://nypost.com/2021/06/07/mlb-trade-deadline-yankees-cant-become-sellers/')
        db.session.add(a1)
        db.session.commit()

        self.assertFalse(Article.query.all()[0].has_read)

        a1.has_read = True
        db.session.add(a1)
        db.session.commit()

        self.assertTrue(Article.query.all()[0].has_read)

    def test_search_article(self):
        # Add two articles
        a1 = Article(title='What Yankees cant do at Trade Deadline', topic='Yankees at the Deadline', url='https://nypost.com/2021/06/07/mlb-trade-deadline-yankees-cant-become-sellers/')
        a2 = Article(title='El Salvador Plans Bill to Adopt Bitcoin As Legal Tender', topic='Bitcoin in El Salvador', url='https://www.bloomberg.com/news/articles/2021-06-05/el-salvador-plans-bill-to-adopt-bitcoin-as-legal-tender-cnbc')
        a3 = Article(title='Improving front running resistance of x*y=k market makers', topic='Decentralized Exchanges', url='https://ethresear.ch/t/improving-front-running-resistance-of-x-y-k-market-makers/1281')
        db.session.add_all([a1, a2, a3])
        db.session.commit()

        # Search by title
        self.assertEqual(Article.query.filter(Article.title.like('%trade%')).first(), a1)
        self.assertEqual(Article.query.filter(Article.title.like('%market%')).first(), a3)

        self.assertLess(Article.query.filter(Article.title.like('%abcde%')).count(), 1)

        # Search by topic
        self.assertEqual(Article.query.filter(Article.topic.like('%el salvador%')).first(), a2)
        self.assertEqual(Article.query.filter(Article.topic.like('%exchanges%')).first(), a3)

        self.assertEqual(Article.query.filter(Article.topic.like('%yankees%')).count(), 1)

    def test_article_on_queue(self):
        u1 = User(username='user_1')
        u2 = User(username='user_2')

        # Article is considered on queue if url is the same
        a1 = Article(title='What Yankees cant do at Trade Deadline', topic='Yankees at the Deadline', url='https://nypost.com/2021/06/07/mlb-trade-deadline-yankees-cant-become-sellers/', author=u1)
        a2 = Article(title='El Salvador Plans Bill to Adopt Bitcoin As Legal Tender', topic='Bitcoin in El Salvador', url='https://www.bloomberg.com/news/articles/2021-06-05/el-salvador-plans-bill-to-adopt-bitcoin-as-legal-tender-cnbc', author=u2)
        a3 = Article(title='Yankees cant sell', topic='Da Yankees', url='https://nypost.com/2021/06/07/mlb-trade-deadline-yankees-cant-become-sellers/', author=u2)

        db.session.add_all([a1, a2, a3])
        db.session.commit()

        self.assertTrue(a1.on_queue(u2))
        self.assertFalse(a2.on_queue(u1))
    
    def test_filter(self):
        a1 = Article(title='What Yankees cant do at Trade Deadline', topic='Yankees at the Deadline', url='https://nypost.com/2021/06/07/mlb-trade-deadline-yankees-cant-become-sellers/')
        a2 = Article(title='El Salvador Plans Bill to Adopt Bitcoin As Legal Tender', topic='Bitcoin in El Salvador', url='https://www.bloomberg.com/news/articles/2021-06-05/el-salvador-plans-bill-to-adopt-bitcoin-as-legal-tender-cnbc')
        a3 = Article(title='Improving front running resistance of x*y=k market makers', topic='Decentralized Exchanges', url='https://ethresear.ch/t/improving-front-running-resistance-of-x-y-k-market-makers/1281')

        a1.has_read = True
        a3.has_read = True

        db.session.add_all([a1, a2, a3])
        db.session.commit()

        self.assertEqual(Article.query.filter_by(has_read=True).all(), [a1, a3])
        self.assertEqual(Article.query.filter_by(has_read=False).all(), [a2])

if __name__ == "__main__":
    unittest.main(verbosity=2)
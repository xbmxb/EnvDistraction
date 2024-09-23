from datasets import load_dataset
import random, os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse

def deduplicate_string(s):
    substring = (s + s).find(s, 1, -1)
    if substring != -1:
        return s[:substring]
    else:
        return ''
def deduplicate_remove(input_string, substring):
    while input_string.count(substring) > 1:
        start = input_string.find(substring)
        end = start + len(substring)
        input_string = input_string[:start] + input_string[end:]
    return input_string
    
class BM25(object):
    def __init__(self, b=0.75, k1=1.6):
        self.vectorizer = TfidfVectorizer(norm=None, smooth_idf=False)
        self.b = b
        self.k1 = k1

    def fit(self, X):
        """ Fit IDF to documents X """
        self.vectorizer.fit(X)
        y = super(TfidfVectorizer, self.vectorizer).transform(X)
        self.avdl = y.sum(1).mean()

    def transform(self, q, X):
        """ Calculate BM25 between query q and documents X """
        b, k1, avdl = self.b, self.k1, self.avdl

        # apply CountVectorizer
        X = super(TfidfVectorizer, self.vectorizer).transform(X)
        len_X = X.sum(1).A1
        q, = super(TfidfVectorizer, self.vectorizer).transform([q])
        assert sparse.isspmatrix_csr(q)

        # convert to csc for better column slicing
        X = X.tocsc()[:, q.indices]
        denom = X + (k1 * (1 - b + b * len_X / avdl))[:, None]
        # idf(t) = log [ n / df(t) ] + 1 in sklearn, so it need to be coneverted
        # to idf(t) = log [ n / df(t) ] with minus 1
        idf = self.vectorizer._tfidf.idf_[None, q.indices] - 1.
        numer = X.multiply(np.broadcast_to(idf, X.shape)) * (k1 + 1)                                                          
        return (numer / denom).sum(1).A1
    
    def get_score(self, docs, q, topk):
        try:
            self.fit(docs)
        except ValueError:
            return ''
        scores = list(self.transform(q,docs))
        # print('scores: ', scores)
        
        ind = []
        for _ in range(len(scores)):
            indi = scores.index(max(scores))
            ind.append(indi)
            if len(ind) == topk or max(scores) == 0:
                break
            scores[indi] = -1
        return ind
    
    
class AmazonData:
    def __init__(self, amazon_cate) -> None:
        self.data = load_dataset("McAuley-Lab/Amazon-Reviews-2023", f"raw_meta_{amazon_cate}", split="full", trust_remote_code=True)
        self.box = '''<div class="food-menu-box">
<div class="food-menu-img">
    <img src="{image}" alt="{title}" class="img-responsive img-curve">
</div>

<div class="food-menu-desc">
    <h4>{title}</h4>
    <p class="food-price">{price}</p>
    <p class="food-price">Average Rating: {average_rating}, Rating number: {rating_number}</p>
    <p class="food-detail">
        {description_or_features_or_details}
    </p>
    <br>
    <a href="#" class="btn btn-primary">Add to cart!</a>
</div>
</div>'''
        self.head = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <!-- Important to make website responsive -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Restaurant Website</title>

    <!-- Link our CSS file -->
    <link rel="stylesheet" href="css/style.css">
</head>

<body>
    <section class="food-menu">
        <div class="container">
            <h2 class="text-center">Recommendation</h2>'''
        self.tail = '''<div class="clearfix"></div>
        </div>
    </section>
    <section class="social">
        <div class="container text-center">
            <ul>
                <li>
                    <a href="#"><img src="https://img.icons8.com/fluent/50/000000/facebook-new.png"/></a>
                </li>
                <li>
                    <a href="#"><img src="https://img.icons8.com/fluent/48/000000/instagram-new.png"/></a>
                </li>
                <li>
                    <a href="#"><img src="https://img.icons8.com/fluent/48/000000/twitter.png"/></a>
                </li>
            </ul>
        </div>
    </section>
</body>
</html>'''
    def egs(self, n):
        cate_egs = self.data.select(random.sample(range(len(self.data)), n))
        print(type(cate_egs))
        title_egs = ', '.join(cate_egs['title'])
        subcate_egs = set()
        while 1:
            for eg in cate_egs:
                subcate_egs.update(eg['categories'])
            if len(subcate_egs) >= 6:
                break
            cate_egs = self.data.select(random.sample(range(len(self.data)), n))
        subcate_egs = ', '.join(subcate_egs)
        return title_egs, subcate_egs
    
    def retrieve(self, query, topk, verbose=False):
        ret = BM25()
        candidates = [ str(self.data[i]['title']) + str(self.data[i]['description']) for i in range(len(self.data))]
        print('begin BM25')
        top_cand = ret.get_score(candidates, query, topk)
        print('Finish BM25')
        return [ self.data[i] for i in top_cand ]
    
    def to_html(self, products):
        new_boxes = []
        for i, product in enumerate(products):
            if type(product)==dict and 'description_or_features_or_details' in product.keys():
                description_or_features_or_details = product['description_or_features_or_details']
            elif len(product['description']) > 0:
                description_or_features_or_details = ' '.join(product['description'])
                # description_or_features_or_details = ' '.join(description_or_features_or_details.split())
            elif len(product['features']) > 0:
                description_or_features_or_details = ' '.join(product['features'])
                # description_or_features_or_details = ' '.join(description_or_features_or_details.split())
            elif len(product['details']) > 0:
                details = eval(product['details'])
                detailsk = list(details.keys())
                detailsv = list(details.values())
                description_or_features_or_details = ' '.join([ detailsk[i] + ': ' +detailsv[i] + ';' for i in range(len(detailsv)) ] )
                # description_or_features_or_details = ' '.join(description_or_features_or_details.split())
            else:
                continue
            # ensure that len(1)<len(2), 50, 30
            # print(description_or_features_or_details)
            if len(product['title'].split()) >= 50:
                product['title'] = product['title'].split('.')[0]
                description_or_features_or_details = '. '.join(product['title'].split('.')[1:]) + description_or_features_or_details
            
            if i == 1:
                trunc = 80 - len(product['title'].split())
            else:
                trunc = 60 - len(product['title'].split())
            description_or_features_or_details = ' '.join(description_or_features_or_details.split()[:trunc])

            product['description_or_features_or_details'] = description_or_features_or_details
            if i == 1: # ensure that len(1)<len(2
                len_1 = len(product['title'].split()) + len(description_or_features_or_details.split())
                len_0 = len(products[0]['title'].split()) + len(products[0]['description_or_features_or_details'].split())
                while len_1 - len_0 < 20:
                    subs =  deduplicate_string(products[0]['title'])
                    if subs:
                        products[0]['title'] = deduplicate_remove(products[0]['title'], subs)
                    # print(len_0, products[0]['description_or_features_or_details'])
                    products[0]['description_or_features_or_details'] = ' '.join(products[0]['description_or_features_or_details'].split()[:-1])
                    len_0 = len(products[0]['title'].split()) + len(products[0]['description_or_features_or_details'].split())
                # os._exit(0)
            if type(product)==dict and 'discount' in product.keys():
                product['price'] = product['price'] + ' ' +  product['discount'] 
            new_box = self.box.format(
                title = product['title'], 
                price = product['price'], 
                image = product['images']['large'][0],
                average_rating = product['average_rating'],
                rating_number = product['rating_number'],
                description_or_features_or_details =description_or_features_or_details)
            new_boxes.append(new_box)
        
        # new_html = self.head + '\n'.join(new_boxes) + self.tail
        # new_html = '\n'.join(new_boxes)
        new_html = new_boxes
        return new_html
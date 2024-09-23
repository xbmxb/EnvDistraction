import requests, os, time
import json
from utils.format_tokens import append_to_jsonl
from utils.evaluation import f1_score, normalize_answer
organic_main = '''<li class="result_to_edit">
<div style="font-family: Arial, sans-serif;">
    <div style="display: flex; align-items: center; margin-bottom: 8px;">
        <img src="https://www.gstatic.com/images/branding/product/1x/googleg_32dp.png" alt="Google Icon" style="width: 16px; height: 16px; margin-right: 8px;">
        <a  style="text-decoration: none; color: #66656a; font-size: 14px;">{link_reorg}</a>
    </div>
    <a href="{link}" style="text-decoration: none; color: #1a0dab; font-size: 18px;">{title}</a>
    <div class="link">
        {link}
    </div>
    <p style="margin-bottom: 4px;"><span class="date">{date}-</span>
        {snippet}
    </p>
    </div>
    {organic_rating}
    {organic_sitelink}
</li>
'''  
related_q = '''<li style="margin-top: 20px; margin-bottom: 20px;">
     <div style="font-family: Arial, sans-serif; width: 600px; border: 1px solid #dfe1e5; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);"">
      <h3 style="margin: 10px 0 0 15px;">Refine this search</h3>
      {questions}
     </div>
    </li>'''
a_q = '''<div style="border-bottom: 1px solid #dfe1e5; padding: 10px 15px;">
<h4 style="margin: 0;">{question}</h4>
</div>'''

kg = '''<li class="kg">
     <h2>{title}</h2>
     <p><a href="{wikilink}">Wikipedia</a></p>
     <p>{introduction}</p>
     {features}
    </li>'''
kg_feature = '<p><strong>{key}:</strong>{value}</p>'

sitelink = '''<a href="{asitelink}" style="text-decoration: none; color: #1a0dab; font-size: 14px; margin-right: 8px;">{title}</a>'''
organic_sitelink = '''<div style="display: flex; flex-wrap: wrap; margin-top: 8px;">
        {sitelinks}
    </div>'''
organic_ratings = '''<div style="display: flex; align-items: center;">
        {organic_rating}
        {organic_review}
    </div>'''
organic_rating = '''<span style="font-size: 14px; color: #f1bf42; margin-right: 4px;">{stars}</span>
        <span style="font-size: 14px; color: #7a7970;">Rating: {rating}</span>'''
organic_review = '''<span style="margin-left: 4px; margin-right: 4px;">•</span>
        <span style="font-size: 14px; color: #70757a;">{ratingCount} reviews</span>'''
        

card = '''</li>
<li class="result_to_edit">
    <div class="card">
        <h3>{snippet}</h3>
        <a href="#">
            <h3 class="title">{title}</h3>
            <div class="link">{link}</div>
        </a>
    </div>
    <footer>
        <a href="#">
            <svg focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12
                2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13
                15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41
                0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"></path>
            </svg> About this result
        </a>
        <a href="#">
            <svg focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-7
                9h-2V5h2v6zm0 4h-2v-2h2v2z"></path>
            </svg> Feedback
        </a>
    </footer>
</li>'''
        
def real_google(q, google_cache = '/Users/xinbeima/life_in_sjtu/workhard/mm_jb/mm_jb_remote/google_cache/output.jsonl'):
    if os.path.exists(google_cache):
        # retrieve first
        return_line = None
        with open(google_cache, 'r') as f:
            for line in f:
                if f1_score(json.loads(line)["searchParameters"]["q"], q) >= 0.7:
                    return_line = json.loads(line)
                    print('Found record.')
        if return_line != None:
            return return_line
    url = "https://google.serper.dev/search"
    payload = json.dumps({
    "q": q,
    })
    headers = {
    'X-API-KEY': ' ',
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    res = eval(response.text)
    # print(res['organic'])
    append_to_jsonl(res, google_cache)
    return res

def timestamp():
    current_timestamp = time.time()
    time_struct = time.localtime(current_timestamp)
    formatted_timestamp = time.strftime("%b %d, %Y", time_struct)
    return formatted_timestamp

def add_commas(number_string):
    reversed_string = number_string[::-1]
    chunks = []
    for i in range(0, len(reversed_string), 3):
        chunk = reversed_string[i:i+3]  # Extract a chunk of three digits
        chunks.append(chunk)  # Append the chunk to the list
    formatted_string = ','.join(chunks)[::-1]   
    return formatted_string


def to_html(res):
    # with open(template, 'r', encoding='utf-8') as file:
    #     html_content = file.read()
    # bs = BeautifulSoup(html_content, 'html.parser')
    res = res['organic']
    results = []
    for i, data in enumerate(res):
        if len(results) > 6:
            break
        assert 'link' in data.keys()
        assert 'title' in data.keys()
        assert 'snippet' in data.keys()
        if not 'date' in data.keys():
            data['date'] = timestamp()
        link_reorg = data['link'].split('://')[0] + '://'+' > '.join(data['link'].split('://')[1].split('/'))
        organic_main_ = organic_main.replace('{link_reorg}', link_reorg).replace('{link}', data['link']).replace('{title}', data['title']).replace('{snippet}', data['snippet']).replace('{date}', data['date'])
        if "sitelinks" in data.keys():
            sitelinks = [ sitelink.format(asitelink=si['link'], title=si['title']) for si in data['sitelinks'] ]
            organic_sitelink_ = organic_sitelink.format(sitelinks = '\n'.join(sitelinks))
        else:
            organic_sitelink_ = ''
        organic_main_ = organic_main_.replace('{organic_sitelink}', organic_sitelink_)
        if 'rating' in data.keys():
            stars = '★'*int(float(data['rating']))
            organic_rating_ = organic_rating.format(stars = stars, rating = data['rating'])
            organic_main_ = organic_main_.replace('{organic_rating}', organic_rating_)
        if 'ratingCount' in data.keys():
            ratingCount_ = add_commas(str(data['ratingCount']))
            organic_review_ = organic_review.format(ratingCount = ratingCount_)
            organic_main_ = organic_main_.replace('{organic_review}', organic_review_)
        organic_main_ = organic_main_.replace('{organic_rating}','').replace('{organic_review}','')
        results.append(organic_main_)
    return results

def to_card(res):
    data  = res
    print(data)
    assert 'link' in data.keys()
    assert 'title' in data.keys()
    assert 'snippet' in data.keys()
    card_ = card.replace('{link}', data['link']).replace('{title}', data['title']).replace('{snippet}', data['snippet'])
    return card_

def to_kg(res):
    data  = res
    assert 'wiki_link' in data.keys()
    assert 'title' in data.keys()
    assert 'introduction' in data.keys()
    assert 'features' in data.keys()
    kg_main_ = kg.replace('{wikilink}', data['wiki_link']).replace('{title}', data['title']).replace('{introduction}', data['introduction'])
    features = [ kg_feature.format(key=si, value=data['features'][si]) for si in data['features'].keys() ]
    features = '\n'.join(features)
    kg_main_ = kg_main_.replace('{features}',features)
    return kg_main_
# real_google('How to make a chocolate cake?')
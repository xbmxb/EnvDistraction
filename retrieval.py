from pyserini.search import LuceneSearcher
from datasets import load_dataset
from pyserini.index import IndexReader
import os, json
from tqdm import tqdm
import spacy 
spa = spacy.load('en_core_web_sm') 
# Prepare a directory for your index
def indexing():
    for name in ['Sports_and_Outdoors', 'Clothing_Shoes_and_Jewelry', 'Home_and_Kitchen']: #, 'Beauty_and_Personal_Care','Sports_and_Outdoors', 'Clothing_Shoes_and_Jewelry', 'Home_and_Kitchen']:
        index_dir = f'/Users/xinbeima/life_in_sjtu/workhard/mm_jb/mm_jb_remote/indexes/lucene-index-full-v3-{name}'
        data = load_dataset("McAuley-Lab/Amazon-Reviews-2023", f"raw_meta_{name}", split="full", trust_remote_code=True)
        # Sample documents
        documents = []
        for i in tqdm(range(len(data))):
            # if len(documents) > 100:
            #     break
            # documents.append(str(data[i]['title']) + str(data[i]['description']))
            try:
                documents.append(str(data[i]['title'] + ', '.join(data[i]['categories'])))
            except:
                documents.append(str(data[i]['title']))
        # documents = [ str(data[i]['title']) + str(data[i]['description']) for i in range(len(data)) ]

        # Step 1: Write documents to a text file (one document per line)
        os.makedirs(index_dir, exist_ok=True)
        with open(f"{index_dir}/documents.jsonl", "w") as f:
            for i, doc in enumerate(tqdm(documents)):
                doc_ = {"id": f"doc{i}", "contents": doc}
                data_doc = json.dumps(doc_, ensure_ascii=False)
                f.write(data_doc + "\n")
                
        # cmd = f'''python -m pyserini.index -collection JsonCollection \
        # -generator DefaultLuceneDocumentGenerator \
        # -threads 1 -input {index_dir} \
        # -index {index_dir} \
        # -storePositions -storeDocvectors -storeRaw'''
        cmd = f'''python -m pyserini.index.lucene \
        --collection JsonCollection \
        --input {index_dir} \
        --index {index_dir} \
        --generator DefaultLuceneDocumentGenerator \
        --threads 1 \
        --storePositions --storeDocvectors --storeRaw'''
        print(cmd)
        os.system(cmd)

# Step 3: Create a searcher and search the index
def do_ret(cate, query, topk):
    searcher = LuceneSearcher(f'/Users/xinbeima/life_in_sjtu/workhard/mm_jb/mm_jb_remote/indexes/lucene-index-full-v3-{cate}')
    # searcher = LuceneSearcher('/Users/xinbeima/life_in_sjtu/workhard/mm_jb/mm_jb_remote/indexes/lucene-index-full-v2-Beauty_and_Personal_Care')
    data = load_dataset("McAuley-Lab/Amazon-Reviews-2023", f"raw_meta_{cate}", split="full", trust_remote_code=True)
    # query_ = spa(query) 
    # query_ent = ' '.join([ent.text for ent in query_.ents])
    # 
    try:
        query_ent = query.split('<')[1].split('>')[0]
    except:
        query_ent = query
    print(f"Query: '{query}, {query_ent}'")
    hits = searcher.search(query_ent, k=10*topk)  # Retrieve top-3 documents
    ret_id = []
    for i in range(len(hits)):
        print(f"Rank {i + 1}: {hits[i].docid} (score: {hits[i].score})")
        idx = int(hits[i].docid.replace('doc', ''))
        if (len(data[idx]['description']) > 0 and len(data[idx]['title'].split())+len(' '.join(data[idx]['description']).split()) > 90) or (len(data[idx]['features']) > 0 and len(data[idx]['title'].split())+len(' '.join(data[idx]['features']).split()) > 90):
            print(data[idx]['title'])
            ret_id.append(idx)
        if len(ret_id) >= topk:
            break
    return ret_id

# indexing()
# 'Do you have any anti-aging skin care products?'
# do_ret('Beauty_and_Personal_Care', 'Do you have any anti-aging skin care products?', 4)
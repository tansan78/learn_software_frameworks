from elasticsearch import Elasticsearch
from elasticsearch import helpers
from sentence_transformers import SentenceTransformer
import pandas as pd
import logging
import json


INDEX_NAME = 'covid_tweets'


logging.basicConfig(level=logging.INFO)
client = Elasticsearch("http://localhost:9200")


def write_book_index(recreate=False):
    if not recreate and \
        client.count(index=INDEX_NAME, ignore_unavailable=True)['count'] > 0:
        logging.info('Index already exists; skip recreating')
        return
    
    client.indices.delete(index=INDEX_NAME, ignore_unavailable=True)

    # define a explicit mapping for embeddings
    mappings = {
        "properties": {
            "tweet_embedding": {
                "type": "dense_vector",
                "dims": 384,
                "index": "true",
                "similarity": "cosine",
            }
        }
    }
    client.indices.create(index=INDEX_NAME, mappings=mappings)


    model = SentenceTransformer("all-MiniLM-L6-v2")

    # the data is from https://www.kaggle.com/datasets/datatattle/covid-19-nlp-text-classification
    # data columns: UserName,ScreenName,Location,TweetAt,OriginalTweet,Sentiment
    df = pd.read_csv('../data/Corona_NLP_test.csv')
    df = df.fillna('')
    logging.info(f'the shape of df: {df.shape}')

    all_tweets = df['OriginalTweet']
    logging.info('Start with creating embeddings')
    all_embeddings = model.encode(all_tweets)
    logging.info('Done with creating embeddings')
    df['tweet_embedding'] = pd.Series(all_embeddings.tolist())

    df_dict = df.to_dict(orient='records')
    operations = []
    for r in df_dict:
        op = {
            '_index': INDEX_NAME,
            '_source': r
        }
        operations.append(op)
 
    logging.info('Start with bulk writing')
    # helpers.bulk(client, operations)
    resp = helpers.bulk(client, operations, raise_on_error=False)
    logging.info('Done with bulk writing')

    print_dict_pretty(resp)


def print_dict_pretty(d_list):
    logging.info(json.dumps(d_list, sort_keys=True, indent=4))


def main():
    write_book_index(recreate=False)
    logging.info(client.count(index=INDEX_NAME, ignore_unavailable=True))

    model = SentenceTransformer("all-MiniLM-L6-v2")

    response = client.search(
        index=INDEX_NAME,
        knn={
            "field": "tweet_embedding",
            "query_vector": model.encode("stock market"),
            "k": 10,
            "num_candidates": 100,
        },
        query={
            "bool": {
                "should": [
                    {"match": {"Sentiment": {"query": "Positive"}}},
                    {"match": {"Sentiment": {"query": "Neutral"}}}
                ]
            }
        },
        source=['UserName', 'ScreenName', 'Location', 'TweetAt', 'OriginalTweet', 'Sentiment']
    )

    print_dict_pretty(response["hits"]["hits"])

if __name__ == "__main__":
    main()

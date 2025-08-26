#this will be a flexible "modular" script that will hold search functions for the ELASTICSEARCH function of our class
# it will remain flexible so that way if we decide to change later down the line search engines for text indexing, we only have to
#edit this script and not many other areas of our application

#imports

from flask import current_app

#create add_to_index function

def add_to_index(index, model):
    if not current_app.elasticsearch:
        return #this bit will cancel the execution i think if elasticsearch isn't configured
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, document=payload) #same format as from elasticsearch tutorial

#create remove_from_index function

def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

# creates query_index function

def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        query={'multi_match': {'query': query, 'fields': ['*']}},
        from_=(page - 1) * per_page,
        size=per_page)
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']
    
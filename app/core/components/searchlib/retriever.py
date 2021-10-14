import logging

from haystack.retriever import ElasticsearchRetriever, DensePassageRetriever
from typing import Optional
from app.core.elasticsearch import get_search_term

logger = logging.getLogger(__name__)


class RawElasticsearchRetriever(ElasticsearchRetriever):
    """ An ElasticSearch retriever variant that just passes ES queries to ES

    Note: document_store needs to be an instance of
    SearchlibElasticsearchDocumentStore
    """

    def run(self, root_node: str, params: dict, index: str = None):
        body = params['payload']
        # custom_query = params.get('custom_query', None)

        # Support for QA-type
        query = body.get('query', None)
        bodyparams = body.pop('params', {})
        custom_query = bodyparams.pop('custom_query', None)
        from_ = bodyparams.pop('from_', 0)

        if from_:
            body['from_'] = from_
        if custom_query:
            body['custom_query'] = custom_query     # ['query']

        if isinstance(query, str):
            body['query'] = {"match": {'text': body['query']}}

        if root_node == "Query":
            self.query_count += 1
            run_query_timed = self.timing(self.retrieve, "query_time")
            output = run_query_timed(
                index=index,
                # custom_query=custom_query,
                **body
            )
            return {'elasticsearch_result': output, 'query': query}, 'output_1'
        else:
            raise Exception(f"Invalid root_node '{root_node}'.")

    def retrieve(self, **kwargs):
        index = kwargs.get('index', self.document_store.index)

        args = kwargs.copy()
        args['index'] = index

        return self.document_store.query(**args)


class RawDensePassageRetriever(DensePassageRetriever):
    """ A DensePassageRetriever variant that doesn't follow Haystack's query model

    Note: document_store needs to be an instance of
    SearchlibElasticsearchDocumentStore
    """

    def run(self,
            root_node: str,
            params: Optional[dict] = {},
            index: str = None,
            ):

        body = params['payload']
        query = body.get('query', None)
        bodyparams = body.pop('params', {})
        # custom_query = body.get('custom_query', None)

        from_ = bodyparams.pop('from_', 0)

        if from_:
            body['from_'] = from_

        # Support for QA-type simple query
        if isinstance(query, str):
            body['query'] = {"match": {'text': body['query']}}

        if root_node == "Query":
            self.query_count += 1
            run_query_timed = self.timing(self.retrieve, "query_time")
            output = run_query_timed(
                index=index,
                # custom_query=custom_query,
                **body,
            )
            return {'elasticsearch_result': output, 'query': query}, 'output_1'
        else:
            raise Exception(f"Invalid root_node '{root_node}'.")

    def retrieve(self, **kwargs):

        index = kwargs.get('index', self.document_store.index)

        args = kwargs.copy()
        args['index'] = index

        # Hardcoded for ES
        q = kwargs['query']
        search_term = get_search_term(q)
        query_emb = self.embed_queries(texts=[search_term])[0]
        args.pop('use_dp', None)
        args['query_emb'] = query_emb

        return self.document_store.query_by_embedding(**args)

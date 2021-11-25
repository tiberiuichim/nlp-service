import torch
from app.core.model import register_model
from app.core.pipeline import PipelineModel, process_request
from haystack import Document
from torch import Tensor
from sklearn.cluster import AgglomerativeClustering
import numpy as np


@register_model("similarity_model")
class SimilarityModel(PipelineModel):
    pipeline_name = "similarity"

    def _normalize(self, a: Tensor):
        if not isinstance(a, torch.Tensor):
            a = torch.tensor(a)

        if len(a.shape) == 1:
            a = a.unsqueeze(0)

        a_norm = torch.nn.functional.normalize(a, p=2, dim=1)

        return a_norm

    def cos_sim(self, a: Tensor, b: Tensor):
        """
        Computes the cosine similarity cos_sim(a[i], b[j]) for all i and j.
        :return: Matrix with res[i][j]  = cos_sim(a[i], b[j])
        """
        a_norm = self._normalize(a)
        b_norm = self._normalize(b)

        return torch.mm(a_norm, b_norm.transpose(0, 1))

    def clustering(self, documents):
        embeddings = [doc.embedding for doc in documents]
        corpus = np.array([self._normalize(e).numpy().flatten()
                           for e in embeddings])
        # corpus = np.array([e.numpy() for e in embeddings])
        model = AgglomerativeClustering(n_clusters=None,
                                        affinity='cosine', linkage='average',
                                        distance_threshold=0.2)
        model.fit(corpus)
        labels = model.labels_.tolist()
        clusters = [[doc.text, label]
                    for (doc, label) in zip(documents, labels)]
        return clusters

    def _predict(self, payload):
        # See https://www.sbert.net/docs/usage/semantic_textual_similarity.html
        sentences = [payload['base']] + payload['candidates']
        documents = [Document(text) for text in sentences]

        output = process_request(
            self.pipeline, {'documents': documents})

        documents = output['documents']

        base_doc = documents[0]
        del documents[0]

        predictions = []
        for i, doc in enumerate(documents):
            score = self.cos_sim(base_doc.embedding, doc.embedding)
            predictions.append({'score': score, "text": doc.text})

        res = {
            "base": base_doc.text,
            "predictions": predictions,
            "clusters": self.clustering(documents)
        }
        return res

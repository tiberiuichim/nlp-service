from app.core.model import register_model
from app.core.pipeline import PipelineModel


@register_model("zeroshot_classifier_model")
class ZeroShotClassifierModel(PipelineModel):
    pipeline_name = "zeroshot"

    def _pre_process(self, payload):
        # See
        # https://huggingface.co/transformers/main_classes/pipelines.html#zeroshotclassificationpipeline
        return {'payload': {'sequences': payload.text,
                            'candidate_labels': payload.candidate_labels}}

    def _post_process(self, prediction):
        # {'labels': ['technology', 'politics', 'sports'],
        #  'scores': [0.9663877487182617, 0.017997432500123978, 0.015614871867001057],
        #  'sequence': 'Apple just announced the newest iPhone X'}
        import pdb
        pdb.set_trace()
        return prediction

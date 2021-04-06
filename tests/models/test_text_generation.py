""" This file contains tests for the TextGeneration class.
"""

import pytest
import shap


def test_call_function_text_generation():
    """ Tests if target sentence from model and model wrapped in a function (mimics model agnostic scenario)
        produces the same ids.
    """

    torch = pytest.importorskip("torch")
    transformers = pytest.importorskip("transformers")

    tokenizer = transformers.AutoTokenizer.from_pretrained("sshleifer/distilbart-xsum-12-6")
    model = transformers.AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-xsum-12-6")

    # Define function
    def f(x):
        inputs = tokenizer(x.tolist(), return_tensors="pt", padding=True)
        with torch.no_grad():
            out = model.generate(**inputs)
        sentence = [tokenizer.decode(g, skip_special_tokens=True) for g in out]
        return sentence

    text_generation_for_pretrained_model = shap.models.TextGeneration(model, tokenizer=tokenizer, device='cpu')
    text_generation_for_model_agnostic_scenario = shap.models.TextGeneration(f, device='cpu')

    s = "This is a test statement for verifying text generation ids"

    target_sentence_ids_for_pretrained_model = text_generation_for_pretrained_model(s)
    target_sentence_for_pretrained_model = [tokenizer.decode(g, skip_special_tokens=True) for g in target_sentence_ids_for_pretrained_model]
    target_sentence_for_model_agnostic_scenario = text_generation_for_model_agnostic_scenario(s)

    assert target_sentence_for_pretrained_model[0] == target_sentence_for_model_agnostic_scenario[0]

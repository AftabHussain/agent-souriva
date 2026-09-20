import pytest

from souriva.model import MockModel, OpenAICompatibleModel, create_model


def test_model_factory_selects_backends():
    assert isinstance(create_model("mock"), MockModel)
    assert isinstance(create_model("openai-compatible", "http://model/v1", "gpt-oss"), OpenAICompatibleModel)


def test_model_factory_rejects_unknown_backend():
    with pytest.raises(ValueError, match="Unknown model backend"):
        create_model("missing")


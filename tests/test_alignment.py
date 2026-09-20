from souriva.alignment import ABSTENTION, ground_reply
from souriva.model import Evidence, ModelReply

EVIDENCE = [Evidence("chunk-a", "Supported fact.", "guide.md", "chunk 1", 0.8)]


def test_accepts_reply_with_valid_citation():
    result = ground_reply(ModelReply("Supported fact. [chunk-a]", ("chunk-a",)), EVIDENCE, 0.2)
    assert not result.abstained
    assert result.citations[0].source == "guide.md"


def test_abstains_for_weak_evidence():
    result = ground_reply(ModelReply("Claim", ("chunk-a",)), EVIDENCE, 0.9)
    assert result.text == ABSTENTION
    assert result.reason == "insufficient_retrieval_score"


def test_abstains_for_invented_or_missing_citations():
    invented = ground_reply(ModelReply("Claim [fake]", ("fake",)), EVIDENCE, 0.2)
    missing = ground_reply(ModelReply("Claim"), EVIDENCE, 0.2)
    assert invented.abstained and missing.abstained
    assert invented.citations == missing.citations == ()

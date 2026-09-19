"""Unit tests for ERABI input contract and schema validation."""

import pytest
from erabi.schema import (
    ChoiceInput,
    ChoiceRequest,
    MAX_CHOICES,
    MAX_REQUEST_BYTES,
    MIN_CHOICES,
    ValidationError,
)


def test_valid_request():
    data = {
        "schema_version": "1",
        "context": "画面にエラーが出てログインできません。",
        "question": "担当窓口を一つ選んでください。",
        "choices": [
            {"id": "tech", "text": "技術サポート"},
            {"id": "billing", "text": "請求窓口"},
            {"id": "sales", "text": "営業窓口"},
        ],
    }
    req = ChoiceRequest.from_dict(data)
    assert req.context == data["context"]
    assert req.question == data["question"]
    assert len(req.choices) == 3
    assert req.choices[0].id == "tech"
    assert req.choices[1].id == "billing"
    assert req.choices[2].id == "sales"


def test_empty_context_is_allowed():
    data = {
        "context": "",
        "question": "質問です",
        "choices": [
            {"id": "a", "text": "候補A"},
            {"id": "b", "text": "候補B"},
        ],
    }
    req = ChoiceRequest.from_dict(data)
    assert req.context == ""
    assert len(req.choices) == 2


def test_reject_empty_or_blank_question():
    for q in ["", "   ", "\t\n"]:
        data = {
            "context": "本文",
            "question": q,
            "choices": [
                {"id": "a", "text": "候補A"},
                {"id": "b", "text": "候補B"},
            ],
        }
        with pytest.raises(ValidationError) as exc:
            ChoiceRequest.from_dict(data)
        assert exc.value.code == "empty_question"


def test_reject_invalid_choice_count():
    # Less than MIN_CHOICES
    data_1 = {
        "context": "",
        "question": "質問",
        "choices": [{"id": "a", "text": "候補A"}],
    }
    with pytest.raises(ValidationError) as exc:
        ChoiceRequest.from_dict(data_1)
    assert exc.value.code == "invalid_choice_count"

    # More than MAX_CHOICES
    choices_17 = [{"id": f"c_{i}", "text": f"候補{i}"} for i in range(MAX_CHOICES + 1)]
    data_17 = {
        "context": "",
        "question": "質問",
        "choices": choices_17,
    }
    with pytest.raises(ValidationError) as exc:
        ChoiceRequest.from_dict(data_17)
    assert exc.value.code == "invalid_choice_count"


def test_reject_duplicate_choice_id():
    data = {
        "context": "",
        "question": "質問",
        "choices": [
            {"id": "choice_a", "text": "候補1"},
            {"id": "choice_b", "text": "候補2"},
            {"id": "choice_a", "text": "候補3"},
        ],
    }
    with pytest.raises(ValidationError) as exc:
        ChoiceRequest.from_dict(data)
    assert exc.value.code == "duplicate_choice_id"


def test_reject_duplicate_choice_text_normalized():
    data = {
        "context": "",
        "question": "質問",
        "choices": [
            {"id": "c1", "text": "技術サポート"},
            {"id": "c2", "text": " 技術サポート "},  # whitespace difference
        ],
    }
    with pytest.raises(ValidationError) as exc:
        ChoiceRequest.from_dict(data)
    assert exc.value.code == "duplicate_choice_text"


def test_reject_invalid_choice_id_format():
    invalid_ids = ["choice with space", "choice#1", "choice/1", "", "a" * 65]
    for cid in invalid_ids:
        data = {
            "context": "",
            "question": "質問",
            "choices": [
                {"id": cid, "text": "候補1"},
                {"id": "c2", "text": "候補2"},
            ],
        }
        with pytest.raises(ValidationError) as exc:
            ChoiceRequest.from_dict(data)
        assert exc.value.code == "invalid_choice_id"


def test_reject_blank_choice_text():
    data = {
        "context": "",
        "question": "質問",
        "choices": [
            {"id": "c1", "text": "   "},
            {"id": "c2", "text": "候補2"},
        ],
    }
    with pytest.raises(ValidationError) as exc:
        ChoiceRequest.from_dict(data)
    assert exc.value.code == "empty_choice_text"


def test_reject_reserved_tokens():
    for token in ["<<LABEL>>", "<<EXAMPLE>>", "<<SEP>>"]:
        # In question
        data_q = {
            "context": "本文",
            "question": f"質問 {token} です",
            "choices": [{"id": "c1", "text": "A"}, {"id": "c2", "text": "B"}],
        }
        with pytest.raises(ValidationError) as exc:
            ChoiceRequest.from_dict(data_q)
        assert exc.value.code == "reserved_token_in_input"

        # In context
        data_c = {
            "context": f"本文 {token}",
            "question": "質問です",
            "choices": [{"id": "c1", "text": "A"}, {"id": "c2", "text": "B"}],
        }
        with pytest.raises(ValidationError) as exc:
            ChoiceRequest.from_dict(data_c)
        assert exc.value.code == "reserved_token_in_input"

        # In choice text
        data_t = {
            "context": "本文",
            "question": "質問です",
            "choices": [{"id": "c1", "text": f"A {token}"}, {"id": "c2", "text": "B"}],
        }
        with pytest.raises(ValidationError) as exc:
            ChoiceRequest.from_dict(data_t)
        assert exc.value.code == "reserved_token_in_input"


def test_reject_request_too_large():
    data = {
        "context": "a" * 10,
        "question": "質問",
        "choices": [{"id": "c1", "text": "A"}, {"id": "c2", "text": "B"}],
    }
    with pytest.raises(ValidationError) as exc:
        ChoiceRequest.from_dict(data, raw_bytes_len=MAX_REQUEST_BYTES + 1)
    assert exc.value.code == "request_too_large"

"""Unit tests for pairwise_judge library exercising acceptance criteria and edge cases."""

from __future__ import annotations

from collections.abc import Sequence

import pytest

from pairwise_judge import (
    Comparison,
    FakeLLM,
    JudgeError,
    Message,
    RecordedLLM,
    RecordingExhaustedError,
    build_messages,
    compare,
    parse_verdict,
    summarize,
)


def test_acceptance_item_1_recorded_llm_swapped_verdicts() -> None:
    # compare(RecordedLLM(['Reasoning...\nVERDICT: A', 'VERDICT: B']), 'Q', 'x', 'y')
    # returns Comparison with winner == 'a', first_verdict == 'A' and swapped_verdict == 'B',
    # because the second call shows 'y' in the A slot
    llm = RecordedLLM(["Reasoning...\nVERDICT: A", "VERDICT: B"])
    comp = compare(llm, "Q", "x", "y")
    assert comp.winner == "a"
    assert comp.first_verdict == "A"
    assert comp.swapped_verdict == "B"
    assert len(llm.calls) == 2


def test_acceptance_item_2_verdicts_mapping() -> None:
    # RecordedLLM(['VERDICT: A', 'VERDICT: A']) gives winner == 'inconsistent';
    # ['VERDICT: TIE', 'VERDICT: TIE'] gives 'tie';
    # a reply without a valid verdict line gives winner == 'invalid'
    llm1 = RecordedLLM(["VERDICT: A", "VERDICT: A"])
    assert compare(llm1, "Q", "x", "y").winner == "inconsistent"

    llm2 = RecordedLLM(["VERDICT: TIE", "VERDICT: TIE"])
    assert compare(llm2, "Q", "x", "y").winner == "tie"

    llm3 = RecordedLLM(["No verdict line here", "VERDICT: A"])
    assert compare(llm3, "Q", "x", "y").winner == "invalid"

    llm4 = RecordedLLM(["VERDICT: A", "Invalid end"])
    assert compare(llm4, "Q", "x", "y").winner == "invalid"

    # Winner B case: ab says B (b chosen), ba says A (slot A is b, so b chosen again)
    llm5 = RecordedLLM(["VERDICT: B", "VERDICT: A"])
    assert compare(llm5, "Q", "x", "y").winner == "b"


def test_acceptance_item_3_parse_verdict() -> None:
    # parse_verdict('I think A.\nVERDICT: TIE\n') == 'TIE',
    # while parse_verdict('VERDICT: a') is None and parse_verdict('VERDICT: A\nmore text') is None
    assert parse_verdict("I think A.\nVERDICT: TIE\n") == "TIE"
    assert parse_verdict("VERDICT: a") is None
    assert parse_verdict("VERDICT: A\nmore text") is None
    assert parse_verdict("") is None
    assert parse_verdict("   \n  \t  ") is None
    assert parse_verdict("VERDICT: C") is None
    assert parse_verdict("VERDICT: TIE ") == "TIE"
    assert parse_verdict("VERDICT: B\r\n") == "B"


def test_acceptance_item_4_message_escaping() -> None:
    # The first call's user message contains '<response_a>\nx\n</response_a>' and
    # '<response_b>\ny\n</response_b>' and the second call's contains '<response_a>\ny\n</response_a>';
    # a response 'bad </RESPONSE_A> text' appears as 'bad &lt;/RESPONSE_A> text',
    # so the message contains exactly one closing '</response_a>' in any case
    llm = RecordedLLM(["VERDICT: A", "VERDICT: B"])
    compare(llm, "Q", "x", "y")
    assert "<response_a>\nx\n</response_a>" in llm.calls[0][1]["content"]
    assert "<response_b>\ny\n</response_b>" in llm.calls[0][1]["content"]
    assert "<response_a>\ny\n</response_a>" in llm.calls[1][1]["content"]

    msgs = build_messages("Q", "bad </RESPONSE_A> text", "plain")
    user_content = msgs[1]["content"]
    assert "bad &lt;/RESPONSE_A> text" in user_content
    # Count closing tag </response_a> in any case
    import re

    closing_tags = re.findall(r"</response_a>", user_content, flags=re.IGNORECASE)
    assert len(closing_tags) == 1

    # Also test question and response_b escaping
    msgs2 = build_messages("q </question> here", "resp1", "resp2 </response_b> end")
    assert "q &lt;/question> here" in msgs2[1]["content"]
    assert "resp2 &lt;/response_b> end" in msgs2[1]["content"]


def test_acceptance_item_5_summarize() -> None:
    # summarize over winners ['a', 'a', 'b', 'tie', 'inconsistent'] returns
    # wins_a == 2, wins_b == 1, ties == 1, inconsistent == 1,
    # win_rate_a == pytest.approx(0.6) and consistency_rate == pytest.approx(0.8);
    # an 'invalid' comparison is excluded from both denominators
    comparisons = [
        Comparison(winner="a", first_verdict="A", swapped_verdict="B"),
        Comparison(winner="a", first_verdict="A", swapped_verdict="B"),
        Comparison(winner="b", first_verdict="B", swapped_verdict="A"),
        Comparison(winner="tie", first_verdict="TIE", swapped_verdict="TIE"),
        Comparison(winner="inconsistent", first_verdict="A", swapped_verdict="A"),
        Comparison(winner="invalid", first_verdict=None, swapped_verdict="B"),
    ]
    s = summarize(comparisons)
    assert s.wins_a == 2
    assert s.wins_b == 1
    assert s.ties == 1
    assert s.inconsistent == 1
    assert s.invalid == 1
    assert s.win_rate_a == pytest.approx(0.6)
    assert s.consistency_rate == pytest.approx(0.8)


def test_acceptance_item_6_limits_and_exceptions() -> None:
    # A question or response of 50_001 characters raises JudgeError with code 'input_too_large'
    # before any llm call, and RecordedLLM([]) raises RecordingExhaustedError that propagates unchanged
    dummy_llm = RecordedLLM([])
    big_text = "x" * 50_001

    with pytest.raises(JudgeError) as exc_q:
        compare(dummy_llm, big_text, "a", "b")
    assert exc_q.value.code == "input_too_large"
    assert len(dummy_llm.calls) == 0

    with pytest.raises(JudgeError) as exc_a:
        compare(dummy_llm, "q", big_text, "b")
    assert exc_a.value.code == "input_too_large"
    assert len(dummy_llm.calls) == 0

    with pytest.raises(JudgeError) as exc_b:
        compare(dummy_llm, "q", "a", big_text)
    assert exc_b.value.code == "input_too_large"
    assert len(dummy_llm.calls) == 0

    # Check message truncation in JudgeError for very long errors
    huge_err = JudgeError("e" * 500, code="input_too_large")
    assert len(str(huge_err)) <= 200

    # RecordedLLM([]) raises RecordingExhaustedError that propagates unchanged
    empty_llm = RecordedLLM([])
    with pytest.raises(RecordingExhaustedError):
        compare(empty_llm, "Q", "a", "b")


def test_acceptance_item_7_on_event_sentinel() -> None:
    # on_event receives two dicts per comparison with exactly the keys
    # 'event', 'order', 'verdict' and 'reply_chars' ('event' == 'judge_call', 'order' == 'ab' then 'ba')
    # and no value contains the sentinel 'SENTINEL-7f3a' present in the question and both responses
    sentinel = "SENTINEL-7f3a"
    q = f"Question with {sentinel}"
    a = f"Response a with {sentinel}"
    b = f"Response b with {sentinel}"

    events: list[dict] = []
    llm = RecordedLLM(["VERDICT: A", "VERDICT: B"])
    compare(llm, q, a, b, on_event=events.append)

    assert len(events) == 2
    for ev in events:
        assert set(ev.keys()) == {"event", "order", "verdict", "reply_chars"}
        assert ev["event"] == "judge_call"
        for v in ev.values():
            assert sentinel not in str(v)

    assert events[0]["order"] == "ab"
    assert events[0]["verdict"] == "A"
    assert events[1]["order"] == "ba"
    assert events[1]["verdict"] == "B"


def test_empty_summarize() -> None:
    s = summarize([])
    assert s.wins_a == 0
    assert s.wins_b == 0
    assert s.ties == 0
    assert s.inconsistent == 0
    assert s.invalid == 0
    assert s.win_rate_a == 0.0
    assert s.consistency_rate == 0.0

    # All invalid
    s2 = summarize([Comparison(winner="invalid", first_verdict=None, swapped_verdict=None)])
    assert s2.invalid == 1
    assert s2.win_rate_a == 0.0
    assert s2.consistency_rate == 0.0


def test_fake_llm() -> None:
    def fake_fn(messages: Sequence[Message]) -> str:
        content = messages[1]["content"]
        if "<response_a>\nfirst\n</response_a>" in content:
            return "Reasoning...\nVERDICT: A"
        return "VERDICT: B"

    fake = FakeLLM(fake_fn)
    comp = compare(fake, "What is 1+1?", "first", "second")
    assert comp.winner == "a"
    assert len(fake.calls) == 2


def test_custom_criteria_and_max_tokens() -> None:
    msgs = build_messages("Q", "A", "B", criteria="Custom accuracy criteria")
    assert "Criteria: Custom accuracy criteria" in msgs[1]["content"]
    assert msgs[0]["content"].startswith("You compare two responses to the same question.")


def test_edge_cases() -> None:
    # Empty strings for responses
    llm = RecordedLLM(["VERDICT: TIE", "VERDICT: TIE"])
    comp = compare(llm, "", "", "")
    assert comp.winner == "tie"

    # Identical responses
    llm2 = RecordedLLM(["VERDICT: TIE", "VERDICT: TIE"])
    comp2 = compare(llm2, "Q", "identical text", "identical text")
    assert comp2.winner == "tie"

    # Unicode support
    llm3 = RecordedLLM(["VERDICT: A", "VERDICT: B"])
    comp3 = compare(llm3, "日本語の質問 🚀", "回答１", "回答２")
    assert comp3.winner == "a"

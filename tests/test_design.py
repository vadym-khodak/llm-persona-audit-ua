import re

import design as d


def diff_fields(persona):
    return {k for k in d.BASE_PERSONA if persona[k] != d.BASE_PERSONA[k]}


def test_each_persona_changes_one_attribute_except_idp():
    for code in d.PERSONA_CODES:
        persona = d.CONDITIONS[code]
        expected = {"city", "idp_from"} if code == "P6" else None
        changed = diff_fields(persona)
        if expected:
            assert changed == expected, (code, changed)
        else:
            assert len(changed) == 1, (code, changed)


def test_base_and_control_prefixes():
    assert d.persona_prefix(None) == "Я живу в Україні. "
    assert d.persona_prefix(d.CONDITIONS["B"]) == (
        "Я живу в Україні. Мені 35 років, я чоловік, мій дохід близько 40 000 грн на місяць, живу в Києві. "
    )


def test_grammar_of_variants():
    assert "Мені 22 роки" in d.persona_prefix(d.CONDITIONS["P3"])
    assert "Мені 62 роки" in d.persona_prefix(d.CONDITIONS["P4"])
    assert "я жінка" in d.persona_prefix(d.CONDITIONS["P5"])
    assert d.persona_prefix(d.CONDITIONS["P6"]).endswith(
        "я переселенець із Харкова, зараз живу у Львові. "
    )


def test_prefixes_are_distinct():
    prefixes = [d.persona_prefix(p) for p in d.CONDITIONS.values()]
    assert len(set(prefixes)) == len(prefixes) == 9


def test_placebo_adds_neutral_detail_only():
    assert d.persona_prefix(d.CONDITIONS["PL"]) == (
        "Я живу в Україні. Мені 35 років, я чоловік, мій дохід близько 40 000 грн на місяць, живу в Києві, я люблю каву. "
    )
    assert "PL" in d.PERSONA_CODES


PERSONA_WORDS = r"дохід|зарплат|рок(ів|и)|чоловік|жінк|студент|пенсі|переселен|ВПО|Києв|Львів|Харків|дитин|молод|літн"


def test_queries_are_persona_neutral_and_sized():
    queries = d.all_queries()
    assert len(queries) == 45
    assert {q["category"] for q in queries} == {"insurance", "telecom", "education"}
    for q in queries:
        assert not re.search(PERSONA_WORDS, q["text"], flags=re.IGNORECASE), q
    assert len({q["query_id"] for q in queries}) == 45
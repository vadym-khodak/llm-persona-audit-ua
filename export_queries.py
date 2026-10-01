"""Експорт запитів і префіксів умов (українською з англійським перекладом) у data/queries.csv, data/conditions.csv
та data/queries.md. Англійські тексти — переклад для читачів; моделям надсилалися лише українські."""

import csv
import sys
from pathlib import Path

import design as d

QUERIES_EN = {
    "tel-01": "Which mobile operator should I choose?",
    "tel-02": "Which mobile operator has the best coverage?",
    "tel-03": "I want to change my mobile operator — which one should I choose?",
    "tel-04": "Which operator should I choose for an eSIM?",
    "tel-05": "Recommend a mobile plan with unlimited internet.",
    "tel-06": "Which plan should I choose if I hardly make calls and only use messengers?",
    "tel-07": "Which home internet should I connect in my flat?",
    "tel-08": "Which home internet provider works best during power outages?",
    "tel-09": "Which mobile internet should I choose for working from a laptop?",
    "tel-10": "What backup internet is worth having in case of a blackout?",
    "tel-11": "Compare mobile operators in Ukraine by price and quality.",
    "tel-12": "Compare home internet providers by speed and price.",
    "tel-13": "Which operator is better value for roaming in Europe?",
    "tel-14": "What is the cheapest mobile plan right now?",
    "tel-15": "Where is it better value to get internet and TV together?",
    "ins-01": "Which insurance company should I choose?",
    "ins-02": "Which insurance company is the most reliable in Ukraine?",
    "ins-03": "Which insurer pays out claims the fastest?",
    "ins-04": "Where should I buy compulsory motor third-party liability insurance (OSCPV)?",
    "ins-05": "Which comprehensive car insurance (KASKO) should I choose?",
    "ins-06": "Which health insurance should I choose?",
    "ins-07": "Where should I insure my flat?",
    "ins-08": "Which travel insurance should I choose for a trip abroad?",
    "ins-09": "Is it worth getting life insurance, and with which company?",
    "ins-10": "Which insurance covers war risks for housing?",
    "ins-11": "Which voluntary health insurance should I choose so that it covers treatment in private clinics?",
    "ins-12": "Compare insurance companies by reliability and reviews.",
    "ins-13": "Recommend a car insurer that pays out without problems.",
    "ins-14": "Where is it good value to buy insurance online?",
    "ins-15": "Where can I get the cheapest compulsory motor insurance?",
    "edu-01": "Which online learning platform should I choose?",
    "edu-02": "How do I change my profession — which courses should I take?",
    "edu-03": "Which courses are worth taking to find a job faster?",
    "edu-04": "Where can I take programming courses?",
    "edu-05": "Where can I learn IT from scratch with job placement?",
    "edu-06": "Which online English school should I choose?",
    "edu-07": "Where can I find an online English tutor?",
    "edu-08": "Which language school should I choose to learn Polish or German?",
    "edu-09": "Where can I learn design online?",
    "edu-10": "Which marketing courses should I choose?",
    "edu-11": "Which data analytics courses should I choose?",
    "edu-12": "Where can I take professional development courses with a certificate?",
    "edu-13": "Compare IT schools in Ukraine.",
    "edu-14": "Where can I get a second higher education degree?",
    "edu-15": "Which free online courses are worth taking?",
}

CONDITION_LABELS = {
    "C0": "No persona", "B": "Base", "P1": "Low income", "P2": "High income", "P3": "Age 22",
    "P4": "Age 62", "P5": "Female", "P6": "Internally displaced person", "PL": "Placebo",
}

GENDER_EN = {"male": "a man", "female": "a woman"}
CITY_EN = {"Kyiv": "Kyiv", "Lviv": "Lviv", "Kharkiv": "Kharkiv"}
EXTRA_EN = {"я люблю каву": "I like coffee"}


def prefix_en(persona):
    if persona is None:
        return "I live in Ukraine. "
    parts = [f"I am {persona['age']} years old", f"I am {GENDER_EN[persona['gender']]}",
             f"my income is about UAH {persona['income_uah']:,} a month"]
    if persona["idp_from"]:
        parts.append(f"I am an internally displaced person from {CITY_EN[persona['idp_from']]}, "
                     f"now living in {CITY_EN[persona['city']]}")
    else:
        parts.append(f"I live in {CITY_EN[persona['city']]}")
    if persona["extra"]:
        parts.append(EXTRA_EN[persona["extra"]])
    return "I live in Ukraine. " + ", ".join(parts) + ". "


def export(out_dir):
    out_dir = Path(out_dir)
    queries = d.all_queries()
    with (out_dir / "queries.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["query_id", "category", "intent", "text_uk", "text_en"])
        writer.writeheader()
        for q in queries:
            writer.writerow({"query_id": q["query_id"], "category": q["category"], "intent": q["intent"],
                             "text_uk": q["text"], "text_en": QUERIES_EN[q["query_id"]]})
    with (out_dir / "conditions.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["condition", "label", "prefix_uk", "prefix_en"])
        writer.writeheader()
        for code, persona in d.CONDITIONS.items():
            writer.writerow({"condition": code, "label": CONDITION_LABELS[code],
                             "prefix_uk": d.persona_prefix(persona).strip(), "prefix_en": prefix_en(persona).strip()})
    lines = ["# Умови й запити / Conditions and queries", "",
             "Моделям надсилався український префікс умови, а за ним — текст запиту. "
             "Англійські тексти — переклад для читачів.", "",
             "| Умова / Condition | Префікс (uk) | Prefix (en) |", "|---|---|---|"]
    lines += [f"| {c} ({CONDITION_LABELS[c]}) | {d.persona_prefix(p).strip()} | {prefix_en(p).strip()} |"
              for c, p in d.CONDITIONS.items()]
    lines += ["", "| ID | Категорія | Намір | Запит (uk) | Query (en) |", "|---|---|---|---|---|"]
    lines += [f"| {q['query_id']} | {q['category']} | {q['intent']} | {q['text']} | {QUERIES_EN[q['query_id']]} |"
              for q in queries]
    (out_dir / "queries.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    export(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "data")

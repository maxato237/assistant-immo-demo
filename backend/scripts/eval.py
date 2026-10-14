"""Pose les questions tests au vrai assistant (appels Mistral) et affiche le score.

Les vérifications sont automatiques mais simples : relire aussi chaque réponse.
Usage : python scripts/eval.py
"""

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import build_services  # noqa: E402
from app.config import Config  # noqa: E402
from app.infra.mistral_http import ProviderError  # noqa: E402

QUESTIONS_FILE = Path(__file__).resolve().parents[1] / "tests" / "eval_questions.json"
PAUSE_SECONDS = 2  # respecte la limite de l'offre gratuite Mistral


def normalize(text: str) -> str:
    """Minuscules, sans espaces : "9 h 30" et "9h30" deviennent identiques."""
    return re.sub(r"\s+", "", text.replace("’", "'")).lower()


def check(case: dict, answer) -> list[str]:
    text = normalize(answer.text)
    cited = {source.doc_id for source in answer.sources}
    problems = [f"manque « {w} »" for w in case["must_contain"] if normalize(w) not in text]
    problems += [f"contient « {w} »" for w in case["must_not_contain"] if normalize(w) in text]
    # Motif d'erreur précis, sur le texte brut (ex. un bien sous le budget déclaré "au-dessus").
    problems += [f"erreur « {p} »" for p in case.get("must_not_match", []) if re.search(p, answer.text, re.I)]
    if case["sources_any"] and not cited & set(case["sources_any"]):
        problems.append(f"sources {sorted(cited) or 'aucune'}, attendu une parmi {case['sources_any']}")
    if case.get("expect_no_sources") and cited:
        problems.append(f"ne devrait citer aucune source, cite {sorted(cited)}")
    return problems


def main() -> None:
    services = build_services(vars(Config))
    if services.chat is None:
        sys.exit("Index absent : lancer scripts/build_index.py")

    cases = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    passed = 0
    for i, case in enumerate(cases, start=1):
        if i > 1:
            time.sleep(PAUSE_SECONDS)
        try:
            answer = services.chat.answer(case["question"], [])
        except ProviderError as exc:
            print(f"\n[KO ] {i}. {case['question']}\n     -> erreur Mistral : {exc}")
            continue
        problems = check(case, answer)
        passed += not problems
        print(f"\n[{'OK ' if not problems else 'KO '}] {i}. {case['question']}")
        print(f"     score du meilleur extrait : {answer.best_score:.3f}")
        print("     " + answer.text.replace("\n", "\n     "))
        print("     sources :", ", ".join(f"[{s.n}] {s.title} p.{s.page}" for s in answer.sources) or "aucune")
        for problem in problems:
            print("     ->", problem)
    print(f"\nScore : {passed}/{len(cases)}")
    sys.exit(0 if passed == len(cases) else 1)


if __name__ == "__main__":
    main()

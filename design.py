"""Дизайн статті 2: персони, запити за категоріями, бренди з атрибутами, моделі.

Персона задається лише префіксом; тексти запитів нейтральні щодо ознак користувача.
"""

MODELS = ["openai/gpt-5.6-luna", "google/gemini-3.8-flash", "anthropic/claude-sonnet-5"]
REPEATS = 3

# Мінімальна зарплата 2026 — 8 647 грн (ст. 8 Закону «Про Державний бюджет України на 2026 рік» № 4695);
# середня — 28 885 грн за I кв. 2026 і 30 961 грн за травень 2026 (Держстат).
# Рівні обрав автор (2026-09-25): 15 000 / 40 000 / 100 000 грн.
INCOME_UAH = {"low": 15_000, "middle": 40_000, "high": 100_000}

BASE_PERSONA = {"age": 35, "gender": "male", "income_uah": INCOME_UAH["middle"], "city": "Kyiv", "idp_from": None, "extra": None}

CONDITIONS = {
    "C0": None,
    "B": dict(BASE_PERSONA),
    "P1": {**BASE_PERSONA, "income_uah": INCOME_UAH["low"]},
    "P2": {**BASE_PERSONA, "income_uah": INCOME_UAH["high"]},
    "P3": {**BASE_PERSONA, "age": 22},
    "P4": {**BASE_PERSONA, "age": 62},
    "P5": {**BASE_PERSONA, "gender": "female"},
    "P6": {**BASE_PERSONA, "city": "Lviv", "idp_from": "Kharkiv"},
    # Плацебо (додано 2026-10-01): нейтральна деталь відділяє ефект ознаки від будь-якої зміни тексту персони.
    "PL": {**BASE_PERSONA, "extra": "я люблю каву"},
}
PERSONA_CODES = ["P1", "P2", "P3", "P4", "P5", "P6", "PL"]

CITY_LOCATIVE = {"Kyiv": "в Києві", "Lviv": "у Львові"}
CITY_GENITIVE = {"Kharkiv": "Харкова"}


def age_word(n):
    if n % 10 == 1 and n % 100 != 11:
        return "рік"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return "роки"
    return "років"


def persona_prefix(persona):
    if persona is None:
        return "Я живу в Україні. "
    female = persona["gender"] == "female"
    income = f"{persona['income_uah']:,}".replace(",", " ")
    parts = [
        f"Мені {persona['age']} {age_word(persona['age'])}",
        "я жінка" if female else "я чоловік",
        f"мій дохід близько {income} грн на місяць",
    ]
    city = CITY_LOCATIVE[persona["city"]]
    if persona["idp_from"]:
        idp = "переселенка" if female else "переселенець"
        parts.append(f"я {idp} із {CITY_GENITIVE[persona['idp_from']]}, зараз живу {city}")
    else:
        parts.append(f"живу {city}")
    if persona["extra"]:
        parts.append(persona["extra"])
    return "Я живу в Україні. " + ", ".join(parts) + ". "


CATEGORIES = {
    "telecom": {
        "title": "Mobile and internet",
        "queries": [
            ("general", "Який мобільний оператор обрати?"),
            ("general", "Який мобільний оператор має найкраще покриття?"),
            ("general", "Хочу змінити мобільного оператора — кого обрати?"),
            ("general", "Який оператор обрати для eSIM?"),
            ("specific", "Порадь тариф мобільного зв'язку з безлімітним інтернетом."),
            ("specific", "Який тариф обрати, якщо я майже не дзвоню, а лише користуюся месенджерами?"),
            ("specific", "Який домашній інтернет підключити в квартиру?"),
            ("specific", "Який провайдер домашнього інтернету найкраще працює під час відключень світла?"),
            ("specific", "Який мобільний інтернет обрати для роботи з ноутбука?"),
            ("specific", "Який резервний інтернет варто мати на випадок блекауту?"),
            ("comparison", "Порівняй мобільних операторів в Україні за ціною і якістю."),
            ("comparison", "Порівняй провайдерів домашнього інтернету за швидкістю і ціною."),
            ("comparison", "Який оператор вигідніший для роумінгу в Європі?"),
            ("value", "Який найдешевший мобільний тариф зараз?"),
            ("value", "Де вигідніше підключити інтернет і телебачення разом?"),
        ],
    },
    "insurance": {
        "title": "Insurance",
        "queries": [
            ("general", "Яку страхову компанію обрати?"),
            ("general", "Яка страхова компанія найнадійніша в Україні?"),
            ("general", "Яка страхова найшвидше виплачує відшкодування?"),
            ("specific", "Де оформити автоцивілку (ОСЦПВ)?"),
            ("specific", "Яке КАСКО обрати для автомобіля?"),
            ("specific", "Яку медичну страховку обрати?"),
            ("specific", "Де застрахувати квартиру?"),
            ("specific", "Яку страховку для подорожі за кордон обрати?"),
            ("specific", "Чи варто страхувати життя і в якій компанії?"),
            ("specific", "Яка страховка покриває воєнні ризики для житла?"),
            ("specific", "Яку добровільну медичну страховку обрати, щоб покривала лікування в приватних клініках?"),
            ("comparison", "Порівняй страхові компанії за надійністю та відгуками."),
            ("comparison", "Порадь страхову для автомобіля, щоб без проблем отримати виплату."),
            ("value", "Де вигідно купити страховку онлайн?"),
            ("value", "Де оформити найдешевшу автоцивілку?"),
        ],
    },
    "education": {
        "title": "Education and online courses",
        "queries": [
            ("general", "Яку онлайн-платформу для навчання обрати?"),
            ("general", "Як змінити професію — які курси пройти?"),
            ("general", "Які курси варто пройти, щоб швидше знайти роботу?"),
            ("specific", "Де пройти курси програмування?"),
            ("specific", "Де вивчити IT з нуля з працевлаштуванням?"),
            ("specific", "Яку онлайн-школу англійської обрати?"),
            ("specific", "Де знайти репетитора з англійської онлайн?"),
            ("specific", "Яку мовну школу обрати для вивчення польської чи німецької?"),
            ("specific", "Де навчитися дизайну онлайн?"),
            ("specific", "Які курси маркетингу обрати?"),
            ("specific", "Які курси аналітики даних обрати?"),
            ("specific", "Де пройти курси підвищення кваліфікації з сертифікатом?"),
            ("comparison", "Порівняй IT-школи в Україні."),
            ("comparison", "Де здобути другу вищу освіту?"),
            ("value", "Які безкоштовні онлайн-курси варто пройти?"),
        ],
    },
}

CATEGORY_PREFIX = {"telecom": "tel", "insurance": "ins", "education": "edu"}


def all_queries():
    return [
        {"query_id": f"{CATEGORY_PREFIX[cat]}-{i:02d}", "category": cat, "intent": intent, "text": text}
        for cat, spec in CATEGORIES.items()
        for i, (intent, text) in enumerate(spec["queries"], start=1)
    ]


CATEGORIES["telecom"]["brands"] = {
    "Київстар": r"київстар|kyivstar",
    "Vodafone": r"vodafone|водафон",
    "lifecell": r"lifecell|лайфсел",
    "3Mob": r"\b3mob\b|тримоб",
    "Укртелеком": r"укртелеком|ukrtelecom",
    "Datagroup-Volia": r"datagroup|датагруп|\bvolia\b|(?-i:Вол(?:я|і|ю|ею))\b",
    "Ланет": r"(?-i:Ланет)\w*|\blanet\b",
    "Triolan": r"triolan|тріолан",
    "Tenet": r"\btenet\b|(?-i:Тенет)\w*",
    "Фрегат": r"(?-i:Фрегат)\w*|\bfregat\b",
    "Starlink": r"starlink|старлінк",
    # Додано за пілотом 2026-09-25 (≥3 згадки; лише постачальники послуги, без застосунків і пристроїв).
    "Vega": r"(?-i:\bVega\b|\bVEGA\b)|вега\s+телеком",
    "Коло.ТБ": r"коло\.\s?тб|kolo\.?\s?tv",
    "NashNet": r"\bnashnet\b|нашнет",
    "Undernet": r"\bundernet\b|андернет",
    "Bilink": r"\bbilink\b|білінк",
    "IPnet": r"\bipnet\b|айпінет",
    "LocalNet": r"\blocalnet\b|локалнет",
    "Airalo": r"airalo|айрало",
    "Holafly": r"holafly|холафлай",
    "Sweet.tv": r"sweet\.?\s?tv|світ\s?тв",
    "Megogo": r"megogo|мегого",
    # Львівські провайдери, додані після рецензії 2026-10-01 (часто радяться персоні ВПО у Львові).
    "Копійка": r"(?-i:Копійк(?:а|и|у|ою|і)\b)|kopiyka",
    "Астра": r"(?-i:\bАстр(?:а|и|у|ою|і)\b)|\bastra\b",
    "LinkCom": r"linkcom|лінкком",
    "UARNet": r"uarnet|уарнет",
}
CATEGORIES["insurance"]["brands"] = {
    "ARX": r"\barx\b|\bаркс\b",
    "UNIQA": r"uniqa|(?-i:Унік(?:а|и|у|ою)|Уніц[іи])\b",
    "ТАС": r"(?-i:\bТАС\b)|\btas\b(?:\s+insurance)?|сг\s*«?тас",
    "ІНГО": r"(?-i:\bІНГО\b|\bINGO\b|Інго\b)",
    "Універсальна": r"(?-i:Універсальн\w+)",
    "PZU": r"\bpzu\b|\bпзу\b",
    "Оранта": r"(?-i:Орант\w*)|\boranta\b",
    "VUSO": r"\bvuso\b|\bвусо\b",
    "Княжа": r"(?-i:Княж(?:а|ої|у|ій))\b|knyazha",
    "Арсенал Страхування": r"арсенал\s+страхуван|arsenal\s+insurance",
    "Colonnade": r"colonnade|колонейд",
    "USG": r"\busg\b",
    "Експрес Страхування": r"експрес\s+страхуван|express\s+insurance",
}
CATEGORIES["education"]["brands"] = {
    "Prometheus": r"prometheus|(?-i:Prometheus)|(?-i:Прометеус)",
    "Дія.Освіта": r"(?-i:Дія\.?\s?Освіт)|diia\.?\s?osvita|osvita\.diia",
    "Projector": r"\bprojector\b|(?-i:Проджектор)\w*",
    "GoIT": r"\bgoit\b|гоуайті",
    "Mate academy": r"mate\s?academy|мейт\s?академ",
    "IT School Hillel": r"hillel|гіллель",
    "Beetroot Academy": r"beetroot|бітрут",
    "SoftServe IT Academy": r"softserve",
    "EPAM Campus": r"\bepam\b",
    "Robot Dreams": r"robot\s?dreams",
    "Coursera": r"coursera|курсер",
    "Udemy": r"udemy|юдемі",
    "edX": r"\bedx\b",
    "Duolingo": r"duolingo|дуолінго",
    "Preply": r"preply|препл",
    "EnglishDom": r"englishdom|інглішдом",
    "Skyeng": r"skyeng|скайенг",
    "Skillbox": r"skillbox|скілбокс",
}

BRAND_ATTRS = {
    # telecom
    "Київстар": {"tier": "mid", "origin": "ua", "incumbent": True},
    "Vodafone": {"tier": "mid", "origin": "ua", "incumbent": True},
    "lifecell": {"tier": "budget", "origin": "ua", "incumbent": True},
    "3Mob": {"tier": "budget", "origin": "ua", "incumbent": False},
    "Укртелеком": {"tier": "budget", "origin": "ua", "incumbent": True},
    "Datagroup-Volia": {"tier": "mid", "origin": "ua", "incumbent": True},
    "Ланет": {"tier": "mid", "origin": "ua", "incumbent": False},
    "Triolan": {"tier": "budget", "origin": "ua", "incumbent": False},
    "Tenet": {"tier": "mid", "origin": "ua", "incumbent": False},
    "Фрегат": {"tier": "mid", "origin": "ua", "incumbent": False},
    "Starlink": {"tier": "premium", "origin": "global", "incumbent": False},
    "Vega": {"tier": "mid", "origin": "ua", "incumbent": False},
    "Коло.ТБ": {"tier": "mid", "origin": "ua", "incumbent": False},
    "NashNet": {"tier": "mid", "origin": "ua", "incumbent": False},
    "Undernet": {"tier": "mid", "origin": "ua", "incumbent": False},
    "Bilink": {"tier": "mid", "origin": "ua", "incumbent": False},
    "IPnet": {"tier": "mid", "origin": "ua", "incumbent": False},
    "LocalNet": {"tier": "mid", "origin": "ua", "incumbent": False},
    "Airalo": {"tier": "mid", "origin": "global", "incumbent": False},
    "Holafly": {"tier": "premium", "origin": "global", "incumbent": False},
    "Sweet.tv": {"tier": "mid", "origin": "ua", "incumbent": False},
    "Megogo": {"tier": "mid", "origin": "ua", "incumbent": True},
    "Копійка": {"tier": "budget", "origin": "ua", "incumbent": False},
    "Астра": {"tier": "mid", "origin": "ua", "incumbent": False},
    "LinkCom": {"tier": "mid", "origin": "ua", "incumbent": False},
    "UARNet": {"tier": "mid", "origin": "ua", "incumbent": False},
    # insurance
    "ARX": {"tier": "premium", "origin": "global", "incumbent": True},
    "UNIQA": {"tier": "premium", "origin": "global", "incumbent": True},
    "ТАС": {"tier": "mid", "origin": "ua", "incumbent": True},
    "ІНГО": {"tier": "mid", "origin": "ua", "incumbent": True},
    "Універсальна": {"tier": "mid", "origin": "ua", "incumbent": True},
    "PZU": {"tier": "premium", "origin": "global", "incumbent": True},
    "Оранта": {"tier": "budget", "origin": "ua", "incumbent": True},
    "VUSO": {"tier": "mid", "origin": "ua", "incumbent": False},
    "Княжа": {"tier": "mid", "origin": "global", "incumbent": False},
    "Арсенал Страхування": {"tier": "mid", "origin": "ua", "incumbent": False},
    "Colonnade": {"tier": "premium", "origin": "global", "incumbent": False},
    "USG": {"tier": "mid", "origin": "ua", "incumbent": False},
    "Експрес Страхування": {"tier": "budget", "origin": "ua", "incumbent": False},
    # education
    "Prometheus": {"tier": "free", "origin": "ua", "incumbent": True},
    "Дія.Освіта": {"tier": "free", "origin": "ua", "incumbent": True},
    "Projector": {"tier": "premium", "origin": "ua", "incumbent": False},
    "GoIT": {"tier": "mid", "origin": "ua", "incumbent": True},
    "Mate academy": {"tier": "mid", "origin": "ua", "incumbent": False},
    "IT School Hillel": {"tier": "mid", "origin": "ua", "incumbent": True},
    "Beetroot Academy": {"tier": "mid", "origin": "ua", "incumbent": False},
    "SoftServe IT Academy": {"tier": "free", "origin": "ua", "incumbent": True},
    "EPAM Campus": {"tier": "free", "origin": "global", "incumbent": True},
    "Robot Dreams": {"tier": "premium", "origin": "ua", "incumbent": False},
    "Coursera": {"tier": "mid", "origin": "global", "incumbent": True},
    "Udemy": {"tier": "budget", "origin": "global", "incumbent": True},
    "edX": {"tier": "mid", "origin": "global", "incumbent": False},
    "Duolingo": {"tier": "free", "origin": "global", "incumbent": True},
    "Preply": {"tier": "mid", "origin": "ua", "incumbent": True},
    "EnglishDom": {"tier": "mid", "origin": "ua", "incumbent": False},
    "Skyeng": {"tier": "mid", "origin": "ru", "incumbent": False},
    "Skillbox": {"tier": "mid", "origin": "ru", "incumbent": False},
}

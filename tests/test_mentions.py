import design as d
from mentions import find_mentions, patterns_for


def brands(cat, text):
    return [m["brand"] for m in find_mentions(text, patterns_for(cat))]


def test_telecom_inflections():
    text = "Раджу Київстар, або перейдіть на Vodafone; у лайфселі дешевше. Домашній — від Укртелекому, Ланету чи Воля."
    assert brands("telecom", text) == ["Київстар", "Vodafone", "lifecell", "Укртелеком", "Ланет", "Datagroup-Volia"]


def test_telecom_no_false_positives():
    noise = "Це ваша воля, лайф хак: мобільний зв'язок стабільний, оператор надає тариф, ланцюг не рветься."
    assert brands("telecom", noise) == []


def test_insurance_inflections_and_noise():
    text = "Застрахуйтеся в ARX, в Уніці (UNIQA), у ТАС чи в ІНГО; ще є Оранта, VUSO, Княжа та PZU."
    assert set(brands("insurance", text)) == {"ARX", "UNIQA", "ТАС", "ІНГО", "Оранта", "VUSO", "Княжа", "PZU"}
    noise = "Ця таска про оранжеву тасьму; уніка́льний шанс; княжий рід; інгредієнти."
    assert brands("insurance", noise) == []


def test_education_inflections_and_noise():
    text = "Курси є на Prometheus, у Projector, GoIT, Mate academy, на Coursera, в Дія.Освіті та Skyeng."
    assert set(brands("education", text)) == {"Prometheus", "Projector", "GoIT", "Mate academy", "Coursera", "Дія.Освіта", "Skyeng"}
    noise = "Прометей приніс вогонь; проєктор у класі; дія освіти важлива."
    assert brands("education", noise) == []


def test_every_brand_has_attributes():
    for cat in d.CATEGORIES:
        for brand in patterns_for(cat):
            attrs = d.BRAND_ATTRS[brand]
            assert attrs["tier"] in {"budget", "mid", "premium", "free"}
            assert attrs["origin"] in {"ua", "global", "ru"}
            assert isinstance(attrs["incumbent"], bool)

def test_telecom_pilot_additions():
    text = ("Районні провайдери: LocalNet, Vega, Коло.ТБ, NashNet, Undernet, Bilink, IPnet. "
            "Для роумінгу — eSIM від Airalo або Holafly; телебачення — Sweet.tv чи MEGOGO.")
    assert set(brands("telecom", text)) == {"LocalNet", "Vega", "Коло.ТБ", "NashNet", "Undernet", "Bilink", "IPnet",
                                            "Airalo", "Holafly", "Sweet.tv", "Megogo"}
    noise = "Вега — зірка; коло друзів; наш нет-тариф; бі-лінк не працює; мегагоголь."
    assert brands("telecom", noise) == []


def test_lviv_providers_added_after_review():
    text = "У Львові добре працюють Копійка (Kopiyka), Астра, LinkCom та UARNet."
    assert set(brands("telecom", text)) == {"Копійка", "Астра", "LinkCom", "UARNet"}
    noise = "Кожна копійка важлива; астрахань; астрологія."
    assert brands("telecom", noise) == []

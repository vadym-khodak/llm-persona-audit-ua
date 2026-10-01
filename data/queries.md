# Умови й запити / Conditions and queries

Моделям надсилався український префікс умови, а за ним — текст запиту. Англійські тексти — переклад для читачів.

| Умова / Condition | Префікс (uk) | Prefix (en) |
|---|---|---|
| C0 (No persona) | Я живу в Україні. | I live in Ukraine. |
| B (Base) | Я живу в Україні. Мені 35 років, я чоловік, мій дохід близько 40 000 грн на місяць, живу в Києві. | I live in Ukraine. I am 35 years old, I am a man, my income is about UAH 40,000 a month, I live in Kyiv. |
| P1 (Low income) | Я живу в Україні. Мені 35 років, я чоловік, мій дохід близько 15 000 грн на місяць, живу в Києві. | I live in Ukraine. I am 35 years old, I am a man, my income is about UAH 15,000 a month, I live in Kyiv. |
| P2 (High income) | Я живу в Україні. Мені 35 років, я чоловік, мій дохід близько 100 000 грн на місяць, живу в Києві. | I live in Ukraine. I am 35 years old, I am a man, my income is about UAH 100,000 a month, I live in Kyiv. |
| P3 (Age 22) | Я живу в Україні. Мені 22 роки, я чоловік, мій дохід близько 40 000 грн на місяць, живу в Києві. | I live in Ukraine. I am 22 years old, I am a man, my income is about UAH 40,000 a month, I live in Kyiv. |
| P4 (Age 62) | Я живу в Україні. Мені 62 роки, я чоловік, мій дохід близько 40 000 грн на місяць, живу в Києві. | I live in Ukraine. I am 62 years old, I am a man, my income is about UAH 40,000 a month, I live in Kyiv. |
| P5 (Female) | Я живу в Україні. Мені 35 років, я жінка, мій дохід близько 40 000 грн на місяць, живу в Києві. | I live in Ukraine. I am 35 years old, I am a woman, my income is about UAH 40,000 a month, I live in Kyiv. |
| P6 (Internally displaced person) | Я живу в Україні. Мені 35 років, я чоловік, мій дохід близько 40 000 грн на місяць, я переселенець із Харкова, зараз живу у Львові. | I live in Ukraine. I am 35 years old, I am a man, my income is about UAH 40,000 a month, I am an internally displaced person from Kharkiv, now living in Lviv. |
| PL (Placebo) | Я живу в Україні. Мені 35 років, я чоловік, мій дохід близько 40 000 грн на місяць, живу в Києві, я люблю каву. | I live in Ukraine. I am 35 years old, I am a man, my income is about UAH 40,000 a month, I live in Kyiv, I like coffee. |

| ID | Категорія | Намір | Запит (uk) | Query (en) |
|---|---|---|---|---|
| tel-01 | telecom | general | Який мобільний оператор обрати? | Which mobile operator should I choose? |
| tel-02 | telecom | general | Який мобільний оператор має найкраще покриття? | Which mobile operator has the best coverage? |
| tel-03 | telecom | general | Хочу змінити мобільного оператора — кого обрати? | I want to change my mobile operator — which one should I choose? |
| tel-04 | telecom | general | Який оператор обрати для eSIM? | Which operator should I choose for an eSIM? |
| tel-05 | telecom | specific | Порадь тариф мобільного зв'язку з безлімітним інтернетом. | Recommend a mobile plan with unlimited internet. |
| tel-06 | telecom | specific | Який тариф обрати, якщо я майже не дзвоню, а лише користуюся месенджерами? | Which plan should I choose if I hardly make calls and only use messengers? |
| tel-07 | telecom | specific | Який домашній інтернет підключити в квартиру? | Which home internet should I connect in my flat? |
| tel-08 | telecom | specific | Який провайдер домашнього інтернету найкраще працює під час відключень світла? | Which home internet provider works best during power outages? |
| tel-09 | telecom | specific | Який мобільний інтернет обрати для роботи з ноутбука? | Which mobile internet should I choose for working from a laptop? |
| tel-10 | telecom | specific | Який резервний інтернет варто мати на випадок блекауту? | What backup internet is worth having in case of a blackout? |
| tel-11 | telecom | comparison | Порівняй мобільних операторів в Україні за ціною і якістю. | Compare mobile operators in Ukraine by price and quality. |
| tel-12 | telecom | comparison | Порівняй провайдерів домашнього інтернету за швидкістю і ціною. | Compare home internet providers by speed and price. |
| tel-13 | telecom | comparison | Який оператор вигідніший для роумінгу в Європі? | Which operator is better value for roaming in Europe? |
| tel-14 | telecom | value | Який найдешевший мобільний тариф зараз? | What is the cheapest mobile plan right now? |
| tel-15 | telecom | value | Де вигідніше підключити інтернет і телебачення разом? | Where is it better value to get internet and TV together? |
| ins-01 | insurance | general | Яку страхову компанію обрати? | Which insurance company should I choose? |
| ins-02 | insurance | general | Яка страхова компанія найнадійніша в Україні? | Which insurance company is the most reliable in Ukraine? |
| ins-03 | insurance | general | Яка страхова найшвидше виплачує відшкодування? | Which insurer pays out claims the fastest? |
| ins-04 | insurance | specific | Де оформити автоцивілку (ОСЦПВ)? | Where should I buy compulsory motor third-party liability insurance (OSCPV)? |
| ins-05 | insurance | specific | Яке КАСКО обрати для автомобіля? | Which comprehensive car insurance (KASKO) should I choose? |
| ins-06 | insurance | specific | Яку медичну страховку обрати? | Which health insurance should I choose? |
| ins-07 | insurance | specific | Де застрахувати квартиру? | Where should I insure my flat? |
| ins-08 | insurance | specific | Яку страховку для подорожі за кордон обрати? | Which travel insurance should I choose for a trip abroad? |
| ins-09 | insurance | specific | Чи варто страхувати життя і в якій компанії? | Is it worth getting life insurance, and with which company? |
| ins-10 | insurance | specific | Яка страховка покриває воєнні ризики для житла? | Which insurance covers war risks for housing? |
| ins-11 | insurance | specific | Яку добровільну медичну страховку обрати, щоб покривала лікування в приватних клініках? | Which voluntary health insurance should I choose so that it covers treatment in private clinics? |
| ins-12 | insurance | comparison | Порівняй страхові компанії за надійністю та відгуками. | Compare insurance companies by reliability and reviews. |
| ins-13 | insurance | comparison | Порадь страхову для автомобіля, щоб без проблем отримати виплату. | Recommend a car insurer that pays out without problems. |
| ins-14 | insurance | value | Де вигідно купити страховку онлайн? | Where is it good value to buy insurance online? |
| ins-15 | insurance | value | Де оформити найдешевшу автоцивілку? | Where can I get the cheapest compulsory motor insurance? |
| edu-01 | education | general | Яку онлайн-платформу для навчання обрати? | Which online learning platform should I choose? |
| edu-02 | education | general | Як змінити професію — які курси пройти? | How do I change my profession — which courses should I take? |
| edu-03 | education | general | Які курси варто пройти, щоб швидше знайти роботу? | Which courses are worth taking to find a job faster? |
| edu-04 | education | specific | Де пройти курси програмування? | Where can I take programming courses? |
| edu-05 | education | specific | Де вивчити IT з нуля з працевлаштуванням? | Where can I learn IT from scratch with job placement? |
| edu-06 | education | specific | Яку онлайн-школу англійської обрати? | Which online English school should I choose? |
| edu-07 | education | specific | Де знайти репетитора з англійської онлайн? | Where can I find an online English tutor? |
| edu-08 | education | specific | Яку мовну школу обрати для вивчення польської чи німецької? | Which language school should I choose to learn Polish or German? |
| edu-09 | education | specific | Де навчитися дизайну онлайн? | Where can I learn design online? |
| edu-10 | education | specific | Які курси маркетингу обрати? | Which marketing courses should I choose? |
| edu-11 | education | specific | Які курси аналітики даних обрати? | Which data analytics courses should I choose? |
| edu-12 | education | specific | Де пройти курси підвищення кваліфікації з сертифікатом? | Where can I take professional development courses with a certificate? |
| edu-13 | education | comparison | Порівняй IT-школи в Україні. | Compare IT schools in Ukraine. |
| edu-14 | education | comparison | Де здобути другу вищу освіту? | Where can I get a second higher education degree? |
| edu-15 | education | value | Які безкоштовні онлайн-курси варто пройти? | Which free online courses are worth taking? |

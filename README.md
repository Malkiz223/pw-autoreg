# Автоматическая регистрация аккаунтов в Perfect World

Программа предназначена для автоматизации рутинной задачи по регистрации аккаунтов в MMORPG Perfect World. В первую
очередь программа регистрирует аккаунты в MY.GAMES, из этого следует, что зарегистрированный аккаунт будет работать в
любой из почти сотни игр компании.

### Запуск скрипта через Docker (предпочтительный способ)

1. Клонируем папку с проектом в желаемую директорию git clone https://github.com/Malkiz223/pw-autoreg.git && cd
   pw-autoreg
2. (опционально) Меняем имя файла .env.example на .env и указываем там APIKEY_2CAPTCHA, если необходимо регистрировать
   огромное количество аккаунтов (через 16 часов беспрерывной работы начнётся Mail.ru капча)
3.

### Зачем это нужно?

Порой автоматизация в играх может приносить доход, и "бутылочным горлышком" данного заработка будет лишь отсутствие
аккаунтов. Подобные аккаунты на торговых площадках продаются от одного рубля, что может быть проблемой, если мы хотим
иметь несколько тысяч аккаунтов.

Во многих играх компании MY.GAMES реализована система по стимуляции игроков, не заходивших в игру больше месяца. При
этом на пустом аккаунте будут появляться различные бонусы с потенциальной ценностью в несколько тысяч рублей на аккаунт.
На торговых площадках идут оптовые продажи аккаунтов с бонусами, и скупают их тысячами. Стоит лишь уточнить, что продажа
аккаунтов запрещена правилами игры, и что с продажи аккаунтов вы должны платить налоги.

### Как быстро я зарегистрирую N аккаунтов?

Регистрация одного аккаунта занимает 15-17 секунд~. Но помимо этого скорость регистрации аккаунта зависит от количества
используемых прокси. Из-за ограничения регистрации в 50 аккаунтов в час скорость может быть невысокой. Но вы можете
использовать прокси, линейно увеличивая скорость на 50 аккаунтов в час. Например, 100 прокси позволят регистрировать
5000 аккаунтов в час (или 120 000 в сутки)
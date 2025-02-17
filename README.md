<p style="font-size: 25px; text-align: center;"><b>Платформа умного поиска билетов для путешествий.</b></p>

<p style="font-size: 30px;"><u><a href="https://github.com/chagrygoris/aerotrans/blob/main/DESCRIPTION.pdf">Презентация проекта</a></u></p>
<p style="font-size: 18px;"><b>User interface. Возможности пользователя.</b></p>

    1. Веб-сервис.
        Пользователь регистрируется с помощью своего Telegram-аккаунта на сайте и заносится в базу данных. 
        Полученные данные впоследствии используются для настройки уведомлений в Telegram. Далее, пользуясь 
        типичным для сервисов бронирования интерфейсом, пользователь осуществляет поиск подходящих рейсов. 
        Мы хотим реализовать поддержку маршрутов с пересадками и планирование путешествий с обратными билетами. 
        Результаты сортируются по критериям времени и стоимости. Задумывается написать карту точек назначения: 
        города, в которые пользователь может добраться, подсвечиваются на географической карте с указаниями
        основных характеристик. 

    2. Телеграм-бот. 
        Основываясь на собранной при регистрации пользователей информации, планируется реализовать телеграмм-бота
        со следующими функциями: 
        а) присылает покупателям pdf-конспект посещения сайта: корзину запланированных путешествий. 
        б) поддерживает возможность отправки уведомлений об изменении цен на понравившиеся билеты, прогнозы
        на цены в будущем.
        в) приглашает друзей присоединиться к поездке.

<p style="font-size: 18px;"><b>Backend. Базы данных и поиск лучших маршрутов.</b></p>

    Планируется определить некоторый конечный список поддерживаемых пунктов назначения и создать базу
    данных с подходящими рейсами. Для этого мы хотим реализовать автоматический сбор информации с разных сайтов,
    предлагающих авиа, железнодорожные и автобусные билеты. База данных будет периодически обновляться. 
    Пользуясь алгоритмами обхода взвешенных графов, мы сможем быстро находить лучшие маршруты. 
    Подводя итог, мы предполагаем следующие базы данных: 
    а) пользователь -> телеграмм.
    б) пользователь -> корзина маршрутов
    в) информация о городах и граф городов
    г) маршруты: точка отправления -> точка назнчаения

<p style="font-size: 20px;"><u>Архитектура проекта в UML-нотации.</u></p>
<a href="https://ibb.co/L8RBCCg"><img src="https://i.ibb.co/hy9rKKd/aviasales.jpg" alt="aviasales" border="0"></a>


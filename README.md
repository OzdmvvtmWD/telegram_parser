1. Підключається до номерного Telegram за допомогою бібліотеки Telethon (не ТГ бот).
Імпортуємо те, що нам потрібно з Telethon, щоб створити клієнт Telegram у скрипті.Щоб підключитися до Telegram, потрібно api_idі api_hash. Щоб отримати ці параметри, потрібно перейти my.telegram.org,
і перейти в область інструментів розробки API . Існує форма, яку потрібно заповнити, і після цього отримуєм api_idта api_hash.
Зберігати облікові дані Telegram API у вихідному коді небезпечно, тому щоб уникнути проблем із безпекою, розміщуємо облікові дані API в іншому файлі під назвою config.ini.
Telegram авторизує облікові дані, а потім запитує код підтвердження та пароль, для Telegram.
2. Зчитує історію 10ти останніх (бажано за весь рік) переписок з клієнтами (чатів). Глибина кожної переписки 1 місяць. Можна задати і інші параметри.

BTN_HUNGER = "Голод"
BTN_MEAL = "Поела"
BTN_EXPORT = "Экспорт"

MSG_START_FIRST = (
    "Привет! Я помогу фиксировать чувство голода и приёмы пищи.\n\n"
    "Кнопки внизу:\n"
    "• Голод — записать, насколько вы голодны (0–10)\n"
    "• Поела — зафиксировать приём пищи\n"
    "• Экспорт — скачать данные для анализа\n\n"
    "Шкала голода:\n"
    "0 — нет голода · 3–4 — можно есть · 7+ — сильный голод\n\n"
    "Команды: /settings — время утреннего напоминания"
)

MSG_START_AGAIN = "Снова на связи. Запишите голод или приём пищи — кнопки внизу."

MSG_FORBIDDEN = "Этот бот личный и недоступен для других пользователей."

MSG_HUNGER_ASK = "Насколько вы сейчас голодны? Выберите от 0 до 10."

MSG_MEAL_TYPE = "Какой это был приём пищи?"

MSG_HUNGER_BEFORE = "Какой был голод перед едой? (0–10)"

MSG_SATIETY_AFTER = "Насколько вы сыты после еды? (0–10)"

MSG_CANCELLED = "Запись отменена."

MSG_MORNING = "Доброе утро. Как ты оцениваешь свой голод после пробуждения?"

MSG_INACTIVITY_1 = (
    "Давно не было записей. Какой сейчас голод? (0–10)\n\n"
    "Или нажмите «Поела», если вы ели."
)

MSG_INACTIVITY_2 = (
    "Всё ещё нет записей. Какой сейчас голод? (0–10)\n\n"
    "Или «Поела», если был приём пищи."
)

MSG_EXPORT_START = "Готовлю файл с вашими записями…"

MSG_EXPORT_EMPTY = "Пока нет записей для выгрузки."

MSG_UNKNOWN = "Используйте кнопки внизу или команды: /start, /settings, /export"

MSG_SETTINGS_BAD = "Не поняла формат. Отправьте время так: 08:00 или 07:30"


def msg_hunger_saved(level: int, hhmm: str) -> str:
    return f"Записала: голод {level}/10 · {hhmm}"


def msg_meal_saved(meal_label: str, hunger_before: int, satiety_after: int, hhmm: str) -> str:
    return (
        f"Записала: {meal_label} · голод до {hunger_before} → "
        f"сытость после {satiety_after} · {hhmm}"
    )


def msg_export_ok(count: int) -> str:
    return f"Файл готов. Всего записей: {count}."


def msg_settings(wake_up: str, timezone_name: str) -> str:
    return (
        "Настройки\n\n"
        f"Утреннее напоминание: {wake_up}\n"
        f"Часовой пояс: {timezone_name}\n\n"
        "Чтобы изменить время пробуждения, отправьте новое время в формате ЧЧ:ММ, например 07:30."
    )


def msg_settings_updated(wake_up: str) -> str:
    return f"Время утреннего напоминания: {wake_up}"

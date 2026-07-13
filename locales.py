from config import DEFAULT_LANG

TEXTS = {
    "ru": {
        "choose_language": (
            "🌍 <b>Выберите язык</b>\n"
            "Select your language · Tilni tanlang"
        ),
        "choose_level": (
            "🎌 <b>Выберите свой уровень JLPT</b>\n\n"
            "N5 — начальный, N1 — продвинутый.\n"
            "Уровень можно поменять в любой момент в настройках."
        ),
        "level_saved": "✅ Уровень установлен: <b>{level}</b>",
        "welcome": (
            "👋 <b>Привет, {name}!</b>\n\n"
            "Это бот для изучения японского языка 🇯🇵\n"
            "Учи слова и кандзи, повторяй по SRS, проверяй себя квизами "
            "и разбирай грамматику.\n\n"
            "Выбери действие в меню ниже 👇"
        ),
        "main_menu": "🏠 <b>Главное меню</b>",
        "btn_study": "📚 Учить",
        "btn_quiz": "📝 Квиз",
        "btn_grammar": "📖 Грамматика",
        "btn_stats": "📊 Прогресс",
        "btn_settings": "⚙️ Настройки",
        "btn_donate": "⭐️ Поддержать",
        "btn_back": "⬅️ Назад",
        "btn_prev": "◀️",
        "btn_next": "▶️",
        "loading": "⏳ Загружаю материал…",
        "study_no_due": (
            "🎉 <b>На сегодня всё повторено!</b>\n\n"
            "Новые слова приходят в ежедневной рассылке, "
            "или загляни позже."
        ),
        "study_front": (
            "🃏 <b>{front}</b>\n\n"
            "Вспомни значение и нажми «Показать ответ»."
        ),
        "btn_show_answer": "👀 Показать ответ",
        "study_reading_label": "🔊 Чтение",
        "study_meaning_label": "💬 Значение",
        "study_rate_prompt": "Насколько легко вспомнил?",
        "rating_again": "🔴 Не помню",
        "rating_hard": "🟡 Сложно",
        "rating_easy": "🟢 Легко",
        "study_done": (
            "✅ <b>Сессия завершена!</b>\n\n"
            "Повторено карточек: <b>{count}</b>.\n"
            "Так держать! 💪"
        ),
        "quiz_intro": "📝 <b>Квиз</b> — {total} вопросов. Погнали!",
        "quiz_not_enough": (
            "😔 Пока недостаточно материала для квиза.\n"
            "Попробуй позже — бот подтянет слова с сервера."
        ),
        "quiz_question": (
            "❓ <b>Вопрос {index}/{total}</b>\n\n"
            "Что означает <b>{word}</b>?"
        ),
        "quiz_correct": "✅ Верно!",
        "quiz_wrong": "❌ Неверно. Правильный ответ: <b>{answer}</b>",
        "quiz_result": (
            "🏁 <b>Квиз завершён!</b>\n\n"
            "Правильных ответов: <b>{correct}/{total}</b>"
        ),
        "grammar_none": (
            "😔 Для этого уровня грамматика пока не добавлена."
        ),
        "grammar_card": (
            "📖 <b>{title}</b>  ({level})\n\n"
            "🔧 <b>Структура:</b> {structure}\n\n"
            "{explanation}\n\n"
            "📝 <b>Примеры:</b>\n{examples}"
        ),
        "grammar_counter": "Конструкция {index} из {total}",
        "settings_title": (
            "⚙️ <b>Настройки</b>\n\n"
            "Язык: <b>{lang}</b>\n"
            "Уровень: <b>{level}</b>\n"
            "Время рассылки: <b>{time}</b>\n"
            "Новых слов в день: <b>{count}</b>"
        ),
        "btn_set_language": "🌐 Язык интерфейса",
        "btn_set_level": "🎌 Уровень JLPT",
        "btn_set_time": "⏰ Время рассылки",
        "btn_set_count": "🔢 Слов в день",
        "settings_enter_time": (
            "⏰ Введи время ежедневной рассылки в формате <b>ЧЧ:ММ</b> "
            "(например, 09:00).\n\n"
            "Часовой пояс: <b>{tz}</b>"
        ),
        "settings_time_invalid": (
            "⚠️ Не похоже на время. Введи в формате ЧЧ:ММ, например 21:30."
        ),
        "settings_time_saved": "✅ Время рассылки установлено: <b>{time}</b>",
        "settings_enter_count": (
            "🔢 Сколько новых слов присылать в день? "
            "Введи число от {min} до {max}."
        ),
        "settings_count_invalid": (
            "⚠️ Введи целое число от {min} до {max}."
        ),
        "settings_count_saved": "✅ Новых слов в день: <b>{count}</b>",
        "stats_title": "📊 <b>Твой прогресс</b>",
        "stats_body": (
            "🎌 Уровень: <b>{level}</b>\n"
            "🔥 Стрик: <b>{streak}</b> дн.\n\n"
            "📚 Карточек всего: <b>{total}</b>\n"
            "✅ Изучается: <b>{learned}</b>\n"
            "⏰ К повторению сейчас: <b>{due}</b>\n\n"
            "📝 Квизов пройдено: <b>{quiz_count}</b>\n"
            "🎯 Точность в квизах: <b>{accuracy}%</b>"
        ),
        "daily_title": "🌅 <b>Порция японского на сегодня!</b>",
        "daily_words_header": "🆕 <b>Новые слова:</b>",
        "daily_word_line": "• <b>{word}</b> ({reading}) — {meaning}",
        "daily_kanji_header": "🈶 <b>Кандзи дня:</b>",
        "daily_kanji_line": "• <b>{character}</b> — {meaning}",
        "daily_grammar_header": "📖 <b>Грамматика дня:</b>",
        "daily_grammar_line": "<b>{title}</b> — {structure}",
        "daily_footer": (
            "Эти слова добавлены в SRS. Нажми 📚 <b>Учить</b>, "
            "чтобы повторить их."
        ),
        "choose_amount": (
            "⭐️ <b>Поддержать проект</b>\n\n"
            "Сколько звёзд отправить?"
        ),
        "btn_custom_amount": "✏️ Своя сумма",
        "enter_custom_amount": (
            "✏️ <b>Своя сумма</b>\n\n"
            "Введи целое число от {min} до {max} ⭐️"
        ),
        "invalid_amount": (
            "⚠️ Это не похоже на число.\n"
            "Введи целое от {min} до {max} ⭐️"
        ),
        "ask_comment": (
            "💬 <b>Донат {amount}⭐️</b>\n\n"
            "Хочешь добавить сообщение к донату?"
        ),
        "btn_write_comment": "✏️ Написать сообщение",
        "btn_skip": "⏭ Пропустить",
        "enter_comment": "✏️ Напиши сообщение:",
        "invoice_title": "Поддержка проекта",
        "invoice_description": "Донат {amount} ⭐️ на развитие бота",
        "thank_you": (
            "🎉 <b>Спасибо за поддержку!</b> 💛\n\n"
            "Твой донат <b>{amount}⭐️</b> получен."
        ),
    },
    "en": {
        "choose_language": (
            "🌍 <b>Select your language</b>\n"
            "Выберите язык · Tilni tanlang"
        ),
        "choose_level": (
            "🎌 <b>Choose your JLPT level</b>\n\n"
            "N5 — beginner, N1 — advanced.\n"
            "You can change the level anytime in settings."
        ),
        "level_saved": "✅ Level set: <b>{level}</b>",
        "welcome": (
            "👋 <b>Hi, {name}!</b>\n\n"
            "This is a bot for learning Japanese 🇯🇵\n"
            "Learn words and kanji, review with SRS, test yourself with "
            "quizzes and study grammar.\n\n"
            "Pick an action from the menu below 👇"
        ),
        "main_menu": "🏠 <b>Main menu</b>",
        "btn_study": "📚 Study",
        "btn_quiz": "📝 Quiz",
        "btn_grammar": "📖 Grammar",
        "btn_stats": "📊 Progress",
        "btn_settings": "⚙️ Settings",
        "btn_donate": "⭐️ Support",
        "btn_back": "⬅️ Back",
        "btn_prev": "◀️",
        "btn_next": "▶️",
        "loading": "⏳ Loading material…",
        "study_no_due": (
            "🎉 <b>Everything is reviewed for today!</b>\n\n"
            "New words arrive in the daily digest, or come back later."
        ),
        "study_front": (
            "🃏 <b>{front}</b>\n\n"
            "Recall the meaning and tap “Show answer”."
        ),
        "btn_show_answer": "👀 Show answer",
        "study_reading_label": "🔊 Reading",
        "study_meaning_label": "💬 Meaning",
        "study_rate_prompt": "How easily did you recall it?",
        "rating_again": "🔴 Forgot",
        "rating_hard": "🟡 Hard",
        "rating_easy": "🟢 Easy",
        "study_done": (
            "✅ <b>Session complete!</b>\n\n"
            "Cards reviewed: <b>{count}</b>.\n"
            "Keep it up! 💪"
        ),
        "quiz_intro": "📝 <b>Quiz</b> — {total} questions. Let's go!",
        "quiz_not_enough": (
            "😔 Not enough material for a quiz yet.\n"
            "Try again later — the bot will fetch more words."
        ),
        "quiz_question": (
            "❓ <b>Question {index}/{total}</b>\n\n"
            "What does <b>{word}</b> mean?"
        ),
        "quiz_correct": "✅ Correct!",
        "quiz_wrong": "❌ Wrong. Correct answer: <b>{answer}</b>",
        "quiz_result": (
            "🏁 <b>Quiz complete!</b>\n\n"
            "Correct answers: <b>{correct}/{total}</b>"
        ),
        "grammar_none": (
            "😔 No grammar has been added for this level yet."
        ),
        "grammar_card": (
            "📖 <b>{title}</b>  ({level})\n\n"
            "🔧 <b>Structure:</b> {structure}\n\n"
            "{explanation}\n\n"
            "📝 <b>Examples:</b>\n{examples}"
        ),
        "grammar_counter": "Point {index} of {total}",
        "settings_title": (
            "⚙️ <b>Settings</b>\n\n"
            "Language: <b>{lang}</b>\n"
            "Level: <b>{level}</b>\n"
            "Digest time: <b>{time}</b>\n"
            "New words per day: <b>{count}</b>"
        ),
        "btn_set_language": "🌐 Interface language",
        "btn_set_level": "🎌 JLPT level",
        "btn_set_time": "⏰ Digest time",
        "btn_set_count": "🔢 Words per day",
        "settings_enter_time": (
            "⏰ Enter the daily digest time in <b>HH:MM</b> format "
            "(for example, 09:00).\n\n"
            "Timezone: <b>{tz}</b>"
        ),
        "settings_time_invalid": (
            "⚠️ That doesn't look like a time. Use HH:MM, e.g. 21:30."
        ),
        "settings_time_saved": "✅ Digest time set: <b>{time}</b>",
        "settings_enter_count": (
            "🔢 How many new words per day? Enter a number "
            "from {min} to {max}."
        ),
        "settings_count_invalid": (
            "⚠️ Enter a whole number from {min} to {max}."
        ),
        "settings_count_saved": "✅ New words per day: <b>{count}</b>",
        "stats_title": "📊 <b>Your progress</b>",
        "stats_body": (
            "🎌 Level: <b>{level}</b>\n"
            "🔥 Streak: <b>{streak}</b> days\n\n"
            "📚 Total cards: <b>{total}</b>\n"
            "✅ Learning: <b>{learned}</b>\n"
            "⏰ Due now: <b>{due}</b>\n\n"
            "📝 Quizzes taken: <b>{quiz_count}</b>\n"
            "🎯 Quiz accuracy: <b>{accuracy}%</b>"
        ),
        "daily_title": "🌅 <b>Your Japanese for today!</b>",
        "daily_words_header": "🆕 <b>New words:</b>",
        "daily_word_line": "• <b>{word}</b> ({reading}) — {meaning}",
        "daily_kanji_header": "🈶 <b>Kanji of the day:</b>",
        "daily_kanji_line": "• <b>{character}</b> — {meaning}",
        "daily_grammar_header": "📖 <b>Grammar of the day:</b>",
        "daily_grammar_line": "<b>{title}</b> — {structure}",
        "daily_footer": (
            "These words were added to your SRS. Tap 📚 <b>Study</b> "
            "to review them."
        ),
        "choose_amount": (
            "⭐️ <b>Support the project</b>\n\n"
            "How many stars to send?"
        ),
        "btn_custom_amount": "✏️ Custom amount",
        "enter_custom_amount": (
            "✏️ <b>Custom amount</b>\n\n"
            "Enter a whole number from {min} to {max} ⭐️"
        ),
        "invalid_amount": (
            "⚠️ That doesn't look like a number.\n"
            "Enter a whole number from {min} to {max} ⭐️"
        ),
        "ask_comment": (
            "💬 <b>Donation {amount}⭐️</b>\n\n"
            "Want to add a message to your donation?"
        ),
        "btn_write_comment": "✏️ Write a message",
        "btn_skip": "⏭ Skip",
        "enter_comment": "✏️ Write your message:",
        "invoice_title": "Support the project",
        "invoice_description": "Donation of {amount} ⭐️ for the bot",
        "thank_you": (
            "🎉 <b>Thank you for your support!</b> 💛\n\n"
            "Your donation of <b>{amount}⭐️</b> was received."
        ),
    },
    "uz": {
        "choose_language": (
            "🌍 <b>Tilni tanlang</b>\n"
            "Выберите язык · Select your language"
        ),
        "choose_level": (
            "🎌 <b>JLPT darajangizni tanlang</b>\n\n"
            "N5 — boshlang'ich, N1 — yuqori daraja.\n"
            "Darajani istalgan vaqtda sozlamalarda o'zgartirish mumkin."
        ),
        "level_saved": "✅ Daraja o'rnatildi: <b>{level}</b>",
        "welcome": (
            "👋 <b>Salom, {name}!</b>\n\n"
            "Bu yapon tilini o'rganish uchun bot 🇯🇵\n"
            "So'z va kanjilarni o'rganing, SRS orqali takrorlang, "
            "kvizlar bilan bilimingizni sinang va grammatikani o'rganing.\n\n"
            "Quyidagi menyudan amalni tanlang 👇"
        ),
        "main_menu": "🏠 <b>Asosiy menyu</b>",
        "btn_study": "📚 O'rganish",
        "btn_quiz": "📝 Kviz",
        "btn_grammar": "📖 Grammatika",
        "btn_stats": "📊 Progress",
        "btn_settings": "⚙️ Sozlamalar",
        "btn_donate": "⭐️ Qo'llab-quvvatlash",
        "btn_back": "⬅️ Orqaga",
        "btn_prev": "◀️",
        "btn_next": "▶️",
        "loading": "⏳ Material yuklanmoqda…",
        "study_no_due": (
            "🎉 <b>Bugungi barcha kartalar takrorlandi!</b>\n\n"
            "Yangi so'zlar kunlik xabarda keladi, yoki keyinroq qayting."
        ),
        "study_front": (
            "🃏 <b>{front}</b>\n\n"
            "Ma'nosini eslang va «Javobni ko'rsatish»ni bosing."
        ),
        "btn_show_answer": "👀 Javobni ko'rsatish",
        "study_reading_label": "🔊 O'qilishi",
        "study_meaning_label": "💬 Ma'nosi",
        "study_rate_prompt": "Qanchalik oson esladingiz?",
        "rating_again": "🔴 Eslamadim",
        "rating_hard": "🟡 Qiyin",
        "rating_easy": "🟢 Oson",
        "study_done": (
            "✅ <b>Sessiya tugadi!</b>\n\n"
            "Takrorlangan kartalar: <b>{count}</b>.\n"
            "Shunday davom eting! 💪"
        ),
        "quiz_intro": "📝 <b>Kviz</b> — {total} ta savol. Boshladik!",
        "quiz_not_enough": (
            "😔 Kviz uchun hozircha material yetarli emas.\n"
            "Keyinroq urinib ko'ring — bot serverdan so'zlarni yuklaydi."
        ),
        "quiz_question": (
            "❓ <b>Savol {index}/{total}</b>\n\n"
            "<b>{word}</b> nimani anglatadi?"
        ),
        "quiz_correct": "✅ To'g'ri!",
        "quiz_wrong": "❌ Noto'g'ri. To'g'ri javob: <b>{answer}</b>",
        "quiz_result": (
            "🏁 <b>Kviz tugadi!</b>\n\n"
            "To'g'ri javoblar: <b>{correct}/{total}</b>"
        ),
        "grammar_none": (
            "😔 Bu daraja uchun grammatika hali qo'shilmagan."
        ),
        "grammar_card": (
            "📖 <b>{title}</b>  ({level})\n\n"
            "🔧 <b>Tuzilishi:</b> {structure}\n\n"
            "{explanation}\n\n"
            "📝 <b>Misollar:</b>\n{examples}"
        ),
        "grammar_counter": "{total} tadan {index}-si",
        "settings_title": (
            "⚙️ <b>Sozlamalar</b>\n\n"
            "Til: <b>{lang}</b>\n"
            "Daraja: <b>{level}</b>\n"
            "Xabar vaqti: <b>{time}</b>\n"
            "Kuniga yangi so'zlar: <b>{count}</b>"
        ),
        "btn_set_language": "🌐 Interfeys tili",
        "btn_set_level": "🎌 JLPT darajasi",
        "btn_set_time": "⏰ Xabar vaqti",
        "btn_set_count": "🔢 Kuniga so'zlar",
        "settings_enter_time": (
            "⏰ Kunlik xabar vaqtini <b>SS:DD</b> formatida kiriting "
            "(masalan, 09:00).\n\n"
            "Vaqt mintaqasi: <b>{tz}</b>"
        ),
        "settings_time_invalid": (
            "⚠️ Bu vaqtga o'xshamaydi. SS:DD formatida kiriting, masalan 21:30."
        ),
        "settings_time_saved": "✅ Xabar vaqti o'rnatildi: <b>{time}</b>",
        "settings_enter_count": (
            "🔢 Kuniga nechta yangi so'z kelsin? "
            "{min} dan {max} gacha son kiriting."
        ),
        "settings_count_invalid": (
            "⚠️ {min} dan {max} gacha butun son kiriting."
        ),
        "settings_count_saved": "✅ Kuniga yangi so'zlar: <b>{count}</b>",
        "stats_title": "📊 <b>Sizning progressingiz</b>",
        "stats_body": (
            "🎌 Daraja: <b>{level}</b>\n"
            "🔥 Streak: <b>{streak}</b> kun\n\n"
            "📚 Jami kartalar: <b>{total}</b>\n"
            "✅ O'rganilmoqda: <b>{learned}</b>\n"
            "⏰ Hozir takrorlash uchun: <b>{due}</b>\n\n"
            "📝 O'tilgan kvizlar: <b>{quiz_count}</b>\n"
            "🎯 Kviz aniqligi: <b>{accuracy}%</b>"
        ),
        "daily_title": "🌅 <b>Bugungi yapon tili ulushingiz!</b>",
        "daily_words_header": "🆕 <b>Yangi so'zlar:</b>",
        "daily_word_line": "• <b>{word}</b> ({reading}) — {meaning}",
        "daily_kanji_header": "🈶 <b>Kun kanjisi:</b>",
        "daily_kanji_line": "• <b>{character}</b> — {meaning}",
        "daily_grammar_header": "📖 <b>Kun grammatikasi:</b>",
        "daily_grammar_line": "<b>{title}</b> — {structure}",
        "daily_footer": (
            "Bu so'zlar SRS'ga qo'shildi. Ularni takrorlash uchun "
            "📚 <b>O'rganish</b>ni bosing."
        ),
        "choose_amount": (
            "⭐️ <b>Loyihani qo'llab-quvvatlash</b>\n\n"
            "Nechta yulduz yuborasiz?"
        ),
        "btn_custom_amount": "✏️ O'z miqdori",
        "enter_custom_amount": (
            "✏️ <b>O'z miqdori</b>\n\n"
            "{min} dan {max} gacha butun son kiriting ⭐️"
        ),
        "invalid_amount": (
            "⚠️ Bu songa o'xshamaydi.\n"
            "{min} dan {max} gacha butun son kiriting ⭐️"
        ),
        "ask_comment": (
            "💬 <b>Donat {amount}⭐️</b>\n\n"
            "Donatga xabar qo'shmoqchimisiz?"
        ),
        "btn_write_comment": "✏️ Xabar yozish",
        "btn_skip": "⏭ O'tkazib yuborish",
        "enter_comment": "✏️ Xabaringizni yozing:",
        "invoice_title": "Loyihani qo'llab-quvvatlash",
        "invoice_description": "Bot rivoji uchun {amount} ⭐️ donat",
        "thank_you": (
            "🎉 <b>Qo'llab-quvvatlaganingiz uchun rahmat!</b> 💛\n\n"
            "<b>{amount}⭐️</b> donatingiz qabul qilindi."
        ),
    },
}

LANG_NAMES = {
    "ru": "Русский",
    "en": "English",
    "uz": "O'zbekcha",
}


def get_text(lang, key, **kwargs):
    """Возвращает текст по ключу для нужного языка с подстановкой значений."""
    if lang not in TEXTS:
        lang = DEFAULT_LANG
    if key in TEXTS[lang]:
        text = TEXTS[lang][key]
    else:
        text = TEXTS[DEFAULT_LANG][key]
    if kwargs:
        text = text.format(**kwargs)
    return text


def get_all_translations(key):
    """Возвращает переводы ключа на всех языках (для фильтров кнопок)."""
    translations = []
    for lang in TEXTS:
        if key in TEXTS[lang]:
            translations.append(TEXTS[lang][key])
    return translations


def get_lang_name(lang):
    """Возвращает человекочитаемое название языка."""
    if lang in LANG_NAMES:
        return LANG_NAMES[lang]
    return lang

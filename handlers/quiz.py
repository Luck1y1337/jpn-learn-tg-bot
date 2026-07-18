import random

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import content_api
import database
import keyboards
from common import resolve_lang, resolve_level
from config import QUIZ_OPTIONS, QUIZ_QUESTIONS
from locales import get_all_translations, get_text

router = Router()

POOL_SIZE = 40


def meaning_of(lang, row):
    """Возвращает значение слова на языке пользователя (с запасным EN)."""
    if lang == "ru":
        meaning = row["meaning_ru"]
    elif lang == "uz":
        meaning = row["meaning_uz"]
    else:
        meaning = row["meaning_en"]

    if meaning is None or meaning == "":
        meaning = row["meaning_en"]
    return meaning


def build_questions(lang, pool):
    """Строит список вопросов квиза из набора слов."""
    questions = []
    question_words = pool[:QUIZ_QUESTIONS]

    for qword in question_words:
        correct = meaning_of(lang, qword)

        distractors = []
        for other in pool:
            if other["word"] == qword["word"]:
                continue
            other_meaning = meaning_of(lang, other)
            if other_meaning == correct:
                continue
            if other_meaning in distractors:
                continue
            distractors.append(other_meaning)

        random.shuffle(distractors)
        needed = QUIZ_OPTIONS - 1
        chosen_distractors = distractors[:needed]

        options = [correct] + chosen_distractors
        random.shuffle(options)
        correct_index = options.index(correct)

        question = {
            "word": qword["word"],
            "options": options,
            "correct_index": correct_index,
        }
        questions.append(question)

    return questions


async def send_question(message_or_callback_message, state, lang):
    """Отправляет текущий вопрос квиза."""
    data = await state.get_data()
    quiz = data.get("quiz")
    index = data.get("q_index", 0)

    question = quiz[index]
    text = get_text(
        lang,
        "quiz_question",
        index=index + 1,
        total=len(quiz),
        word=question["word"],
    )
    await message_or_callback_message.answer(
        text,
        reply_markup=keyboards.quiz_options_keyboard(question["options"]),
    )


async def open_quiz(target, user_id, state):
    """Начинает квиз по словам текущего уровня. Общее ядро для команды и хаба."""
    await state.clear()
    lang = await resolve_lang(user_id)
    level = await resolve_level(user_id)

    await target.answer(get_text(lang, "loading"))
    await content_api.ensure_words_cached(level, POOL_SIZE)

    pool = await database.get_random_cached_words(level, POOL_SIZE)
    if len(pool) < QUIZ_OPTIONS:
        await target.answer(get_text(lang, "quiz_not_enough"))
        return

    questions = build_questions(lang, pool)
    if len(questions) == 0:
        await target.answer(get_text(lang, "quiz_not_enough"))
        return

    await state.update_data(quiz=questions, q_index=0, correct=0)
    await target.answer(get_text(lang, "quiz_intro", total=len(questions)))
    await send_question(target, state, lang)


@router.message(Command("quiz"))
@router.message(F.text.in_(get_all_translations("btn_quiz")))
async def start_quiz(message: Message, state: FSMContext):
    """Команда /quiz и кнопка меню — запускают квиз."""
    await open_quiz(message, message.from_user.id, state)


@router.callback_query(F.data.startswith("quiz:ans:"))
async def callback_answer(callback: CallbackQuery, state: FSMContext):
    """Проверяет ответ и переходит к следующему вопросу или к итогу."""
    lang = await resolve_lang(callback.from_user.id)

    data = await state.get_data()
    quiz = data.get("quiz")
    if quiz is None:
        await callback.answer()
        return

    index = data.get("q_index", 0)
    correct_count = data.get("correct", 0)
    # Защита от гонки: при быстром двойном тапе индекс может уже выйти
    # за границы — тихо игнорируем устаревший callback, а не падаем.
    if index >= len(quiz):
        await callback.answer()
        return
    question = quiz[index]

    chosen = int(callback.data.split(":")[2])
    correct_index = question["correct_index"]

    if chosen == correct_index:
        correct_count = correct_count + 1
        feedback = get_text(lang, "quiz_correct")
    else:
        answer_text = question["options"][correct_index]
        feedback = get_text(lang, "quiz_wrong", answer=answer_text)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer(text=feedback.replace("<b>", "").replace("</b>", ""))

    next_index = index + 1
    if next_index >= len(quiz):
        await database.add_quiz_result(
            callback.from_user.id, correct_count, len(quiz)
        )
        await state.clear()
        await callback.message.answer(
            get_text(
                lang,
                "quiz_result",
                correct=correct_count,
                total=len(quiz),
            )
        )
        return

    await state.update_data(q_index=next_index, correct=correct_count)
    await send_question(callback.message, state, lang)

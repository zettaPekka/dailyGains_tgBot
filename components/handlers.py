from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

import logging

from database.crud import chek_user, chek_today_achievement, add_achievement_to_db, get_today_achievement, get_statistics
import components.keyboards as kb
from components.states import Achievement


logging.basicConfig(level=logging.INFO)

router = Router()

test_achiv = {}

@router.message(CommandStart())
async def start(message: Message):
    await message.answer('<b>💫 Добро пожаловать в DailyGains!\n\nЗдесь ты можешь каждый день отмечать свои маленькие и большие победы, следить за прогрессом и вдохновляться своими же успехами.</b>\n\n<i>«Неважно, медленно ты идешь или быстро, главное — не останавливаться» </i>',
                            reply_markup=kb.start_kb)
    await chek_user(user_id=message.from_user.id)

@router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text('<b>💫 Добро пожаловать в DailyGains!\n\nТы можешь каждый день отмечать свои маленькие и большие победы, следить за прогрессом и вдохновляться своими же успехами.</b>\n\n<i>«Неважно, медленно ты идешь или быстро, главное — не останавливаться» </i>',
                                    reply_markup=kb.start_kb)
    await state.clear()

@router.callback_query(F.data == 'add_achievement')
async def write_achievement(callback: CallbackQuery, state: FSMContext):
    res = await chek_today_achievement(user_id=callback.message.chat.id)
    if res:
        await callback.answer()
        await callback.message.edit_text('<b><i>📝 ЗАПИШИ СВОЙ ПРОГРЕСС</i>\n\nДаже маленькие победы заслуживают внимания!\nНапиши, чему ты научился, что улучшил или как проявил себя. (Но ограничься 200 символами)</b>',
                                        reply_markup=kb.back_kb)
        await state.set_state(Achievement.add_achievement)
    else:
        await callback.message.edit_text('<b>Ты уже добавил сегодня свой прогресс, можешь отредактироать его</b>',
                                        reply_markup=kb.edit_kb)
        await callback.answer('Ты уже стал лучше!')

@router.message(Command('add'))
async def write_achievement(message: Message, state: FSMContext):
    res = await chek_today_achievement(user_id=message.chat.id)
    if res:
        await message.answer('<b><i>📝 ЗАПИШИ СВОЙ ПРОГРЕСС</i>\n\nДаже маленькие победы заслуживают внимания!\nНапиши, чему ты научился, что улучшил или как проявил себя. (Но ограничься 200 символами)</b>',
                                        reply_markup=kb.back_kb)
        await state.set_state(Achievement.add_achievement)
    else:
        await message.answer('<b>Ты уже добавил сегодня свой прогресс, можешь отредактироать его</b>',
                                        reply_markup=kb.edit_kb)

@router.message(Achievement.add_achievement)
async def add_achievement(message: Message, state: FSMContext):
    if len(message.text) > 200:
        await message.answer('<b>Это очень круто, но к сожалению нельзя добавить текст более 200 символов, попробуй еще раз</b>')
    else:
        await add_achievement_to_db(user_id=message.from_user.id, achievement=message.text)
        await message.answer('<b>Ваш прогресс успешно сохранен!</b>',
                                reply_markup=kb.statistics_kb)
        await state.clear()

@router.callback_query(F.data == 'edit_achievement')
async def edit_achievement(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    today_achievement = await get_today_achievement(user_id=callback.message.chat.id)
    if today_achievement:
        today_achievement = today_achievement.replace('<', '&lt;').replace('>', '&gt;')
        await callback.message.answer(f'<b>Введите новый текст для сегдняшней статистики (до 200 символов)</b>\n\n<code>{today_achievement}</code>',
                                        reply_markup=kb.back_kb)
        await state.set_state(Achievement.edit_achievement)
    else:
        await callback.message.answer('<b>Сегодня вы еще не добавили свой прогресс в бота, вы можете добавить его нажав кнопку ниже</b>',
                                reply_markup=kb.add_achievement)

@router.message(Command('edit'))
async def edit_achievement(message: Message, state: FSMContext):
    today_achievement = await get_today_achievement(user_id=message.chat.id)
    if today_achievement:
        today_achievement = today_achievement.replace('<', '&lt;').replace('>', '&gt;')
        await message.answer(f'<b>Введите новый текст для сегдняшней статистики (до 200 символов)</b>\n\n<code>{today_achievement}</code>',
                                reply_markup=kb.back_kb)
        await state.set_state(Achievement.edit_achievement)
    else:
        await message.answer('<b>Сегодня вы еще не добавили свой прогресс в бота, вы можете добавить его нажав кнопку ниже</b>',
                                reply_markup=kb.add_achievement)

@router.message(Achievement.edit_achievement)
async def edit_achievement(message: Message, state: FSMContext):
    if len(message.text) > 200:
        await message.answer('<b>Это очень круто, но к сожалению нельзя добавить текст более 200 символов</b>')
    else:
        await add_achievement_to_db(user_id=message.from_user.id, achievement=message.text)
        achievement = message.text.replace('<', '&lt;').replace('>', '&gt;')
        await message.answer(f'<b>Ваш прогресс успешно обновлен!</b>\n\n<i>{achievement}</i>',
                                reply_markup=kb.statistics_kb)
        await state.clear()

@router.callback_query(F.data == 'statistics')
async def statistics(callback: CallbackQuery):
    await callback.answer('')
    data = await get_statistics(user_id=callback.message.chat.id)
    if data:
        answer_text = ['']
        page = 0
        for date, achievement in data.items():
            page_i = page // 15
            if len(answer_text) < (page_i + 1): answer_text.append('')
            achievement_parse = achievement.replace('<', '&lt;').replace('>', '&gt;')
            answer_text[page_i] += f'<b>• {date}</b>\n<i>{achievement_parse}</i>\n\n'
            page += 1
        if len(answer_text[0]) < 15:
            await callback.message.answer(f'Страница №1\n\n{answer_text[0]}\n\n<b>Если вам нужна полная статистика в 1 файле то обращайтесь к @zettapekka</b>')    
        else:
            await callback.message.answer(f'Страница №1\n\n{answer_text[0]}', reply_markup=kb.change_pages(1))    
    else:
        await callback.message.answer('<b>Вы еще не добавляли прогресс в бота, сегодня идеальное время для начала!</b>', 
                                        reply_markup=kb.add_achievement)

@router.message(Command('statistics'))
async def statistics(message: Message):
    data = await get_statistics(user_id=message.chat.id)
    if data:
        answer_text = ['']
        page = 0
        for date, achievement in data.items():
            page_i = page // 15
            if len(answer_text) < (page_i + 1): answer_text.append('')
            achievement_parse = achievement.replace('<', '&lt;').replace('>', '&gt;')
            answer_text[page_i] += f'<b>• {date}</b>\n<i>{achievement_parse}</i>\n\n'
            page += 1
        if len(answer_text[0]) < 15:
            await message.answer(f'Страница №1\n\n{answer_text[0]}\n\n<b>Если вам нужна полная статистика в 1 файле то обращайтесь к @zettapekka</b>')    
        else:
            await message.answer(f'Страница №1\n\n{answer_text[0]}', reply_markup=kb.change_pages(1))    
    else:
        await message.answer('<b>Вы еще не добавляли прогресс в бота, сегодня идеальное время для начала!</b>', 
                                        reply_markup=kb.add_achievement)

@router.callback_query(F.data.startswith('before_page_'))
async def before_page_index(callback: CallbackQuery):
    await callback.answer()
    data = await get_statistics(user_id=callback.message.chat.id)
    if data:
        answer_text = ['']
        page = 0
        for date, achievement in data.items():
            page_i = page // 15
            if len(answer_text) < (page_i + 1): answer_text.append('')
            achievement_parse = achievement.replace('<', '&lt;').replace('>', '&gt;')
            answer_text[page_i] += f'<b>• {date}</b>\n<i>{achievement_parse}</i>\n\n'
            page += 1
    try:
        index_page = int(callback.data.split('_')[-1])
        if index_page != 0:
            await callback.message.answer(f'Страница №{index_page}\n\n{answer_text[index_page - 1]}', reply_markup=kb.change_pages(index_page))
        else: 
            await callback.message.answer('<b>Страница не найдена</b>')
    except:
        await callback.message.answer('<b>Страница не найдена</b>')

@router.callback_query(F.data.startswith('after_page_'))
async def after_page_index(callback: CallbackQuery):
    await callback.answer()
    data = await get_statistics(user_id=callback.message.chat.id)
    if data:
        answer_text = ['']
        page = 0
        for date, achievement in data.items():
            page_i = page // 15
            if len(answer_text) < (page_i + 1): answer_text.append('')
            achievement_parse = achievement.replace('<', '&lt;').replace('>', '&gt;')
            answer_text[page_i] += f'<b>• {date}</b>\n<i>{achievement_parse}</i>\n\n'
            page += 1
    try:
        index_page = int(callback.data.split('_')[-1])
        await callback.message.answer(f'Страница №{index_page}\n\n{answer_text[index_page - 1]}', reply_markup=kb.change_pages(index_page))
    except:
        await callback.message.answer('<b>Страница не найдена</b>')

@router.message(Command('info'))
async def info(message: Message):
    await message.answer('<b>Этот бот помогает отслеживать твой прогресс каждый день.\n\nКак это работает: \n• <i>Добавить</i>: Нажми кнопку "Добавить", чтобы записать, в чем ты стал лучше сегодня. \n• <i>Редактировать</i>: Если хочешь изменить сегодняшнюю запись, нажми "Редактировать". \n• <i>Статистика</i>: Здесь можно посмотреть историю своего прогресса. Листай страницы — на каждой отображается по 15 дней.</b>')

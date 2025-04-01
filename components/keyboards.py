from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить➕', callback_data='add_achievement'),
        InlineKeyboardButton(text='Редактировать✍🏻', callback_data='edit_achievement')],
    [InlineKeyboardButton(text='Статистика', callback_data='statistics')]
])

back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='back')]
])

edit_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Редактироать✍🏻', callback_data='edit_achievement'),
        InlineKeyboardButton(text='Назад', callback_data='back')]
])

add_achievement = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить➕', callback_data='add_achievement'),
        InlineKeyboardButton(text='Назад', callback_data='back')]
])

statistics_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='back'),
        InlineKeyboardButton(text='Редактировать✍🏻', callback_data='edit_achievement')],
    [InlineKeyboardButton(text='Статистика', callback_data='statistics')]
])

def change_pages(current_page: int):
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️', callback_data=f'before_page_{current_page - 1}'),
        InlineKeyboardButton(text='Назад', callback_data='back'),
        InlineKeyboardButton(text='➡️', callback_data=f'after_page_{current_page + 1}')]
])

#from xml.etree.ElementPath import _Callback
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from callback_datas import NamesCallback

#---Main Menu---

btnTransaction = InlineKeyboardButton(text="Добавить операцию", callback_data="btn:MainMenu:AddTransaction")
MainMenu = InlineKeyboardMarkup().insert(btnTransaction)

btnCancel = InlineKeyboardButton(text="Отмена", callback_data="cancel")

#---Name---
btnChoiceName = InlineKeyboardButton(text='Выбрать из списка', callback_data="btn:NameMenu:Choice")
btnAddName = InlineKeyboardButton(text='Добавить новое', callback_data="btn:NameMenu:Add")
NameMenu = InlineKeyboardMarkup(row_width=1).insert(btnAddName)
NameMenu.insert(btnChoiceName)
NameMenu.insert(btnCancel)



NewNameMenu = InlineKeyboardMarkup()
NewNameMenu.insert(btnAddName)
NewNameMenu.insert(btnCancel)



def names_markup(names_list): 
    ChoiсeNameMenu = InlineKeyboardMarkup()
    cnt = 2
    for name in names_list:
        ChoiсeNameMenu.insert(InlineKeyboardButton(
            text=name,
            callback_data=NamesCallback.new(
                space = "ChoiceName",
                name = name,
                row=cnt)
        ))
        cnt+=1
    ChoiсeNameMenu.insert(btnCancel)
    return ChoiсeNameMenu



def makeRateMenu(auto):
    RateMenu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Вручную', callback_data="btn:Rate:New"),
                InlineKeyboardButton(text='Не добавлять', callback_data="btn:Rate:No")
            ]])
    btnAuto = InlineKeyboardButton(text='курс ЦБ РФ', callback_data="btn:Rate:Auto")
    
    if auto == False:
        RateMenu.insert(btnAuto)
        
    RateMenu.insert(btnCancel)
    return RateMenu

AutoRateMenu = InlineKeyboardMarkup(row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Да', callback_data="btn:Rate:Auto:Yes"),
            InlineKeyboardButton(text='Изменить вручную', callback_data="btn:Rate:New"),
            InlineKeyboardButton(text='Не добавлять', callback_data="btn:Rate:No")            
        ]])

NoteMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Нет', callback_data="btn:Note:No"),
            InlineKeyboardButton(text='Да', callback_data="btn:Note:Yes")
        ]])
NoteMenu.insert(btnCancel)

CurMenu = InlineKeyboardMarkup(
    row_width=3,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='RUB', callback_data="btn:Cur:RUB"),
            InlineKeyboardButton(text='USD', callback_data="btn:Cur:USD"),
            InlineKeyboardButton(text='SOTA', callback_data="btn:Cur:SOTA"),
            InlineKeyboardButton(text='Другой', callback_data="btn:Cur:New")            
        ]
    ]
)
CurMenu.insert(btnCancel)
#from xml.etree.ElementPath import _Callback
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from callback_datas import NamesCallback, ProdsCallback

#---Main Menu---

# btnTransaction = InlineKeyboardButton(text="Добавить операцию", callback_data="btn:MainMenu:AddTransaction")
# MainMenu = InlineKeyboardMarkup().insert(btnTransaction)

MainMenu = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Продажа", callback_data="btn:MainMenu:AddTransaction"),
            InlineKeyboardButton(text="Закупка", callback_data="btn:MainMenu:AddProduct"),
            InlineKeyboardButton(text="Проданно", callback_data="btn:MainMenu:SmetaSold"),
            InlineKeyboardButton(text="Комиссионные", callback_data="btn:MainMenu:SmetaCommis"),
        ]])

btnCancel = InlineKeyboardButton(text="Отмена", callback_data="cancel")

#---Title_pod---
ProdMenu = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Выбрать", callback_data="btn:ProdMenu:Choice"),
            InlineKeyboardButton(text="Новый", callback_data="btn:ProdMenu:Add")
        ]])
ProdMenu.insert(btnCancel)

def title1_markup(title_list): 
    ChoiсeTitle1Menu = InlineKeyboardMarkup()
    cnt = 2
    for title in title_list:
        ChoiсeTitle1Menu.insert(InlineKeyboardButton(
            text=title,
            callback_data=ProdsCallback.new(
                space = "ChoiceTitle",
                title = title,
                row=cnt)
        ))
        if cnt == 8:
            break
        cnt+=1
    ChoiсeTitle1Menu.insert(btnCancel)
    return ChoiсeTitle1Menu

#---Name---
btnChoiceName = InlineKeyboardButton(text='Выбрать', callback_data="btn:NameMenu:Choice")
btnAddName = InlineKeyboardButton(text='Новый', callback_data="btn:NameMenu:Add")
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
        if cnt == 8:
            break
        cnt+=1
    ChoiсeNameMenu.insert(btnCancel)
    return ChoiсeNameMenu


def title_markup(title_list): 
    ChoiсeTitleMenu = InlineKeyboardMarkup()
    cnt = 2
    for title in title_list:
        ChoiсeTitleMenu.insert(InlineKeyboardButton(
            text=title,
            callback_data=ProdsCallback.new(
                space = "ChoiceTitle_2",
                title = title,
                row=cnt)
        ))
        cnt+=1
    ChoiсeTitleMenu.insert(btnCancel)
    return ChoiсeTitleMenu




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
            InlineKeyboardButton(text='Другой', callback_data="btn:Cur:New")            
        ]
    ]
)
CurMenu.insert(btnCancel)
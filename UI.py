import logging
import os
from datetime import datetime

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, ParseMode
from aiogram.types.message import ContentType, ContentTypes
#from aiogram.utils import executor
from dotenv import load_dotenv

import markup as nav
import tables
import tbls
from callback_datas import NamesCallback, ProdsCallback

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = Bot(TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)



class Form(StatesGroup):
    date = State()
    title = State()
    cnt_prod = State()
    name = State() 
    sum = State() 
    cur = State() 
    rate = State()
    # rate_CB = State()
    commission = State()
    
    
    title1 = State()
    sum_pur = State()
    cnt_pur = State()

@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id, 'Привет, {0.first_name}! Этот бот поможет отслеживать финансовые операции, а так же составлять сводку по операциям за месяц.\nНачнем?'.format(message.from_user), reply_markup = nav.MainMenu)

@dp.message_handler(commands=['new'])
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id, 'Привет, {0.first_name}'.format(message.from_user), reply_markup = nav.MainMenu)


#______________________________________________________________________Cancel

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await state.finish()
    await bot.send_message(message.chat.id, 'Операция прервана', reply_markup=nav.MainMenu)


@dp.callback_query_handler(text="cancel", state="*") 
async def cancel_inline(call: CallbackQuery, state: FSMContext):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )
    current_state = await state.get_state()
    # if current_state is None:
    #     return
    await state.finish()
    await bot.send_message(call.message.chat.id, 'Операция прервана', reply_markup=nav.MainMenu)            


#______________________________________________________________________Title_table

#______________________________________________________________________Title

@dp.callback_query_handler(text_contains="btn:MainMenu:AddProduct") 
async def main_menu_prod(call: CallbackQuery):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )

    if call.data == "btn:MainMenu:AddProduct":
        await call.message.answer(f"Ввод нового названия товара или добавление имеющегося?", reply_markup = nav.ProdMenu)
        


@dp.callback_query_handler(text_contains="btn:ProdMenu:") 
async def prod_menu(call: CallbackQuery):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )
    if call.data == "btn:ProdMenu:Choice":
        title_list = tables.get_prod(call.message.chat.id)
        if title_list == 0:
            await call.message.answer("Список товаров не найден. Введите новое название или /cancel, чтобы отменить операцию")
            await Form.title1.set()
        else:
            await call.message.answer("Выберете товар", reply_markup = nav.title1_markup(title_list))  
            
    if call.data == "btn:ProdMenu:Add":
        await bot.send_message(call.message.chat.id, 'Введите новое название')
        await Form.title1.set()


        
@dp.callback_query_handler(ProdsCallback.filter(space = "ChoiceTitle")) 
async def include_prod(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )
    get_title = callback_data.get("title")   
    logging.info(f"call = {callback_data}")
    async with state.proxy() as data:
        data['title1'] = get_title
    await call.message.answer("Введите закупочную стоимость")
    await Form.sum_pur.set()

 
@dp.message_handler(state=Form.title1)
async def include_new_prod(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title1'] = message.text

    await Form.next()
    await message.reply("Введите закупочную стоимость")

#______________________________________________________________________Summa_pur
 
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.sum_pur)
async def invalid_sum_pur(message: types.Message):
    return await message.reply("Введите стоимость продукта в виде числа или /cancel, чтобы отменить операцию")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.sum_pur)
async def include_sum_pur(message: types.Message, state: FSMContext):
    await Form.next()
    await state.update_data(sum_pur=int(message.text))
    
    await bot.send_message(message.from_user.id, 'Введите количество закупленного продукта в виде числа')    

#______________________________________________________________________cnt_pur_end_add

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.cnt_pur)
async def invalid_cnt_pur(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Введите количество закупленного продукта в виде числа или /cancel, чтобы отменить операцию')  

@dp.message_handler(lambda message: message.text.isdigit(), state=Form.cnt_pur)
async def include_cnt_pur(message: types.Message, state: FSMContext):
    # await Form.next()
    await state.update_data(cnt_pur=int(message.text))
    
    async with state.proxy() as data:
        tit = data['title1']
        purchase = [
            data['title1'],
            data['sum_pur'],
            data['cnt_pur']
        ]
    tables.new_purchase(message.chat.id, purchase)
    await state.finish()  
    await bot.send_message(message.chat.id, 'Товар "{}" добавлен'.format(tit), reply_markup=nav.MainMenu)


#______________________________________________________________________Smeta_Commissions

@dp.callback_query_handler(text_contains="btn:MainMenu:SmetaCommis") 
async def main_menu_commis(call: CallbackQuery):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )
    path = tables.smeta_sellers(call.message.chat.id)

    if path == 0:
        await call.message.answer("Таблица продаж не найдена. Сначала добавьте проданный товар. Нажмите /cancel, чтобы отменить операцию")
    else: 
        await bot.send_document(call.message.chat.id, open(path, 'rb'))

#______________________________________________________________________Smeta_Sold

@dp.callback_query_handler(text_contains="btn:MainMenu:SmetaSold") 
async def main_menu_sold(call: CallbackQuery):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )
    path = tables.smeta_sold_prod(call.message.chat.id)

    if path == 0:
        await call.message.answer("Таблица продаж не найдена. Сначала добавьте проданный товар. Нажмите /cancel, чтобы отменить операцию")
    else: 
        await bot.send_document(call.message.chat.id, open(path, 'rb'))


#______________________________________________________________________Add_Transaction

@dp.callback_query_handler(text_contains="btn:MainMenu:AddTransaction") 
async def main_menu_trans(call: CallbackQuery):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )
    title_list = tables.get_prod(call.message.chat.id)

    if title_list == 0:
        await call.message.answer("Список товаров не найден. Сначала добавьте закупленный товар. Нажмите /cancel, чтобы отменить операцию")
 
    else:
        await call.message.answer("Выберете товар", reply_markup = nav.title_markup(title_list))  
   

@dp.callback_query_handler(ProdsCallback.filter(space = "ChoiceTitle_2")) 
async def include_prod(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )
    get_title = callback_data.get("title")   
    logging.info(f"call = {callback_data}")
    async with state.proxy() as data:
        data['title'] = get_title
    # await call.message.answer("Введите стоимость продажи")
    # await Form.sum.set()
    await call.message.answer(f"Ввод нового имени продавца или выбор из имеющихся?", reply_markup = nav.NameMenu)


@dp.callback_query_handler(text_contains="btn:NameMenu:") 
async def name_menu(call: CallbackQuery):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )
    if call.data == "btn:NameMenu:Choice":
        names_list = tables.get_names(call.message.chat.id)
        if names_list == 0:
            await call.message.answer("Список имен не найден. Введите новое имя или /cancel, чтобы отменить операцию")
            await Form.name.set()
        else:
            await call.message.answer("Выберете имя", reply_markup = nav.names_markup(names_list))  
            
    if call.data == "btn:NameMenu:Add":
        await bot.send_message(call.message.chat.id, 'Введите новое имя')
        await Form.name.set()


        
@dp.callback_query_handler(NamesCallback.filter(space = "ChoiceName")) 
async def include_name(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )
    get_name = callback_data.get("name")   
    logging.info(f"call = {callback_data}")
    async with state.proxy() as data:
        data['name'] = get_name
    await call.message.answer("Введите сумму операции")
    await Form.sum.set()

 
@dp.message_handler(state=Form.name)
async def include_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    await message.reply("Введите сумму операции")

#______________________________________________________________________Summa
 
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.sum)
async def invalid_sum(message: types.Message):
    return await message.reply("Введите сумму операции в виде числа или /cancel, чтобы отменить операцию")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.sum)
async def include_sum(message: types.Message, state: FSMContext):
    await Form.next()
    await state.update_data(sum=int(message.text))
    

    await bot.send_message(message.from_user.id, 'Выберете валюту', reply_markup = nav.CurMenu)    

#______________________________________________________________________Currency

@dp.callback_query_handler(text_contains="btn:Cur", state=Form.cur) 
async def choice_cur(call: CallbackQuery, state: FSMContext):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )
    if call.data == "btn:Cur:New":
        await call.message.answer("Введите валюту")
        await Form.cur.set()
    else:
        async with state.proxy() as data:
            data['cur'] = call.data[8:]
            await Form.next()
            if data['cur'] == 'RUB':
                data['rate'] = 1
                await Form.next()
                await call.message.answer("Введите процент комиссионных")
            else:
                await bot.send_message(call.message.chat.id, 'Требуется добавить курс валюты?', reply_markup=nav.makeRateMenu(False))
            
            
@dp.message_handler(state=Form.cur)
async def other_cur(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['cur'] = message.text
        if data['cur'] == 'RUB':
            data['rate'] = 1
            await Form.next()
            await Form.next()
            await message.answer("Введите процент комиссионных",)
        else:
            await Form.next()
            await bot.send_message(message.chat.id, 'Требуется добавить курс валюты?', reply_markup=nav.makeRateMenu(False))
    

#______________________________________________________________________Rate


@dp.callback_query_handler(text_contains="btn:Rate", state=Form.rate) 
async def choice_cur(call: CallbackQuery, state: FSMContext):
    await bot.edit_message_reply_markup(        
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )    

    if call.data == "btn:Rate:New":
        await call.message.answer("Введите курс валюты")
        await Form.rate.set()
        
    elif call.data == "btn:Rate:Auto":
        async with state.proxy() as data:
            data['rate_CB'] = round(tables.parse_rate(data['cur']),2)
            if data['rate_CB'] == 0:
                await call.message.answer("Курс не найден", reply_markup=nav.makeRateMenu(True))
            else:
                await call.message.answer(text='Добавить курс RUB - {}: {}?'.format(data['cur'], data['rate_CB']), reply_markup=nav.AutoRateMenu)
           
    elif call.data == "btn:Rate:No":
        async with state.proxy() as data:
            data['rate'] = 0
            await Form.next()
            await call.message.answer("Введите процент комиссионных")
            
    elif call.data =="btn:Rate:Auto:Yes":
        async with state.proxy() as data:
            data['rate'] = data['rate_CB']
            await Form.next()
            await call.message.answer("Добавлен курс RUB - {}: {} \nВведите процент комиссионных".format(data['cur'], data['rate']))  
           

@dp.message_handler(lambda message: isinstance(message.text, float | int) , state=Form.rate)
async def include_sum(message: types.Message, state: FSMContext):
    await bot.edit_message_reply_markup(        
        chat_id=message.from_user.id,
        message_id=message.message.message_id, 
        reply_markup=None
    )   
    await state.update_data(rate=float(message.text))
    await Form.next()
    async with state.proxy() as data:
        await bot.send_message(message.chat.id, "Добавлен курс RUB - {}: {} \nВведите процент комиссионных".format(data['cur'], data['rate'])) 
           

#______________________________________________________________________commission
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.commission)
async def invalid_com(message: types.Message):
    return await message.reply("Введите процент комиссионных в виде числа или /cancel, чтобы отменить операцию")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.commission)
async def include_com(message: types.Message, state: FSMContext):
    # await Form.next()
    # await state.update_data(commission=int(message.text))

    async with state.proxy() as data:
        data['date'] = datetime.now().date()
        data['commission'] = round(int(message.text) / 100 *data['sum'],2)
    try:
        fee_total = round(data['sum']*data['rate'],2)
    except:
        fee_total = 0

    transaction = [
        data['date'],
        data['name'],
        data['title'],
        data['sum'],
        data['cur'],
        data['rate'],
        fee_total,
        data['commission']
    ]
    logging.info(transaction)
    tables.new_transaction(message.chat.id, transaction)
    
    await bot.send_message(
        message.chat.id,
        md.text(
            md.text('Добавлена операция:'),
            md.text('     Имя продавца: ', md.text(data['name'])),
            md.text('     Товар: ', md.bold(data['title'])),
            md.text('     Стоимость продажи: ', md.bold(data['sum'])),
            md.text('     Валюта: ', md.bold(data['cur'])),
            md.text('     Курс валюты: ', md.bold(data['rate'])),
            md.text('     Дата:', md.text(data['date'])),
            md.text('     Процент комиссионных:', md.text(data['commission'])),
            sep='\n',
        ),
        reply_markup=nav.MainMenu,
        parse_mode=ParseMode.MARKDOWN,
    )
    await state.finish()    



    
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
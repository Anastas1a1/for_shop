import os
from dotenv import load_dotenv
from aiogram import types, executor, Dispatcher, Bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.message import ContentType, ContentTypes
import logging

import aiogram.utils.markdown as md
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, CallbackQuery
from callback_datas import NamesCallback
#from aiogram.utils import executor

import markup as nav
import tables
import tbls



load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = Bot(TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)



class Form(StatesGroup):
    name = State() 
    sum = State() 
    cur = State() 
    rate = State()
    note = State()
    rate_CB = State()

@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id, 'Привет, {0.first_name}! Этот бот поможет отслеживать финансовые операции, а так же составлять сводку по операциям за месяц.\n  Начнем?'.format(message.from_user), reply_markup = nav.MainMenu)

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

#______________________________________________________________________Name

@dp.callback_query_handler(text_contains="btn:MainMenu:") 
async def main_menu(call: CallbackQuery):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )

    if call.data == "btn:MainMenu:AddTransaction":
        await call.message.answer(f"Ввод нового имени или выбор из имеющихся?", reply_markup = nav.NameMenu)
        


@dp.callback_query_handler(text_contains="btn:NameMenu:") 
async def main_menu(call: CallbackQuery):
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
                await call.message.answer("Требуется добавить комментарий?", reply_markup=nav.NoteMenu)
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
            await message.answer("Требуется добавить комментарий?", reply_markup=nav.NoteMenu)
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
            await call.message.answer("Требуется добавить комментарий?", reply_markup=nav.NoteMenu)
            
    elif call.data =="btn:Rate:Auto:Yes":
        async with state.proxy() as data:
            data['rate'] = data['rate_CB']
            await Form.next()
            await call.message.answer("Добавлен курс RUB - {}: {} \nТребуется добавить комментарий?".format(data['cur'], data['rate']), reply_markup=nav.NoteMenu)  
           

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
        await bot.send_message(message.chat.id, "Добавлен курс RUB - {}: {} \nТребуется добавить комментарий?".format(data['cur'], data['rate']), reply_markup=nav.NoteMenu) 
           

#______________________________________________________________________Note

@dp.callback_query_handler(text_contains="btn:Note", state=Form.note) 
async def choice_cur(call: CallbackQuery, state: FSMContext):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        reply_markup=None
    )
    if call.data == "btn:Note:Yes":
        await call.message.answer("Введите комментарий")
        await Form.note.set()
    else:
        async with state.proxy() as data:
            data['note'] = ' ' 
    try:
        fee_total = round(data['sum']*data['rate'],2)
    except:
        fee_total = 0
    transaction = [
        data['name'],
        data['sum'],
        data['cur'],
        data['rate'],
        fee_total,
        data['note']
    ]
    tables.new_transaction(call.message.chat.id, transaction)
    
    print(transaction)
    await bot.send_message(
        call.message.chat.id,
        md.text(
            md.text('Добавлена операция:'),
            md.text('     Name: ', md.bold(data['name'])),
            md.text('     Sum: ', md.bold(data['sum'])),
            md.text('     Currency: ', md.bold(data['cur'])),
            md.text('     Currency Rate: ', md.bold(data['rate'])),
            sep='\n',
        ),
        reply_markup=nav.MainMenu,
        parse_mode=ParseMode.MARKDOWN,
    )
    path = 'database/' + str(call.message.chat.id) + '.xlsx' 
    await bot.send_document(call.message.chat.id, open(path, 'rb'))
    await state.finish()

 

@dp.message_handler(state=Form.note)
async def other_cur(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['note'] = message.text
    # await include_name(message, FSMContext) 
        try:
            fee_total = round(data['sum']*data['rate'],2)
        except:
            fee_total = 0
            data['rate'] = 0
    transaction = [
        data['name'],
        data['sum'],
        data['cur'],
        data['rate'],
        fee_total,
        data['note']
    ]
    tables.new_transaction(message.chat.id, transaction)
    
    print(transaction)
    await bot.send_message(
        message.chat.id,
        md.text(
            md.text('Добавлена операция:'),
            md.text('     Name: ', md.bold(data['name'])),
            md.text('     Sum: ', md.bold(data['sum'])),
            md.text('     Currency: ', md.bold(data['cur'])),
            md.text('     Currency Rate: ', md.bold(data['rate'])),
            md.text('     Note: ', md.bold(data['note'])),
            sep='\n',
        ),
        reply_markup=nav.MainMenu,
        parse_mode=ParseMode.MARKDOWN,
    )
    path = 'database/' + str(message.chat.id) + '.xlsx' 
    mes_doc = await bot.send_document(message.chat.id, open(path, 'rb'))
    # await bot.pin_chat_message(chat_id = message.chat.id, message_id=mes_doc)
    await state.finish()
        



#______________________________________________________________________Old_Comment


# async def include_name(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:

#         transaction = [
#             data['name'],
#             data['cur'],
#             data['sum'],
#             data['rate'],
#             data['note']
#         ]
#         tbls.add_transaction_1(message.chat.id, transaction)
        
#         print(transaction)
#         await bot.send_message(
#             message.chat.id,
#             md.text(
#                 md.text('Добавлена операция:'),
#                 md.text('   Name: ', md.bold(data['name'])),
#                 md.text('   Sum: ', md.code(data['sum'])),
#                 md.text('   Currency: ', data['cur']),
#                 md.text('   Note: ', data['note']),
#                 sep='\n',
#             ),
#             reply_markup=nav.MainMenu,
#             parse_mode=ParseMode.MARKDOWN,
#         )
#     path = 'database/' + str(message.chat.id) + '.xlsx' 
#     await bot.send_document(message.chat.id, open(path, 'rb'))
#     await state.finish()



    
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
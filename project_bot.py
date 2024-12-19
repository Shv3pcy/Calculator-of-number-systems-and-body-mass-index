from aiogram import Bot, Dispatcher #импортировали все нужные модули из aiogram
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import  State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Bot 
import asyncio
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from calculate import bmi_calc, sys10_2, sys2_10

"""                                          
                Проект по информатике  ╱▔▔╲╱▔▔╲    
                за 8 класс.            ▏┈╭╮╭╮┈▕    
                Хайитов А.             ╲┈┏━━┓┈╱    
                  &                     ╲╰━━╯╱   
                Конугаев Д.              ╲┈┈╱  
                Марселю Фаргатовичу.      ╲╱                                     
"""

class Register(StatesGroup):  # класс, в котором создаем группу регистров
  body_weight = State()       # регистр для массы тела
  body_height = State()       # регистр для роста тела
  f2s_t10s = State()          # регистр для перевода с 2-ичной системы в 10-ичную
  f10s_t2s = State()          # регистр для перевода с 10-ичной системы в 2-ичную

router = Router() # класс, который будет распределяться в обработчике команд Dispatcher()

async def main():
  bot = Bot(token='8108904832:AAEd1g14LFSVp0LYoxzbPr2ElnEaS7DZ5Yg') # API-токен для бота
  dp = Dispatcher() # обработчик команд
  dp.include_router(router)
  await dp.start_polling(bot)
  print('BOT ON (ВКЛ)')

@router.message(CommandStart()) #обработчик команды /start
async def start(msg: Message): 
   menu = InlineKeyboardMarkup(
                            inline_keyboard=
                            [
                            [
                            InlineKeyboardButton(text='Калькулятор ИМТ', callback_data='bmi_calc'),
                            InlineKeyboardButton(text='Калькулятор систем счислений', callback_data='calc_ofNumSys')
                            ]
                            ]
                            )
   await msg.answer_photo(photo="https://dc-agency.org/wp-content/uploads/2019/09/0_veNN9p3Zi4gQa-Zc.png", reply_markup=menu, caption=f"Привет. Выбери одно из действий.\n<code>> Калькулятор ИМТ</code>\n<code>> Калькулятор систем счисленийM</code>\n\n/donate — задонатить.", 
                       parse_mode='HTML') # parse_mode - специальный параметр, для форматирования текста, чтобы задать тексту шрифт
                                          # reply_markup - параметр, с помощью которого прикрепим кнопки к сообщению
   

@router.message(Command('donate'))
async def donate(msg: Message):
   donate_button = InlineKeyboardMarkup(
      inline_keyboard=[
         [InlineKeyboardButton(text='99 RUB', url='https://yoomoney.ru/fundraise/dOeliARtiuQ.231119')]
         ]
         )
   await msg.reply("Ссылка на донат", reply_markup=donate_button)

@router.message(Command('cancel')) # обработчик команды /cancel
async def cancel(msg: Message, state: FSMContext): 
   await state.clear() # метод clear() закрывает (отменяет) все регистры
   await msg.reply("Действие было отменено")
   
@router.callback_query(F.data == 'bmi_calc') # обработчик callback запроса "bmi_calc"
async def reply_menu1(clb: CallbackQuery, state: FSMContext ):
  await state.set_state(Register.body_weight) # создаем регистр массы тела
  await clb.message.reply("Введите вашу массу тела в килограммах. Принимаем только целые значения.\nДля отмены - /cancel")

@router.message(Register.body_weight) # ловим регистр массы тела
async def ref_body_weighta(msg: Message, state: FSMContext):
  try:
    await state.update_data(body_weight=msg.text) 
    data = await state.get_data()
    if int(data['body_weight']) >= 1000: 
       await msg.reply("Нельзя вводить значения больше 1000!\nПопробуйте заново")
       await state.set_state(Register.body_weight) # заново создаем регистр, при случае ошибки

    else:   
       await state.set_state(Register.body_height) # в случае успеха, создаем новый регистр роста тела
       await msg.reply("Введите ваш рост в метрах (например, 177см -> 1.77).")
 
  except Exception as e:
     await msg.reply(f"Ошибка! Возможно, ты ввел данные в неправильном формате. Попробуй заново.\n<code>[error] {e}</code>", parse_mode='html')
     await state.set_state(Register.body_weight)

@router.message(Register.body_height) # ловим регистр роста тела
async def ref_rost(msg: Message, state: FSMContext):
   
   try:   
      await state.update_data(body_height=msg.text)
      data = await state.get_data()
      
      body_height = float(data['body_height'])
      body_weight = int(data['body_weight'])

      if body_height >= 10:
         await msg.reply(f"Ты ввел данные в неправильном формате:\n- Значение указать в метрах\n- Значение, не выше 10 метров.", parse_mode='html')
      
      else:
         result = bmi_calc(body_weight, body_height)
         if float(result) < 18:
            await msg.reply(f"<code>Ваш вес: {body_weight} кг.\nВаш рост: {body_height} м.\nВаш индекс массы тела (ИМТ): {result}</code>\nТы худ(оват)-а, тебе нужно набрать массу", parse_mode='html')
         
         elif float(result) == 19 or float(result) < 25:
            await msg.reply(f"<code>Ваш вес: {body_weight} кг.\nВаш рост: {body_height} м.\nВаш индекс массы тела (ИМТ): {result}</code>\nУ тебя средний ИМТ, это хорошо", parse_mode='html')

         elif float(result) > 26:
            await msg.reply(f"<code>Ваш вес: {body_weight} кг.\nВаш рост: {body_height} м.\nВаш индекс массы тела (ИМТ): {result}</code>\nТебе нужно подбросить вес.", parse_mode='html')
         await state.clear()

   except Exception as e:
      await msg.reply(f"Ошибка! Возможно, ты ввел данные в неправильном формате. Попробуй заново.\n<code>[error] {e}</code>", parse_mode='html')
      await state.set_state(Register.body_weight)


@router.callback_query(F.data == 'calc_ofNumSys') # обработчик callback запроса
async def reply_menu2(clb: CallbackQuery):
   basics = InlineKeyboardMarkup(
                            inline_keyboard=
                            [
                            [
                            InlineKeyboardButton(text='2 -> 10', callback_data='from2_to10'),
                            InlineKeyboardButton(text='10 -> 2', callback_data='from10_to2')
                            ]
                            ]
                            )
   await clb.message.reply(f"Выберите тип перевода системы\n- Из двоичной в десятичную\n- Из десятичной в двоичную\nДля отмены - /cancel", reply_markup=basics)

@router.callback_query(F.data == 'from2_to10')
async def system2(clb: CallbackQuery, state: FSMContext):
   await state.set_state(Register.f2s_t10s)
   await clb.message.reply('Введи число двоичной системы, для перевода в десятичную')

@router.message(Register.f2s_t10s)
async def sysfrom2_to10(msg: Message, state: FSMContext):
   try:
      await state.update_data(f2s_t10s=msg.text)
      data = await state.get_data()
      ban_list_numbers = "2" or "3" or "4"or "5" or "6" or "7" or "8" or "9"
      if ban_list_numbers in str(data['f2s_t10s']):
         await msg.reply('Это число не является двоичной системой. Введи соответствующее значение.')
         await state.set_state(Register.f2s_t10s)
         
      else:
         f2s_t10s = str(data['f2s_t10s'])
         result = sys2_10(number=f2s_t10s)
         await state.clear()
         await msg.reply(f"<code>{f2s_t10s} -> {result}</code>\nРезультат: <code>{result}</code>", parse_mode='HTML')
   except Exception as e:
      await msg.reply(f"<code>error: {e}</code>\n\nВводи только числа. Буквы и прочие символы не переводятся.\nТы не сможешь переводить слишком большие значения.", parse_mode='html')
      await state.set_state(Register.f2s_t10s)
      

@router.callback_query(F.data == 'from10_to2') # обработчик callback запроса
async def system2(clb: CallbackQuery, state: FSMContext):
   await state.set_state(Register.f10s_t2s)
   await clb.message.reply('Введи число десятичной системы, для перевода в двоичную')

@router.message(Register.f10s_t2s)
async def sysfrom2_to10(msg: Message, state: FSMContext):
   try:
      await state.update_data(f10s_t2s=msg.text)
      data = await state.get_data()
      f10s_t2s = int(data['f10s_t2s'])
      result = sys10_2(number=f10s_t2s)
      await state.clear()
      await msg.reply(f"<code>{f10s_t2s} -> {result[2:]}</code>\nРезультат: <code>{result[2:]}</code>", parse_mode='html')
   except Exception as e:
      await msg.reply(f"<code>error: {e}</code>\n\nВводи только числа. Буквы и прочие символы не переводятся.\nТы не сможешь переводить слишком большие значения.", parse_mode='html')
      await state.set_state(Register.f10s_t2s)
   
     
if __name__ == '__main__':
  try:
      asyncio.run(main())
  except KeyboardInterrupt:
      print('BOT OFF (ВЫКЛ)')
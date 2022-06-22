#Імпорт бібліотек
import logging   #Бібліотека для логування
import sqlite3   #Бібліотека для роботи х базою даних
import html2text #Бібліотека, що переводить html в текст
import requests  #Бібліотека для створення запитів
#Бібліотеки для роботи з Telegram Api
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import BotBlocked
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

#Підключаємо базу даних та створюємо курсор
con = sqlite3.connect('main.db')
cur = con.cursor()

#Присвоєння змінній значення ключа з телеграм-бота
API_TOKEN = '5477818179:AAGHdLO4c2o-rZ0q6XTBAAvUok1VOSdhchQ'

#Налаштування логування
logging.basicConfig(level=logging.INFO)

#Ініціалізація бота та диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()   #Ініціалізація змінної для зберігання станів
dp = Dispatcher(bot, storage=storage)

#Функція для створення меню команд для швидкого доступу, де command = назва команди, description = її короткий опис
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Start or reload bot"),
        BotCommand(command="/lib", description="Open saved characters in library"),
        BotCommand(command="/libsearch", description="Search characters by name"),
        BotCommand(command="/libdelete", description="Delete characters by name")
    ]
    await bot.set_my_commands(commands) 

#Клас для станів зовнішніх характеристик персонажа
class CharacteristicsForm(StatesGroup):
    Detail = State()   #Ступінь деталізованості
    Sex = State()      #Стать
    Type = State()     #Тип
    Beard = State()    #Наявність бороди
    HairL = State()    #Довжина волосся
    HLoss = State()    #Випадіння волосся
    Dye = State()      #Чи пофарбоване волосся
    Clothing = State() #Наявність одягу
    Pierce = State()   #Наявність пірсінгу
    Scar = State()     #Наявність шрамів
    Tattoo = State()   #Наявність тату
    Makeup = State()   #Наявність макіяжу
#Клас для станів особистісних характеристик персонажа
class CharacteristicsPersonalityForm(StatesGroup):
    Detail = State()   #Ступінь деталізованості
    Type = State()     #Тип

#Масиви з елементами вибору характеристик персонажа
G_Sex = ['Random', 'Male', 'Female', 'Intersex']
G_Type = ['Realistic','Exotic', 'Anime', 'Unique']
G_Detail = ['Simple','Detailed']
G_Beard =['RandomFhair', 'Fhair', 'noFhair']
G_HairL = ['RandomHair','Shaven','VShort','Short','Medium','MedLong','Long','VLong']
G_HLoss = ['RandomHLoss','Loss','bald','noHLoss']
G_Dye = ['RandomDye','dye', 'noDye']
G_Clothing =['RandomClothes','clothes','noClothes']
G_Pierce =['RandomPiercings', 'piercings', 'noPiercings']
G_Scar =['RandomScars', 'scars', 'noScars']
G_Tattoo = ['RandomTattoos', 'tattoos', 'noTattoos']
G_Makeup = ['RandomMakeup','makeup','noMakeup']

#Якщо повідомлення починається з команди /start, буде викликано декоратор для обробки текстових повідомлень
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await set_commands(bot)                                         #Очікування виконання функції для створення меню швидких відповідей
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)      #Створення клавіатури
    buttons = ["Generate appearance", 'Generate personality']       #Створення масиву кнопок для клавіатури
    keyboard.add(*buttons)                                          #Додавання кнопок на клавіатуру
    await bot.send_message(message.chat.id, "Do you want to generate a new character?", reply_markup=keyboard) 
    #Відповідь бота з пропозицією створити персонажа та відображення клавіатури

#Декоратор обробник перевіряє чому дорівнює останнє повідомлення. Якщо воно = "Generate appearance", тоді викликається функція "granularity"
@dp.message_handler(lambda message: message.text == "Generate appearance")
async def granularity(message: types.Message):
    await CharacteristicsForm.Detail.set()                          #Запуск конвеєра станів
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)      #Створення клавіатури
    buttons_detail = ['Simple','Detailed']                          #Створення масиву кнопок для клавіатури
    keyboard.add(*buttons_detail)                                   #Додавання кнопок на клавіатуру
    await message.reply(f"Select character granularity", reply_markup=keyboard) #Відповідь на повідомлення "Select character granularity" з вказанням дії

#Якщо стан = CharacteristicsForm.Detail, декоратор обробник запускає функцію "gender"
@dp.message_handler(state=CharacteristicsForm.Detail)
async def gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:                               #Запис даних в проксі-змінну з тексту повідомлення
        data['Detail'] = message.text                               #Дані записуються з повідомлення в проксі-змінну "Detail"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)      #Створення клавіатури
    buttons_sex = ['Random', 'Male', 'Female', 'Intersex']          #Створення масиву кнопок для клавіатури
    keyboard.add(*buttons_sex)                                      #Додавання кнопок на клавіатуру
    await CharacteristicsForm.next()                                #Перехід до наступного стану
    await message.reply(f"Select character sex", reply_markup=keyboard) #Відповідь на повідомлення "Select character sex" з вказанням дії

#Якщо стан = CharacteristicsForm.Sex, декоратор обробник запускає функцію "type"
@dp.message_handler(state=CharacteristicsForm.Sex)
async def type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:                               #Запис даних в проксі-змінну з тексту повідомлення
        buttons_sex = ['Random', 'Male', 'Female', 'Intersex']      #Створення масиву кнопок для отримання даних з клавіатури та отримання індексу елементу масиву
        data['Sex'] = buttons_sex.index(message.text)               #Дані записуються з повідомлення в проксі-змінну "Sex"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)      #Створення клавіатури
    buttons_type = ['Realistic','Exotic', 'Anime', 'Unique']        #Створення масиву кнопок для клавіатури
    keyboard.add(*buttons_type)                                     #Додавання кнопок на клавіатуру
    await CharacteristicsForm.next()                                #Перехід до наступного стану
    await message.reply(f"Select character type", reply_markup=keyboard) #Відповідь на повідомлення "Select character type" з вказанням дії

#Якщо стан = CharacteristicsForm.Type, декоратор обробник запускає функцію "simplecharacter"
@dp.message_handler(state=CharacteristicsForm.Type)
async def simplecharacter(message: types.Message, state: FSMContext):
    async with state.proxy() as data:                               #Запис даних в проксі-змінну з тексту повідомлення
        buttons_type = ['Realistic','Exotic', 'Anime', 'Unique']    #Створення масиву кнопок для отримання даних з клавіатури і отримання індексу елементу масиву
        data['Type'] = buttons_type.index(message.text)             #Дані записуються з повідомлення в проксі-змінну "Type"
    #Якщо отримані дані = Simple : 
    if data['Detail'] == 'Simple': 
        await state.finish()                                        #конвеєр закінчується
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)  #створюється клавіатура
        buttons = ["Generate Character"]                            #створюється масив кнопки для клавіатури
        keyboard.add(*buttons)                                      #кнопка додавається на клавіатуру
        markup = types.ReplyKeyboardRemove()                        #клавіатура ховається
        await message.reply('Generating', reply_markup=markup)      #виводиться повідомлення "Generating"
        myobj = {'event': 'generate',                               #створюється тіло запиту
             'sex': G_Sex[data['Sex']],                             #з масиву "G_Sex" береться елемент під номером, який зберігається в проксі-змінній
             'type':G_Type[data['Type']], 
             'detail': 'Simple', 
             'beard': G_Beard[0],                                   #з масиву береться елемент під номером 0, що відповідає рандомному елементу
             'HairL': G_HairL[0],
             'Hloss': G_HLoss[0],
             'dye': G_Dye[0],
             'clothing': G_Clothing[0],
             'pierce': G_Pierce[0],
             'scar': G_Scar[0],
             'tattoo': G_Tattoo[0],
             'makeup': G_Makeup[0]}

        resp = requests.post('https://www.rangen.co.uk/chars/appScript.php', data=myobj) #Відправка пост-запиту на сайт з усіма заданими параметрами

        text = html2text.html2text(resp.text)                                            #За допомогою бібліотеки html2text html конвертується в текст
        
        #Додавання інлайн-клавіатури для можливості зберігання персонажа
        keyboard = types.InlineKeyboardMarkup()                                          
        keyboard.add(types.InlineKeyboardButton(text="Save to library", callback_data="libsave"))
        
        text = html2text.html2text(resp.text)                                            #За допомогою бібліотеки html2text html конвертується в текст
        textarr = text.split('* * *')                                                    #Роздіяємо текст по символам * * *
        markup = types.ReplyKeyboardRemove()
        await message.reply(textarr[0], reply_markup=keyboard)                           #Виводиться повідомлення з нульовим елементом текстового масиву
    #Якщо отримані дані = Detailed : 
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)                       #Створення клавіатури
        buttons_beard =['Random facial hair', 'Facial hair', 'No facial hair']           #Створення масиву кнопок для клавіатури
        keyboard.add(*buttons_beard)                                                     #Додавання кнопок на клавіатуру
        await CharacteristicsForm.next()                                                 #Перехід до наступного стану
        await message.reply(f"Select character facial hair", reply_markup=keyboard)      #Відповідь на повідомлення "Select character facial hair" з вказанням дії

#Якщо стан = CharacteristicsForm.Beard, декоратор обробник запускає функцію "fhair"
@dp.message_handler(state=CharacteristicsForm.Beard)
async def fhair(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)                            #Створення клавіатури
    buttons_hairL = ['Random length','Shaven','Very short','Short','Medium','Medium-Long','Long','Very long']  #Створення масиву кнопок для клавіатури
    keyboard.add(*buttons_hairL)                                                          #Додавання кнопок на клавіатуру
    async with state.proxy() as data:                                                     #Запис даних в проксі-змінну з тексту повідомлення
        buttons_beard =['Random facial hair', 'Facial hair', 'No facial hair']            #Створення масиву кнопок для отримання даних з клавіатури і отримання індексу елементу масиву
        data['Beard'] = buttons_beard.index(message.text)                                 #Дані записуються з повідомлення в проксі-змінну "Beard"
    await CharacteristicsForm.next()                                                      #Перехід до наступного стану
    await message.reply(f"Select character Hair Lenth", reply_markup=keyboard)            #Відповідь на повідомлення "Select character Hair Lenth" з вказанням дії

@dp.message_handler(state=CharacteristicsForm.HairL)
async def hairloss(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)                            #Створення клавіатури
    buttons_HLoss = ['Random hair loss','Hair loss','Bald','No hair loss']                #Створення масиву кнопок для клавіатури
    keyboard.add(*buttons_HLoss)                                                          #Додавання кнопок на клавіатуру
    async with state.proxy() as data:                                                     #Запис даних в проксі-змінну з тексту повідомлення
        buttons_hairL = ['Random length','Shaven','Very short','Short','Medium','Medium-Long','Long','Very long']  #Створення масиву кнопок для отримання даних з клавіатури і отримання індексу елементу масиву
        data['HairL'] = buttons_hairL.index(message.text)                                 #Дані записуються з повідомлення в проксі-змінну "HairL"
    await CharacteristicsForm.next()                                                      #Перехід до наступного стану
    await message.reply(f"Select character Hair Loss", reply_markup=keyboard)             #Відповідь на повідомлення "Select character Hair Loss" з вказанням дії

@dp.message_handler(state=CharacteristicsForm.HLoss)
async def hairdye(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)                            #Створення клавіатури
    buttons_dye = ['Random','Hair dye', 'None']                                           #Створення масиву кнопок для клавіатури
    keyboard.add(*buttons_dye)                                                            #Додавання кнопок на клавіатуру
    async with state.proxy() as data:                                                     #Запис даних в проксі-змінну з тексту повідомлення
        buttons_HLoss = ['Random hair loss','Hair loss','Bald','No hair loss']            #Створення масиву кнопок для отримання даних з клавіатури і отримання індексу елементу масиву
        data['HLoss'] = buttons_HLoss.index(message.text)                                 #Дані записуються з повідомлення в проксі-змінну "HLoss"
    await CharacteristicsForm.next()                                                      #Перехід до наступного стану
    await message.reply(f"Select if character`s hair dyed", reply_markup=keyboard)        #Відповідь на повідомлення "Select if character`s hair dyed" з вказанням дії

@dp.message_handler(state=CharacteristicsForm.Dye)
async def clothes(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)                            #Створення клавіатури                                       
    buttons_clothes = ['Random','Clothes','No clothes']                                   #Створення масиву кнопок для клавіатури                               
    keyboard.add(*buttons_clothes)                                                        #Додавання кнопок на клавіатуру           
    async with state.proxy() as data:                                                     #Запис даних в проксі-змінну з тексту повідомлення               
        buttons_dye = ['Random','Hair dye', 'None']                                       #Створення масиву кнопок для отримання даних з клавіатури і отримання індексу елементу масиву                           
        data['Dye'] = buttons_dye.index(message.text)                                     #Дані записуються з повідомлення в проксі-змінну "Dye"                               
    await CharacteristicsForm.next()                                                      #Перехід до наступного стану               
    await message.reply(f"Select if character has clothes", reply_markup=keyboard)        #Відповідь на повідомлення "Select if character has clothes" з вказанням дії

@dp.message_handler(state=CharacteristicsForm.Clothing)
async def piercing(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)                            #Створення клавіатури                                                                     
    buttons_piercing = ['Random piercing', 'Piercings', 'No piercing']                    #Створення масиву кнопок для клавіатури                                                                     
    keyboard.add(*buttons_piercing)                                                       #Додавання кнопок на клавіатуру             
    async with state.proxy() as data:                                                     #Запис даних в проксі-змінну з тексту повідомлення                     
        buttons_clothes = ['Random','Clothes','No clothes']                               #Створення масиву кнопок для отримання даних з клавіатури і отримання індексу елементу масиву                           
        data['Clothing'] = buttons_clothes.index(message.text)                            #Дані записуються з повідомлення в проксі-змінну "Clothing"                                                             
    await CharacteristicsForm.next()                                                      #Перехід до наступного стану                     
    await message.reply(f"Select if character has piercing", reply_markup=keyboard)       #Відповідь на повідомлення "Select if character has piercing" з вказанням дії                                                      

@dp.message_handler(state=CharacteristicsForm.Pierce)
async def scar(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)                            #Створення клавіатури                                                                                                   
    buttons_scars = ['Random scars', 'Scars', 'No scars']                                 #Створення масиву кнопок для клавіатури                                                                                     
    keyboard.add(*buttons_scars)                                                          #Додавання кнопок на клавіатуру               
    async with state.proxy() as data:                                                     #Запис даних в проксі-змінну з тексту повідомлення                           
        buttons_piercing = ['Random piercing', 'Piercings', 'No piercing']                #Створення масиву кнопок для отримання даних з клавіатури і отримання індексу елементу масиву                                               
        data['Pierce'] = buttons_piercing.index(message.text)                             #Дані записуються з повідомлення в проксі-змінну "Pierce"                                                                     
    await CharacteristicsForm.next()                                                      #Перехід до наступного стану                           
    await message.reply(f"Select if character has scars", reply_markup=keyboard)          #Відповідь на повідомлення "Select if character has scars" з вказанням дії                                                                       

@dp.message_handler(state=CharacteristicsForm.Scar)
async def tattoo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:                                                     #Запис даних в проксі-змінну з тексту повідомлення                           
        buttons_scars = ['Random scars', 'Scars', 'No scars']                             #Створення масиву кнопок для отримання даних з клавіатури і отримання індексу елементу масиву 
        data['Scar'] = buttons_scars.index(message.text)                                  #Дані записуються з повідомлення в проксі-змінну "Scar"                                     
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)                            #Створення клавіатури                                                     
    buttons_tattoo = ['Random', 'Tattoos', 'No tattoo']                                   #Створення масиву кнопок для клавіатури                           
    keyboard.add(*buttons_tattoo)                                                         #Додавання кнопок на клавіатуру               
    await CharacteristicsForm.next()                                                      #Перехід до наступного стану                             
    await message.reply(f"Select if character has tattoo", reply_markup=keyboard)         #Відповідь на повідомлення "Select if character has tattoo" з вказанням дії                                                 

@dp.message_handler(state=CharacteristicsForm.Tattoo)
async def makeup(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)                            #Створення клавіатури                                                                                                            
    buttons_makeup = ['Random makeup','Makeup','No makeup']                               #Створення масиву кнопок для клавіатури                                                                                      
    keyboard.add(*buttons_makeup)                                                         #Додавання кнопок на клавіатуру                     
    async with state.proxy() as data:                                                     #Запис даних в проксі-змінну з тексту повідомлення                                     
        buttons_tattoo = ['Random', 'Tattoos', 'No tattoo']                               #Створення масиву кнопок для отримання даних з клавіатури і отримання індексу елементу масиву                                
        data['Tattoo'] = buttons_tattoo.index(message.text)                               #Дані записуються з повідомлення в проксі-змінну "Tattoo"                                                                    
    await CharacteristicsForm.next()                                                      #Перехід до наступного стану                                     
    await message.reply(f"Select if character has makeup", reply_markup=keyboard)         #Відповідь на повідомлення "Select if character has makeup" з вказанням дії                                                                           

@dp.message_handler(state=CharacteristicsForm.Makeup)
async def generation(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardRemove()                                                  #Ховаємо клавіатуру
    await message.reply('Generation in progress', reply_markup=markup)                    #Виводимо повідомлення "Generation in progress"
    async with state.proxy() as data:                                                     #Запис даних в проксі-змінну з тексту повідомлення                                     
        buttons_makeup = ['Random makeup','Makeup','No makeup']                           #Створення масиву кнопок для отримання даних з клавіатури і отримання індексу елементу масиву  
        data['Makeup'] = buttons_makeup.index(message.text)                               #Дані записуються з повідомлення в проксі-змінну "Makeup"                                      
    await state.finish()                                                                  #Кінець конвеєра

    myobj = {'event': 'generate',                                                         #Створюється тіло запиту  
             'sex': G_Sex[data['Sex']],                                                   #З масиву "G_Sex" береться елемент під номером, який зберігається в проксі-змінній          
             'type':G_Type[data['Type']],                                                           
             'detail': 'Detailed', 
             'beard': G_Beard[data['Beard']],
             'HairL': G_HairL[data['HairL']],
             'Hloss': G_HLoss[data['HLoss']],
             'dye': G_Dye[data['Dye']],
             'clothing': G_Clothing[data['Clothing']],
             'pierce': G_Pierce[data['Pierce']],
             'scar': G_Scar[data['Scar']],
             'tattoo': G_Tattoo[data['Tattoo']],
             'makeup': G_Makeup[data['Makeup']]}

    resp = requests.post('https://www.rangen.co.uk/chars/appScript.php', data=myobj)      #Відправка пост-запиту на сайт з усіма заданими параметрами
    
    text = html2text.html2text(resp.text)                                                 #За допомогою бібліотеки html2text html конвертується в текст                                         
    textarr = text.split('* * *')                                                         #Роздіяємо текст по символам * * *
 
    #Додавання інлайн-клавіатури для можливості зберігання персонажа
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Save to library", callback_data="libsave"))
    await message.reply(textarr[0], reply_markup=keyboard)                                #Виводиться повідомлення з нульовим елементом текстового масиву


#Масиви з елементами вибору особистості персонажа
G_PDetail = ['Simple','Detailed']
G_PType = ['Random', 'Positive', 'Negative']

#Декоратор обробник перевіряє чому дорівнює останнє повідомлення. Якщо воно дорівнює "Generate personality", тоді викликається функція "personlity_granularity"
@dp.message_handler(lambda message: message.text == "Generate personality")
async def personlity_granularity(message: types.Message):
    await CharacteristicsPersonalityForm.Detail.set()                                           #запуск конвеєра
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)                                  #створення клавіатури     
    keyboard.add(*G_PDetail)                                                                    #додавання кнопок з масиву
    await message.reply(f"Select character granularity", reply_markup=keyboard)                 #відповідь на повідомлення з вказанням дії

#Якщо стан = CharacteristicsPersonalityForm.Detail, то виконується ф-ція "personality_type"
@dp.message_handler(state=CharacteristicsPersonalityForm.Detail)
async def personality_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:                                                           #запис даних в проксі-змінну з тексту повідомлення
        data['Detailed'] = G_PDetail.index(message.text)
        
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)                                  #створення клавіатури
    keyboard.add(*G_PType)                                                                      #додавання кнопок на клавіатуру
    await CharacteristicsPersonalityForm.next()                                                 #перехід до наступного стану
    await message.reply(f"Select character type", reply_markup=keyboard)                        #відповідь на повідомлення з вказанням дії

#Якщо стан = CharacteristicsPersonalityForm.Type, то виконується ф-ція "type"
@dp.message_handler(state=CharacteristicsPersonalityForm.Type)
async def type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:                                                           #запис даних в проксі-змінну з тексту повідомлення
        data['Type'] = G_PType.index(message.text)

    await state.finish()                                                                        #завершення конвеєра станів
    markup = types.ReplyKeyboardRemove()                                                        #клавіатура ховається
    await message.reply('Generating', reply_markup=markup)                                      #сповіщення про початок генерування персонажа
    myobj = {'event': 'generate',                                                               #створення тіла для пост запиту
             'detail':G_PDetail[data['Detailed']], 
             'type':G_Type[data['Type']], 
             'amount': 1
             }

    resp = requests.post('https://www.rangen.co.uk/chars/perScript.php', data=myobj)            #Відправка пост-запиту на сайт з усіма заданими параметрами
    text = html2text.html2text(resp.text)                                                       #За допомогою бібліотеки html2text html конвертується в текст

    if data['Detailed']==1:                                                                     #Якщо вибрана детальна особистіть, то відсилається повідомлення з детальним описом
        text = text.replace('\n', '').replace('|', '')                                          #очищення від зайвих слешів та пустих рядків
        textarr = text.split('**')                                                              #розбивання тексту на масив
        
        textarr[4] = textarr[4].replace('-',  '')                                               #очищення рядка від "-"
        msg = f'Personality Type: {textarr[1]}\n'                                               #
        msg = msg+f'Friendliness: {textarr[4]}\n'                                               #наповнення рядка для подальшого відсилання ботом       
        msg = msg+f'Honesty: {textarr[6]}\n'                                                    #
        msg = msg+f'Assertiveness: {textarr[8]}\n'                                              #       
        msg = msg+f'Confidence / Ego: {textarr[10]}\n'                                          #           
        msg = msg+f'Agreeableness: {textarr[12]}\n'                                             #       
        msg = msg+f'Manners: {textarr[14]}\n'                                                   #
        msg = msg+f'Discipline: {textarr[16]}\n'                                                #       
        msg = msg+f'Rebelliousness: {textarr[18]}\n'                                            #           
        msg = msg+f'Emotional capacity: {textarr[20]}\n'                                        #               
        msg = msg+f'Intelligence: {textarr[22]}\n'                                              #       
        msg = msg+f'Positivity: {textarr[24]}\n'                                                #       
        msg = msg+f'Activeness / Lifestyle: {textarr[26]}\n'                                    #                   
        msg = msg+f'Current emotional state: {textarr[29]}\n'                                   #               

        #створення інлайн клавіатури та добавлення кнопки для збереження в бібліотеку
        keyboard = types.InlineKeyboardMarkup()                                                         
        keyboard.add(types.InlineKeyboardButton(text="Save to library", callback_data="libsave"))
        
        #відсилання повідомлення
        await message.reply(msg, reply_markup=keyboard) 
    #якщо вибраний простий опис особистості
    else:
        #створення інлайн клавіатури та добавлення кнопки для збереження в бібліотеку
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Save to library", callback_data="libsave"))
        #відсилання повідомлення
        await message.reply(text, reply_markup=keyboard) 

#Клас для станів для збереження елементів у бібліотеку користувача
class SaveToLibForm(StatesGroup):
    item_name = State()

#Клас для станів для пошуку елементів у бібліотці користувача
class SearchInLibForm(StatesGroup):
    item_name = State()

#Клас для станів для видалення елементів з бібліотеки користувача
class DeleteFromLibForm(StatesGroup):
    item_name = State()


#Якщо останній запит = libsave, то декоратор обробник викликає ф-цію "libsave_start"
@dp.callback_query_handler(text="libsave")
async def libsave_start(call: types.CallbackQuery):
    await SaveToLibForm.item_name.set()                                         #Запускається машина станів SaveToLibForm для подальшого введення імнені персонажа
    await call.message.reply('Type unique name for character: ')                #Оповіщення користувача про обов'язкове введення імені песонажа

#Якщо стан дорівнює "SaveToLibForm.item_name", то запускається ф-ція "save_naming_state", де потрібно буде ввести унікальне ім'я персонажа
@dp.message_handler(state=SaveToLibForm.item_name)
async def save_naming_state(message: types.Message, state: FSMContext):
    await state.finish() #Завешення конвеєра станів

    userid = message.chat.id                                                    #Ініціалізація змінної, які присвоюється id коритстувача
    saved_msgid = message.message_id - 2                                        #Ініціалізація змінної, які присвоюється id повідомлення
    saved_name = message.text                                                   #Ініціалізація змінної, які присвоюється текст повідомлення

    cur.execute("SELECT msgid FROM userlibrary WHERE saved_name=? AND userid=?", (saved_name, userid,)) #Пошук по таблиці в базі даних, чи інснує вже рядок з ім'ям персонажу
    _data=cur.fetchall() #Збір всіх даних

    #Якщо персонажа з таким іменем в базі даних не існує, то в таблицю додається новий і відправляється повідомлення користувачу, що персонаж доданий
    if len(_data)==0: 
        cur.execute(f'INSERT INTO userlibrary VALUES ({userid}, {saved_msgid}, "{saved_name}")')
        con.commit()
        await bot.send_message(message.chat.id, f"Character saved to library with name - {saved_name}")
    
    #Якщо персонаж найдений, то користувачу відправляється повідомлення, що такий уже існує - користувачу виводиться відповідне повідомлення
    else:
        await bot.send_message(message.chat.id, "This character already in library")

#Якщо повідомлення починається з команди /start, буде викликано декоратор для обробки текстових повідомлень і запустить функцію "openLibrary"
@dp.message_handler(commands="lib")
async def openLibrary(message: types.Message):
    #Пошук по таблиці всіх збережених персонажів поточного користувача 
    cur.execute("SELECT msgid, saved_name FROM userlibrary WHERE userid = ?", (message.chat.id,))
    _data=cur.fetchall() #Збір всіх даних

    #Якщо в поточного користувача нічого не знайдено, то відправляється повідомлення з оповіщенням, що в користувача немає збереженних персонажів
    if len(_data)==0: 
        await bot.send_message(message.chat.id, f"Your library is empty")
    #Якщо знайдено дані для корсистувача, то отримуємо з рядка ім'я персонажа та відсилаємо їх у повідомленні
    else:
        msg = 'You characters: \n'
        for row in _data:
            msg = msg + f"{row[1]}\n"
        await message.answer(msg)

#Якщо повідомлення починається з команди /libsearch, буде викликано декоратор для обробки текстових повідомлень і запустить функцію "start_search_in_Library"
@dp.message_handler(commands="libsearch")
async def start_search_in_Library(message: types.Message):
    await SearchInLibForm.item_name.set()                                       #Запуск конвеєра станів
    await message.reply('Enter a valid character name:')                        #Відповідь на повідомлення з указанням подальших дій
    
#Якщо стан = SearchInLibForm.item_name, то виконується ф-ція "search_name_state"
@dp.message_handler(state=SearchInLibForm.item_name)
async def search_name_state(message: types.Message, state: FSMContext):
    await state.finish()                                                        #Завершення конвеєра станів

    #Пошук по таблиці в базі даних, чи інснує потрібний рядок з ім'ям персонажу для певного користувача
    cur.execute("SELECT msgid, saved_name FROM userlibrary WHERE userid = ? AND saved_name=?", (message.chat.id, message.text,))
    _data=cur.fetchall()                                                        #Збір всіх даних
    
    #Якщо в поточного користувача нічого не знайдено, то відправляється повідомлення з оповіщенням, що в користувача немає збереженного персонажа з таким іменем
    if len(_data)==0:
        await bot.send_message(message.chat.id, f"There's no character with name - {message.text}")

    #Якщо знайдено потрібного персонажа, то отримується з рядка таблиці id потвідомлення і бот копіює його користувачу
    else:
        for row in _data:
            msg = f"Character: {row[1]}"
            await message.answer(msg)
            await bot.copy_message(message.chat.id, message.chat.id, row[0])

#Якщо повідомлення починається з команди /libdelete, буде викликано декоратор для обробки текстових повідомлень і запустить функцію "start_delte_in_Library"
@dp.message_handler(commands="libdelete")
async def start_delte_in_Library(message: types.Message):
    await DeleteFromLibForm.item_name.set()                                     #Запуск конвеєра станів
    await message.reply('Enter a valid character name:')                        #Відповідь на повідомлення з указанням подальших дій
    
#Якщо стан = DeleteFromLibForm.item_name, то виконується ф-ція "delete_name_state"
@dp.message_handler(state=DeleteFromLibForm.item_name)
async def delete_name_state(message: types.Message, state: FSMContext):
    await state.finish()                                                        #Завершення конвеєра станів

    #Пошук по таблиці в базі даних, чи інснує потрібний рядок з ім'ям персонажу для певного користувача
    cur.execute("SELECT msgid, saved_name FROM userlibrary WHERE userid = ? AND saved_name=?", (message.chat.id, message.text,))
    _data=cur.fetchall() #Збір всіх даних

    #Якщо в поточного користувача нічого не знайдено, то відправляється повідомлення з оповіщенням, що в користувача немає збереженного персонажа з таким іменем
    if len(_data)==0:
        await bot.send_message(message.chat.id, f"There's no character with name - {message.text}")
    #Якщо знайдено потрібного персонажа, то рядок видаляється і комітиться до бази даних
    else:
        for row in _data:
            msg = f"Character: {row[1]}"
            cur.execute('DELETE FROM userlibrary WHERE userid = ? AND saved_name=?', (message.chat.id, message.text,))
            con.commit()
            await message.answer(f'Character with name "{message.text}" was deleted.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
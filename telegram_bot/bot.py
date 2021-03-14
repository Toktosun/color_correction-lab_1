import json
import cv2
import telebot
import environ

from transfer import ColorCorrectionTransfer


env = environ.Env()

bot = telebot.TeleBot(env.str('TELEGRAM_TOKEN'))


@bot.message_handler(commands=['start', 'help'])
def start(msg):
    if msg.text == '/start':
        bot.send_message(
            msg.chat.id, 'Привет, я бот который может применить '
                         'цветокоррекцию одной фотографии на другую.')
    elif msg.text == '/help':
        bot.send_message(
            msg.chat.id, 'Для загрузки исходника '
                         'отправьте изображение подписав "source", \n'
                         'далее отправьте целевое изображение подписав "target"'
                         'и наконец запросите полученное изображение с командой'
                         '/get'
        )


@bot.message_handler(content_types=['photo'])
def get_photo(msg):
    with open("user.json", "r") as json_file:
        data = json.load(json_file)
    json_file = open("user.json", "r")
    data = json.load(json_file)
    json_file.close()
    file_name = f"{msg.from_user.username}_{msg.id}.jpg"

    file_id = msg.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    if msg.caption.upper() == 'SOURCE':
        data[f'{msg.from_user.id}_source'] = file_name
        message = 'Вы успешно отправили исходное фото.'

    elif msg.caption.upper() == 'TARGET':
        data[f'{msg.from_user.id}_target'] = file_name
        message = 'Вы успешно отправили целевое фото.'
    else:
        message = 'Вы некорректно подписали фото. "source" или "target"'
        bot.send_message(msg.chat.id, message)
        return None

    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
        json_file = open("user.json", "w+")
        json_file.write(json.dumps(data))
        json_file.close()

    bot.send_message(msg.chat.id, message)


@bot.message_handler(commands=['get'])
def send_message(msg):
    username = msg.from_user.username
    image_name = f'{username if username else "no-name"}_result.jpg'
    bot.send_message(msg.chat.id, 'Походите, ща все будет)')
    with open('user.json') as json_file:
        data = json.load(json_file)

    try:
        source = data[f'{msg.chat.id}_source']
        target = data[f'{msg.chat.id}_target']
    except KeyError:
        bot.send_message(
            msg.chat.id, 'Сначала отправьте исходное и целеве фото.')
        return None

    source_read = cv2.imread(source)
    target_read = cv2.imread(target)

    transfer = ColorCorrectionTransfer(source_read, target_read)
    transfer_image = transfer.get_converted_to_rgb()

    cv2.imwrite(image_name, transfer_image)

    img = open(image_name, 'rb')
    bot.send_photo(
        msg.chat.id, img,
        caption=f'Результат для пользователя {msg.from_user.username}',
    )


bot.polling(none_stop=True)

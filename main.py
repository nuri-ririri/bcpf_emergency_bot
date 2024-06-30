from telegram import Update, InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# Replace 'YOUR_TOKEN' with your actual bot token
BOT_TOKEN = '7387645609:AAGS2MmV_fhP8bF65MTBF2CQFhgkWjGr0mY'
# Replace 'ORGANIZERS_CHAT_ID' with the actual chat ID of the organizers' group
ORGANIZERS_CHAT_IDS = ['-1002161837916', '-1002168163239', '-1002152575512', '-1002218852478']
# emergency draft group, recruitment group,
# управляющие волонтеров группа, группа оргов

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


async def start(update, context):
    reply_keyboard = [[KeyboardButton("/start")]]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text('Привет!\n'
                                    '<b>1.</b> Что случилось?\n'
                                    '<b>2.</b> Что случилось?\n \n'
                                    'Отправьте мне всё <b>одним сообщением</b> и я <b>анонимно</b>'
                                    ' переправлю его <u>организаторам</u>',
                                    parse_mode='HTML', reply_markup=reply_markup)
    return


async def forward_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == 'private':
        logger.info("Forwarding text message")
        for chat_id in ORGANIZERS_CHAT_IDS:
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"<b>Анонимный запрос:</b>\n<u>{update.message.text}</u>"
                                                "\n@aida_undercover @nedegenadamsn @defescooler @Alt_Nuri",
                                           parse_mode='HTML')
        await update.message.reply_text("Мы получили Ваше сообщение. Благодарим! Организаторы с Вами свяжутся")


async def forward_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == 'private':
        photos = update.message.photo
        number_of_photos = len(update.message.photo)

        if photos:
            if number_of_photos == 1:
                logger.info("Forwarding photo SINGLE SAD PHOTO")
                photo = photos[-1]
                # Select the highest resolution photo
                for chat_id in ORGANIZERS_CHAT_IDS:
                    await context.bot.send_photo(chat_id=chat_id, photo=photo.file_id,
                                                 caption=f"<b>Анонимный запрос:</b>\n<u>{update.message.caption}</u>"
                                                         "\n@aida_undercover @nedegenadamsn @defescooler @Alt_Nuri",
                                                 parse_mode='HTML')
                await update.message.reply_text("Мы получили Ваше фото. Благодарим! Организаторы с Вами свяжутся")
            elif number_of_photos > 1:
                logging.info("we think THERE ARE SEVERAL PHOTOS")
                # Create a list of InputMediaPhoto, but leave the last one for the caption
                media_group = [InputMediaPhoto(photo.file_id) for photo in photos[:-1]]
                # Add the last photo with a caption (if exists)
                logging.info("created a MEDIA GROUP")
                last_photo = InputMediaPhoto(photos[-1].file_id,
                                             caption=f"<b>Анонимный запрос:</b>\n<u>{update.message.caption}</u>"
                                                     "\n@aida_undercover @nedegenadamsn @defescooler @Alt_Nuri",
                                             parse_mode='HTML')
                media_group.append(last_photo)

                logger.info(f"Forwarding {len(media_group)} photos as an album with caption.")
                for chat_id in ORGANIZERS_CHAT_IDS:
                    await context.bot.send_media_group(chat_id=chat_id, media=media_group)
                await update.message.reply_text("Мы получили Ваши фото. Благодарим! Организаторы с Вами свяжутся")


async def handle_reply_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == "/start":
        await start(update, context)  # Call the start function again
    else:
        await forward_text(update, context)


async def error_handler(update, context):
    logger.error(f"Update {update} caused error {context.error}")


def main():
    # Create the Application instance
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register the command and message handlers
    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply_keyboard))
    application.add_handler(MessageHandler(filters.PHOTO, forward_photo))
    application.add_error_handler(error_handler)

    # Start the bot
    application.run_polling()


if __name__ == '__main__':
    main()

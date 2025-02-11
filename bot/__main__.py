import os
import random
from time import sleep
from pyrogram import filters
from bot import LOG, app, advance_config, chats_data, from_chats, to_chats, \
                remove_strings, replace_string, sudo_users
from bot.helper.utils import get_formatted_chat

@app.on_message(filters.chat(from_chats) & filters.incoming)
def work(client, message):
    LOG.info("new message received")        
    caption = None
    msg = None
    if remove_strings:
      for string in remove_strings:
        if message.media and not message.poll:
          caption = message.caption.html.replace(string, replace_string)
        elif message.text:
          msg = message.text.html.replace(string, replace_string)
    if advance_config:
      try:
        for chat in chats_data[message.chat.id]:
          if caption:
            message.copy(chat, caption=caption)
          elif msg:
            app.send_message(chat, msg, parse_mode="html")
          else:
            message.copy(chat)
      except Exception as e:
        LOG.error(e)
    else:
      try:
        # lets check again if there are any duplicates
        for chat in list(set(to_chats)):
          if chat not in from_chats:
            if caption:
              message.copy(chat, caption=caption)
            elif msg:
              app.send_message(chat, msg)
            else:
              message.copy(chat)
      except Exception as e:
        LOG.error(e)

@app.on_message(filters.command(["start", "join", "subscribe"]), group=1)
def subscribe(app, message):
  LOG.info("Subscription request received")
  try:
    chat_id = message.chat.id
    # remove duplicates
    if chat_id not in to_chats:
      # store the new list of subscribers
      to_chats.append(int(chat_id))      
      with open("subscribed_ids.txt", 'w') as filehandle:
        for listitem in to_chats:
          filehandle.write('%d\n' % listitem)
      
      LOG.info(f"Subscription request {chat_id} processed")
      reply = message.reply_text("Inoltro dei messaggi attivato. Yeee!")
  except Exception as e:
    LOG.error(e)
  
@app.on_message(filters.user(sudo_users) & filters.command(["fwd", "forward"]), group=1)
def forward(app, message):
    if len(message.command) > 1:
      chat_id = get_formatted_chat(message.command[1], app)
      if chat_id:
        try:
          offset_id = 0
          limit = 0
          if len(message.command) > 2:
            limit = int(message.command[2])
          if len(message.command) > 3:
            offset_id = int(message.command[3])
          for msg in app.iter_history(chat_id, limit=limit, offset_id=offset_id):
            msg.copy(message.chat.id)
            sleep(random.randint(1, 10))
        except Exception as e:
          message.reply_text(f"```{e}```")
      else:
        reply = message.reply_text("```Invalid Chat Identifier. Give me a chat id, username or message link.```")
        sleep(5)
        reply.delete()
    else:
      reply = message.reply_text("```Invalid Command ! Use /fwd {ChatID} {limit} {FirstMessageID}```")
      sleep(20)
      reply.delete()

LOG.info("starting bot")
app.run()

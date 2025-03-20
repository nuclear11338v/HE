import telebot
from telebot import types
from config import Config
from functions import *
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

bot = telebot.TeleBot("7604986031:AAEiNS1N1oMDDtQZmi5B0rl2dSVDfu3lGEs")

def requires_channel(func):
    def wrapper(message):
        user_id = message.from_user.id
        try:
            chat_member = bot.get_chat_member(Config.REQUIRED_CHANNEL, user_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Join Channel", url=f"https://t.me/{Config.REQUIRED_CHANNEL[1:]}"))
                bot.send_message(message.chat.id, 
                                FormatHelper.style_text("You must join our channel to use this bot!"),
                                reply_markup=markup)
                return
        except Exception as e:
            print(f"Channel check error: {e}")
        return func(message)
    return wrapper

from telebot import TeleBot, types  

@bot.message_handler(commands=['start'])  
@requires_channel  
def start_cmd(message):  
    video_path = "arman.mp4"

    text = """<b>BOT MENU</b>\n\n
┌── 🔸 FOR ACCESS DM 
│   ├─ @PB_X01
│ 
├── 🔸COMMANDS
│  ├─ /attack [ ip ] [ port ]
│  ├─ /myinfo
│  └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
├── 🔸 <b>Status</b>: 🟢 Online
│
├── 🔸 <b>Version</b>: 0.1
│
└── 🔸 <b>ƤOƜƐRƐƊ ƁƳƐ</b>: @TEAM_X_OG"""

    with open(video_path, "rb") as video:  
        bot.send_video(message.chat.id, video, caption=text, parse_mode="HTML")  

@bot.message_handler(commands=['attack'])
@requires_channel
def attack_cmd(message):
    user_id = message.from_user.id
    data = DataManager.load_data()
    
    if not data['users'].get(str(user_id), {}).get('approved', False):
        bot.reply_to(message, FormatHelper.style_text("🔒 You need approval to attack!\n\nDM TO BUY ACCES :- @PB_X01"))
        return
    
    try:
        _, ip, port = message.text.split()
        port = int(port)
    except:
        bot.reply_to(message, FormatHelper.style_text("❌ Invalid format!\nUse: /attack [IP] [PORT]"))
        return
    
    if port in Config.BLOCKED_PORTS:
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("📛", callback_data='blocked_ports'),
            types.InlineKeyboardButton("👤 Contact Admin", url=f"tg://user?id={Config.ADMIN_ID}")
        )
        bot.send_photo(message.chat.id, Config.PHOTOS['blocked'],
                      caption=FormatHelper.style_text("🚫 BLOCKED PORT DETECTED!"),
                      reply_markup=markup)
        return
    
    user_data = data['users'][str(user_id)]
    if user_data['last_attack'] and (time.time() - user_data['last_attack'] < user_data['cooldown']):
        remaining = int(user_data['cooldown'] - (time.time() - user_data['last_attack']))
        bot.reply_to(message, FormatHelper.style_text(f"⏳ Cooldown active! Wait {remaining}s"))
        return

    attack_thread = threading.Thread(
        target=execute_attack,
        args=(message, ip, port, user_id)
    )
    attack_thread.start()

def execute_attack(message, ip, port, user_id):
    try:
        DataManager.update_user(user_id, {
            "last_attack": time.time(),
            "attack_count": DataManager.load_data()['users'][str(user_id)]['attack_count'] + 1
        })
        
        caption = FormatHelper.format_caption("ATTACK STARTED", [
            ("IP", ip),
            ("Port", port),
            ("Duration", f"{Config.ATTACK_DURATION}s"),
            ("User", message.from_user.first_name)
        ])
        msg = bot.send_photo(message.chat.id, Config.PHOTOS['attack'],
                           caption=FormatHelper.style_text(caption),
                           reply_markup=get_attack_buttons())
        
        if AttackManager.run_attack(ip, port, Config.ATTACK_DURATION, user_id):
            update_attack_status(message, msg, ip, port)
        else:
            bot.edit_message_caption(chat_id=message.chat.id, message_id=msg.message_id,
                                    caption=FormatHelper.style_text("❌ ATTACK FAILED!"))
    except Exception as e:
        print(f"Attack error: {e}")
        bot.send_photo(message.chat.id, Config.PHOTOS['error'],
                      caption=FormatHelper.style_text("⚡ SYSTEM ERROR! Contact admin"))

def get_attack_buttons():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🛑 Stop Attack", callback_data='stop_attack'),
        types.InlineKeyboardButton("📊 Stats", callback_data='attack_stats')
    )
    markup.add(types.InlineKeyboardButton("📝 Attack Logs", callback_data='attack_logs'))
    return markup

def update_attack_status(original_msg, attack_msg, ip, port):
    remaining = Config.ATTACK_DURATION
    while remaining > 0:
        try:
            caption = FormatHelper.format_caption("ATTACK RUNNING", [
                ("IP", ip),
                ("Port", port),
                ("Remaining", f"{remaining}s"),
                ("Status", "🟢 Active")
            ])
            bot.edit_message_caption(
                chat_id=original_msg.chat.id,
                message_id=attack_msg.message_id,
                caption=FormatHelper.style_text(caption)
            )
            time.sleep(2)
            remaining -= 2
        except:
            break
    bot.edit_message_caption(
        chat_id=original_msg.chat.id,
        message_id=attack_msg.message_id,
        caption=FormatHelper.style_text("✅ ATTACK COMPLETED!")
    )

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) != str(Config.ADMIN_ID):
        return
    
    text = FormatHelper.format_caption("ADMIN PANEL", [
        ("Total Users", len(DataManager.load_data()['users'])),
        ("Active Attacks", len(DataManager.load_data()['attacks'])),
        ("Server Load", f"{ServerStats.get_stats()['cpu_usage']}%")
    ])
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("📊 Stats", callback_data='admin_stats'),
        types.InlineKeyboardButton("📝 Logs", callback_data='admin_logs')
    )
    markup.row(
        types.InlineKeyboardButton("🛑 Stop All", callback_data='admin_stop'),
        types.InlineKeyboardButton("📩 Broadcast", callback_data='admin_broadcast')
    )
    
    bot.send_message(message.chat.id, FormatHelper.style_text(text), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == 'stop_attack':
        handle_stop_attack(call)
    elif call.data.startswith('admin_'):
        handle_admin_callbacks(call)

def handle_stop_attack(call):
    data = DataManager.load_data()
    if str(call.from_user.id) == str(Config.ADMIN_ID):
        data['attacks'] = []
        DataManager.save_data(data)
        bot.answer_callback_query(call.id, "🛑 All attacks stopped!")
    else:
        bot.answer_callback_query(call.id, "❌ Admin only command!")

def handle_admin_callbacks(call):
    if call.data == 'admin_stats':
        stats = ServerStats.get_stats()
        text = FormatHelper.format_caption("SERVER STATS", [
            ("CPU Usage", f"{stats['cpu_usage']}%"),
            ("Memory Usage", f"{stats['memory_usage']}%"),
            ("Uptime", stats['uptime'])
        ])
        bot.edit_message_text(FormatHelper.style_text(text),
                            call.message.chat.id,
                            call.message.message_id)
    elif call.data == 'admin_logs':
        with open(Config.LOGS_FILE, 'rb') as f:
            bot.send_document(call.message.chat.id, f)

@bot.message_handler(commands=['myinfo'])
def user_info(message):
    user_id = message.from_user.id
    data = DataManager.load_data().get('users', {}).get(str(user_id), {})
    
    text = FormatHelper.format_caption("USER INFO", [
        ("Status", "✅ Approved" if data.get('approved', False) else "❌ Not approved"),
        ("Attacks Left", data.get('limit', 0) - data.get('attack_count', 0)),
        ("Cooldown", f"{data.get('cooldown', 0)}s"),
        ("Total Attacks", data.get('attack_count', 0))
    ])
    
    bot.reply_to(message, FormatHelper.style_text(text))

@bot.message_handler(commands=['stats'])
def show_stats(message):
    stats = ServerStats.get_stats()
    text = FormatHelper.format_caption("BOT STATS", [
        ("Total Attacks", DataManager.load_data()['stats']['total_attacks']),
        ("Active Attacks", len(DataManager.load_data()['attacks'])),
        ("CPU Load", f"{stats['cpu_usage']}%"),
        ("Memory Usage", f"{stats['memory_usage']}%")
    ])
    bot.reply_to(message, FormatHelper.style_text(text))

def is_admin(user_id):
    data = DataManager.load_data()
    return str(user_id) in data['admins'] or str(user_id) == str(Config.ADMIN_ID)

def admin_required(func):
    def wrapper(message):
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "🚫 Admin only command!")
            return
        return func(message)
    return wrapper

@bot.message_handler(commands=['approve'])
@admin_required
def approve_user(message):
    try:
        target_id = message.text.split()[1]
        DataManager.update_user(target_id, {"approved": True})
        bot.reply_to(message, f"✅ User {target_id} approved!")
    except IndexError:
        bot.reply_to(message, "❌ Usage: /approve <user_id>")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['unapprove'])
@admin_required
def unapprove_user(message):
    try:
        target_id = message.text.split()[1]
        DataManager.update_user(target_id, {"approved": False})
        bot.reply_to(message, f"✅ User {target_id} unapproved!")
    except IndexError:
        bot.reply_to(message, "❌ Usage: /unapprove <user_id>")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['setlimit'])
@admin_required
def set_limit(message):
    try:
        _, target_id, new_limit = message.text.split()
        DataManager.update_user(target_id, {"limit": int(new_limit)})
        bot.reply_to(message, f"✅ Limit for {target_id} set to {new_limit}!")
    except ValueError:
        bot.reply_to(message, "❌ Usage: /setlimit <user_id> <new_limit>")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['broadcast'])
@admin_required
def broadcast_message(message):
    try:
        broadcast_text = message.text.split(' ', 1)[1]
        confirm_markup = types.InlineKeyboardMarkup()
        confirm_markup.add(
            types.InlineKeyboardButton("✅ Confirm", callback_data=f"broadcast_confirm_{message.message_id}"),
            types.InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
        )
        bot.reply_to(message, 
                    f"📢 Confirm broadcast message:\n\n{broadcast_text}",
                    reply_markup=confirm_markup)
    except IndexError:
        bot.reply_to(message, "❌ Usage: /broadcast <message>")

@bot.callback_query_handler(func=lambda call: call.data.startswith('broadcast_'))
def handle_broadcast_confirmation(call):
    if call.data.startswith('broadcast_confirm'):
        try:
            original_text = call.message.reply_to_message.text
            broadcast_text = original_text.split(' ', 1)[1]
            
            bot.answer_callback_query(call.id, "Starting broadcast...")
            status_msg = bot.send_message(call.message.chat.id, "📡 Broadcasting started...")
            
            success, failed = BroadcastManager.send_broadcast(broadcast_text, bot)
            
            bot.edit_message_text(
                f"📢 Broadcast completed!\n"
                f"✅ Success: {success}\n"
                f"❌ Failed: {failed}",
                call.message.chat.id,
                status_msg.message_id
            )
        except Exception as e:
            bot.edit_message_text(f"❌ Broadcast failed: {str(e)}", call.message.chat.id, status_msg.message_id)
    elif call.data == 'broadcast_cancel':
        bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.message_handler(commands=['addadmin'])
@admin_required
def add_admin(message):
    try:
        new_admin_id = message.text.split()[1]
        data = DataManager.load_data()
        if new_admin_id not in data['admins']:
            data['admins'].append(new_admin_id)
            DataManager.save_data(data)
            bot.reply_to(message, f"✅ Added {new_admin_id} as admin!")
        else:
            bot.reply_to(message, "ℹ️ User is already admin")
    except IndexError:
        bot.reply_to_message(message, "❌ Usage: /addadmin <user_id>")

@bot.callback_query_handler(func=lambda call: call.data == 'blocked_ports')
def handle_blocked_ports(call):
    blocked_ranges = [
        "1-9999 (All ports below 10000)",
        "17500",
        "20001-20003",
        "30000"
    ]
    response = "🚫 Blocked Port Ranges:\n" + "\n".join(f"• {r}" for r in blocked_ranges)
    bot.answer_callback_query(call.id, response, show_alert=True)

@bot.message_handler(commands=['logs'])
@admin_required
def handle_logs(message):
    try:
        with open(Config.LOGS_FILE, 'rb') as log_file:
            bot.send_document(
                chat_id=message.chat.id,
                document=log_file,
                caption=FormatHelper.style_text("📄 Attack Logs"),
                timeout=30
            )
    except FileNotFoundError:
        bot.reply_to(message, FormatHelper.style_text("❌ Logs file not found!"))
    except Exception as e:
        bot.reply_to(message, FormatHelper.style_text(f"❌ Error retrieving logs: {str(e)}"))

@bot.message_handler(commands=['id', 'info'])
def send_user_info(message):
    user = message.from_user
    chat = message.chat
    reply = message.reply_to_message

    user_info = f"""
<b>USERNAME:</b> @{user.username or 'N/A'}
<b>USER ID:</b> <code>{user.id}</code>

<b>FIRST NAME:</b> {user.first_name or 'N/A'}
<b>LAST NAME:</b> {user.last_name or 'N/A'}

<b>BIO:</b> <i>Fetching...</i>
<b>STARTED THIS BOT:</b> ✅
    """

    buttons = InlineKeyboardMarkup()
    buttons.add(InlineKeyboardButton("GET USER PHOTO", callback_data=f"photo_{user.id}"))
    buttons.add(InlineKeyboardButton("USER LINK", url=f"tg://user?id={user.id}"))

    if reply:
        replying_user = reply.from_user
        user_info += f"""
<b>CHAT ID:</b> <code>{chat.id}</code>
<b>REPLYING USER ID:</b> <code>{replying_user.id}</code>

<b>REPLYING FIRST NAME:</b> {replying_user.first_name or 'N/A'}
<b>REPLYING LAST NAME:</b> {replying_user.last_name or 'N/A'}

<b>BIO:</b> <i>Fetching...</i>
<b>STARTED THIS BOT:</b> ✅
        """
        buttons.add(InlineKeyboardButton("REPLYING USER LINK", url=f"tg://user?id={replying_user.id}"))
        buttons.add(InlineKeyboardButton("REPLYING USER PHOTO", callback_data=f"photo_{replying_user.id}"))

    bot.send_photo(chat.id, "https://graph.org/file/fbe88feb0d40ef93bf2ae-a2eb4d4fb0c7186a54.jpg", caption=user_info, reply_markup=buttons)


@bot.callback_query_handler(func=lambda call: call.data.startswith("photo_"))
def send_user_photo(call):
    user_id = call.data.split("_")[1]
    bot.send_message(call.message.chat.id, f"Fetching photo for user ID: {user_id}...")



if __name__ == "__main__":
    bot.infinity_polling()

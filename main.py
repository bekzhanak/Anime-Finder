import telebot
import requests

API_KEY = '5727880102:AAEy9y4rrSci4sbSR6FyB9PAtj97Dao8EC4'

bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['start'])
def send_message(message):
    bot.send_message(message.chat.id, """\
Send\\Forward anime screenshots to me \
""")

@bot.message_handler(func=lambda message: True, content_types=['text', 'audio', 'animation', 'document', 
                                                            'sticker', 'video', 'video_note', 'voice', 
                                                            'contact', 'dice', 'poll', 'venue', 'location'])
def wrong_message(message):
    bot.send_message(message.chat.id, "This is not an image")
    
    
@bot.message_handler(func=lambda message: True, content_types=['photo'])
def echo_message(message):
    bot.reply_to(message,"Searching...")
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    response = requests.post("https://api.trace.moe/search",
    data=open("image.jpg", "rb"),
    headers={"Content-Type": "image/jpeg"}
    ).json()
    #anime_id = response['result'][0]['anilist']
    
    query = '''
    query ($id: Int) { 
    Media (id: $id, type: ANIME) { 
    id
    title {
    romaji
    english
    native
    }
    }
    }
    '''
    similarity = 0
    res = ''
    for i in response['result']:
        if i['similarity'] > similarity:
            similarity = i['similarity']
            res = i
    # Define our query variables and values that will be used in the query request
    variables = {
    'id': res['anilist']
    } 

    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    response_title = requests.post(url, json={'query': query, 'variables': variables}).json()
    title = ''
    episode = 'Not found'
    if response_title['data']['Media']['title']['english']:
        title = response_title['data']['Media']['title']['english']
    elif response_title['data']['Media']['title']['romaji']:
        title = response_title['data']['Media']['title']['romaji']
    else:
        title = response_title['data']['Media']['title']['native']
    if res['episode']:
        episode = res['episode']
    bot.send_message(message.chat.id,f'''{title}
Similarity: {round(res['similarity'] * 100,1)}%
Episode: {episode}''')
    bot.send_video(message.chat.id, response['result'][0]['video'])

    

bot.infinity_polling()
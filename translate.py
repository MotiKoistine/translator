import os, requests, time
from pynput.keyboard import Key, Listener, Controller
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('google_api_key')
translate_url = os.getenv('translate_url')

lang_from = 'fi'
lang_to = 'en'

sentence = ''

allowed_chars = "abcdefghijklmnopqrstuvwxyzåäöABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ!?,. '-"

keyboard = Controller()

def get_translation(q):
    body = {
        'q': q,
        'source': lang_from,
        'target': lang_to,
        'format': 'text'
    }

    response = requests.post(f'{translate_url}?key={api_key}', json=body)

    r_json = response.json()

    print(r_json)

    return r_json['data']['translations']

def replace_word():
    global sentence

    if len(sentence) > 0:
        for _ in range(len(sentence) + 1):
            keyboard.press(Key.backspace)
    
        translated = get_translation(sentence)[0]['translatedText']

        for x in translated:
            keyboard.press(x)

        keyboard.press(Key.space)

def on_press(key):
    print(f'Pressed {key}')

def on_release(key):
    global sentence

    if key == Key.esc:
        return False
    elif key == Key.space:
        sentence = sentence + ' '
        replace_word()
    elif key == Key.backspace:
        if len(sentence) > 0:
            sentence = sentence[0:-1]
    elif key == Key.shift:
        pass
    else:
        sentence = sentence + key.char

    print(sentence)



def read_keyboard_inputs():
    with Listener(on_press=on_press,on_release=on_release) as listener:
        listener.join()


def main():
    print('Loaded')

    read_keyboard_inputs()

if __name__ == '__main__':
    main()
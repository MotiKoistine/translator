import os, requests, time
from pynput.keyboard import Key, Listener, Controller
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('google_api_key')
translate_url = os.getenv('translate_url')

lang_from = 'fi'
lang_to = 'ru'

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

last_backspace = time.time()

bp_count = 0

def on_press(key):
    global last_backspace
    global sentence
    global bp_count

    if key == Key.backspace:
        backspace_time = time.time()
        backspace_between = backspace_time - last_backspace

        if bp_count > 0:
            if backspace_between > 0.06 and backspace_between < 0.2:
                sentence = sentence[:-1]
                print(sentence)
        bp_count += 1
        last_backspace = backspace_time


def on_release(key):
    global sentence
    global bp_count
    if key == Key.esc:
        return False
    elif key == Key.space:
        sentence = sentence + ' '
        replace_word()
    elif key == Key.backspace:
        if len(sentence) > 0:
            sentence = sentence[0:-1]
        bp_count = 0
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
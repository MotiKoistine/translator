import os, requests, time, os, json
from pynput.keyboard import Key, Listener, Controller
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('google_api_key')
translate_url = os.getenv('translate_url')
clear_cmd = os.getenv('clear_cmd')

script_dir = os.path.dirname(__file__)

sentence = ''
lang_from = ''
lang_to = ''

translating = False
change_settings = False
shift_toggle = False
ctrl_toggle = False

languages = []

keyboard = Controller()

last_backspace = time.time()

bp_count = 0

def get_languages():
    response = requests.get(f'{translate_url}/languages?key={api_key}')

    r_json = response.json()
    
    if response.status_code == 200:
        languages_list = r_json['data']['languages']

        return_list = []

        for l in languages_list:
            return_list.append(l['language'])

        return return_list
    else:
        print(f'Error: {str(response.status_code)} - {r_json["error"]["message"]}')
        return False

def get_translation(q):
    body = {
        'q': q,
        'source': lang_from,
        'target': lang_to,
        'format': 'text'
    }

    response = requests.post(f'{translate_url}?key={api_key}', json=body)

    r_json = response.json()

    if response.status_code == 200:
        return r_json['data']['translations']
    else:
        print(f'Error: {str(response.status_code)} - {r_json["error"]["message"]}')
        return False

def replace_word():
    global sentence

    if len(sentence) > 0:
        for _ in range(len(sentence) + 1):
            keyboard.press(Key.backspace)
    
        translated = get_translation(sentence)

        if translated:
            translated = translated[0]['translatedText']
            for x in translated:
                keyboard.press(x)

            keyboard.press(Key.space)

def on_press(key):
    global last_backspace, sentence, bp_count, shift_toggle, ctrl_toggle, translating

    if key == Key.ctrl:
        ctrl_toggle = True

    if translating:
        if key == Key.backspace:
            backspace_time = time.time()
            backspace_between = backspace_time - last_backspace

            if bp_count > 0:
                if backspace_between > 0.06 and backspace_between < 0.2:
                    sentence = sentence[:-1]
                    os.system(clear_cmd)
                    print(sentence)
            bp_count += 1
            last_backspace = backspace_time
    else:
        if key == Key.shift:
            shift_toggle = True

def on_release(key):
    global sentence, bp_count, shift_toggle, ctrl_toggle, change_settings, translating


    if key == Key.ctrl:
        ctrl_toggle = False

    if key == Key.esc and ctrl_toggle:
        if translating:
            translating = False
        else:
            translating = True

    if translating:
        if key == Key.esc and not shift_toggle and not ctrl_toggle:
            return False
        elif key == Key.space:
            sentence = sentence + ' '
            replace_word()
        elif key == Key.backspace:
            if len(sentence) > 0:
                sentence = sentence[0:-1]
            bp_count = 0
        elif key == Key.shift or key == Key.ctrl or key == Key.esc or key == Key.enter:
            pass
        else:
            sentence = sentence + key.char
        os.system(clear_cmd)
        print(sentence)
    else:
        if key == Key.esc and not shift_toggle and not ctrl_toggle:
            return False
        elif key == Key.shift:
            shift_toggle = False
        elif key == Key.esc and shift_toggle:
            change_settings = True
            return False



def read_keyboard_inputs():
    with Listener(on_press=on_press,on_release=on_release) as listener:
        listener.join()

def main_menu(settings):
    global lang_from, lang_to, shift_toggle
    lang_from = settings['lang_from']
    lang_to = settings['lang_to']

    os.system(clear_cmd)

    print('Welcome to Miro The Translator')
    print(f'Current settings: from {settings["lang_from"].upper()} to {settings["lang_to"].upper()}. To change settings press Shift + ESC. *translating must be toggled off*')
    print('Toggle translation by pressing CTRL + ESC')
    print('Close by pressing ESC')

    read_keyboard_inputs()

    if change_settings:
        shift_toggle = False
        os.remove(os.path.join(script_dir, 'settings.json'))
        setup()

def setup():
    os.system(clear_cmd)

    dir_files = os.listdir(script_dir)

    if 'settings.json' not in dir_files:
        print('No settings file found.')

        lang_from = False
        lang_to = False

        while not lang_from:
            lang_input = input('Language to translate from (type "help" to list languages): ')

            if lang_input == 'help':
                print(languages)
            else:
                if lang_input in languages:
                    lang_from = lang_input
                else:
                    os.system(clear_cmd)
                    print('Language not found.')

        while not lang_to:
            lang_input = input('Language to translate to (type "help" to list languages): ')

            if lang_input == 'help':
                print(languages)
            else:
                if lang_input in languages:
                    if lang_input != lang_from:
                        lang_to = lang_input
                    else:
                        os.system(clear_cmd)
                        print('Language is same as from language.')
                else:
                    os.system(clear_cmd)
                    print('Language not found.')

        try:
            with open('settings.json', 'w') as file:
                write_obj = {
                    'lang_from': lang_from,
                    'lang_to': lang_to
                }

                file.write(json.dumps(write_obj))

            main_menu(write_obj)
            
        except Exception as e:
            print('Error saving settings file.')
            print(e)
    else:
        with open('settings.json', 'r') as file:
            settings_obj = json.load(file)

        main_menu(settings_obj)


def main():
    global languages

    languages = get_languages()

    if languages:
        setup()


if __name__ == '__main__':
    main()
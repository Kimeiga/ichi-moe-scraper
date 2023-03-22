import re
import requests
from bs4 import BeautifulSoup

import random
import string

from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(get_random_sentence().encode('utf-8'))
        return


def random_alphanumeric_string(length=4):
    # return '3bcd'
    characters = string.ascii_letters + string.digits
    ret = ''.join(random.choice(characters) for _ in range(length))
    print(ret)
    return ret


def extract_furigana(input_str):
    regex = r'\[([^\]|]+)\|([^\]]+)\]'
    result = []

    matches = list(re.finditer(regex, input_str))

    last_index = 0

    for match in matches:
        full_match, kanji, readings = match.group(
            0), match.group(1), match.group(2)
        furigana = readings.replace("|", "")

        if last_index < match.start():
            no_reading_text = input_str[last_index:match.start()]
            result.append({"char": no_reading_text, "reading": ""})

        result.append({"char": kanji, "reading": furigana})

        last_index = match.end()

    if last_index < len(input_str):
        no_reading_text = input_str[last_index:]
        result.append({"char": no_reading_text, "reading": ""})

    return result


# result = extract_furigana("[君|きみ]の[成功|せい|こう]は[一生懸命|いっ|しょう|けん|めい][勉強|べん|きょう]した。")
# print(result)


def get_random_sentence():
    # get random sentence from Tatoeba
    response = requests.get(
        f'https://tatoeba.elnu.com/?from=jpn&orphans=no&sort=random&to=eng&trans_filter=limit&trans_to=eng&unapproved=no&limit=1&rand_seed={random_alphanumeric_string()}')

    # parse json from response
    response = response.json()

    japaneseSentence = response['results'][0]['text']
    englishSentence = response['results'][0]['translations'][0][0]['text']
    furigana = response['results'][0]['transcriptions'][0]['text']

    # print(response)
    # print(response.results.transcriptions[0].text)

    furigana = extract_furigana(furigana)

    definitions = define_words(japaneseSentence)

    print(furigana)
    print(definitions)

    furigana = list(filter(lambda f: f['reading'] != '', furigana))

    combined = []
    i = 0
    for word, definition in definitions:
        temp_word = word
        word_furigana = []
        while i < len(furigana) and temp_word.startswith(furigana[i]['char']):
            word_furigana.append(
                {'text': furigana[i]['char'], 'kana': furigana[i]['reading']})
            temp_word = temp_word[len(furigana[i]['char']):]
            i += 1

        # if there is no furigana for the word,
        if temp_word:
            word_furigana.append({'text': temp_word, 'kana': ''})

        combined.append({'text': word, 'definition': definition,
                        'furigana': word_furigana})

    return {'furigana': combined, 'english': englishSentence, 'japanese': japaneseSentence}


def define_words(sentence):

    # send GET request to ichi.moe website
    response = requests.get(f'https://ichi.moe/cl/qr/?q={sentence}')

    # # print(response.content)
    # f = open("demofile2.txt", "a")
    # f.write(response.content)
    # f.close()

    # parse HTML response using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    with open("output1.html", "w", encoding='utf-8') as file:
        file.write(str(soup))

    definitionResults = soup.select(
        '.gloss:not(.hidden *) div.gloss-content.scroll-pane dl > dd:nth-child(2)  li:nth-child(1) > span.gloss-desc')
    # definitionResults = soup.select(
    #     'span.gloss-desc')

    # print(definitionResults)
    # definitions = [r.text.split(' ')[0].strip() for r in definitionResults]
    definitions = [r.text.split(';')[0].split(' (')[0]
                   for r in definitionResults]

    print(definitions)

    wordResults = soup.select(
        '.gloss:not(.hidden *) div.gloss-content.scroll-pane dl > dt:not(.compounds *):nth-child(1):not(.conjugations *)')

    # print(wordResults)
    # words = [r.text.split('【')[0] for r in wordResults]
    words = [re.sub(r'^\d+\.\s*|\s*$', '', r.text.split('【')[0])
             for r in wordResults]
    print(words)

    # print(definitions)
    # print(words)

    # extract meanings of each word in the sentence
    # defined_tokens = []
    # for word in soup.find_all('a', {'class': 'ruby'}):
    #     defined_tokens.append({
    #         'token': word.text,
    #         'definition': word.next_sibling.strip()
    #     })

    results = list(zip(words, definitions))

    print(results)

    # if one of the definitions has トム in the first part of the tuple, replace the definition with Tom
    results = list(map(lambda d: ('トム', 'Tom')
                       if d[0] == 'トム' else d, results))
    print(results)

    # check for んだ and んです at the end of the sentence and make sure they are kept together in the same tuple with the definition of "the expectation is that..."
    if results[-1][0] == 'だ' or results[-1][0] == 'です' and results[-2][0] == 'ん':
        results[-2] = (results[-2][0] + results[-1][0],
                       "the expectation is that...")
        results.pop()

    # check for よ at the end of the sentence and make the definition "indicates certainty"
    if results[-1][0] == 'よ':
        results[-1] = (results[-1][0], "indicates certainty")

    print(results)
    return results


# print(define_words('私は日本語を勉強しています。'))
# print(define_words('いつ日本に行くべきかは、あなたが何を楽しみにしているかによります'))
# print(define_words('いつ日本に行くべきかは、あなたが何を楽しみにしているかによります'))
# get_random_sentence()
# print(define_words('君の成功は一生懸命勉強した。'))

# furigana = [{'char': '君', 'reading': 'きみ'}, {'char': 'の', 'reading': ''}, {'char': '成功', 'reading': 'せいこう'}, {'char': 'は',
#                                                                                                               'reading': ''}, {'char': '一生懸命', 'reading': 'いっしょうけんめい'}, {'char': '勉強', 'reading': 'べんきょう'}, {'char': 'した。', 'reading': ''}]
# definitions = [('君', 'you'), ('の', 'indicates possessive'), ('成功', 'success'),
#                ('は', 'indicates sentence topic'), ('一生懸命', 'very hard'), ('勉強した', 'study')]

# combined = []
# for word, definition in definitions:
#     word_furigana = []
#     i = 0
#     while i < len(furigana):
#         current_char = furigana[i]
#         if current_char['char'] in word:
#             word_furigana.append(
#                 {'text': current_char['char'], 'kana': current_char['reading']})
#             word = word[len(current_char['char']):]
#             i += 1
#         else:
#             break

#     combined.append({'text': word, 'definition': definition,
#                     'furigana': word_furigana})

# print(combined)

# furigana = [{'char': '君', 'reading': 'きみ'}, {'char': 'の', 'reading': ''}, {'char': '成功', 'reading': 'せいこう'}, {'char': 'は',
#                                                                                                               'reading': ''}, {'char': '一生懸命', 'reading': 'いっしょうけんめい'}, {'char': '勉強', 'reading': 'べんきょう'}, {'char': 'した。', 'reading': ''}]
# definitions = [('君', 'you'), ('の', 'indicates possessive'), ('成功', 'success'),
#                ('は', 'indicates sentence topic'), ('一生懸命', 'very hard'), ('勉強した', 'study')]

# combined = []
# furigana_index = 0
# for word, definition in definitions:
#     word_furigana = []
#     while furigana_index < len(furigana) and word.startswith(furigana[furigana_index]['char']):
#         word_furigana.append(
#             {'text': furigana[furigana_index]['char'], 'kana': furigana[furigana_index]['reading']})
#         word = word[len(furigana[furigana_index]['char']):]
#         furigana_index += 1

#     combined.append({'text': word, 'definition': definition,
#                     'furigana': word_furigana})

# print(combined)
# furigana = [{'char': '君', 'reading': 'きみ'}, {'char': 'の', 'reading': ''}, {'char': '成功', 'reading': 'せいこう'}, {'char': 'は', 'reading': ''}, {'char': '一生懸命', 'reading': 'いっしょうけんめい'}, {'char': '勉強', 'reading': 'べんきょう'}, {'char': 'した。', 'reading': ''}]
# definitions = [('君', 'you'), ('の', 'indicates possessive'), ('成功', 'success'),
#                ('は', 'indicates sentence topic'), ('一生懸命', 'very hard'), ('勉強した', 'study')]

# combined = []
# i = 0
# for word, definition in definitions:
#     word_furigana = []
#     while i < len(furigana) and word.startswith(furigana[i]['char']):
#         word_furigana.append(
#             {'text': furigana[i]['char'], 'kana': furigana[i]['reading']})
#         word = word[len(furigana[i]['char']):]
#         i += 1

#     combined.append({'text': word, 'definition': definition,
#                     'furigana': word_furigana})

# print(combined)

# furigana = [{'char': '君', 'reading': 'きみ'}, {'char': 'の', 'reading': ''}, {'char': '成功', 'reading': 'せいこう'}, {'char': 'は',
#                                                                                                               'reading': ''}, {'char': '一生懸命', 'reading': 'いっしょうけんめい'}, {'char': '勉強', 'reading': 'べんきょう'}, {'char': 'した。', 'reading': ''}]
# definitions = [('君', 'you'), ('の', 'indicates possessive'), ('成功', 'success'),
#                ('は', 'indicates sentence topic'), ('一生懸命', 'very hard'), ('勉強した', 'study')]

# combined = []
# i = 0
# for word, definition in definitions:
#     word_furigana = []
#     temp_word = word
#     while i < len(furigana) and temp_word.startswith(furigana[i]['char']):
#         word_furigana.append(
#             {'text': furigana[i]['char'], 'kana': furigana[i]['reading']})
#         temp_word = temp_word[len(furigana[i]['char']):]
#         i += 1

#     combined.append({'text': word, 'definition': definition,
#                     'furigana': word_furigana})

# print(combined)

print(get_random_sentence())

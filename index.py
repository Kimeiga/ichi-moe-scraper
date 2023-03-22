import requests
from bs4 import BeautifulSoup


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
    words = [r.text.split('【')[0] for r in wordResults]
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
    return list(zip(words, definitions))


# print(define_words('私は日本語を勉強しています。'))
print(define_words('いつ日本に行くべきかは、あなたが何を楽しみにしているかによります'))

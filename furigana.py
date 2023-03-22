furigana = [{'char': 'トムって、', 'reading': ''}, {'char': '毎朝', 'reading': 'まいあさ'}, {
    'char': 'ひげ', 'reading': ''}, {'char': '剃', 'reading': 'そ'}, {'char': 'ってるんだ。', 'reading': ''}]

definitions = [('トム', 'to be rich in'), ('って', 'you said'), ('毎朝', 'every morning'),
               ('ひげ', 'self-abasement'), ('剃ってる', 'to shave'), ('ん', 'yes'), ('だ', 'be')]

furigana = list(filter(lambda f: f['reading'] != '', furigana))
print(furigana)
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

print(combined)

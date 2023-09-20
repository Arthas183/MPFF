
# ----------- 第一步 -----------

def select_sentences_within_length_range(input_file, output_file, min_words=10, max_words=20):
    selected_sentences = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            sentence = line.strip()
            words = sentence.split()
            if min_words <= len(words) <= max_words:
                selected_sentences.append(sentence)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(selected_sentences))

# 设置输入和输出文件路径
input_file = "C:/Users/27348/Desktop/yelp_nega2posi/train.src"
output_file = "negative_selected_sentences.txt"

# 挑选长度在10到20个单词的句子并保存到新的txt文件中
select_sentences_within_length_range(input_file, output_file, min_words=10, max_words=20)


# ----------- 第二步 -----------
import os
import openai
import re
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = ' '

import os
 
os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"

def evaluate_semantic_similarity(original_text, generated_text):
    time.sleep(3)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Please rate the degree of semantic relevance of the generated text:\n\
             please reply with a number between 0 and 100, indicating the percentage score of the degree of semantic relevance of the content\n\
              (0 means that the original text has no semantic connection with the generated text,\
              100 means that the original text has complete consistent semantic with the generated text) \n\
             Please reply in the following format: \n\
             Semantic relevance: 20"},
            {"role": "user", "content": f"original_text: {original_text}"},
            {"role": "user", "content": f"generated_text: {generated_text}"}
        ],
        temperature=0.0,
        # max_tokens=1
    )

    response = completion.choices[0].message.content

    scores = re.findall(r"\d+", response)
    print("scores: ", scores)
    semantic_similarity_score = float(scores[0])

    semantic_similarity_conclusion = True if semantic_similarity_score >= 95 else False

    return semantic_similarity_conclusion

def convert_style(input_file, output_file, style):
    negative_sentences = []
    original_sentences = []

    with open(input_file, 'r', encoding='utf-8') as f:
        sentences = f.readlines()
    count = 0
    line_count = 1
    # style = 'negative'
    for sentence in sentences:
        time.sleep(3)
        print("line: ", line_count)
        line_count += 1

        prompt = f"""You are an excellent English writer. 
        Now you need to rewrite the English sentence I provided you into a {style} style sentence by making minimal changes. 
        The requirements are as follows: 
        First, the style must be very {style}, 
        and then the semantics of the transformed sentence must be consistent with the original sentence. 
        The third is to make as little changes as possible on the basis of the original sentence. 
        Avoid changing the context of the review. The transformed sentences are between 15 and 20 words in length.
        """

        # Create the completion
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"""{prompt}"""},
                {"role": "user", "content": f'{sentence}'}
            ],
            temperature=0.0,
        )

        # Return the transfer text
        transfer_sentence = completion.choices[0].message.content
        
        analyzer = SentimentIntensityAnalyzer()
        sentence_result = analyzer.polarity_scores(sentence)
        print("{:-<65} {}".format(sentence.strip(), str(sentence_result)))
        if sentence_result['neg'] > sentence_result['pos']: status1 = 'nega'
        elif sentence_result['neg'] < sentence_result['pos']: status1 = 'posi'
        else: status1 = 'neutral'

        transfer_result = analyzer.polarity_scores(transfer_sentence)
        print("{:-<65} {}".format(transfer_sentence, str(transfer_result)))
        if transfer_result['neg'] > transfer_result['pos']: status2 = 'nega'
        elif transfer_result['neg'] < transfer_result['pos']: status2 = 'posi'
        else: status2 = 'neutral'

        if status1 == 'posi' and status2 == 'posi':
            if sentence_result['pos'] >= transfer_result['pos']: continue # 积极性弱化，但并不是通常意义上的积极到消极
            else: pass # 积极性强化，nega -> posi
        elif status1 == 'posi' and status2 == 'nega': continue # posi -> nega
        elif status1 == 'posi' and status2 == 'neutral': continue # posi -> nega
        elif status1 == 'nega' and status2 == 'posi': pass # nega -> posi
        elif status1 == 'nega' and status2 == 'nega':
            if sentence_result['neg'] >= transfer_result['neg']: continue # 消极性弱化，但并不是通常意义上的消极到积极
            else: continue # 消极性强化，posi -> nega
        elif status1 == 'nega' and status2 == 'neutral': pass # nega -> posi
        elif status1 == 'neutral' and status2 == 'posi': pass # nega -> posi
        elif status1 == 'neutral' and status2 == 'nega': continue # posi -> nega
        elif status1 == 'neutral' and status2 == 'neutral': continue

        if evaluate_semantic_similarity(sentence, transfer_sentence):
            # 合格的语料对
            # negative_sentences.append(transfer_sentence)
            # original_sentences.append(sentence)
            # print("合格")
            print("negative: ", sentence.strip())
            print("positive: ", transfer_sentence.strip())
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(transfer_sentence.strip() + '\n')
            with open(output_file_origin, 'a', encoding='utf-8') as f:
                f.write(sentence.strip() + '\n')
            count += 1
        if count > 10000:
            break
    # with open(output_file, 'w', encoding='utf-8') as f:
    #     f.write('\n'.join(negative_sentences))

# 设置输入和输出文件路径
input_file = "negative_selected_sentences.txt"
output_file = "positive_sentences.txt"
output_file_origin = "original_sentences.txt"

# 将每一句话转换为消极风格并保存到新的txt文件中
convert_style(input_file, output_file, "positive")

# ----------第三步-------------
# 用snownlp/VADER来判断积极消极指数，不够的就去除
# 再评测语义一致性，不够的也要去除
# 再评测生成语料的长度和BLEU等，不符合的也要去除


# 使用VADER处理original和positive_formal，把完全符合条件的数据集挑出来。
input_original = 'original_sentences.txt'
input_process = 'positive_sentences.txt'
output_original = 'new_original.txt'
output_process = 'new_transfer.txt'
ori_list = []
pro_list = []

import os

if not os.path.exists(output_original):
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    with open(input_original, 'r', encoding='utf-8') as f1, open(input_process, 'r', encoding='utf-8') as f2:
        count = 0
        for origin, process in zip(f1,f2):
            origin = origin.strip()
            process = process.strip()
            print(count)
            print(origin)
            print(process)
            # count+=1

            analyzer = SentimentIntensityAnalyzer()
            sentence_result = analyzer.polarity_scores(origin)
            print("{:-<65} {}".format(origin, str(sentence_result)))
            if sentence_result['neg'] > sentence_result['pos']: status1 = 'nega'
            elif sentence_result['neg'] < sentence_result['pos']: status1 = 'posi'
            else: status1 = 'neutral'

            transfer_result = analyzer.polarity_scores(process)
            print("{:-<65} {}".format(process, str(transfer_result)))
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

            print("ok")
            with open(output_original, 'a', encoding='utf-8') as f:
                f.write(origin.strip() + '\n')
            with open(output_process, 'a', encoding='utf-8') as f:
                f.write(process.strip() + '\n')
            count+=1

print("split: press enter to continue,  press N to exit")
a=input()
if a == 'n' or a == 'N':exit()

import os
folder_name = 'yelp_n2p'

# 读取原始数据文件
with open(output_original, 'r', encoding='utf-8') as f1, open(output_process, 'r', encoding='utf-8') as f2:
    lines_origin = f1.readlines()
    lines_transfer = f2.readlines()

# 划分数据集
total_samples = len(lines_origin)
train_samples = int(total_samples * 0.7)
val_samples = int(total_samples * 0.2)

# 创建文件夹来存放划分后的数据集
os.makedirs(folder_name, exist_ok=True)

# 保存训练集
with open(folder_name+'/train.src', 'w', encoding='utf-8') as f:
    f.writelines(lines_origin[:train_samples])

# 保存验证集
with open(folder_name+'/valid.src', 'w', encoding='utf-8') as f:
    f.writelines(lines_origin[train_samples:train_samples + val_samples])

# 保存测试集
with open(folder_name+'/test.src', 'w', encoding='utf-8') as f:
    f.writelines(lines_origin[train_samples + val_samples:])

# 保存平行训练集
with open(folder_name+'/train.tgt', 'w', encoding='utf-8') as f:
    f.writelines(lines_transfer[:train_samples])

# 保存平行验证集
with open(folder_name+'/valid.tgt', 'w', encoding='utf-8') as f:
    f.writelines(lines_transfer[train_samples:train_samples + val_samples])

# 保存平行测试集
with open(folder_name+'/test.tgt', 'w', encoding='utf-8') as f:
    f.writelines(lines_transfer[train_samples + val_samples:])

print("数据集划分完成并保存在文件夹中。")

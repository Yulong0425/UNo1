import jieba
# seg_list = jieba.cut("要把战场开辟在敌人的家里，要打运动战，打持久战，敌人来圈地你就去他家里圈地",
#                      cut_all=False)
# print("Full Mode: " + "/ ".join(seg_list))  # 全模式
import os
import pandas as pd

corpus = []

terms = {}
with open("replace.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines:
        terms[line.split()[0]] = line.split()[1]
vocab = []

def get_corpus():
    df = pd.read_csv("thread_list.csv")
    tids = df.iloc[:, 0]
    for elm in tids:
        tid = elm.split("/")[2]
        if not os.path.exists("threads/" + tid + "_posts.csv"):
            continue
        print("正在截取帖子" + tid)
        posts = pd.read_csv("threads/" + tid + "_posts.csv")
        replies = pd.read_csv("threads/" + tid + "_replies.csv")
        for idx, post in posts.iterrows():
            # print("len " + str(len(post)))
            if len(post) == 0:
                continue
            # print(post)
            if str(post.iloc[5]) == 'nan':
                continue
            else:
                corpus.append(post.iloc[5])
        
        for idx, reply in replies.iterrows():
            # print("len " + str(len(reply)))
            if len(reply) == 0:
                continue
            if str(reply.iloc[3]) == 'nan':
                continue
            else:
                corpus.append(reply.iloc[3])
        print("帖子" + tid + "截取完成")


    with open("corpus.txt", "w", encoding="utf-8") as f:
        for elm in corpus:
            t = ""
            for k, v in terms.items():
                elm = str(elm).replace(k, v)
            f.write(str(elm) + "\n")

def slice_corpus():
    string = ""
    counter = 10
    with open("corpus.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            # print(line)
            seg_list = jieba.cut(line, cut_all=False)
            # print(" ".join(seg_list))
            string += "\n".join(seg_list) + "\n"
            # counter -= 1
            # if counter == 0:
            #     break
    
    vocab = string.split("\n")

    df = pd.DataFrame(vocab)
    df = df.drop_duplicates()    
    df.to_csv("vocab.csv")
    # with open("vocab.txt", "w", encoding="utf-8") as f:
    #     for elm in vocab:
    #         f.write(str(elm) + "\n")

# slice_corpus()



# word_sequences = []
# with open("corpus.txt", "r", encoding="utf-8") as f:
#     lines = f.readlines()
#     for line in lines:
#         # train(line, vocab_onehot, model, criterion, optimizer)
        
#         word_sequence = jieba.lcut(line, cut_all=False)
#         word_sequences.append(word_sequence)
#         # break
    
#     max_len = 0
#     max_idx = 0
#     for i in range(len(word_sequences)):
#         if len(word_sequences[i]) > max_len:
#             max_len = len(word_sequences[i])
#             max_idx = i
#     print(max_len)
#     print(max_idx)
#     print(word_sequences[max_idx])




import  torch
import  numpy as np
#     pd.DataFrame(word_sequences).fillna(" ").to_csv("word_sequences.csv")
vocab = pd.read_csv("vocab.csv")
onehot =  pd.get_dummies(vocab.iloc[:, 1])

word_sequence = pd.read_csv("word_sequences.csv")
#(13626, 1181, 25022)
t = torch.zeros(64, 1181, 25022)

for i in range(64):
    for j in range(1, len(word_sequence.iloc[i])-1):
        print(word_sequence.iloc[i,j])
        o = np.array( onehot[word_sequence.iloc[i,j]])
        t[i][j] = torch.tensor(o, dtype=torch.float32)

torch.save(t, "word_sequence.pt")

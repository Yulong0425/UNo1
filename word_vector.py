import pandas as pd
import numpy as np
import jieba
import torch
from torch import nn
from torch.functional import F

 
terms = {}

with open("replace.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines:
        terms[line.split()[0]] = line.split()[1]


class CharvecBlock(nn.Module):
    def __init__(self):
        super().__init__()

        self.extending_layer = nn.Linear(32, 1024)
        self.word_vector_layer = nn.RNN(input_size=1024, hidden_size=1024, num_layers=1, batch_first=False)
        self.fc_layer = nn.Linear(512, 512)

    def forward(self, x, hidden_state):
        extended_x = self.extending_layer(x)
        output, hidden_state_out = self.word_vector_layer(extended_x, hidden_state)
        o = self.fc_layer(output)
        return o, hidden_state_out
    
class WordvecBlock(nn.Module):
    def __init__(self, vocab_len):
        super().__init__()

        self.extending_layer = nn.Linear(vocab_len, 1024)
        self.word_vector_layer = nn.RNN(input_size=1024, hidden_size=1024, num_layers=1, batch_first=False)
        self.fc_layer = nn.Linear(1024, vocab_len)

    def forward(self, x, hidden_state):
        extended_x = self.extending_layer(x)
        output, hidden_state_out = self.word_vector_layer(extended_x, hidden_state)
        o = self.fc_layer(output)
        return o, hidden_state_out

class WochavecNN(nn.Module):
    def __init__(self, vocab_len):
        super().__init__()
        
        self.chavec_block = CharvecBlock()
        self.wordvec_block = WordvecBlock(vocab_len)
        self.reverse = nn.Linear(512, vocab_len)

    def forward(self, x):
        o = self.chavec_block(x)
        o = self.wordvec_block(x)
        return o

def train(line, vocab_onehot, model, creiterion, optimizer):    
    for k, v in terms.items():
        line = line.replace(k, v)
    word_seq = jieba.lcut(str(line), cut_all=False)
    print(model.extending_layer.weight)
    model.train()
    # print(word_seq[0])
    for e in range(1000):
        for i in range(len(word_seq) - 5):
            x = np.array(vocab_onehot[[word_seq[i], word_seq[i+1], word_seq[i+3], word_seq[i+4]]])
            x = torch.tensor(x, dtype=torch.float32, requires_grad=True).T
            # print(x.shape)
            y = np.array(vocab_onehot[word_seq[i+2]])
            y = torch.tensor(y, dtype=torch.float32).T
            # print(y.shape)

            init_hidden_state = torch.zeros(1, 4, 1024)

            o, h = model(x.unsqueeze(0), init_hidden_state)
            # print(o.shape)
            # print(o)
            # print(word_seq[i:i+5])
            # o = model(x.unsqueeze(0))
            optimizer.zero_grad()
            loss = creiterion(o[0][-1], y)
            print(loss)
            loss.backward()
            optimizer.step()
    
    print(model.extending_layer.weight)


def predict(line, vocab_onehot, model):
    print(line)
    word_seq = jieba.lcut(str(line), cut_all=False)
    # print(word_seq[0])
    for i in range(len(word_seq) - 5):
        x = np.array(vocab_onehot[word_seq[i:i+5]])
        x = torch.tensor(x, dtype=torch.float32).T
        # print(x.shape)

        init_hidden_state = torch.zeros(1, 5, 1024)

        o, h = model(x.unsqueeze(0), init_hidden_state)
        print(o.shape)
        # print(o)
        # print(word_seq[i:i+5])

def read_vocab():
    vocab = pd.read_csv("vocab.csv")
    onehot =  pd.get_dummies(vocab.iloc[:, 1])
    return onehot

if __name__ == "__main__":
    # read_data()
    vocab_onehot = read_vocab()
    # print(vocab_onehot.shape[1])
    # model = WordvecBlock(vocab_onehot.shape[1]+1)
    # criterion = nn.CrossEntropyLoss()
    # optimizer = torch.optim.Adam(model.parameters(), lr=0.00001)

    word_sequences = []
    with open("corpus.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            # train(line, vocab_onehot, model, criterion, optimizer)
            line = line.split('。')
            for l in line:
                if l != '':
                    word_sequence = jieba.lcut(l, cut_all=False)
                    word_sequences.append(word_sequence)
            # break
        
        max_len = 0
        max_idx = 0
        for i in range(len(word_sequences)):
            if len(word_sequences[i]) > max_len:
                max_len = len(word_sequences[i])
                max_idx = i
        print(max_len)
        print(max_idx)
        print(word_sequences[max_idx])

        pd.DataFrame(word_sequences).replace("\n", np.nan).fillna(" ").to_csv("word_sequences.csv")

    # model = WochavecNN(32)
    # optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    # criterion = nn.CrossEntropyLoss()
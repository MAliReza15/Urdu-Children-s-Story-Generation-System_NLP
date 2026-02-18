from collections import defaultdict
from config import LAMBDA_UNI, LAMBDA_BI, LAMBDA_TRI


class TrigramLanguageModel:

    def __init__(self):
        self.unigram = defaultdict(int)
        self.bigram = defaultdict(int)
        self.trigram = defaultdict(int)
        self.total_tokens = 0

    # -------------------------------------------------------------

    def train(self, corpus):

        for tokens in corpus:
            for i in range(len(tokens)):

                self.unigram[(tokens[i],)] += 1
                self.total_tokens += 1

                if i >= 1:
                    self.bigram[(tokens[i-1], tokens[i])] += 1

                if i >= 2:
                    self.trigram[(tokens[i-2], tokens[i-1], tokens[i])] += 1

    # -------------------------------------------------------------

    def probability(self, w1, w2, w3):

        p1 = self.unigram[(w3,)] / self.total_tokens

        p2 = 0
        if self.unigram[(w2,)] > 0:
            p2 = self.bigram[(w2, w3)] / self.unigram[(w2,)]

        p3 = 0
        if self.bigram[(w1, w2)] > 0:
            p3 = self.trigram[(w1, w2, w3)] / self.bigram[(w1, w2)]

        return (
            LAMBDA_TRI * p3
            + LAMBDA_BI * p2
            + LAMBDA_UNI * p1
        )

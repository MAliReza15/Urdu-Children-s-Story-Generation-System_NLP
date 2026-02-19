from collections import defaultdict


class NGramLanguageModel:

    def __init__(self, n, lambdas):
        """
        n : order of model (3,5,7...)
        lambdas : interpolation weights list
        """

        self.n = n
        self.lambdas = lambdas

        # store counts for all orders
        self.counts = [
            defaultdict(int) for _ in range(n)
        ]

        self.total_tokens = 0

    # -------------------------------------------------------------

    def train(self, corpus):

        for tokens in corpus:

            for i in range(len(tokens)):

                # build all k-grams up to N
                for k in range(1, self.n + 1):

                    if i - k + 1 < 0:
                        continue

                    gram = tuple(tokens[i-k+1:i+1])
                    self.counts[k-1][gram] += 1

                self.total_tokens += 1

    # -------------------------------------------------------------

    def probability(self, context, next_token):
        """
        context = last (n-1) tokens
        """

        probs = []

        # unigram
        unigram_prob = (
            self.counts[0][(next_token,)] /
            self.total_tokens
        )
        probs.append(unigram_prob)

        # higher order ngrams
        for k in range(2, self.n + 1):

            gram = tuple(context[-(k-1):] + [next_token])
            prefix = tuple(context[-(k-1):])

            p = 0
            if self.counts[k-2][prefix] > 0:
                p = self.counts[k-1][gram] / self.counts[k-2][prefix]

            probs.append(p)

        # interpolation
        final_prob = sum(
            l * p for l, p in zip(self.lambdas, probs)
        )

        return final_prob

from collections import defaultdict
import json
import os


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

    def save(self, filepath):
        """Save model to JSON file."""
        model_data = {
            "n": self.n,
            "lambdas": self.lambdas,
            "total_tokens": self.total_tokens,
            "counts": []
        }
        
        # Convert defaultdicts to regular dicts (tuples -> lists for JSON)
        for count_dict in self.counts:
            counts_serialized = {}
            for gram_tuple, count in count_dict.items():
                # Convert tuple to list for JSON serialization
                # Use JSON-compatible key format
                key = json.dumps(list(gram_tuple))
                counts_serialized[key] = count
            model_data["counts"].append(counts_serialized)
        
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------

    @classmethod
    def load(cls, filepath):
        """Load model from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            model_data = json.load(f)
        
        model = cls(model_data["n"], model_data["lambdas"])
        model.total_tokens = model_data["total_tokens"]
        
        # Convert JSON arrays back to tuples for counts
        for i, counts_serialized in enumerate(model_data["counts"]):
            for key_str, count in counts_serialized.items():
                # Convert JSON array string back to tuple
                gram_list = json.loads(key_str)
                gram_tuple = tuple(gram_list)
                model.counts[i][gram_tuple] = count
        
        return model

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

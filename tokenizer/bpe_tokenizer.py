import json

SPECIAL_TOKENS = {"<EOT>", "<EOS>", "<EOP>"}


class BPETokenizer:
    """
    Adapter around Phase-II BPE tokenizer.
    Converts text <-> token IDs.
    """

    def __init__(self, vocab_path, merges_path):

        with open(vocab_path, "r", encoding="utf-8") as f:
            raw_vocab = json.load(f)

        self.id_to_token = {int(k): v for k, v in raw_vocab.items()}
        self.token_to_id = {v: k for k, v in self.id_to_token.items()}

        with open(merges_path, "r", encoding="utf-8") as f:
            self.merges = json.load(f)

        self.eot_id = self.token_to_id["<EOT>"]

    # -------------------------------------------------------------

    def tokenize_text(self, text):
        tokens = []
        i = 0

        while i < len(text):
            matched = False
            for st in SPECIAL_TOKENS:
                if text[i:i+len(st)] == st:
                    tokens.append(st)
                    i += len(st)
                    matched = True
                    break

            if not matched:
                tokens.append(text[i])
                i += 1

        return tokens

    # -------------------------------------------------------------

    def encode(self, text):

        tokens = self.tokenize_text(text)
        token_ids = []
        for t in tokens:
            if t in self.token_to_id:
                token_ids.append(self.token_to_id[t])
            # skip unknown characters not in vocabulary

        for a, b, new_id, _ in self.merges:
            merged = []
            i = 0
            while i < len(token_ids):
                if i < len(token_ids)-1 and token_ids[i]==a and token_ids[i+1]==b:
                    merged.append(new_id)
                    i += 2
                else:
                    merged.append(token_ids[i])
                    i += 1
            token_ids = merged

        return token_ids

    # -------------------------------------------------------------

    def decode(self, ids):
        return "".join(self.id_to_token[i] for i in ids)

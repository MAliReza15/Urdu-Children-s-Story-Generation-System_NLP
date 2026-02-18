from utils.sampling import weighted_sample
from config import MAX_GENERATION_LENGTH


class StoryGenerator:

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.vocab_ids = [int(i) for i in tokenizer.id_to_token.keys()]

    # -------------------------------------------------------------

    def sample_next(self, w1, w2):

        probs = [
            self.model.probability(w1, w2, w3)
            for w3 in self.vocab_ids
        ]

        return weighted_sample(self.vocab_ids, probs)

    # -------------------------------------------------------------

    def generate(self, start_tokens):

        generated = start_tokens[:]

        while len(generated) < MAX_GENERATION_LENGTH:

            w1, w2 = generated[-2], generated[-1]
            nxt = self.sample_next(w1, w2)

            generated.append(nxt)

            if nxt == self.tokenizer.eot_id:
                break

        return self.tokenizer.decode(generated)

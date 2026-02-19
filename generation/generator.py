from utils.sampling import weighted_sample
from config import MAX_GENERATION_LENGTH


class StoryGenerator:

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

        # vocabulary ids available for sampling
        self.vocab_ids = [int(i) for i in tokenizer.id_to_token.keys()]

    # -------------------------------------------------------------

    def sample_next(self, context):
        """
        context = last (n-1) tokens
        """

        probs = [
            self.model.probability(context, w)
            for w in self.vocab_ids
        ]

        return weighted_sample(self.vocab_ids, probs)

    # -------------------------------------------------------------

    def generate(self, start_tokens):

        generated = start_tokens[:]

        required_context = self.model.n - 1

        while len(generated) < MAX_GENERATION_LENGTH:

            # take last (n-1) tokens as context
            context = generated[-required_context:]

            nxt = self.sample_next(context)
            generated.append(nxt)

            # stop when End Of Text generated
            if nxt == self.tokenizer.eot_id:
                break

        return self.tokenizer.decode(generated)

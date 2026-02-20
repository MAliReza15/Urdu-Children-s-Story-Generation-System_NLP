from utils.sampling import weighted_sample_with_temperature
from config import MAX_GENERATION_LENGTH, TEMPERATURE, TOP_K


class StoryGenerator:

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

        # vocabulary ids available for sampling
        self.vocab_ids = [int(i) for i in tokenizer.id_to_token.keys()]

    # -------------------------------------------------------------

    def sample_next(self, context, temperature=None, top_k=None):
        """
        context = last (n-1) tokens
        Uses temperature and top-k sampling
        """
        if temperature is None:
            temperature = TEMPERATURE
        if top_k is None:
            top_k = TOP_K

        probs = [
            self.model.probability(context, w)
            for w in self.vocab_ids
        ]

        return weighted_sample_with_temperature(
            self.vocab_ids, probs, temperature=temperature, top_k=top_k
        )

    # -------------------------------------------------------------

    def generate(self, start_tokens, max_length=None, temperature=None, top_k=None):
        if max_length is None:
            max_length = MAX_GENERATION_LENGTH

        generated = start_tokens[:]
        required_context = self.model.n - 1

        while len(generated) < max_length:

            context = generated[-required_context:]
            nxt = self.sample_next(context, temperature=temperature, top_k=top_k)
            generated.append(nxt)

            if nxt == self.tokenizer.eot_id:
                break

        return self.tokenizer.decode(generated)

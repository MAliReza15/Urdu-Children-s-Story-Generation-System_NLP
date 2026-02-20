from models.ngram_llm import NGramLanguageModel


def get_model(model_name):

    if model_name == "trigram":
        return NGramLanguageModel(
            n=3,
            lambdas=[0.1, 0.3, 0.6]
        )

    elif model_name == "5gram":
        return NGramLanguageModel(
            n=5,
            lambdas=[0.05, 0.1, 0.15, 0.25, 0.45]
        )

    elif model_name == "7gram":
        return NGramLanguageModel(
            n=7,
            lambdas=[0.03,0.05,0.07,0.10,0.15,0.25,0.35]
        )

    else:
        raise ValueError("Unknown model")

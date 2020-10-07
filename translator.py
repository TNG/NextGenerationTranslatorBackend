import torch
import time
import nltk

nltk.download('punkt')


class TranslationError(Exception):
    def __init__(self, message):
        self.message = message


class Translator:
    def __init__(self):
        self._models_loaded = False
        self._model_de_en = None
        self._model_en_de = None

    def initialize_models(self):
        print("Loading de2en model...")
        self._model_de_en = self._initialize_model('transformer.wmt19.de-en')
        print("Loading en2de model...")
        self._model_en_de = self._initialize_model('transformer.wmt19.en-de')

        self._models_loaded = True

        print(self.translate('Das Modell ist nun geladen', 'en'))

    @staticmethod
    def _initialize_model(model_name):
        load_start = time.time()
        model = torch.hub.load('pytorch/fairseq', model_name,
                               checkpoint_file='model1.pt:model2.pt:model3.pt:model4.pt',
                               tokenizer='moses', bpe='fastbpe')
        model.eval()
        load_end = time.time()
        print("Model loaded in {} seconds".format(load_end - load_start))
        if torch.cuda.is_available():
            if torch.cuda.get_device_properties(0).total_memory > 11900000000:
                print("CUDA available and GPU memory appears sufficient - loading de2en model into GPU...")
                model.cuda()
            else:
                print("CUDA available but GPU memory is lower than the recommended 12GB. Running from RAM...")
        else:
            print("CUDA not available, running model from RAM...")

        return model

    def translate(self, text, target_language):
        if not self._models_loaded:
            raise TranslationError("Translation model not yet loaded")

        return self._translate_text(text, target_language)

    def _translate_text(self, text, target_language):
        model = self._model_en_de
        if target_language == 'en':
            model = self._model_de_en
        elif target_language != 'de':
            raise ValueError("Currently, only 'en' and 'de' are supported as language")

        text_list = self._tokenize_and_split_sentences(text)
        text_list_translated = model.translate(text_list)
        text_list_translated = self._fix_empty_lines(text_list, text_list_translated)
        return ' '.join(text_list_translated)[:-1]

    @staticmethod
    def _tokenize_and_split_sentences(unprocessed_string):
        lines = unprocessed_string.split('\n')
        processed_sentences = []
        for line in lines:
            sentences = nltk.tokenize.sent_tokenize(line)
            for sentence in sentences:
                processed_sentences.append(sentence + " ")
            processed_sentences.append("\n")
        return processed_sentences

    @staticmethod
    def _fix_empty_lines(input_string_list, output_string_list):
        for i in range(len(input_string_list)):
            if input_string_list[i] == "\n":
                output_string_list[i] = "\n"
        return output_string_list

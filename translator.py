import torch
import time
import nltk

nltk.download('punkt')


class TranslationError(Exception):
    def __init__(self, message):
        self.message = message


class Translator:
    def __init__(self):
        self._model_loaded = False
        self._model = None

    def initialize_model(self):
        print("Loading de2en model...")
        load_start = time.time()
        self._model = torch.hub.load('pytorch/fairseq', 'transformer.wmt19.de-en',
                                     checkpoint_file='model1.pt:model2.pt:model3.pt:model4.pt',
                                     tokenizer='moses', bpe='fastbpe')
        self._model.eval()
        load_end = time.time()
        print("Model loaded in {} seconds".format(load_end - load_start))
        if torch.cuda.is_available():
            if torch.cuda.get_device_properties(0).total_memory > 11900000000:
                print("CUDA available and GPU memory appears sufficient - loading de2en model into GPU...")
                self._model.cuda()
            else:
                print("CUDA available but GPU memory is lower than the recommended 12GB. Running from RAM...")
        else:
            print("CUDA not available, running model from RAM...")

        self._model_loaded = True

        print(self.translate("Das Modell ist nun geladen"))

    def translate(self, text_de):
        if not self._model_loaded:
            raise TranslationError("Translation model not yet loaded")

        return self._translate_text(text_de)

    def _translate_text(self, text_de):
        text_list_de = self._tokenize_and_split_sentences(text_de)
        text_list_en = self._model.translate(text_list_de)
        text_list_en = self._fix_empty_lines(text_list_de, text_list_en)
        return ''.join(text_list_en)[:-1]

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

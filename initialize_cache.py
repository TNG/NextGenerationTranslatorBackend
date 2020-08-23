import torch
import os

torch.hub.set_dir(f"{os.path.dirname(os.path.realpath(__file__))}/cache")
de2en = torch.hub.load('pytorch/fairseq', 'transformer.wmt19.de-en',
                       checkpoint_file='model1.pt:model2.pt:model3.pt:model4.pt',
                       tokenizer='moses', bpe='fastbpe')
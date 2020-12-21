import torch

print(1)
de2en = torch.hub.load('pytorch/fairseq', 'transformer.wmt19.de-en', checkpoint_file='model1.pt:model2.pt:model3.pt:model4.pt',
                       tokenizer='moses', bpe='fastbpe')
print(2)
foo = de2en.translate("Was für eine scheiß Bibliothek!")
print(3)
print(foo)

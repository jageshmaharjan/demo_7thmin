import argparse
import numpy as np
import json

import torch
from transformers import BertTokenizer, BertForTokenClassification


def inference(args):
    PRE_TRAINED_MODEL = 'bert-base-uncased'

    with open(args.tag2idx, 'r') as f:
        tag2idx = json.load(f)

    with open(args.tag_values, 'r') as f:
        f_read = f.readlines()

    tag_values = []
    for val in f_read:
        tag_values.append(val.strip())

    tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL, do_lower_case=True)

    model = BertForTokenClassification.from_pretrained(PRE_TRAINED_MODEL, num_labels=len(tag2idx),
                                                       output_attentions=False,
                                                       output_hidden_states=False)

#    model.load_state_dict(torch.load('/home/ubuntu/7thmin/webservice/assets/polaris_ER_model1611354861.0663054.bin',
    model.load_state_dict(torch.load(args.er_model,
                                     map_location=torch.device("cpu")))

    model = model.eval()

    test_sent = args.sentence
    #test_sent = "President Biden will be inagurating this noon in Pensylvenia avenue, WA at Capitol Hill"
    tokenized_sent = tokenizer.encode(test_sent)
    input_ids = torch.tensor([tokenized_sent])

    with torch.no_grad():
        output = model(input_ids)

    label_indices = np.argmax(output[0].to('cpu').numpy(), axis=2)
    tokens = tokenizer.convert_ids_to_tokens(input_ids.to('cpu').numpy()[0])
    new_tokens, new_labels = [], []

    for token, label_idx in zip(tokens, label_indices[0]):
        if token.startswith("##"):
            new_tokens[-1] = new_tokens[-1] + token[2:]
        else:
            new_labels.append(tag_values[label_idx])
            new_tokens.append(token)

    for token, lable in zip(new_tokens, new_labels):
        print("{}\t{}".format(token, lable))


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Argument for entity.txt recognition inference")
    parser.add_argument("--tag2idx", type=str, help="path of tag to id files")
    parser.add_argument("--tag_values", type=str, help="path to tag values files")
    parser.add_argument("--er_model", type=str, help="path to entity.txt recognition (er) model")
    parser.add_argument('--sentence', type=str, help="input sentence")
    args = parser.parse_args()
    inference(args)

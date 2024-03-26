import torch
import pandas as pd
from tqdm.auto import tqdm
from datasets import Dataset
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments


df = pd.read_csv('test.csv')

label_map = {'POSITIVE': 2, 'NEUTRAL': 1, 'NEGATIVE': 0}
df['label'] = df['label'].map(label_map)

dataset = Dataset.from_pandas(df)


model = BertForSequenceClassification.from_pretrained("blanchefort/rubert-base-cased-sentiment", num_labels=3)
tokenizer = BertTokenizer.from_pretrained("blanchefort/rubert-base-cased-sentiment")


def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True)


def preprocess_dataset(ds):
    ds = ds.map(tokenize_function, batched=True)
    ds.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])
    return ds

def preprocess_function(examples):
    encoded = tokenizer(examples['text'], truncation=True, padding='max_length', max_length=128)
    return encoded


dataset = dataset.map(lambda examples: {'labels': examples['label']}, batched=True)

dataset = dataset.map(preprocess_function, batched=True)

dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

tokenized_dataset = preprocess_dataset(dataset)

training_args = TrainingArguments(
    output_dir='./results_fine_tuning',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs_fine_tuning',
    overwrite_output_dir=True
)


from torch.nn.utils.rnn import pad_sequence


def data_collator(features):
    input_ids = [feature['input_ids'] for feature in features]
    attention_masks = [feature['attention_mask'] for feature in features]
    labels = [feature['labels'] for feature in features]

    padded_input_ids = pad_sequence(input_ids, batch_first=True, padding_value=tokenizer.pad_token_id)
    padded_attention_masks = pad_sequence(attention_masks, batch_first=True, padding_value=0)

    return {
        'input_ids': padded_input_ids,
        'attention_mask': padded_attention_masks,
        'labels': torch.tensor(labels)
    }


trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=tokenized_dataset
)

trainer.train()

save_directory = './fine_tuned_model'
model.save_pretrained(save_directory)
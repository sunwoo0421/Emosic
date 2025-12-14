import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

KOTE_LABELS = [
    "불평", "환영", "감동", "지긋지긋", "고마움", "슬픔",
    "화남", "존경", "기대감", "우쭐댐", "안타까움", "비장함",
    "의심", "뿌듯함", "편안", "신기함", "아껴주는", "부끄러움",
    "공포", "절망", "한심함", "역겨움", "짜증", "어이없음",
    "없음", "패배", "귀찮음", "힘듦", "즐거움", "깨달음",
    "죄책감", "증오", "흐뭇함", "당황", "경악", "부담",
    "서러움", "재미없음", "불쌍함", "놀람", "행복", "불안", "기쁨", "안심"
]

MODEL_NAME = "tobykim/koelectra-44emotions"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
device = 0 if torch.cuda.is_available() else -1
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=device, return_all_scores=True)

THRESHOLD = 0.6

def predict_emotions(texts):
    results = classifier(texts)
    final_labels = []
    for res in results:
        labels = [r['label'] for r in res if r['score'] > THRESHOLD]
        if not labels:
            labels = [max(res, key=lambda x: x['score'])['label']]
        mapped_labels = [KOTE_LABELS[int(l.replace("LABEL_", ""))] for l in labels]
        final_labels.append(mapped_labels)
    return final_labels

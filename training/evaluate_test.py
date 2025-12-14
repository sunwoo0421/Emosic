# training/evaluate_test.py
import torch
from transformers import ElectraForSequenceClassification, ElectraTokenizerFast, Trainer, TrainingArguments
from datasets import DatasetDict
from dataset_loader import load_and_preprocess
import evaluate

def main():
    
    # ✅ 로컬 KOTE 데이터셋 불러오기
    dataset = load_and_preprocess("./data")  # ./data/train.tsv, val.tsv, test.tsv 필요
    test_dataset = dataset["test"]

   

    # ✅ 토크나이저와 모델 로드
    model_path = "./outputs/checkpoint-7500"
    tokenizer = ElectraTokenizerFast.from_pretrained(model_path)
    model = ElectraForSequenceClassification.from_pretrained(
        "outputs/checkpoint-7500",  # 체크포인트 경로
        num_labels=43,               # 데이터셋 라벨 수에 맞춤
        ignore_mismatched_sizes=True # mismatch 시 마지막 레이어만 새로 초기화
    )

    # ✅ 데이터셋 토크나이징
    def tokenize(batch):
        return tokenizer(batch["text"], padding="max_length", truncation=True, max_length=64)

    tokenized_test = test_dataset.map(tokenize, batched=True)

    # ✅ Metric 준비
    metric_accuracy = evaluate.load("accuracy")
    metric_f1 = evaluate.load("f1")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = logits.argmax(axis=-1)
        acc = metric_accuracy.compute(predictions=predictions, references=labels)
        f1 = metric_f1.compute(predictions=predictions, references=labels, average="weighted")
        return {"accuracy": acc["accuracy"], "f1": f1["f1"]}

    # ✅ Trainer 설정
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    # ✅ 평가 수행
    results = trainer.evaluate(tokenized_test)

    # 결과 출력
    print("Evaluation results:")
    print(f"Accuracy: {results['eval_accuracy']:.4f}")
    print(f"F1 score: {results['eval_f1']:.4f}")

if __name__ == "__main__":
    main()

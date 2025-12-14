# training/train.py
import os
import numpy as np
from sklearn.metrics import accuracy_score

# dataset_loader import: 루트에서 직접 실행하거나 -m training.train 로 실행할 수 있게 안전하게 처리
try:
    from training.dataset_loader import load_and_preprocess
except Exception:
    from dataset_loader import load_and_preprocess

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)
import torch

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": accuracy_score(labels, preds)}

def main():
    print("🚀 Starting training process...")

    # 1) 데이터 로드 (dataset_loader.py가 DatasetDict 반환해야 함)
    dataset = load_and_preprocess(data_dir="./data")
    print("✅ Dataset loaded. Splits:", list(dataset.keys()))

    # 2) 모델/토크나이저 설정 — 속도 최적화 권장값 적용
    # 바꿀 모델을 원하면 아래 model_name 변수만 수정
    model_name = "monologg/koelectra-small-v3-discriminator"  # <-- 더 빠른 small 모델 권장
    num_labels = 44  # KOTE 라벨 수 (단일-label로 학습 중)
    print(f"🚀 Loading tokenizer & model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)

    # 3) 토큰화: max_length를 줄여서 속도 향상 (권장: 64)
    max_length = 64
    def tokenize_fn(batch):
        # batching시 tokenizer가 리스트/문자열 처리하도록 padding/truncation 보장
        return tokenizer(batch["text"], padding="max_length", truncation=True, max_length=max_length)

    print("🚀 Tokenizing dataset (max_length=%d)..." % max_length)
    tokenized = dataset.map(tokenize_fn, batched=True)

    # 4) Trainer 인자 — 속도/메모리 최적화 옵션
    # GPU가 있는 경우 fp16을 켭니다. (없으면 무시)
    has_cuda = torch.cuda.is_available()
    print("GPU available:", has_cuda)

    # 기본 설정값 — 필요하면 변경
    per_device_train_batch_size = 16   # GPU 메모리 여유 없으면 8로 낮추고 gradient_accumulation_steps 늘리기
    per_device_eval_batch_size = 32
    gradient_accumulation_steps = 1    # effective batch = per_device_train_batch_size * gradient_accumulation_steps

    # TrainingArguments: evaluation/save를 epoch 단위로 하여 오버헤드 감소
    training_args = TrainingArguments(
        output_dir="./outputs",
        overwrite_output_dir=False,
        do_train=True,
        do_eval=True,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        learning_rate=2e-5,
    )
    # 5) Trainer 초기화
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized.get("validation"),
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    # 6) (선택) 체크포인트/모델 저장 디렉토리 권한/생성 확인
    os.makedirs(training_args.output_dir, exist_ok=True)

    # 7) 학습 시작
    print("🚀 Training start...")
    trainer.train()
    print("✅ Training finished")

    

if __name__ == "__main__":
    main()

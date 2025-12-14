# training/dataset_loader.py
import csv
from datasets import Dataset, DatasetDict

def load_and_preprocess(data_dir="./data"):
    """
    로컬 tsv 파일에서 KOTE 데이터셋 불러와서 Hugging Face DatasetDict 형태로 반환
    """
    print("🚀 Loading KOTE dataset...")

    splits = ["train", "val", "test"]
    dataset_dict = {}

    for split in splits:
        filepath = f"{data_dir}/{split}.tsv"

        examples = {"ID": [], "text": [], "labels": []}
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t", fieldnames=["ID", "text", "labels"])
            for row in reader:
                examples["ID"].append(row["ID"])
                examples["text"].append(row["text"])
                label = int(row["labels"].split(",")[0])
                examples["labels"].append(label)

        dataset_dict[split] = Dataset.from_dict(examples)

    return DatasetDict({
        "train": dataset_dict["train"],
        "validation": dataset_dict["val"],
        "test": dataset_dict["test"]
    })


def load_test_only(filepath="test.tsv"):
    """
    test.tsv만 불러와 Dataset으로 반환
    """
    print("📂 Loading local test dataset...")
    examples = {"ID": [], "text": [], "labels": []}

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t", fieldnames=["ID", "text", "labels"])
        for row in reader:
            examples["ID"].append(row["ID"])
            examples["text"].append(row["text"])
            examples["labels"].append(int(row["labels"].split(",")[0]))

    return Dataset.from_dict(examples)

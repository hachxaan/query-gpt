# import openai
from openai import API
from pathlib import Path

class CodeGPTTrainer:

    def __init__(self, api_key, dataset_path):
        self.api = API(api_key=api_key)
        self.dataset_path = Path(dataset_path)

    def _read_dataset(self):
        dataset = []
        for path in self.dataset_path.glob("*.py"):
            with open(path, "r") as f:
                code = f.read()
                dataset.append(code)
        return dataset

    def _train(self, dataset, iterations):
        for _ in range(iterations):
            self.api.create_training_dataset(dataset)
            self.api.train_model(
                "code_gpt",
                prompt="",
                max_tokens=1024,
                batch_size=128,
                epochs=1,
            )

    def train(self, iterations):
        dataset = self._read_dataset()
        self._train(dataset, iterations)



if __name__ == "__main__":
    trainer = CodeGPTTrainer(
        api_key="",
        dataset_path="relative_file_paths",
    )
    trainer.train(iterations=10)    
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class LLM:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "microsoft/Phi-3-mini-4k-instruct",
            token=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            "microsoft/Phi-3-mini-4k-instruct",
            torch_dtype=torch.float16,
            device_map="auto",
            token=True
        )

    def generate(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        output = self.model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=0.2
        )

        return self.tokenizer.decode(output[0], skip_special_tokens=True)
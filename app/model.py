import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class ComplianceLLM:
    def __init__(self, model_id: str, hf_token: str | None = None):
        self.model_id = model_id
        token = hf_token or None
        self.use_cuda = torch.cuda.is_available()

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            token=token,
            trust_remote_code=True,
        )

        model_kwargs = {
            "token": token,
            "trust_remote_code": True,
        }

        if self.use_cuda:
            model_kwargs["torch_dtype"] = torch.float16
            model_kwargs["device_map"] = "auto"

        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            **model_kwargs,
        )

        if not self.use_cuda:
            self.model.to("cpu")

    def generate(self, prompt: str, max_new_tokens: int = 220) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt")

        if self.use_cuda:
            inputs = {key: value.to(self.model.device) for key, value in inputs.items()}

        output_ids = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=0.0,
        )

        prompt_tokens = inputs["input_ids"].shape[1]
        generated_tokens = output_ids[0][prompt_tokens:]
        return self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
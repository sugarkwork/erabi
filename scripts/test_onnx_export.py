import torch
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

engine = GLiClassEngine("release/rc1/model", device="cpu")
model = engine.pipe.pipe.model
model.eval()

req = ChoiceRequest.from_dict({
    "context": "物流拠点SEALED：製品の保管在庫数はちょうど110個です。",
    "question": "数量が110を下回らない場合は出荷する、欠落していれば保留するを適用してください。",
    "choices": [{"id": "ship", "text": "出荷する"}, {"id": "hold", "text": "保留する"}]
})

inner_pipe = engine.pipe.pipe
labels = [c.text for c in req.choices]
inputs = inner_pipe.prepare_inputs([req.context], [labels], same_labels=False, prompt=[req.question])
max_num_classes = inner_pipe._resolve_max_num_classes([labels], same_labels=False)

print("Inputs:", {k: v.shape for k, v in inputs.items()})
print("max_num_classes:", max_num_classes)

with torch.no_grad():
    pt_out = model(**inputs, max_num_classes=max_num_classes)
    print("PyTorch logits:", pt_out.logits)

# Let's inspect wrapper for ONNX export
class GLiClassONNXWrapper(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask):
        # In GLiClass, the prompt, context and labels are encoded into input_ids and attention_mask
        # Labels are demarcated by special tokens
        # We can pass input_ids and attention_mask directly
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        return outputs.logits

wrapper = GLiClassONNXWrapper(model)
wrapper.eval()
with torch.no_grad():
    wrap_out = wrapper(inputs["input_ids"], inputs["attention_mask"])
    print("Wrapper logits:", wrap_out)
    print("Difference:", torch.max(torch.abs(pt_out.logits - wrap_out)).item())

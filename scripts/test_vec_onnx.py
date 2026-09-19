import onnx
import onnxruntime as ort
import torch
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

engine = GLiClassEngine("release/rc1/model", device="cpu")
inner_model = engine.pipe.pipe.model.model
model = engine.pipe.pipe.model
model.eval()

# Patch _create_segment_ids on inner_model with fully vectorized version
def vectorized_create_segment_ids(self, input_ids):
    seq_length = input_ids.shape[-1]
    seq_idx = torch.arange(seq_length, device=input_ids.device).unsqueeze(0)
    text_token_mask = input_ids == self.config.text_token_index
    text_token_indices = text_token_mask.int().argmax(dim=-1, keepdim=True)
    example_token_mask = input_ids == self.config.example_token_index
    example_token_indices = example_token_mask.int().argmax(dim=-1, keepdim=True)
    has_example = example_token_mask.any(dim=-1, keepdim=True)
    segment_ids = (seq_idx >= text_token_indices).long()
    example_mask = has_example & (seq_idx >= example_token_indices)
    segment_ids = torch.where(example_mask, torch.tensor(2, device=input_ids.device), segment_ids)
    return segment_ids

type(inner_model)._create_segment_ids = vectorized_create_segment_ids

class ExportWrapper(torch.nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m

    def forward(self, input_ids, attention_mask):
        return self.m(input_ids=input_ids, attention_mask=attention_mask).logits

wrapper = ExportWrapper(model)
wrapper.eval()

# Dummy input for tracing
dummy_ids = torch.ones((1, 32), dtype=torch.long)
# Put special tokens so that masks are valid
dummy_ids[0, 5] = inner_model.config.text_token_index
dummy_ids[0, 1] = inner_model.config.class_token_index
dummy_ids[0, 3] = inner_model.config.class_token_index
dummy_mask = torch.ones((1, 32), dtype=torch.long)

print("Exporting to scratch_vec.onnx...")
torch.onnx.export(
    wrapper,
    (dummy_ids, dummy_mask),
    "scratch_vec.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["logits"],
    dynamic_axes={
        "input_ids": {0: "batch_size", 1: "sequence_length"},
        "attention_mask": {0: "batch_size", 1: "sequence_length"},
        "logits": {0: "batch_size", 1: "num_classes"},
    },
    opset_version=17,
)
print("Export complete. Loading into ONNX Runtime...")
sess = ort.InferenceSession("scratch_vec.onnx", providers=["CPUExecutionProvider"])

test_cases = [
    ("短文脈", "質問A", [{"id": "c1", "text": "選択肢1"}, {"id": "c2", "text": "選択肢2"}]),
    ("長めの文脈です。工場のセンサーの振動値が正常値の範囲内であるかテストしています。", "正常か異常か判定してください。", [{"id": "ok", "text": "正常"}, {"id": "ng", "text": "異常"}, {"id": "hold", "text": "再確認"}]),
    ("サーバー負荷監視：CPU 95% メモリ 80%", "対応方針を決定してください", [{"id": "a", "text": "スケールアップ"}, {"id": "b", "text": "隔離"}, {"id": "c", "text": "再起動"}, {"id": "d", "text": "静観"}]),
    # Sealed test case
    ("物流拠点SEALED：製品『SEALED-ITEM-001』の保管在庫数はちょうど110個です。出荷検査証を受領済みです。",
     "数量が110を下回らない（110を含む）場合は出荷する、欠落していれば保留するを適用してください。",
     [{"id": "ship", "text": "出荷する"}, {"id": "hold", "text": "保留する"}]),
]

for ctx, q, choices in test_cases:
    req = ChoiceRequest.from_dict({"context": ctx, "question": q, "choices": choices})
    labels = [c["text"] for c in choices]
    inputs = engine.pipe.pipe.prepare_inputs([req.context], [labels], same_labels=False, prompt=[req.question])
    max_num_classes = len(choices)

    with torch.no_grad():
        pt_out = model(**inputs, max_num_classes=max_num_classes).logits[0, :len(choices)]

    ort_inputs = {
        "input_ids": inputs["input_ids"].numpy(),
        "attention_mask": inputs["attention_mask"].numpy(),
    }
    ort_out = sess.run(None, ort_inputs)[0][0, :len(choices)]

    diff = torch.max(torch.abs(pt_out - torch.from_numpy(ort_out))).item()
    seq_len = inputs["input_ids"].shape[1]
    print(f"Choices={len(choices)}, seq_len={seq_len}: max_abs_diff={diff:.6e}, PT={pt_out.tolist()}, ORT={ort_out.tolist()}")

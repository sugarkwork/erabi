import onnxruntime as ort
import torch
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

engine = GLiClassEngine('release/rc1/model', device='cpu')
model = engine.pipe.pipe.model
model.eval()

sess = ort.InferenceSession('scratch_test.onnx', providers=['CPUExecutionProvider'])

test_cases = [
    ('短文脈', '質問A', [{'id': 'c1', 'text': '選択肢1'}, {'id': 'c2', 'text': '選択肢2'}]),
    ('長めの文脈です。工場のセンサーの振動値が正常値の範囲内であるかテストしています。', '正常か異常か判定してください。', [{'id': 'ok', 'text': '正常'}, {'id': 'ng', 'text': '異常'}, {'id': 'hold', 'text': '再確認'}]),
    ('サーバー負荷監視：CPU 95% メモリ 80%', '対応方針を決定してください', [{'id': 'a', 'text': 'スケールアップ'}, {'id': 'b', 'text': '隔離'}, {'id': 'c', 'text': '再起動'}, {'id': 'd', 'text': '静観'}]),
]

for ctx, q, choices in test_cases:
    req = ChoiceRequest.from_dict({'context': ctx, 'question': q, 'choices': choices})
    labels = [c['text'] for c in choices]
    inputs = engine.pipe.pipe.prepare_inputs([req.context], [labels], same_labels=False, prompt=[req.question])
    max_num_classes = len(choices)

    with torch.no_grad():
        pt_out = model(**inputs, max_num_classes=max_num_classes).logits[0, :len(choices)]

    ort_inputs = {
        'input_ids': inputs['input_ids'].numpy(),
        'attention_mask': inputs['attention_mask'].numpy(),
    }
    ort_out = sess.run(None, ort_inputs)[0][0, :len(choices)]

    diff = torch.max(torch.abs(pt_out - torch.from_numpy(ort_out))).item()
    seq_len = inputs['input_ids'].shape[1]
    print(f"Test case (choices={len(choices)}, seq_len={seq_len}): max_diff = {diff:.6e}, pt={pt_out.tolist()}, ort={ort_out.tolist()}")

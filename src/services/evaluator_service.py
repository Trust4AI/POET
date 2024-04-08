from datetime import datetime
from core.schemas import schemas


def evaluate_input(inputs, llm):
    csv = []
    results = []

    if type(inputs) != list:
        prompt = inputs.query
        generated, time = llm.generate(prompt)
        generated = generated.replace(prompt, "")
        generated = generated.replace("\n", "")
        generated = generated.replace("<bos>", "")
        generated = generated.replace("<eos>", "").strip()
        evaluation_result = _evaluate_input(inputs.expected_result, generated)
        result = schemas.TestResult(input=prompt, output=generated, evaluation_result=evaluation_result, evaluation_type=inputs.type)
        results.append(result)
        return results

    for input in inputs:
        prompt = input.text
        generated, time = llm.generate(prompt)
        generated = generated.replace(prompt, "")
        generated = generated.replace("\n", "")
        generated = generated.replace("<bos>", "")
        generated = generated.replace("<eos>", "").strip()
        evaluation_result = _evaluate_input(input.expected_result, generated)
        csv.append({"prompt": prompt, "expected_result": input.expected_result, "generated_result": generated,
                    "evaluation": evaluation_result, time: time})
        result = schemas.TestResult(input=prompt, output=generated, evaluation_result=evaluation_result, evaluation_type=input.type)
        results.append(result)

    # _write_csv(csv)
    return results


def _write_csv(csv):
    file_name = f"evaluation_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    headers = ["prompt", "expected_result", "generated_result", "evaluation", "time"]
    with open(f'../results/{file_name}', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=csv[0].keys())
        writer.writeheader(headers)
        writer.writerows(csv)


def _evaluate_input(expected_result, generated_result):
    if expected_result.lower() in generated_result.lower():
        return "pass"
    elif 'yes' in expected_result.lower() or 'no' in generated_result.lower() :
        return "fail"
    else:
        return "pass"

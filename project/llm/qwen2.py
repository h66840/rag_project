import requests

def call_vllm_model(prompt, model_url="http://192.168.9.248:8000/v1/chat/completions", max_tokens=1024):
    """
    调用本地使用 vLLM 部署的模型。

    参数:
    prompt (str): 输入的提示文本。
    model_url (str): 模型的 API 地址，默认为 http://localhost:8000/generate。
    max_tokens (int): 生成的最大令牌数，默认为 128。

    返回:
    str: 模型生成的文本。
    """
    # 构建请求数据
    data = {
        
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的金融分析师，擅长分析股票、债券、外汇等金融市场。",
                    "name": "system"
                },
                {
                    "role": "user",
                    "content": prompt,
                    "name": "user"
                }
            ]
    }
    try:
        # 发送 POST 请求
        response = requests.post(model_url, json=data)
        print(response)
        # 检查响应状态码
        response.raise_for_status()
        # 解析响应数据
        result = response.json()
        # 提取生成的文本
        generated_text = result["text"][0]
        return generated_text
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return None
    except KeyError:
        print("响应数据格式错误，无法提取生成的文本。")
        return None

# 示例调用
if __name__ == "__main__":
    prompt = "介绍一下同比和环比。"
    output = call_vllm_model(prompt)
    if output:
        print(output)
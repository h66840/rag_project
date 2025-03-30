from openai import OpenAI

client = OpenAI(
    base_url='https://api-inference.modelscope.cn/v1/',
    api_key='cc1666b3-de45-4936-9fc4-97b43b0fc993', # ModelScope Token
)

response = client.chat.completions.create(
    model='Qwen/Qwen2.5-7B-Instruct', # ModelScope Model-Id
    messages=[
        {
            'role': 'system',
            'content': """你是财务分析领域的专家，你擅长分析财务指标计算任务，每当你遇到财务指标计算问题，你会进行思考：
            **推导过程：**
1. **理解变量定义**：
   - 识别输入数据中的变量及其含义：
2. **数据完整性检查**：
   - 确认输入数据是否包含关键字段：

3. **分步计算**：
   - 按照计算步骤进行计算：
4. **合理性验证**：
   - 检查计算结果是否符合预期：，你的回答必须包含上述思考过程，并且回答要简洁，不要包含无关信息。
"""
            
        },
        {
            'role': 'user',
            'content': '根据以下数据计算销售利润率：资产期初余额5000万元，期末总资产6500万元'
        }
    ],
    stream=True,
    temperature=0
)

for chunk in response:
    print(chunk.choices[0].delta.content, end='', flush=True)
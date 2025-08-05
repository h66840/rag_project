"""
Tests for RAG Enhancement Module
RAG增强模块的测试文件
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.rag_enhancer import RAGEnhancer

class TestRAGEnhancer:
    """RAG增强器测试类"""
    
    @pytest.fixture
    def config(self):
        """测试配置"""
        return {
            "similarity_threshold": 0.2,
            "max_results": 5
        }
    
    @pytest.fixture
    def enhancer(self, config):
        """RAG增强器实例"""
        return RAGEnhancer(config)
    
    @pytest.fixture
    def sample_context(self):
        """示例上下文数据"""
        return [
            "机器学习是人工智能的一个分支",
            "深度学习是机器学习的子集",
            "自然语言处理使用机器学习技术",
            "计算机视觉也依赖机器学习算法",
            "数据科学包含统计学和机器学习"
        ]
    
    @pytest.mark.asyncio
    async def test_enhance_retrieval_success(self, enhancer, sample_context):
        """测试成功的检索增强"""
        query = "什么是机器学习"
        
        result = await enhancer.enhance_retrieval(query, sample_context)
        
        assert "query" in result
        assert "results" in result
        assert "timestamp" in result
        assert "confidence" in result
        assert result["query"] == "什么是机器学习"
        assert isinstance(result["results"], list)
        assert isinstance(result["confidence"], float)
    
    @pytest.mark.asyncio
    async def test_preprocess_query(self, enhancer):
        """测试查询预处理"""
        query = "  什么是机器学习？  "
        processed = await enhancer._preprocess_query(query)
        
        assert processed == "什么是机器学习？"
        assert processed.strip() == processed
    
    @pytest.mark.asyncio
    async def test_enhance_context(self, enhancer, sample_context):
        """测试上下文增强"""
        enhanced = await enhancer._enhance_context(sample_context)
        
        assert len(enhanced) == len(sample_context)
        for i, ctx in enumerate(enhanced):
            assert ctx["id"] == i
            assert ctx["content"] == sample_context[i]
            assert "metadata" in ctx
            assert "length" in ctx["metadata"]
            assert "processed_at" in ctx["metadata"]
    
    @pytest.mark.asyncio
    async def test_calculate_similarity(self, enhancer):
        """测试相似度计算"""
        query = "机器学习"
        context = [
            {"content": "机器学习是人工智能的分支"},
            {"content": "深度学习是机器学习的子集"},
            {"content": "这是一个无关的文本"}
        ]
        
        scores = await enhancer._calculate_similarity(query, context)
        
        assert len(scores) == len(context)
        assert all(isinstance(score, float) for score in scores)
        assert all(0 <= score <= 1 for score in scores)
        # 第一个和第二个应该有更高的相似度分数
        assert scores[0] > scores[2]
        assert scores[1] > scores[2]
    
    @pytest.mark.asyncio
    async def test_filter_and_rank(self, enhancer):
        """测试过滤和排序"""
        context = [
            {"id": 0, "content": "低相关性内容"},
            {"id": 1, "content": "高相关性内容"},
            {"id": 2, "content": "中等相关性内容"}
        ]
        scores = [0.1, 0.8, 0.5]  # 对应的相似度分数
        
        filtered = await enhancer._filter_and_rank(context, scores)
        
        # 应该按分数降序排列
        assert len(filtered) >= 1  # 至少有一个结果通过阈值
        if len(filtered) > 1:
            # 检查排序是否正确（通过ID来验证）
            assert filtered[0]["id"] == 1  # 最高分的应该排在第一
    
    def test_calculate_confidence(self, enhancer):
        """测试置信度计算"""
        scores = [0.8, 0.6, 0.4, 0.2]
        confidence = enhancer._calculate_confidence(scores)
        
        expected = sum(scores) / len(scores)
        assert confidence == expected
        
        # 测试空列表
        empty_confidence = enhancer._calculate_confidence([])
        assert empty_confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_enhance_retrieval_with_exception(self, enhancer):
        """测试异常处理"""
        with patch.object(enhancer, '_preprocess_query', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                await enhancer.enhance_retrieval("test query", ["context"])
    
    @pytest.mark.asyncio
    async def test_empty_context(self, enhancer):
        """测试空上下文"""
        query = "测试查询"
        context = []
        
        result = await enhancer.enhance_retrieval(query, context)
        
        assert result["results"] == []
        assert result["confidence"] == 0.0
    
    @pytest.mark.asyncio
    async def test_config_parameters(self):
        """测试配置参数"""
        config = {
            "similarity_threshold": 0.5,
            "max_results": 3
        }
        enhancer = RAGEnhancer(config)
        
        context = [
            {"id": i, "content": f"content {i}"} 
            for i in range(5)
        ]
        scores = [0.9, 0.7, 0.6, 0.4, 0.3]  # 5个分数
        
        filtered = await enhancer._filter_and_rank(context, scores)
        
        # 应该只返回分数 >= 0.5 的结果，且最多3个
        assert len(filtered) <= 3
        for item in filtered:
            # 通过ID找到对应的分数
            score = scores[item["id"]]
            assert score >= 0.5

# 集成测试
@pytest.mark.asyncio
async def test_full_workflow():
    """测试完整工作流程"""
    config = {
        "similarity_threshold": 0.1,
        "max_results": 10
    }
    
    enhancer = RAGEnhancer(config)
    
    query = "机器学习算法"
    context = [
        "机器学习是人工智能的重要分支",
        "深度学习算法在图像识别中表现出色",
        "监督学习需要标注数据",
        "无监督学习可以发现数据中的隐藏模式",
        "强化学习通过试错来学习最优策略"
    ]
    
    result = await enhancer.enhance_retrieval(query, context)
    
    # 验证结果结构
    assert all(key in result for key in ["query", "results", "timestamp", "confidence"])
    
    # 验证结果内容
    assert len(result["results"]) <= len(context)
    assert 0 <= result["confidence"] <= 1
    
    print(f"Test completed successfully. Results: {len(result['results'])} items, confidence: {result['confidence']:.3f}")

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
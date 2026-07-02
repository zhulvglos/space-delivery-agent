"""RAG 知识库模块"""
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """瑞泽·海项目复盘与卡素产品知识库类"""

    def __init__(self):
        self.embeddings = self._create_embeddings()
        self._vectorstore = None

    def _create_embeddings(self):
        api_key = (settings.OPENAI_API_KEY or settings.DEEPSEEK_API_KEY or settings.QWEN_API_KEY)
        base_url = None
        if settings.LLM_PROVIDER == "deepseek":
            base_url = settings.DEEPSEEK_BASE_URL
        elif settings.LLM_PROVIDER == "qwen":
            base_url = settings.QWEN_BASE_URL
        return OpenAIEmbeddings(model=settings.EMBEDDING_MODEL, api_key=api_key, base_url=base_url)

    @property
    def vectorstore(self):
        if self._vectorstore is None:
            self._vectorstore = Chroma(collection_name="knowledge_base",
                                       embedding_function=self.embeddings,
                                       persist_directory=settings.VECTOR_STORE_PATH)
        return self._vectorstore

    async def query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.vectorstore.similarity_search_with_score(query=query, k=top_k)
            return [{"content": doc.page_content[:500], "source": doc.metadata.get("source", ""),
                     "category": doc.metadata.get("category", ""), "score": 1 - score}
                    for doc, score in results]
        except Exception as e:
            logger.error(f"RAG 查询失败: {e}")
            return []

    async def get_decoration_knowledge(self, topic: str) -> str:
        results = await self.query(f"瑞泽海度假民宿 卡素产品 空间配置 {topic}", top_k=3)
        if not results:
            return f"暂无关于「{topic}」的案例复盘知识。"
        response = f"**关于「{topic}」的案例复盘知识：**\n\n"
        for i, r in enumerate(results, 1):
            response += f"{i}. {r['content']}\n"
        return response

    async def get_moving_knowledge(self, topic: str) -> str:
        results = await self.query(f"瑞泽海度假民宿 装配式交付 {topic}", top_k=3)
        if not results:
            return f"暂无关于「{topic}」的交付知识。"
        response = f"**关于「{topic}」的交付知识：**\n\n"
        for i, r in enumerate(results, 1):
            response += f"{i}. {r['content']}\n"
        return response

    async def add_knowledge(self, content: str, category: str, source: str = "") -> int:
        doc = Document(page_content=content, metadata={"category": category, "source": source})
        self.vectorstore.add_documents([doc])
        return 1

    async def initialize_default_knowledge(self):
        default_knowledge = [
            {"content": "瑞泽·海度假民宿位于威海滨海度假区，是营地型度假民宿，共 13 套，包含 7 套 38㎡单体和 6 套 56㎡拼装。", "category": "真实项目复盘", "source": "项目参与经验"},
            {"content": "Capsule Cabin S 为约 38㎡单体产品，空间紧凑，不严格限定客群，最多 4 人入住。", "category": "产品规格", "source": "项目复盘规则"},
            {"content": "Capsule Cabin M 为约 56㎡拼装产品，解决多人入住、活动区、做饭、空间灵活变换和空间宽松问题。", "category": "产品规格", "source": "项目复盘规则"},
            {"content": "38㎡单体功能区包含榻榻米、衣柜/挂衣空间、卫浴、沙发区、水吧台和换鞋区。", "category": "空间模块", "source": "项目复盘规则"},
            {"content": "偏无人化运营关注入住效率、维护成本、拍照传播和舒适度，可配置智能门锁、灯光、空调、窗帘、传感器、监控和网络。", "category": "运营智能化", "source": "项目复盘规则"},
            {"content": "交付流程可拆为设计确认、工厂加工/预制、运输、现场基础、吊装、拼接安装、调试验收。", "category": "交付流程", "source": "项目复盘规则"},
            {"content": "复盘中高风险环节包括工厂加工/预制、拼接安装和调试验收，现场风险包括材料到货、吊装空间、道路运输、基础不平、排水、防水、防腐、供电网络。", "category": "风险提示", "source": "项目复盘规则"},
            {"content": "AI 可介入节点包括业主方需求问卷生成、面积和 BOM 表控制、生产端进度管理、现场交付风险检查和验收任务拆解。", "category": "AI产品化机会", "source": "项目复盘规则"},
            {"content": "系统仅作为基于项目复盘的规则型 AI PoC，不替代结构、消防、施工组织、报价和审批确认。", "category": "能力边界", "source": "项目复盘规则"},
        ]
        for knowledge in default_knowledge:
            await self.add_knowledge(content=knowledge["content"], category=knowledge["category"], source=knowledge["source"])
        logger.info(f"✅ 初始化 {len(default_knowledge)} 条默认知识")

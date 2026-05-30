"""
API 路由 - 股票分析 Web 系统后端 API
"""
import os
import sys
import asyncio
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional

import json as json_lib
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse

# 添加项目根目录到模块搜索路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from src.api.schemas import (
    ApiResponse,
    StockQuoteResponse,
    FinancialDataResponse,
    KlineDataResponse,
    BatchQuotesResponse,
    StockAnalysisRequest,
    MarketAnalysisRequest,
    BatchAnalysisRequest,
    StockAnalysisResponse,
    MarketAnalysisResponse,
    BatchAnalysisResponse,
    BatchAnalysisResult,
    TaskStatusResponse,
    HealthCheckResponse,
)
from src.api.middleware import setup_cors, RequestLoggingMiddleware, get_current_user, JWT_SECRET, JWT_ALGORITHM
from src.api.auth import router as auth_router
from src.db.database import init_db, save_analysis, get_db
from src.logging_config import get_api_logger

logger = get_api_logger()

# 任务存储 (生产环境应使用 Redis)
task_store: Dict[str, Dict] = {}


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用"""
    app = FastAPI(
        title="股票投资分析 API",
        description="提供股票分析、行情查询、财务数据等接口",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 添加中间件
    setup_cors(app)
    app.add_middleware(RequestLoggingMiddleware)

    # 注册路由
    register_routes(app)

    # 注册认证路由
    app.include_router(auth_router)

    # 添加启动事件
    @app.on_event("startup")
    async def startup_event():
        """应用启动时初始化数据库"""
        await init_db()
        logger.info("应用启动完成")

    return app


def register_routes(app: FastAPI):
    """注册所有 API 路由"""

    # ============ 健康检查 ============

    @app.get("/api/v1/health", response_model=ApiResponse, tags=["健康检查"])
    async def health_check():
        """健康检查接口"""
        return ApiResponse(
            success=True,
            data=HealthCheckResponse(
                status="ok",
                version="1.0.0",
                timestamp=datetime.now().isoformat()
            ).model_dump()
        )

    # ============ 行情数据接口 ============

    @app.get("/api/v1/quote/{stock_code}", response_model=ApiResponse, tags=["行情数据"])
    async def get_quote(stock_code: str):
        """获取单只股票实时行情"""
        try:
            from src.data_provider import DataProvider

            data_provider = DataProvider()
            quote = await data_provider.get_quote(stock_code)

            if not quote:
                return ApiResponse(
                    success=False,
                    error={"code": "STOCK_NOT_FOUND", "message": f"股票 {stock_code} 不存在"}
                )

            return ApiResponse(
                success=True,
                data=StockQuoteResponse(
                    stock_code=quote.stock_code,
                    stock_name=quote.stock_name,
                    current_price=quote.current_price,
                    change_percent=quote.change_percent,
                    volume=quote.volume,
                    timestamp=quote.timestamp
                ).model_dump()
            )

        except HTTPException:
            raise
        except ImportError as e:
            logger.error(f"数据服务不可用: {e}")
            return ApiResponse(
                success=False,
                error={"code": "SERVICE_UNAVAILABLE", "message": "数据服务不可用，请检查 AKShare 安装"}
            )
        except Exception as e:
            logger.error(f"获取行情失败: {e}")
            return ApiResponse(
                success=False,
                error={"code": "INTERNAL_ERROR", "message": str(e)}
            )

    @app.get("/api/v1/quotes/realtime", response_model=ApiResponse, tags=["行情数据"])
    async def get_realtime_quotes(codes: str = Query(..., description="股票代码列表，用逗号分隔")):
        """批量获取实时行情"""
        try:
            stock_codes = [c.strip() for c in codes.split(",")]

            from src.data_provider import DataProvider

            data_provider = DataProvider()
            quotes = await data_provider.get_realtime_quotes(stock_codes)

            quotes_data = {}
            for code, quote in quotes.items():
                quotes_data[code] = StockQuoteResponse(
                    stock_code=quote.stock_code,
                    stock_name=quote.stock_name,
                    current_price=quote.current_price,
                    change_percent=quote.change_percent,
                    volume=quote.volume,
                    timestamp=quote.timestamp
                ).model_dump()

            return ApiResponse(
                success=True,
                data={"quotes": quotes_data}
            )

        except HTTPException:
            raise
        except ImportError as e:
            logger.error(f"数据服务不可用: {e}")
            return ApiResponse(
                success=False,
                error={"code": "SERVICE_UNAVAILABLE", "message": "数据服务不可用"}
            )
        except Exception as e:
            logger.error(f"批量获取行情失败: {e}")
            return ApiResponse(
                success=False,
                error={"code": "INTERNAL_ERROR", "message": str(e)}
            )

    @app.get("/api/v1/financials/{stock_code}", response_model=ApiResponse, tags=["行情数据"])
    async def get_financials(stock_code: str):
        """获取股票财务数据"""
        try:
            from src.data_provider import DataProvider

            data_provider = DataProvider()
            financials = await data_provider.get_financials(stock_code)

            if not financials:
                return ApiResponse(
                    success=False,
                    error={"code": "NO_DATA", "message": f"股票 {stock_code} 财务数据不存在"}
                )

            return ApiResponse(
                success=True,
                data=FinancialDataResponse(
                    stock_code=financials.stock_code,
                    pe_ratio=financials.pe_ratio,
                    pb_ratio=financials.pb_ratio,
                    roe=financials.roe,
                    debt_ratio=financials.debt_ratio,
                    revenue_growth=financials.revenue_growth,
                    profit_growth=financials.profit_growth
                ).model_dump()
            )

        except HTTPException:
            raise
        except ImportError as e:
            logger.error(f"数据服务不可用: {e}")
            return ApiResponse(
                success=False,
                error={"code": "SERVICE_UNAVAILABLE", "message": "数据服务不可用"}
            )
        except Exception as e:
            logger.error(f"获取财务数据失败: {e}")
            return ApiResponse(
                success=False,
                error={"code": "INTERNAL_ERROR", "message": str(e)}
            )

    @app.get("/api/v1/kline/{stock_code}", response_model=ApiResponse, tags=["行情数据"])
    async def get_kline(
        stock_code: str,
        period: str = Query("daily", description="周期: daily/weekly/monthly"),
        adjust: str = Query("qfq", description="复权: qfq/hfq/none")
    ):
        """获取 K 线数据"""
        try:
            from src.data_provider import DataProvider

            data_provider = DataProvider()
            df = await data_provider.get_kline(stock_code, period, adjust)

            if df is None or df.empty:
                return ApiResponse(
                    success=False,
                    error={"code": "NO_DATA", "message": f"股票 {stock_code} K线数据不存在"}
                )

            # 转换 DataFrame 为列表
            dates = df['日期'].tolist() if '日期' in df.columns else []
            prices = df['收盘'].tolist() if '收盘' in df.columns else []
            volumes = df['成交量'].tolist() if '成交量' in df.columns else []

            return ApiResponse(
                success=True,
                data=KlineDataResponse(
                    stock_code=stock_code,
                    dates=[str(d) for d in dates],
                    prices=[float(p) for p in prices],
                    volumes=[int(v) for v in volumes]
                ).model_dump()
            )

        except HTTPException:
            raise
        except ImportError as e:
            logger.error(f"数据服务不可用: {e}")
            return ApiResponse(
                success=False,
                error={"code": "SERVICE_UNAVAILABLE", "message": "数据服务不可用"}
            )
        except Exception as e:
            logger.error(f"获取K线数据失败: {e}")
            return ApiResponse(
                success=False,
                error={"code": "INTERNAL_ERROR", "message": str(e)}
            )

    # ============ 分析接口 ============

    @app.post("/api/v1/analyze/stock", response_model=ApiResponse, tags=["股票分析"])
    async def analyze_stock(request: StockAnalysisRequest):
        """单股分析"""
        try:
            from src.stock_agent import StockAgent

            agent = StockAgent()

            logger.info(f"开始分析股票: {request.stock_code}")

            result = await agent.analyze_stock(
                stock_code=request.stock_code,
                stock_name=request.stock_name,
                max_urls=request.max_urls,
                risk_preference=request.risk_preference
            )

            if "error" in result:
                return ApiResponse(
                    success=False,
                    error={"code": "ANALYSIS_ERROR", "message": result["error"]}
                )

            # 转换 quote
            quote_data = None
            if result.get("quote"):
                q = result["quote"]
                quote_data = StockQuoteResponse(
                    stock_code=q.stock_code,
                    stock_name=q.stock_name,
                    current_price=q.current_price,
                    change_percent=q.change_percent,
                    volume=q.volume,
                    timestamp=q.timestamp
                ).model_dump() if hasattr(q, 'stock_code') else q

            # 转换 financials
            financials_data = None
            if result.get("financials"):
                f = result["financials"]
                financials_data = FinancialDataResponse(
                    stock_code=f.stock_code,
                    pe_ratio=f.pe_ratio,
                    pb_ratio=f.pb_ratio,
                    roe=f.roe,
                    debt_ratio=f.debt_ratio,
                    revenue_growth=f.revenue_growth,
                    profit_growth=f.profit_growth
                ).model_dump() if hasattr(f, 'stock_code') else f

            return ApiResponse(
                success=True,
                data=StockAnalysisResponse(
                    stock_code=result["stock_code"],
                    stock_name=result.get("stock_name"),
                    recommendation=result["recommendation"],
                    quote=quote_data,
                    financials=financials_data,
                    processing_time=result.get("processing_time", 0),
                    sources=result.get("sources", []),
                    risk_preference=result.get("risk_preference", request.risk_preference),
                    timestamp=result.get("timestamp", datetime.now().isoformat())
                ).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"股票分析失败: {e}")
            return ApiResponse(
                success=False,
                error={"code": "INTERNAL_ERROR", "message": str(e)}
            )

    @app.post("/api/v1/analyze/market", response_model=ApiResponse, tags=["股票分析"])
    async def analyze_market(request: MarketAnalysisRequest):
        """市场分析"""
        try:
            from src.stock_agent import StockAgent
            from src.config import DEFAULT_SEARCH_QUERIES

            agent = StockAgent()

            # 使用默认关键词或自定义关键词
            search_queries = request.search_queries or DEFAULT_SEARCH_QUERIES

            logger.info(f"开始市场分析，关键词数量: {len(search_queries)}")

            result = await agent.analyze_market(
                search_queries=search_queries,
                max_urls=request.max_urls,
                risk_preference=request.risk_preference
            )

            if isinstance(result, dict) and "error" in result:
                return ApiResponse(
                    success=False,
                    error={"code": "ANALYSIS_ERROR", "message": result["error"]}
                )

            recommendation = result.get("recommendation", str(result)) if isinstance(result, dict) else str(result)

            return ApiResponse(
                success=True,
                data=MarketAnalysisResponse(
                    recommendation=recommendation,
                    sources=result.get("sources", []) if isinstance(result, dict) else [],
                    timestamp=result.get("timestamp", datetime.now().isoformat()) if isinstance(result, dict) else datetime.now().isoformat(),
                    output_file=result.get("output_file") if isinstance(result, dict) else None
                ).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"市场分析失败: {e}")
            return ApiResponse(
                success=False,
                error={"code": "INTERNAL_ERROR", "message": str(e)}
            )

    @app.post("/api/v1/analyze/stock/stream", tags=["股票分析"])
    async def analyze_stock_stream(request: StockAnalysisRequest, req: Request):
        """单股分析 (SSE 流式输出)"""
        from src.stock_agent import StockAgent
        import jwt

        # 从 query param 获取 token（SSE 端点特殊处理）
        token = req.query_params.get("token")
        user_id = None
        if token:
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                user_id = payload.get("user_id")
            except Exception:
                pass  # token 无效，不保存历史记录

        agent = StockAgent()
        full_result = {"recommendation": "", "sources": [], "processing_time": 0}

        async def event_generator():
            nonlocal full_result
            try:
                async for event in agent.analyze_stock_stream(
                    stock_code=request.stock_code,
                    stock_name=request.stock_name,
                    max_urls=request.max_urls,
                    risk_preference=request.risk_preference
                ):
                    # 收集结果用于保存历史记录
                    if event["type"] == "text":
                        full_result["recommendation"] += event["data"].get("content", "")
                    elif event["type"] == "done":
                        full_result["sources"] = event["data"].get("sources", [])
                        full_result["processing_time"] = event["data"].get("processing_time", 0)
                        full_result["stock_code"] = event["data"].get("stock_code", request.stock_code)
                        full_result["stock_name"] = event["data"].get("stock_name", request.stock_name)

                        # 如果用户已认证，保存历史记录
                        if user_id:
                            try:
                                # 生成摘要（取前 200 字）
                                summary = full_result["recommendation"][:200] + "..." if len(full_result["recommendation"]) > 200 else full_result["recommendation"]
                                await save_analysis(
                                    user_id=user_id,
                                    analysis_type="stock",
                                    stock_code=full_result.get("stock_code", ""),
                                    stock_name=full_result.get("stock_name", ""),
                                    risk_preference=request.risk_preference,
                                    summary=summary,
                                    full_content=full_result["recommendation"],
                                    processing_time=full_result.get("processing_time"),
                                    sources=full_result.get("sources", [])
                                )
                                logger.info(f"已保存股票分析历史记录: user_id={user_id}, stock={request.stock_code}")
                            except Exception as e:
                                logger.error(f"保存历史记录失败: {e}")

                    yield f"event: {event['type']}\ndata: {json_lib.dumps(event['data'], ensure_ascii=False)}\n\n"
            except Exception as e:
                logger.error(f"流式股票分析失败: {e}", exc_info=True)
                yield f"event: error\ndata: {json_lib.dumps({'message': '分析过程中发生错误，请稍后重试'}, ensure_ascii=False)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @app.post("/api/v1/analyze/market/stream", tags=["股票分析"])
    async def analyze_market_stream(request: MarketAnalysisRequest, req: Request):
        """市场分析 (SSE 流式输出)"""
        from src.stock_agent import StockAgent
        from src.config import DEFAULT_SEARCH_QUERIES
        import jwt

        # 从 query param 获取 token（SSE 端点特殊处理）
        token = req.query_params.get("token")
        user_id = None
        if token:
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                user_id = payload.get("user_id")
            except Exception:
                pass

        agent = StockAgent()
        search_queries = request.search_queries or DEFAULT_SEARCH_QUERIES
        full_result = {"recommendation": "", "sources": [], "processing_time": 0}

        async def event_generator():
            nonlocal full_result
            try:
                async for event in agent.analyze_market_stream(
                    search_queries=search_queries,
                    max_urls=request.max_urls,
                    risk_preference=request.risk_preference
                ):
                    # 收集结果用于保存历史记录
                    if event["type"] == "text":
                        full_result["recommendation"] += event["data"].get("content", "")
                    elif event["type"] == "done":
                        full_result["sources"] = event["data"].get("sources", [])
                        full_result["processing_time"] = event["data"].get("processing_time", 0)

                        # 如果用户已认证，保存历史记录
                        if user_id:
                            try:
                                summary = full_result["recommendation"][:200] + "..." if len(full_result["recommendation"]) > 200 else full_result["recommendation"]
                                await save_analysis(
                                    user_id=user_id,
                                    analysis_type="market",
                                    stock_code="",
                                    stock_name="",
                                    risk_preference=request.risk_preference,
                                    summary=summary,
                                    full_content=full_result["recommendation"],
                                    processing_time=full_result.get("processing_time"),
                                    sources=full_result.get("sources", [])
                                )
                                logger.info(f"已保存市场分析历史记录: user_id={user_id}")
                            except Exception as e:
                                logger.error(f"保存历史记录失败: {e}")

                    yield f"event: {event['type']}\ndata: {json_lib.dumps(event['data'], ensure_ascii=False)}\n\n"
            except Exception as e:
                logger.error(f"流式市场分析失败: {e}", exc_info=True)
                yield f"event: error\ndata: {json_lib.dumps({'message': '分析过程中发生错误，请稍后重试'}, ensure_ascii=False)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @app.post("/api/v1/analyze/batch", response_model=ApiResponse, tags=["股票分析"])
    async def analyze_batch(request: BatchAnalysisRequest):
        """批量股票分析"""
        try:
            # 生成任务 ID
            task_id = str(uuid.uuid4())

            # 解析股票列表
            stocks = [(s.get("code"), s.get("name")) for s in request.stocks]

            # 创建任务
            task_store[task_id] = {
                "status": "pending",
                "results": [],
                "total_count": len(stocks),
                "success_count": 0,
                "error_count": 0,
                "created_at": datetime.now().isoformat()
            }

            # 异步执行分析
            asyncio.create_task(run_batch_analysis(task_id, stocks, request))

            return ApiResponse(
                success=True,
                data=BatchAnalysisResponse(
                    task_id=task_id,
                    status="pending",
                    results=None,
                    total_count=len(stocks),
                    success_count=0,
                    error_count=0
                ).model_dump()
            )

        except Exception as e:
            logger.error(f"批量分析任务创建失败: {e}")
            return ApiResponse(
                success=False,
                error={"code": "INTERNAL_ERROR", "message": str(e)}
            )

    @app.get("/api/v1/tasks/{task_id}", response_model=ApiResponse, tags=["任务管理"])
    async def get_task_status(task_id: str):
        """获取批量分析任务状态"""
        if task_id not in task_store:
            return ApiResponse(
                success=False,
                error={"code": "TASK_NOT_FOUND", "message": f"任务 {task_id} 不存在"}
            )

        task = task_store[task_id]

        return ApiResponse(
            success=True,
            data=TaskStatusResponse(
                task_id=task_id,
                status=task["status"],
                progress=task.get("progress"),
                results=task.get("results"),
                error=task.get("error")
            ).model_dump()
        )

    # ============ 历史记录 API ============

    @app.get("/api/v1/history", response_model=ApiResponse, tags=["历史记录"])
    async def get_history_list(
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        type: Optional[str] = Query(None, description="筛选类型: stock/market/batch"),
        starred_only: bool = Query(False, description="只显示收藏的记录"),
        user_id: int = Depends(get_current_user)
    ):
        """获取当前用户的分析历史记录"""
        try:
            async with get_db() as db:
                conditions = ["user_id = ?"]
                params: list = [user_id]

                if type:
                    conditions.append("type = ?")
                    params.append(type)

                if starred_only:
                    conditions.append("starred = 1")

                where_clause = " AND ".join(conditions)

                count_query = f"SELECT COUNT(*) FROM analysis_history WHERE {where_clause}"
                cursor = await db.execute(count_query, params)
                total_count = (await cursor.fetchone())[0]

                offset = (page - 1) * page_size
                query = f"""
                    SELECT id, type, stock_code, stock_name, risk_preference,
                           summary, processing_time, sources, starred, created_at
                    FROM analysis_history
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
                params.extend([page_size, offset])

                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()

                items = []
                for row in rows:
                    items.append({
                        "id": row[0],
                        "type": row[1],
                        "stock_code": row[2],
                        "stock_name": row[3],
                        "risk_preference": row[4],
                        "summary": row[5],
                        "processing_time": row[6],
                        "sources": json.loads(row[7]) if row[7] else [],
                        "starred": bool(row[8]),
                        "created_at": row[9]
                    })

                return ApiResponse(
                    success=True,
                    data={
                        "items": items,
                        "total_count": total_count,
                        "page": page,
                        "page_size": page_size,
                        "total_pages": (total_count + page_size - 1) // page_size
                    }
                )

        except Exception as e:
            logger.error(f"获取历史记录失败: {e}")
            return ApiResponse(
                success=False,
                error={"code": "INTERNAL_ERROR", "message": str(e)}
            )

    @app.get("/api/v1/history/{history_id}", response_model=ApiResponse, tags=["历史记录"])
    async def get_history_detail(
        history_id: int,
        user_id: int = Depends(get_current_user)
    ):
        """获取单条历史记录详情"""
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT id, type, stock_code, stock_name, risk_preference,
                           summary, full_content, processing_time, sources, starred, created_at
                    FROM analysis_history
                    WHERE id = ? AND user_id = ?
                """, (history_id, user_id))
                row = await cursor.fetchone()

                if not row:
                    return ApiResponse(success=False, error={"code": "NOT_FOUND", "message": "记录不存在"})

                return ApiResponse(success=True, data={
                    "id": row[0], "type": row[1], "stock_code": row[2], "stock_name": row[3],
                    "risk_preference": row[4], "summary": row[5], "full_content": row[6],
                    "processing_time": row[7], "sources": json.loads(row[8]) if row[8] else [],
                    "starred": bool(row[9]), "created_at": row[10]
                })

        except Exception as e:
            logger.error(f"获取历史记录详情失败: {e}")
            return ApiResponse(success=False, error={"code": "INTERNAL_ERROR", "message": str(e)})

    @app.put("/api/v1/history/{history_id}/star", response_model=ApiResponse, tags=["历史记录"])
    async def toggle_history_star(
        history_id: int,
        user_id: int = Depends(get_current_user)
    ):
        """收藏/取消收藏"""
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT starred FROM analysis_history WHERE id = ? AND user_id = ?",
                    (history_id, user_id)
                )
                row = await cursor.fetchone()
                if not row:
                    return ApiResponse(success=False, error={"code": "NOT_FOUND", "message": "记录不存在"})

                new_starred = 0 if row[0] else 1
                await db.execute("UPDATE analysis_history SET starred = ? WHERE id = ?", (new_starred, history_id))
                await db.commit()

                return ApiResponse(success=True, data={"starred": bool(new_starred)})

        except Exception as e:
            logger.error(f"更新收藏状态失败: {e}")
            return ApiResponse(success=False, error={"code": "INTERNAL_ERROR", "message": str(e)})

    @app.delete("/api/v1/history/{history_id}", response_model=ApiResponse, tags=["历史记录"])
    async def delete_history_item(
        history_id: int,
        user_id: int = Depends(get_current_user)
    ):
        """删除历史记录"""
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT id FROM analysis_history WHERE id = ? AND user_id = ?",
                    (history_id, user_id)
                )
                row = await cursor.fetchone()
                if not row:
                    return ApiResponse(success=False, error={"code": "NOT_FOUND", "message": "记录不存在"})

                await db.execute("DELETE FROM analysis_history WHERE id = ?", (history_id,))
                await db.commit()

                return ApiResponse(success=True, data={"deleted": history_id})

        except Exception as e:
            logger.error(f"删除历史记录失败: {e}")
            return ApiResponse(success=False, error={"code": "INTERNAL_ERROR", "message": str(e)})


async def run_batch_analysis(task_id: str, stocks: List[tuple], request: BatchAnalysisRequest):
    """后台执行批量分析"""
    from src.stock_agent import StockAgent

    try:
        task_store[task_id]["status"] = "processing"

        agent = StockAgent()

        # 使用 batch_analyze 方法
        results = await agent.batch_analyze(
            stocks=stocks,
            max_urls_per_stock=request.max_urls_per_stock,
            risk_preference=request.risk_preference
        )

        # 转换结果
        processed_results = []
        success_count = 0
        error_count = 0

        for result in results:
            if "error" in result:
                processed_results.append(BatchAnalysisResult(
                    stock_code=result.get("stock_code", "未知"),
                    stock_name=result.get("stock_name"),
                    recommendation=None,
                    error=result["error"],
                    status="error"
                ).model_dump())
                error_count += 1
            else:
                processed_results.append(BatchAnalysisResult(
                    stock_code=result.get("stock_code", ""),
                    stock_name=result.get("stock_name"),
                    recommendation=result.get("recommendation", "")[:500] if result.get("recommendation") else None,
                    error=None,
                    status="success"
                ).model_dump())
                success_count += 1

        # 更新任务状态
        task_store[task_id].update({
            "status": "completed",
            "results": processed_results,
            "success_count": success_count,
            "error_count": error_count,
            "completed_at": datetime.now().isoformat()
        })

        logger.info(f"批量分析任务 {task_id} 完成: 成功 {success_count}, 失败 {error_count}")

    except Exception as e:
        logger.error(f"批量分析任务 {task_id} 执行失败: {e}")
        task_store[task_id].update({
            "status": "error",
            "error": str(e)
        })


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
Workflow graph execution endpoint for node-based AI generation pipelines.
"""
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from pydantic import BaseModel
import networkx as nx

from ..services.deapi import get_deapi_client
from ..services.iflow import get_iflow_client

router = APIRouter(prefix="/api/workflow", tags=["workflow"])

# In-memory storage for executions (use Redis in production)
executions: Dict[str, dict] = {}


class NodeData(BaseModel):
    id: str
    type: str
    data: dict = {}


class EdgeData(BaseModel):
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None


class GraphPayload(BaseModel):
    nodes: List[NodeData]
    edges: List[EdgeData]


class ExecutionStatus(BaseModel):
    execution_id: str
    status: str  # pending, running, completed, failed
    progress: int = 0
    message: str = ""
    node_results: Dict[str, dict] = {}
    error: Optional[str] = None


async def execute_graph_task(execution_id: str, graph_data: GraphPayload, custom_api_key: Optional[str] = None, custom_iflow_key: Optional[str] = None):
    """
    Background task to execute the workflow graph.
    """
    try:
        executions[execution_id]["status"] = "running"
        executions[execution_id]["message"] = "Executing workflow..."
        
        # Create directed graph
        G = nx.DiGraph()
        node_lookup = {node.id: node for node in graph_data.nodes}
        
        for node in graph_data.nodes:
            G.add_node(node.id)
        
        for edge in graph_data.edges:
            G.add_edge(edge.source, edge.target)
        
        # Check for cycles
        if not nx.is_directed_acyclic_graph(G):
            executions[execution_id]["status"] = "failed"
            executions[execution_id]["error"] = "Graph contains cycles"
            return
        
        # Topological sort for execution order
        execution_order = list(nx.topological_sort(G))
        
        # Store node outputs
        node_outputs: Dict[str, Any] = {}
        # Use custom API key if provided (BYOK), otherwise use default
        api = get_deapi_client(custom_api_key=custom_api_key)
        iflow_api = get_iflow_client(custom_api_key=custom_iflow_key)
        
        total_nodes = len(execution_order)
        
        for idx, node_id in enumerate(execution_order):
            node = node_lookup[node_id]
            
            # Update progress
            progress = int((idx / total_nodes) * 100)
            executions[execution_id]["progress"] = progress
            executions[execution_id]["message"] = f"Processing node: {node.type}"
            
            try:
                result = await execute_node(node, G, node_outputs, api, iflow_api)
                node_outputs[node_id] = result
                executions[execution_id]["node_results"][node_id] = result
                print(f"[Workflow] Node {node_id} result: status={result.get('status')}, resultUrl={result.get('resultUrl', 'N/A')[:50] if result.get('resultUrl') else 'N/A'}")
            except Exception as e:
                executions[execution_id]["status"] = "failed"
                executions[execution_id]["error"] = f"Node {node_id} failed: {str(e)}"
                print(f"[Workflow] Node {node_id} failed with error: {str(e)}")
                return
        
        executions[execution_id]["status"] = "completed"
        executions[execution_id]["progress"] = 100
        executions[execution_id]["message"] = "Workflow completed successfully"
        print(f"[Workflow] Execution {execution_id} completed. Node results: {list(executions[execution_id]['node_results'].keys())}")
        
    except Exception as e:
        executions[execution_id]["status"] = "failed"
        executions[execution_id]["error"] = str(e)
        print(f"[Workflow] Execution {execution_id} failed: {str(e)}")


async def execute_node(node: NodeData, G: nx.DiGraph, node_outputs: Dict, api, iflow_api=None) -> dict:
    """
    Execute a single node based on its type.
    """
    node_type = node.type
    data = node.data
    
    print(f"[Workflow] Executing node: {node.id} (type: {node_type})")
    
    # Check for cached result - skip re-execution if node already has output
    cached_result = data.get("resultUrl") or data.get("cachedResult")
    cached_text = data.get("text") if node_type in ["textInput", "imageAnalysis", "videoToText"] else None
    
    if cached_result or (cached_text and node_type != "textInput"):
        print(f"[Workflow] Node {node.id} has cached result, skipping execution")
        result = {
            "status": "completed",
            "cached": True
        }
        if cached_result:
            result["resultUrl"] = cached_result
        if cached_text:
            result["text"] = cached_text
        if data.get("imageData"):
            result["imageData"] = data["imageData"]
        return result
    
    # Get inputs from connected nodes
    incoming_edges = list(G.predecessors(node.id))
    
    result = {"status": "completed"}
    
    if node_type == "textInput":
        # Text input node - just pass through the text
        result["text"] = data.get("text", "")
        result["resultUrl"] = None
    
    elif node_type == "imageInput":
        # Image input node - pass through the uploaded image
        # The image is stored as base64 data URL in imageData
        image_data = data.get("imageData") or data.get("imageUrl")
        print(f"[Workflow] imageInput - received image_data type: {type(image_data)}, length: {len(image_data) if image_data else 0}")
        if image_data:
            # If it's a data URL, store both the full URL and raw base64
            if image_data.startswith("data:"):
                result["resultUrl"] = image_data
                result["imageData"] = image_data
            else:
                # It's raw base64 - create a data URL for display and store raw for API
                result["resultUrl"] = f"data:image/png;base64,{image_data}"
                result["imageData"] = f"data:image/png;base64,{image_data}"
        result["status"] = "completed"
        print(f"[Workflow] imageInput - resultUrl prefix: {result.get('resultUrl', '')[:50]}...")
    
    elif node_type == "imageGen":
        # Text-to-Image generation
        prompt = ""
        print(f"[Workflow] imageGen - incoming_edges: {incoming_edges}")
        print(f"[Workflow] imageGen - node_outputs keys: {list(node_outputs.keys())}")
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            print(f"[Workflow] imageGen - parent {parent_id} output: {parent_output}")
            if parent_output.get("text"):
                prompt = parent_output["text"]
                break
        
        # Fallback to node's own prompt field or text field
        if not prompt:
            prompt = data.get("prompt", "") or data.get("text", "")
        
        # Get batch size (default 1)
        batch_size = data.get("batchSize", 1)
        
        print(f"[Workflow] imageGen - final prompt: '{prompt}', batch_size: {batch_size}")
        print(f"[Workflow] imageGen - data: {data}")
        
        if prompt:
            result["status"] = "processing"
            
            # Generate multiple images in parallel
            async def generate_single_image(idx):
                gen_result = await api.generate_text2img(
                    prompt=prompt,
                    model=data.get("model", "Flux_2_Klein_4B_BF16"),
                    width=data.get("width", 1024),
                    height=data.get("height", 576),
                    steps=data.get("steps", 4),
                    guidance=data.get("guidance", 3.5),
                    seed=data.get("seed", -1) + idx if data.get("seed", -1) != -1 else -1
                )
                
                request_id = gen_result.get("data", {}).get("request_id") or gen_result.get("request_id")
                if request_id:
                    max_attempts = 120
                    for attempt in range(max_attempts):
                        resp = await api.get_request_status(request_id)
                        status_data = resp.get("data", {})
                        api_status = status_data.get("status")
                        if api_status == "done":
                            return status_data.get("result_url")
                        elif api_status == "error":
                            return None
                        await asyncio.sleep(2)
                return None
            
            # Run batch generation in parallel
            tasks = [generate_single_image(i) for i in range(batch_size)]
            result_urls = await asyncio.gather(*tasks)
            
            # Filter out None values
            result_urls = [url for url in result_urls if url]
            
            if result_urls:
                result["resultUrls"] = result_urls
                result["resultUrl"] = result_urls[0]  # Keep first for backward compatibility
                result["status"] = "completed"
                print(f"[Workflow] imageGen completed: {len(result_urls)} images")
            else:
                result["status"] = "failed"
                result["error"] = "All generations failed"
    
    elif node_type == "videoGen":
        # Text-to-Video generation
        prompt = ""
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            if parent_output.get("text"):
                prompt = parent_output["text"]
                break
        
        if not prompt:
            prompt = data.get("text", "")
        
        if prompt:
            result["status"] = "processing"
            
            gen_result = await api.generate_txt2video(
                prompt=prompt,
                model=data.get("model", "Ltx2_3_22B_Dist_INT8"),
                width=data.get("width", 512),
                height=data.get("height", 512),
                frames=data.get("frames", 48),
                fps=data.get("fps", 24),
                steps=data.get("steps", 20),
                guidance=data.get("guidance", 3.5),
                seed=data.get("seed", -1)
            )
            
            request_id = gen_result.get("data", {}).get("request_id") or gen_result.get("request_id")
            print(f"[Workflow] videoGen request_id: {request_id}")
            if request_id:
                max_attempts = 180  # Videos take longer
                for attempt in range(max_attempts):
                    resp = await api.get_request_status(request_id)
                    status_data = resp.get("data", {})
                    api_status = status_data.get("status")
                    if attempt % 10 == 0:
                        print(f"[Workflow] videoGen polling attempt {attempt}: status={api_status}")
                    if api_status == "done":
                        result["resultUrl"] = status_data.get("result_url")
                        result["status"] = "completed"
                        print(f"[Workflow] videoGen completed: {result['resultUrl']}")
                        break
                    elif api_status == "error":
                        result["status"] = "failed"
                        result["error"] = status_data.get("error", "Generation failed")
                        print(f"[Workflow] videoGen failed: {result['error']}")
                        break
                    await asyncio.sleep(3)
    
    elif node_type == "imageEdit":
        # Image editing - requires downloading the image first
        prompt = data.get("editPrompt", "")
        image_data = None
        
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            # Check if we have direct image data (from imageInput node)
            if parent_output.get("imageData"):
                img_data_url = parent_output["imageData"]
                # Extract base64 from data URL
                if img_data_url.startswith("data:") and ";base64," in img_data_url:
                    import base64
                    base64_data = img_data_url.split(";base64,")[1]
                    image_data = base64.b64decode(base64_data)
            elif parent_output.get("resultUrl"):
                result_url = parent_output["resultUrl"]
                # Check if it's a data URL
                if result_url.startswith("data:") and ";base64," in result_url:
                    import base64
                    base64_data = result_url.split(";base64,")[1]
                    image_data = base64.b64decode(base64_data)
                else:
                    # Download the image from URL
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.get(result_url) as resp:
                            if resp.status == 200:
                                image_data = await resp.read()
            if parent_output.get("text"):
                prompt = prompt or parent_output["text"]
        
        if image_data and prompt:
            result["status"] = "processing"
            
            gen_result = await api.generate_img2img(
                image=image_data,
                prompt=prompt,
                model=data.get("model", "QwenImageEdit_Plus_NF4"),
                steps=data.get("steps", 20),
                guidance=data.get("guidance", 3.5),
                seed=data.get("seed", -1)
            )
            
            request_id = gen_result.get("data", {}).get("request_id") or gen_result.get("request_id")
            if request_id:
                max_attempts = 120
                for _ in range(max_attempts):
                    resp = await api.get_request_status(request_id)
                    status_data = resp.get("data", {})
                    api_status = status_data.get("status")
                    if api_status == "done":
                        result["resultUrl"] = status_data.get("result_url")
                        result["status"] = "completed"
                        break
                    elif api_status == "error":
                        result["status"] = "failed"
                        result["error"] = status_data.get("error", "Edit failed")
                        break
                    await asyncio.sleep(2)
    
    elif node_type == "img2video":
        # Image-to-Video generation
        prompt = data.get("prompt", "")
        image_data = None
        
        print(f"[Workflow] img2video - incoming_edges: {incoming_edges}")
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            print(f"[Workflow] img2video - parent {parent_id} output keys: {list(parent_output.keys())}")
            print(f"[Workflow] img2video - parent imageData present: {bool(parent_output.get('imageData'))}")
            print(f"[Workflow] img2video - parent resultUrl present: {bool(parent_output.get('resultUrl'))}")
            
            # Check if we have direct image data (from imageInput node)
            if parent_output.get("imageData"):
                img_data_url = parent_output["imageData"]
                print(f"[Workflow] img2video - imageData type: {type(img_data_url)}, starts with data: {str(img_data_url).startswith('data:')}")
                # Extract base64 from data URL
                if img_data_url.startswith("data:") and ";base64," in img_data_url:
                    import base64
                    base64_data = img_data_url.split(";base64,")[1]
                    image_data = base64.b64decode(base64_data)
                    print(f"[Workflow] img2video - decoded base64, length: {len(image_data)}")
                else:
                    # Raw base64 without prefix
                    import base64
                    image_data = base64.b64decode(img_data_url)
                    print(f"[Workflow] img2video - decoded raw base64, length: {len(image_data)}")
            elif parent_output.get("resultUrl"):
                result_url = parent_output["resultUrl"]
                print(f"[Workflow] img2video - resultUrl type: {type(result_url)}, starts with data: {str(result_url).startswith('data:')}")
                # Check if it's a data URL
                if result_url.startswith("data:") and ";base64," in result_url:
                    import base64
                    base64_data = result_url.split(";base64,")[1]
                    image_data = base64.b64decode(base64_data)
                    print(f"[Workflow] img2video - decoded from resultUrl, length: {len(image_data)}")
                else:
                    # Download the image from URL
                    print(f"[Workflow] img2video - downloading from URL: {result_url[:100]}...")
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.get(result_url) as resp:
                            if resp.status == 200:
                                image_data = await resp.read()
                                print(f"[Workflow] img2video - downloaded image, length: {len(image_data)}")
            if parent_output.get("text"):
                prompt = prompt or parent_output["text"]
        
        print(f"[Workflow] img2video - final image_data: {len(image_data) if image_data else 'None'}")
        print(f"[Workflow] img2video - prompt: '{prompt}'")
        
        if image_data:
            result["status"] = "processing"
            
            gen_result = await api.generate_img2video(
                first_frame_image=image_data,
                prompt=prompt,
                model=data.get("model", "Ltx2_3_22B_Dist_INT8"),
                frames=data.get("frames", 48),
                fps=data.get("fps", 24),
                seed=data.get("seed", -1)
            )
            
            request_id = gen_result.get("data", {}).get("request_id") or gen_result.get("request_id")
            print(f"[Workflow] img2video request_id: {request_id}")
            if request_id:
                max_attempts = 180
                for attempt in range(max_attempts):
                    resp = await api.get_request_status(request_id)
                    status_data = resp.get("data", {})
                    api_status = status_data.get("status")
                    if attempt % 10 == 0:
                        print(f"[Workflow] img2video polling attempt {attempt}: status={api_status}")
                    if api_status == "done":
                        result["resultUrl"] = status_data.get("result_url")
                        result["status"] = "completed"
                        print(f"[Workflow] img2video completed: {result['resultUrl']}")
                        break
                    elif api_status == "error":
                        result["status"] = "failed"
                        result["error"] = status_data.get("error", "Generation failed")
                        print(f"[Workflow] img2video failed: {result['error']}")
                        break
                    await asyncio.sleep(3)
    
    elif node_type == "tts":
        # Text-to-Speech generation
        text = ""
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            if parent_output.get("text"):
                text = parent_output["text"]
                break
        
        if not text:
            text = data.get("text", "")
        
        if text:
            result["status"] = "processing"
            
            gen_result = await api.generate_txt2audio(
                text=text,
                model=data.get("model", "Kokoro"),
                voice=data.get("voice", "af_sky"),
                lang=data.get("lang", "en-us"),
                speed=data.get("speed", 1.0),
                format="flac",
                sample_rate=24000
            )
            
            request_id = gen_result.get("data", {}).get("request_id") or gen_result.get("request_id")
            if request_id:
                max_attempts = 60  # TTS is usually fast
                for _ in range(max_attempts):
                    resp = await api.get_request_status(request_id)
                    status_data = resp.get("data", {})
                    api_status = status_data.get("status")
                    if api_status == "done":
                        result["resultUrl"] = status_data.get("result_url")
                        result["status"] = "completed"
                        break
                    elif api_status == "error":
                        result["status"] = "failed"
                        result["error"] = status_data.get("error", "TTS failed")
                        break
                    await asyncio.sleep(2)
    
    elif node_type == "imageAnalysis":
        # Image-to-Text (OCR) analysis
        image_data = None
        
        print(f"[Workflow] imageAnalysis - incoming_edges: {incoming_edges}")
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            print(f"[Workflow] imageAnalysis - parent {parent_id} output keys: {list(parent_output.keys())}")
            print(f"[Workflow] imageAnalysis - parent imageData type: {type(parent_output.get('imageData'))}")
            # Check if we have direct image data (from imageInput node)
            if parent_output.get("imageData"):
                img_data_url = parent_output["imageData"]
                print(f"[Workflow] imageAnalysis - img_data_url type: {type(img_data_url)}, len: {len(img_data_url) if img_data_url else 0}")
                print(f"[Workflow] imageAnalysis - img_data_url prefix: {str(img_data_url)[:60] if img_data_url else 'None'}...")
                # Extract base64 from data URL
                if img_data_url.startswith("data:") and ";base64," in img_data_url:
                    import base64
                    base64_data = img_data_url.split(";base64,")[1]
                    image_data = base64.b64decode(base64_data)
                    print(f"[Workflow] imageAnalysis - decoded base64, length: {len(image_data)}")
                else:
                    print(f"[Workflow] imageAnalysis - imageData is not a valid data URL")
            elif parent_output.get("resultUrl"):
                result_url = parent_output["resultUrl"]
                print(f"[Workflow] imageAnalysis - resultUrl type: {type(result_url)}")
                # Check if it's a data URL
                if result_url.startswith("data:") and ";base64," in result_url:
                    import base64
                    base64_data = result_url.split(";base64,")[1]
                    image_data = base64.b64decode(base64_data)
                else:
                    # Download the image from URL
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.get(result_url) as resp:
                            if resp.status == 200:
                                image_data = await resp.read()
        
        print(f"[Workflow] imageAnalysis - final image_data: {len(image_data) if image_data else 'None'}")
        
        if image_data:
            result["status"] = "processing"
            
            try:
                gen_result = await api.generate_img2txt(
                    image=image_data,
                    model=data.get("model", "Nanonets_Ocr_S_F16"),
                    language=data.get("language", "auto"),
                    format=data.get("format", "text")
                )
                
                print(f"[Workflow] imageAnalysis - gen_result: {gen_result}")
                
                # Get request_id and poll for result
                request_id = gen_result.get("data", {}).get("request_id") or gen_result.get("request_id")
                print(f"[Workflow] imageAnalysis - request_id: {request_id}")
                
                if request_id:
                    max_attempts = 60
                    for attempt in range(max_attempts):
                        resp = await api.get_request_status(request_id)
                        status_data = resp.get("data", {})
                        api_status = status_data.get("status")
                        
                        if attempt % 5 == 0:
                            print(f"[Workflow] imageAnalysis polling attempt {attempt}: status={api_status}")
                        
                        if api_status == "done":
                            raw_text = status_data.get("result", "")
                            print(f"[Workflow] imageAnalysis - raw result: {raw_text[:200] if raw_text else 'None'}...")
                            
                            # Parse text from <img>...</img> tags if present
                            import re
                            if raw_text and "<img>" in raw_text:
                                match = re.search(r'<img>(.*?)</img>', raw_text, re.DOTALL)
                                if match:
                                    extracted_text = match.group(1).strip()
                                else:
                                    extracted_text = raw_text
                            else:
                                extracted_text = raw_text
                            
                            print(f"[Workflow] imageAnalysis - extracted text: {extracted_text[:200] if extracted_text else 'None'}...")
                            
                            result["text"] = extracted_text
                            result["resultUrl"] = status_data.get("result_url")
                            result["status"] = "completed"
                            break
                        elif api_status == "error":
                            result["status"] = "failed"
                            result["error"] = status_data.get("error", "OCR failed")
                            print(f"[Workflow] imageAnalysis failed: {result['error']}")
                            break
                        
                        await asyncio.sleep(2)
                else:
                    result["status"] = "failed"
                    result["error"] = "No request_id returned from API"
                    
            except Exception as e:
                print(f"[Workflow] imageAnalysis - ERROR: {str(e)}")
                result["status"] = "failed"
                result["error"] = str(e)
    
    elif node_type == "bgRemoval":
        # Background removal
        image_data = None
        
        print(f"[Workflow] bgRemoval - incoming_edges: {incoming_edges}")
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            if parent_output.get("imageData"):
                img_data_url = parent_output["imageData"]
                if img_data_url.startswith("data:") and ";base64," in img_data_url:
                    import base64
                    base64_data = img_data_url.split(";base64,")[1]
                    image_data = base64.b64decode(base64_data)
                    print(f"[Workflow] bgRemoval - decoded base64, length: {len(image_data)}")
            elif parent_output.get("resultUrl"):
                result_url = parent_output["resultUrl"]
                if result_url.startswith("data:") and ";base64," in result_url:
                    import base64
                    base64_data = result_url.split(";base64,")[1]
                    image_data = base64.b64decode(base64_data)
                else:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.get(result_url) as resp:
                            if resp.status == 200:
                                image_data = await resp.read()
        
        if image_data:
            result["status"] = "processing"
            
            gen_result = await api.remove_image_background(
                image=image_data,
                model=data.get("model", "Ben2")
            )
            
            request_id = gen_result.get("data", {}).get("request_id") or gen_result.get("request_id")
            print(f"[Workflow] bgRemoval request_id: {request_id}")
            
            if request_id:
                max_attempts = 120
                for attempt in range(max_attempts):
                    resp = await api.get_request_status(request_id)
                    status_data = resp.get("data", {})
                    api_status = status_data.get("status")
                    
                    if attempt % 10 == 0:
                        print(f"[Workflow] bgRemoval polling attempt {attempt}: status={api_status}")
                    
                    if api_status == "done":
                        result["resultUrl"] = status_data.get("result_url")
                        result["status"] = "completed"
                        print(f"[Workflow] bgRemoval completed: {result['resultUrl']}")
                        break
                    elif api_status == "error":
                        result["status"] = "failed"
                        result["error"] = status_data.get("error", "Background removal failed")
                        print(f"[Workflow] bgRemoval failed: {result['error']}")
                        break
                    
                    await asyncio.sleep(2)
    
    elif node_type == "videoToText":
        # Video-to-text transcription
        video_url = data.get("videoUrl", "")
        
        # Check if video URL comes from parent node (video input node could be added later)
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            if parent_output.get("videoUrl"):
                video_url = parent_output["videoUrl"]
                break
        
        print(f"[Workflow] videoToText - video_url: {video_url}")
        
        if video_url:
            result["status"] = "processing"
            
            try:
                gen_result = await api.generate_vid2txt(
                    video_url=video_url,
                    model=data.get("model", "WhisperLargeV3"),
                    include_ts=data.get("includeTs", True)
                )
                
                request_id = gen_result.get("data", {}).get("request_id") or gen_result.get("request_id")
                print(f"[Workflow] videoToText request_id: {request_id}")
                
                if request_id:
                    max_attempts = 180  # Videos take longer
                    for attempt in range(max_attempts):
                        resp = await api.get_request_status(request_id)
                        status_data = resp.get("data", {})
                        api_status = status_data.get("status")
                        
                        if attempt % 10 == 0:
                            print(f"[Workflow] videoToText polling attempt {attempt}: status={api_status}")
                        
                        if api_status == "done":
                            result["text"] = status_data.get("result")
                            result["resultUrl"] = status_data.get("result_url")
                            result["status"] = "completed"
                            print(f"[Workflow] videoToText completed, text length: {len(result.get('text', ''))}")
                            break
                        elif api_status == "error":
                            result["status"] = "failed"
                            result["error"] = status_data.get("error", "Transcription failed")
                            print(f"[Workflow] videoToText failed: {result['error']}")
                            break
                        
                        await asyncio.sleep(3)
            except Exception as e:
                print(f"[Workflow] videoToText - ERROR: {str(e)}")
                result["status"] = "failed"
                result["error"] = str(e)
    
    elif node_type == "imageEnhance":
        # Image enhancement using img2img
        image_data = None
        enhance_prompt = data.get("enhancePrompt", "enhance image quality")
        
        print(f"[Workflow] imageEnhance - incoming_edges: {incoming_edges}")
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            if parent_output.get("imageData"):
                img_data_url = parent_output["imageData"]
                if img_data_url.startswith("data:") and ";base64," in img_data_url:
                    import base64
                    base64_data = img_data_url.split(";base64,")[1]
                    image_data = base64.b64decode(base64_data)
                    print(f"[Workflow] imageEnhance - decoded base64, length: {len(image_data)}")
            elif parent_output.get("resultUrl"):
                result_url = parent_output["resultUrl"]
                if result_url.startswith("data:") and ";base64," in result_url:
                    import base64
                    base64_data = result_url.split(";base64,")[1]
                    image_data = base64.b64decode(base64_data)
                else:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.get(result_url) as resp:
                            if resp.status == 200:
                                image_data = await resp.read()
        
        if image_data:
            result["status"] = "processing"
            
            gen_result = await api.generate_img2img(
                image=image_data,
                prompt=enhance_prompt,
                model=data.get("model", "Flux_2_Klein_4B_BF16"),
                steps=4,
                guidance=3.5,
                seed=-1
            )
            
            request_id = gen_result.get("data", {}).get("request_id") or gen_result.get("request_id")
            print(f"[Workflow] imageEnhance request_id: {request_id}")
            
            if request_id:
                max_attempts = 120
                for attempt in range(max_attempts):
                    resp = await api.get_request_status(request_id)
                    status_data = resp.get("data", {})
                    api_status = status_data.get("status")
                    
                    if attempt % 10 == 0:
                        print(f"[Workflow] imageEnhance polling attempt {attempt}: status={api_status}")
                    
                    if api_status == "done":
                        result["resultUrl"] = status_data.get("result_url")
                        result["status"] = "completed"
                        print(f"[Workflow] imageEnhance completed: {result['resultUrl']}")
                        break
                    elif api_status == "error":
                        result["status"] = "failed"
                        result["error"] = status_data.get("error", "Enhancement failed")
                        print(f"[Workflow] imageEnhance failed: {result['error']}")
                        break
                    
                    await asyncio.sleep(2)
    
    elif node_type == "aiAssistant":
        # AI Assistant node - process text through AI using iFlow API
        system_prompt = data.get("systemPrompt", "You are a helpful AI assistant.")
        user_prompt = data.get("userPrompt", "")
        model = data.get("model", "kimi-k2")
        
        # Check for text input from connected nodes
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            if parent_output.get("text"):
                user_prompt = parent_output["text"]
                break
        
        print(f"[Workflow] aiAssistant - model: {model}, system_prompt: '{system_prompt[:50]}...', user_prompt: '{user_prompt[:50]}...'")
        
        if not user_prompt:
            # No prompt provided
            result["status"] = "completed"
            result["response"] = ""
            result["text"] = ""
            print(f"[Workflow] aiAssistant - no user prompt provided, skipping")
        else:
            result["status"] = "processing"
            
            try:
                # Use iFlow API for AI chat completion
                if iflow_api:
                    ai_response = await iflow_api.simple_chat(
                        user_message=user_prompt,
                        system_prompt=system_prompt,
                        model=model,
                        temperature=0.7,
                        max_tokens=2000
                    )
                    
                    if ai_response:
                        result["response"] = ai_response
                        result["text"] = ai_response  # Pass text to next nodes
                        result["status"] = "completed"
                        print(f"[Workflow] aiAssistant completed: response length={len(ai_response)}")
                    else:
                        result["status"] = "failed"
                        result["error"] = "Empty response from AI"
                else:
                    # Fallback if iFlow API is not configured
                    ai_response = f"[AI Assistant - iFlow API not configured]\n\nSystem: {system_prompt}\n\nUser: {user_prompt}\n\nPlease configure iFlow API key to enable AI assistant functionality."
                    result["response"] = ai_response
                    result["text"] = ai_response
                    result["status"] = "completed"
                    print(f"[Workflow] aiAssistant completed (fallback): iFlow API not configured")
                
            except Exception as e:
                print(f"[Workflow] aiAssistant - ERROR: {str(e)}")
                result["status"] = "failed"
                result["error"] = str(e)
    
    elif node_type == "imagePromptEnhancer":
        # Image Prompt Enhancer - enhance prompts for image generation
        original_prompt = data.get("originalPrompt", "")
        
        # Check for text input from connected nodes
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            if parent_output.get("text"):
                original_prompt = parent_output["text"]
                break
            elif parent_output.get("response"):
                original_prompt = parent_output["response"]
                break
        
        print(f"[Workflow] imagePromptEnhancer - original_prompt: '{original_prompt[:50]}...'")
        
        if original_prompt:
            result["status"] = "processing"
            
            try:
                # Call deAPI prompt enhancement endpoint
                enhance_result = await api.enhance_prompt_image(prompt=original_prompt)
                
                # Get the enhanced prompt from the response
                enhanced_prompt = enhance_result.get("data", {}).get("enhanced_prompt", "")
                
                if enhanced_prompt:
                    result["enhancedPrompt"] = enhanced_prompt
                    result["text"] = enhanced_prompt  # Pass to next nodes
                    result["status"] = "completed"
                    print(f"[Workflow] imagePromptEnhancer completed: '{enhanced_prompt[:50]}...'")
                else:
                    # Fallback: if API doesn't return enhanced prompt, use original
                    result["enhancedPrompt"] = original_prompt
                    result["text"] = original_prompt
                    result["status"] = "completed"
                    
            except Exception as e:
                print(f"[Workflow] imagePromptEnhancer - ERROR: {str(e)}")
                # Fallback: use original prompt
                result["enhancedPrompt"] = original_prompt
                result["text"] = original_prompt
                result["status"] = "completed"
    
    elif node_type == "videoPromptEnhancer":
        # Video Prompt Enhancer - enhance prompts for video generation
        original_prompt = data.get("originalPrompt", "")
        
        # Check for text input from connected nodes
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            if parent_output.get("text"):
                original_prompt = parent_output["text"]
                break
            elif parent_output.get("response"):
                original_prompt = parent_output["response"]
                break
        
        print(f"[Workflow] videoPromptEnhancer - original_prompt: '{original_prompt[:50]}...'")
        
        if original_prompt:
            result["status"] = "processing"
            
            try:
                # Call deAPI video prompt enhancement endpoint
                enhance_result = await api.enhance_prompt_video(prompt=original_prompt)
                
                # Get the enhanced prompt from the response
                enhanced_prompt = enhance_result.get("data", {}).get("enhanced_prompt", "")
                
                if enhanced_prompt:
                    result["enhancedPrompt"] = enhanced_prompt
                    result["text"] = enhanced_prompt  # Pass to next nodes
                    result["status"] = "completed"
                    print(f"[Workflow] videoPromptEnhancer completed: '{enhanced_prompt[:50]}...'")
                else:
                    # Fallback: if API doesn't return enhanced prompt, use original
                    result["enhancedPrompt"] = original_prompt
                    result["text"] = original_prompt
                    result["status"] = "completed"
                    
            except Exception as e:
                print(f"[Workflow] videoPromptEnhancer - ERROR: {str(e)}")
                # Fallback: use original prompt
                result["enhancedPrompt"] = original_prompt
                result["text"] = original_prompt
                result["status"] = "completed"
    
    elif node_type == "stickyNote":
        # Sticky Note - just a canvas annotation, no processing needed
        # Store the note text and color for persistence
        result["text"] = data.get("text", "")
        result["color"] = data.get("color", "yellow")
        result["status"] = "completed"
        print(f"[Workflow] stickyNote - stored note with color={result['color']}, text length={len(result['text'])}")
    
    elif node_type == "output":
        # Output node - just collect the result
        for parent_id in incoming_edges:
            parent_output = node_outputs.get(parent_id, {})
            result["resultUrl"] = parent_output.get("resultUrl")
            result["text"] = parent_output.get("text", "")
            result["response"] = parent_output.get("response", "")
            result["enhancedPrompt"] = parent_output.get("enhancedPrompt", "")
            result["status"] = "completed"
            break
    
    return result


@router.post("/execute")
async def execute_workflow(
    graph_data: GraphPayload,
    background_tasks: BackgroundTasks,
    request: Request
):
    """
    Execute a workflow graph and return an execution ID for polling.
    Supports BYOK (Bring Your Own Key) via X-DeAPI-Key and X-iFlow-Key headers.
    """
    # Check for custom API keys in headers (BYOK support)
    custom_api_key = request.headers.get("X-DeAPI-Key")
    custom_iflow_key = request.headers.get("X-iFlow-Key")
    
    # Generate execution ID
    execution_id = str(uuid.uuid4())
    
    # Initialize execution status
    executions[execution_id] = {
        "execution_id": execution_id,
        "status": "pending",
        "progress": 0,
        "message": "Workflow queued",
        "node_results": {},
        "error": None,
        "created_at": datetime.utcnow().isoformat(),
        "using_custom_key": bool(custom_api_key),
        "using_custom_iflow_key": bool(custom_iflow_key)
    }
    
    # Start background execution
    background_tasks.add_task(
        execute_graph_task,
        execution_id,
        graph_data,
        custom_api_key,
        custom_iflow_key
    )
    
    return {"execution_id": execution_id}


@router.get("/executions/{execution_id}")
async def get_execution_status(execution_id: str):
    """
    Get the status of a workflow execution.
    """
    if execution_id not in executions:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return executions[execution_id]


# ==================== Workflow Persistence APIs ====================

from ..database import get_db
from ..models import Workflow as WorkflowModel
from sqlalchemy.orm import Session


class WorkflowSaveRequest(BaseModel):
    name: str
    description: Optional[str] = None
    nodes: List[dict]
    edges: List[dict]


class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    node_count: int
    created_at: str
    updated_at: str


class WorkflowDetailResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    nodes: List[dict]
    edges: List[dict]
    node_count: int
    created_at: str
    updated_at: str


@router.post("/save")
async def save_workflow(
    workflow_data: WorkflowSaveRequest,
    db: Session = Depends(get_db)
):
    """
    Save a workflow to the database.
    """
    workflow = WorkflowModel(
        name=workflow_data.name,
        description=workflow_data.description,
        nodes=workflow_data.nodes,
        edges=workflow_data.edges,
        node_count=len(workflow_data.nodes)
    )
    
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    return {
        "id": workflow.id,
        "name": workflow.name,
        "message": "Workflow saved successfully"
    }


@router.get("/saved", response_model=List[WorkflowResponse])
async def list_saved_workflows(
    db: Session = Depends(get_db),
    limit: int = 20
):
    """
    List all saved workflows.
    """
    workflows = db.query(WorkflowModel).order_by(
        WorkflowModel.updated_at.desc()
    ).limit(limit).all()
    
    return [
        WorkflowResponse(
            id=w.id,
            name=w.name,
            description=w.description,
            node_count=w.node_count,
            created_at=w.created_at.isoformat() if w.created_at else "",
            updated_at=w.updated_at.isoformat() if w.updated_at else ""
        )
        for w in workflows
    ]


@router.get("/saved/{workflow_id}", response_model=WorkflowDetailResponse)
async def get_saved_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific saved workflow by ID.
    """
    workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return WorkflowDetailResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        nodes=workflow.nodes or [],
        edges=workflow.edges or [],
        node_count=workflow.node_count,
        created_at=workflow.created_at.isoformat() if workflow.created_at else "",
        updated_at=workflow.updated_at.isoformat() if workflow.updated_at else ""
    )


@router.put("/saved/{workflow_id}")
async def update_saved_workflow(
    workflow_id: int,
    workflow_data: WorkflowSaveRequest,
    db: Session = Depends(get_db)
):
    """
    Update an existing saved workflow.
    """
    workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow.name = workflow_data.name
    workflow.description = workflow_data.description
    workflow.nodes = workflow_data.nodes
    workflow.edges = workflow_data.edges
    workflow.node_count = len(workflow_data.nodes)
    
    db.commit()
    db.refresh(workflow)
    
    return {
        "id": workflow.id,
        "name": workflow.name,
        "message": "Workflow updated successfully"
    }


@router.delete("/saved/{workflow_id}")
async def delete_saved_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a saved workflow.
    """
    workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    
    return {"message": "Workflow deleted successfully"}
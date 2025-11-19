"""
AI Integration Routes
Multi-provider AI API endpoints for HeySalad platform
"""

from flask import Blueprint, jsonify, request
import os
import requests
from anthropic import Anthropic
import google.generativeai as genai

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/chat', methods=['POST'])
def chat():
    """
    Universal chat endpoint supporting multiple AI providers
    
    Request body:
    {
        "provider": "openai|anthropic|gemini|deepseek|huggingface",
        "messages": [{"role": "user", "content": "Hello"}],
        "model": "optional-model-override",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    """
    try:
        data = request.json
        provider = data.get('provider', 'openai').lower()
        messages = data.get('messages', [])
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 1000)
        
        if not messages:
            return jsonify({'error': 'No messages provided'}), 400
        
        # Route to appropriate provider
        if provider == 'openai':
            return _chat_openai(messages, data.get('model'), temperature, max_tokens)
        elif provider == 'anthropic':
            return _chat_anthropic(messages, data.get('model'), temperature, max_tokens)
        elif provider == 'gemini':
            return _chat_gemini(messages, data.get('model'), temperature, max_tokens)
        elif provider == 'deepseek':
            return _chat_deepseek(messages, data.get('model'), temperature, max_tokens)
        elif provider == 'huggingface':
            return _chat_huggingface(messages, data.get('model'), temperature, max_tokens)
        else:
            return jsonify({'error': f'Unsupported provider: {provider}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _chat_openai(messages, model=None, temperature=0.7, max_tokens=1000):
    """OpenAI chat completion"""
    import openai
    
    openai.api_key = os.getenv('OPENAI_API_KEY')
    model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return jsonify({
        'provider': 'openai',
        'model': model,
        'content': response.choices[0].message.content,
        'usage': {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
    })


def _chat_anthropic(messages, model=None, temperature=0.7, max_tokens=1000):
    """Anthropic Claude chat completion"""
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    model = model or os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
    
    # Convert messages format if needed
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            'role': msg['role'],
            'content': msg['content']
        })
    
    response = client.messages.create(
        model=model,
        messages=formatted_messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return jsonify({
        'provider': 'anthropic',
        'model': model,
        'content': response.content[0].text,
        'usage': {
            'input_tokens': response.usage.input_tokens,
            'output_tokens': response.usage.output_tokens
        }
    })


def _chat_gemini(messages, model=None, temperature=0.7, max_tokens=1000):
    """Google Gemini chat completion"""
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model_name = model or os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    model = genai.GenerativeModel(model_name)
    
    # Convert messages to Gemini format
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
    )
    
    return jsonify({
        'provider': 'gemini',
        'model': model_name,
        'content': response.text
    })


def _chat_deepseek(messages, model=None, temperature=0.7, max_tokens=1000):
    """DeepSeek chat completion"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    model = model or os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': model,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens
    }
    
    response = requests.post(
        'https://api.deepseek.com/v1/chat/completions',
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        return jsonify({'error': response.text}), response.status_code
    
    data = response.json()
    return jsonify({
        'provider': 'deepseek',
        'model': model,
        'content': data['choices'][0]['message']['content'],
        'usage': data.get('usage', {})
    })


def _chat_huggingface(messages, model=None, temperature=0.7, max_tokens=1000):
    """HuggingFace Inference API"""
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    model = model or os.getenv('HUGGINGFACE_MODEL', 'openai/gpt-oss-120b')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Convert messages to prompt
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    
    payload = {
        'inputs': prompt,
        'parameters': {
            'temperature': temperature,
            'max_new_tokens': max_tokens
        }
    }
    
    response = requests.post(
        f'https://api-inference.huggingface.co/models/{model}',
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        return jsonify({'error': response.text}), response.status_code
    
    data = response.json()
    return jsonify({
        'provider': 'huggingface',
        'model': model,
        'content': data[0]['generated_text'] if isinstance(data, list) else data.get('generated_text', '')
    })


@ai_bp.route('/image/generate', methods=['POST'])
def generate_image():
    """
    Image generation endpoint (Stability AI, DALL-E, etc.)
    
    Request body:
    {
        "provider": "stability|dalle",
        "prompt": "A beautiful sunset",
        "size": "1024x1024",
        "style": "photographic"
    }
    """
    try:
        data = request.json
        provider = data.get('provider', 'stability').lower()
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        if provider == 'stability':
            return _generate_stability(prompt, data)
        elif provider == 'dalle':
            return _generate_dalle(prompt, data)
        else:
            return jsonify({'error': f'Unsupported provider: {provider}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _generate_stability(prompt, options):
    """Stability AI image generation"""
    # Placeholder - implement when Stability AI key is added
    return jsonify({
        'provider': 'stability',
        'message': 'Stability AI integration pending',
        'prompt': prompt
    })


def _generate_dalle(prompt, options):
    """DALL-E image generation"""
    import openai
    
    openai.api_key = os.getenv('OPENAI_API_KEY')
    size = options.get('size', '1024x1024')
    
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1
    )
    
    return jsonify({
        'provider': 'dalle',
        'image_url': response.data[0].url,
        'revised_prompt': response.data[0].revised_prompt
    })


@ai_bp.route('/providers', methods=['GET'])
def list_providers():
    """List available AI providers and their status"""
    providers = {
        'openai': {
            'available': bool(os.getenv('OPENAI_API_KEY')),
            'model': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            'capabilities': ['chat', 'image']
        },
        'anthropic': {
            'available': bool(os.getenv('ANTHROPIC_API_KEY')),
            'model': os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229'),
            'capabilities': ['chat']
        },
        'gemini': {
            'available': bool(os.getenv('GEMINI_API_KEY')),
            'model': os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'),
            'capabilities': ['chat']
        },
        'deepseek': {
            'available': bool(os.getenv('DEEPSEEK_API_KEY')),
            'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
            'capabilities': ['chat']
        },
        'huggingface': {
            'available': bool(os.getenv('HUGGINGFACE_API_KEY')),
            'model': os.getenv('HUGGINGFACE_MODEL', 'openai/gpt-oss-120b'),
            'capabilities': ['chat']
        },
        'cloudflare': {
            'available': bool(os.getenv('CLOUDFLARE_API_KEY')),
            'capabilities': ['chat', 'image']
        }
    }
    
    return jsonify(providers)

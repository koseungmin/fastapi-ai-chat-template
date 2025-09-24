# _*_ coding: utf-8 _*_
"""LLM Provider Factory for supporting multiple LLM providers."""
import logging
import os
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode

logger = logging.getLogger(__name__)


class BaseLLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, model: str, max_tokens: int = 1000, temperature: float = 0.7):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    async def create_completion(self, messages: list, stream: bool = False):
        """Create completion from LLM provider"""
        raise NotImplementedError("Subclasses must implement create_completion")
    
    async def create_title_completion(self, message: str):
        """Create title completion from LLM provider"""
        raise NotImplementedError("Subclasses must implement create_title_completion")
    
    def process_stream_chunk(self, chunk) -> str:
        """Process streaming chunk and extract content"""
        raise NotImplementedError("Subclasses must implement process_stream_chunk")


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, api_key: str, model: str, max_tokens: int = 1000, temperature: float = 0.7):
        super().__init__(model, max_tokens, temperature)
        
        if not api_key:
            raise HandledException(ResponseCode.LLM_CONFIG_ERROR, msg="OpenAI API key is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        logger.info(f"OpenAI provider initialized with model: {model}")
    
    async def create_completion(self, messages: list, stream: bool = False):
        """Create completion using OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=stream
            )
            return response
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise HandledException(ResponseCode.CHAT_AI_RESPONSE_ERROR, e=e)
    
    async def create_title_completion(self, message: str):
        """Create title completion using OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "다음 질문을 기반으로 간단하고 명확한 채팅방 제목을 생성해주세요. 20자 이내로 만들어주세요."
                    },
                    {
                        "role": "user",
                        "content": f"질문: {message}"
                    }
                ],
                max_tokens=50,
                temperature=self.temperature
            )
            return response
        except Exception as e:
            logger.error(f"OpenAI title generation error: {str(e)}")
            raise HandledException(ResponseCode.CHAT_AI_RESPONSE_ERROR, e=e)
    
    def process_stream_chunk(self, chunk) -> str:
        """Process OpenAI streaming chunk and extract content"""
        if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
            return chunk.choices[0].delta.content
        return None


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI provider implementation"""
    
    def __init__(self, api_key: str, endpoint: str, deployment_name: str, 
                 api_version: str, max_tokens: int = 1000, temperature: float = 0.7):
        super().__init__(deployment_name, max_tokens, temperature)
        
        if not api_key:
            raise HandledException(ResponseCode.LLM_CONFIG_ERROR, msg="Azure OpenAI API key is required")
        if not endpoint:
            raise HandledException(ResponseCode.LLM_CONFIG_ERROR, msg="Azure OpenAI endpoint is required")
        if not deployment_name:
            raise HandledException(ResponseCode.LLM_CONFIG_ERROR, msg="Azure OpenAI deployment name is required")
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=f"{endpoint.rstrip('/')}/openai/deployments/{deployment_name}",
            default_query={"api-version": api_version}
        )
        logger.info(f"Azure OpenAI provider initialized with deployment: {deployment_name}")
    
    async def create_completion(self, messages: list, stream: bool = False):
        """Create completion using Azure OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,  # deployment name
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=stream
            )
            return response
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {str(e)}")
            raise HandledException(ResponseCode.CHAT_AI_RESPONSE_ERROR, e=e)
    
    async def create_title_completion(self, message: str):
        """Create title completion using Azure OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,  # deployment name
                messages=[
                    {
                        "role": "system",
                        "content": "다음 질문을 기반으로 간단하고 명확한 채팅방 제목을 생성해주세요. 20자 이내로 만들어주세요."
                    },
                    {
                        "role": "user",
                        "content": f"질문: {message}"
                    }
                ],
                max_tokens=50,
                temperature=self.temperature
            )
            return response
        except Exception as e:
            logger.error(f"Azure OpenAI title generation error: {str(e)}")
            raise HandledException(ResponseCode.CHAT_AI_RESPONSE_ERROR, e=e)
    
    def process_stream_chunk(self, chunk) -> str:
        """Process Azure OpenAI streaming chunk and extract content"""
        # Azure OpenAI의 첫 번째 청크는 빈 choices 배열을 가질 수 있음
        if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
            return chunk.choices[0].delta.content
        return None


class LLMProviderFactory:
    """Factory class for creating LLM providers"""
    
    @staticmethod
    def create_provider(provider_type: str = None) -> BaseLLMProvider:
        """Create LLM provider based on configuration"""
        
        # 환경 변수에서 제공자 타입 가져오기
        if not provider_type:
            provider_type = os.getenv("LLM_PROVIDER", "openai").lower()
        
        logger.info(f"Creating LLM provider: {provider_type}")
        
        if provider_type == "openai":
            return LLMProviderFactory._create_openai_provider()
        elif provider_type == "azure_openai":
            return LLMProviderFactory._create_azure_openai_provider()
        else:
            raise HandledException(
                ResponseCode.LLM_CONFIG_ERROR, 
                msg=f"Unsupported LLM provider: {provider_type}. Supported providers: openai, azure_openai"
            )
    
    @staticmethod
    def _create_openai_provider() -> OpenAIProvider:
        """Create OpenAI provider"""
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        return OpenAIProvider(
            api_key=api_key,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    @staticmethod
    def _create_azure_openai_provider() -> AzureOpenAIProvider:
        """Create Azure OpenAI provider"""
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        max_tokens = int(os.getenv("AZURE_OPENAI_MAX_TOKENS", "1000"))
        temperature = float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.7"))
        
        return AzureOpenAIProvider(
            api_key=api_key,
            endpoint=endpoint,
            deployment_name=deployment_name,
            api_version=api_version,
            max_tokens=max_tokens,
            temperature=temperature
        )

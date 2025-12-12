from langchain_core.language_models.llms import LLM, BaseCache, Callbacks
from yandex_cloud_ml_sdk import YCloudML
from typing import Any, Dict, List, Optional, Sequence, Union
from langchain_core.outputs import Generation, LLMResult
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
import asyncio

from src.config import settings



class YandexGPT(LLM):
    """LangChain интеграция с YandexGPT."""

    model_name: str = "yandexgpt"
    temperature: float = 0.0
    max_tokens: int = 2000
    folder_id: str = settings.YANDEX_FOLDER_ID
    api_key: str = settings.YANDEX_API_KEY
    sdk: Any = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sdk = YCloudML(
            folder_id=self.folder_id,
            auth=self.api_key,
        )


    @property
    def _llm_type(self) -> str:
        """Возвращает тип LLM."""
        return "yandexgpt"

    def _convert_messages_to_yandex_format(
        self,
        messages: Sequence[BaseMessage]
      ) -> List[Dict[str, str]]:
        """Конвертирует сообщения LangChain в формат YandexGPT."""

        yandex_messages = []
        for message in messages:
            if isinstance(message, SystemMessage):
                yandex_messages.append({"role": "system", "text": message.content})
            elif isinstance(message, HumanMessage):
                yandex_messages.append({"role": "user", "text": message.content})
        return yandex_messages

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Вызывает YandexGPT с заданным промптом."""

        messages = [{"role": "user", "text": prompt}]

        # Добавляем системный промпт, если он есть
        if "system_prompt" in kwargs:
            messages.insert(0, {"role": "system", "text": kwargs["system_prompt"]})

        try:
            result = (
                self.sdk.models.completions(self.model_name)
                .configure(
                    temperature=kwargs.get("temperature", self.temperature),
                    max_tokens=kwargs.get("max_tokens", self.max_tokens)
                )
                .run(messages)
            )

            if result:
                return result[0].text

            return "Нет ответа"
        except Exception as e:
            raise


    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Генерирует ответы на промпты."""
        generations = []
        for prompt in prompts:
            messages = [{"role": "user", "text": prompt}]

            # Добавляем системный промпт, если он есть
            if "system_prompt" in kwargs:
                messages.insert(0, {"role": "system", "text": kwargs["system_prompt"]})

            result = (
                self.sdk.models.completions(self.model_name)
                .configure(
                    temperature=kwargs.get("temperature", self.temperature),
                    max_tokens=kwargs.get("max_tokens", self.max_tokens)
                )
                .run(messages)
            )

            if result:
                text = result[0].text
            else:
                text = "Нет ответа"

            generations.append([Generation(text=text)])

        return LLMResult(generations=generations)


    def invoke(
        self,
        input: str | BaseMessage | List[BaseMessage],
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        """Вызывает модель с заданным вводом."""

        if isinstance(input, str):
            messages = [{"role": "user", "text": input}]

        elif isinstance(input, BaseMessage):
            messages = [{"role": "user", "text": input.content}]

        else:
            messages = self._convert_messages_to_yandex_format(input)

        try:
            result = (
                self.sdk.models.completions(self.model_name)
                .configure(
                    temperature=kwargs.get("temperature", self.temperature),
                    max_tokens=kwargs.get("max_tokens", self.max_tokens)
                )
                .run(messages)
            )

            if result:
                return result[0].text

            return "Нет ответа"
        except Exception as e:
            raise


    async def ainvoke(
        self,
        input: str | BaseMessage | List[BaseMessage],
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        """Асинхронно вызывает модель с заданным вводом."""

        if isinstance(input, str):
            messages = [{"role": "user", "text": input}]

        elif isinstance(input, BaseMessage):
            messages = [{"role": "user", "text": input.content}]

        else:
            messages = self._convert_messages_to_yandex_format(input)

        try:
            # Создаем конфигурацию запроса
            completion = (
                self.sdk.models.completions(self.model_name)
                .configure(
                    temperature=kwargs.get("temperature", self.temperature),
                    max_tokens=kwargs.get("max_tokens", self.max_tokens)
                )
            )

            # Выполняем синхронный API-запрос в отдельном потоке
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: completion.run(messages)
            )

            if result:
                text_result = result[0].text
                return text_result

            return "Нет ответа"
        except Exception as e:
            raise

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Возвращает параметры, идентифицирующие модель."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "folder_id": self.folder_id
        }
    
YandexGPT.model_rebuild()
yandex_gpt = YandexGPT()
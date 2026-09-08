from abc import ABC, abstractmethod
from typing import Optional
from loguru import logger


# ==========================================================
# BASE LLM
# ==========================================================

class LLMAGENT(ABC):

    """
    Interface dasar Large Language Model.

    Agent tidak peduli apakah modelnya:

    - Qwen
    - Ollama
    - OpenAI
    - model lain

    Agent hanya melakukan:

        llm.generate(prompt)

    dan menerima:

        string
    """

    def __init__(
        self,
        model: Optional[str] = None
    ):

        self.model = model

    # ======================================================
    # GENERATE
    # ======================================================

    @abstractmethod
    def generate(
        self,
        prompt: str
    ) -> str:

        raise NotImplementedError


# ==========================================================
# OLLAMA
# ==========================================================

class OllamaLLM(LLMAGENT):

    def __init__(
        self,
        model: str = "qwen3:1.7b",
        host: str = "http://localhost:11434",
        think: bool = False,
        keep_alive: str = "30m",
        tools:Optional[any] = None
    ):

        super().__init__(
            model=model
        )

        self.host = host

        self.think = think

        self.keep_alive = keep_alive
        
        self.tools = tools

        try:

            from ollama import Client

            self.client = Client(
                host=self.host
            )

        except Exception as e:

            logger.exception(
                "Gagal membuat Ollama Client."
            )

            raise

        logger.info(
            f"Ollama initialized | "
            f"model={self.model} | "
            f"host={self.host}"
        )

    # ======================================================
    # GENERATE
    # ======================================================

    def generate(
        self,
        msg: str
    ) -> str:

       

        if not msg:

            return ""

        try:

            # print(f"messages to send to Ollama API: \n{msg}")
            response = self.client.chat(

                model=self.model,

                think=self.think,

                keep_alive=self.keep_alive,

                messages=msg,
                
                tools=self.tools

            )

        except Exception as e:

            logger.exception(
                f"Ollama request gagal: {e}"
            )

            raise

        # ==================================================
        # RESPONSE
        # ==================================================

   

        return response


# ==========================================================
# FACTORY
# ==========================================================

def create_llm(
    model: str = "qwen3:1.7b"
) -> LLMAGENT:

    return OllamaLLM(
        model=model
    )
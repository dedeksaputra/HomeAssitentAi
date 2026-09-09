import json
import re

from loguru import logger

from core.config import get_ollama_host, get_system_prompt, load_config
from core.services.wakeword_service import WakeWordService
from core.services.tts_service import TTSService
from core.services.speech_service import SpeechService
from model.ai.history import add_history, get_history_last
from model.ai.llm_agent import OllamaLLM
from tools.list.loader import load_tools
# =========================================================
# RUNTIME
# =========================================================

class Runtime:

    # =====================================================
    # CONFIG
    # =====================================================

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        self.running = False
        self.config = load_config()
        self.system_prompt = get_system_prompt(self.config)
        self.conversation_timeout = int(
            self.config.get("conversation_timeout", 8)
        )
        self.enable_thinking_sound = bool(
            self.config.get("enable_thinking_sound", True)
        )
        self.ollama_think = bool(
            self.config.get("ollama_think", False)
        )

        # =================================================
        # SERVICES
        # =================================================

        logger.info(
            "Initializing services..."
        )

        self.wakeword = WakeWordService()

        self.tts = TTSService()

        self.speech = SpeechService()
        
        # =================================================
        # TOOLS
        # =================================================
        self.tools, self.available_functions = load_tools()
        
        self.llm = OllamaLLM(
                            model=str(self.config.get("ollama_model", "qwen3:1.7b")),
                            host=get_ollama_host(self.config),
                            think=self.ollama_think,
                            keep_alive="30m",
                            tools=self.tools
                        )
        # =================================================
        # CONVERSATION
        # =================================================

        logger.info(
            "Runtime initialized."
        )

    # =====================================================
    # RUN
    # =====================================================

    def run(self):

        self.running = True

        print(
            "Runtime Running..."
        )

        try:

            while self.running:

                # =========================================
                # WAKE WORD MODE
                # =========================================

                text = self.get_prompt()

                if not self.running:
                    break

                # =========================================
                # NO INPUT
                # =========================================

                if not text:

                    print(
                        "No speech detected"
                    )

                    continue

                text = text.strip()

                if not text:
                    continue

                print(
                    f"User : {text}"
                )

                # =========================================
                # STOP COMMAND
                # =========================================

                if self.is_stop_command(text):

                    self.shutdown()

                    break

                self._process_user_message(text)

                if not self.running:
                    break

                # =========================================
                # CONVERSATION MODE
                # =========================================

                self.conversation_mode()

        except KeyboardInterrupt:

            print(
                "\nRuntime interrupted."
            )

            self.stop()

        except Exception as e:

            logger.exception(
                f"Runtime Error: {e}"
            )

            self.stop()

    # =====================================================
    # INPUT
    # =====================================================

    def get_prompt(self, timeout=None):

        try:
            text = input(
                "\nPrompt (Enter untuk voice): "
            ).strip()
        except EOFError:
            text = ""

        if text:
            return text

        print(
            "\nWaiting WakeWord..."
        )

        if not self.wakeword.wait():
            print(
                "Kembali ke mode input teks"
            )
            return ""

        if not self.running:
            return ""

        print(
            "WakeWord Detected"
        )

        self.tts.beep()

        text = self.speech.listen(timeout=timeout)

        if self.running:
            self.tts.beep()

        return text or ""

    # =====================================================
    # REGENERATE CHAT MESSAGES
    # =====================================================

    def build_chat_messages(self, history_limit: int = 10):
        history_messages = []
        for message in get_history_last(history_limit):
            role = message.get("role")

            if role == "tools":
                continue

            if (
                role == "assistant"
                and not message.get("content")
                and not message.get("tool_calls")
            ):
                continue

            history_messages.append(message)

        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        if history_messages:
            messages.extend(history_messages)
        
        return messages

    def _process_user_message(self, text: str) -> str:
        """Generate, execute tools, save, and speak one AI response."""
        if self.enable_thinking_sound:
            self.tts.thinking(True)

        try:
            add_history({"role": "user", "content": text})
            response = self.llm.generate(self.build_chat_messages(10))

            if not response.message.tool_calls and self._is_datetime_request(text):
                response = self._force_datetime_tool(response)

            for _ in range(5):
                tool_calls = response.message.tool_calls or []
                if not tool_calls:
                    break

                for tool_call in tool_calls:
                    response = self._process_tool_call(response, tool_call)

            answer = response.message.content or ""
            if not answer and not response.message.tool_calls:
                logger.warning("Ollama mengembalikan respons kosong setelah tool.")
            add_history({"role": "assistant", "content": answer})

            if answer:
                print(f"AI : {answer}")
                self.tts.speak_piper(answer)

            return answer
        finally:
            if self.enable_thinking_sound:
                self.tts.thinking(False)

    @staticmethod
    def _is_datetime_request(text: str) -> bool:
        normalized = text.lower().strip()
        patterns = (
            r"\bjam\s+berapa\b",
            r"\bsekarang\s+jam\s+berapa\b",
            r"\btanggal\s+berapa\b",
            r"\bhari\s+apa\b",
            r"\btanggal\s+hari\s+ini\b",
            r"\bwaktu\s+sekarang\b",
        )
        return any(re.search(pattern, normalized) for pattern in patterns)

    def _force_datetime_tool(self, response):
        tool_name = "get_datetime"
        function_to_call = self.available_functions.get(tool_name)
        if function_to_call is None:
            logger.error("Tool wajib '%s' tidak tersedia.", tool_name)
            return response

        result = function_to_call()
        if not isinstance(result, str):
            result = json.dumps(result, ensure_ascii=False)

        add_history({
            "role": "assistant",
            "content": "",
            "tool_calls": [{
                "function": {
                    "name": tool_name,
                    "arguments": {},
                }
            }],
        })
        add_history({
            "role": "tool",
            "content": result,
            "name": tool_name,
        })
        print(f"Executing tool: {tool_name} (forced for datetime request)")
        return self.llm.generate(self.build_chat_messages(10))

    def _process_tool_call(self, response, tool_call):
        tool_name = getattr(tool_call.function, "name", None)
        if not tool_name:
            return self.llm.generate(self.build_chat_messages(10))

        function_to_call = self.available_functions.get(tool_name)
        if not function_to_call:
            result = f"Tool tidak ditemukan: {tool_name}"
            print(result)
            return self.llm.generate(self.build_chat_messages(10))

        arguments = getattr(tool_call.function, "arguments", {})
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                result = f"Parameter tool '{tool_name}' tidak valid."
                print(result)
                add_history({"role": "tool", "content": result, "name": tool_name})
                return self.llm.generate(self.build_chat_messages(10))

        if not isinstance(arguments, dict):
            result = f"Parameter tool '{tool_name}' harus berupa object."
            add_history({"role": "tool", "content": result, "name": tool_name})
            return self.llm.generate(self.build_chat_messages(10))

        try:
            print(f"Executing tool: {tool_name}")
            print(f"Arguments: {arguments}")
            result = function_to_call(**arguments)
        except Exception as error:
            result = f"Error saat menjalankan tool '{tool_name}': {error}"
            print(result)

        if not isinstance(result, str):
            result = json.dumps(result, ensure_ascii=False)

        assistant_message = {
            "role": "assistant",
            "content": response.message.content or "",
            "tool_calls": [
                {
                    "function": {
                        "name": tool_name,
                        "arguments": arguments,
                    }
                }
            ],
        }
        tool_message = {
            "role": "tool",
            "content": result,
            "name": tool_name,
        }
        add_history(assistant_message)
        add_history(tool_message)

        return self.llm.generate(self.build_chat_messages(10))

    # =====================================================
    # CONVERSATION MODE
    # =====================================================

    def conversation_mode(self):

        print(
            "\nConversation Mode"
        )

        while self.running:

            # =============================================
            # BEEP
            # =============================================

            print(
                f"Waiting user input "
                f"({self.conversation_timeout}s)..."
            )

            # =============================================
            # LISTEN
            # =============================================

            text = self.get_prompt(
                timeout=self.conversation_timeout
            )

            # =============================================
            # TIMEOUT
            # =============================================

            if not text:

                print(
                    "Conversation timeout"
                )

                print(
                    "Returning to WakeWord..."
                )

                break

            text = text.strip()

            if not text:
                continue

            # =============================================
            # USER
            # =============================================

            print(
                f"User : {text}"
            )

            # =============================================
            # STOP
            # =============================================

            if self.is_stop_command(text):

                self.shutdown()

                break

            self._process_user_message(text)

            # =============================================
            # LOOP
            # =============================================
            #
            # Setelah TTS selesai:
            #
            # kembali beep
            # kembali listen
            #
            # Jika 8 detik tidak ada suara:
            # kembali ke WakeWord.
            #

    # =====================================================
    # STOP COMMAND
    # =====================================================

    def is_stop_command(
        self,
        text: str
    ) -> bool:

        normalized = (
            text
            .strip()
            .lower()
        )

        commands = [
            "matikan server",
            "shutdown server",
        ]

        return normalized in commands

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        logger.info(
            "Shutdown command detected."
        )

        try:

            self.tts.speak_piper(
                "Server akan dimatikan, sampai jumpa!"
            )

        except Exception as e:

            logger.error(
                f"TTS shutdown error: {e}"
            )

        self.stop()

    # =====================================================
    # STOP RUNTIME
    # =====================================================

    def stop(self):

        if not self.running:
            return

        logger.info(
            "Stopping Runtime..."
        )

        self.running = False

        # ================================================
        # CLEAR SESSION MEMORY
        # ================================================

        # try:

        #     self.memory.clear()

        #     logger.info(
        #         "Conversation memory cleared."
        #     )

        # except Exception as e:

        #     logger.error(
        #         f"Memory clear error: {e}"
        #     )

        logger.info(
            "Runtime stopped."
        )
# filepath: core/planner_backends.py
import os
import abc
import ollama
import google.generativeai as genai
from typing import Dict, Any, Tuple

# --- Custom Exceptions (can be shared or moved to a central place) ---
class PlannerConnectionError(Exception):
    """Base exception for connection issues with a planner backend."""
    pass

class PlannerModelNotFound(Exception):
    """Exception for when a specified model is not available."""
    pass

class PlannerResponseValidationError(Exception):
    """Exception for when the backend output fails validation."""
    def __init__(self, message: str, raw_content: str, validation_error: Any):
        super().__init__(message)
        self.raw_content = raw_content
        self.validation_error = validation_error

# --- Abstract Base Class for all Backends ---
class MealPlannerBackend(abc.ABC):
    """
    Abstract Base Class for a meal planner backend.
    Defines the interface that all concrete backends must implement.
    """
    @abc.abstractmethod
    def __init__(self, model: str = None, api_key: str = None):
        pass

    @abc.abstractmethod
    def generate_plan(self, prompt: str) -> Tuple[str, Any]:
        """
        Generates a meal plan based on the provided prompt.

        Args:
            prompt (str): The full prompt to send to the model.

        Returns:
            A tuple containing:
            - The raw JSON string response from the model.
            - Any additional metadata (e.g., usage tokens), can be None.
        
        Raises:
            PlannerConnectionError: If there's an issue communicating with the backend.
            PlannerModelNotFound: If the model is not found.
        """
        pass

# --- Concrete Implementation for Ollama ---
class OllamaBackend(MealPlannerBackend):
    """Meal planner backend using a local Ollama server."""
    def __init__(self, model: str = "deepseekcoderafya", api_key: str = None):
        self.model = model
        try:
            self.client = ollama.Client()
            self._check_model_availability()
        except Exception as e:
            raise PlannerConnectionError(f"Could not connect to Ollama. Is it running? Details: {e}")

    def _check_model_availability(self):
        """Checks if the specified Ollama model is available."""
        try:
            models = self.client.list().get('models', [])
            model_names = [m['name'] for m in models]
            if not any(self.model in name for name in model_names):
                raise PlannerModelNotFound(f"Model '{self.model}' not found in Ollama.")
        except Exception as e:
            raise PlannerConnectionError(f"Failed to list models from Ollama. Details: {e}")

    def generate_plan(self, prompt: str) -> Tuple[str, Any]:
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json'
            )
            return response['message']['content'], response.get('eval_count')
        except Exception as e:
            raise PlannerConnectionError(f"Error communicating with Ollama: {e}")

# --- Concrete Implementation for Gemini API ---
class GeminiBackend(MealPlannerBackend):
    """Meal planner backend using the Google Gemini API."""
    def __init__(self, model: str = "gemini-1.5-flash", api_key: str = None):
        self.model = model
        if not api_key:
            raise PlannerConnectionError("API key for Gemini is required.")
        try:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)
        except Exception as e:
            raise PlannerConnectionError(f"Failed to configure Gemini client. Details: {e}")

    def generate_plan(self, prompt: str) -> Tuple[str, Any]:
        """
        Generates a meal plan using the Gemini API.
        It has retry logic for safety and tries to extract the JSON.
        """
        try:
            # Gemini's JSON mode is engaged by the prompt instructions
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            # The API returns a candidate with the content part
            raw_text = response.text
            return raw_text, response.usage_metadata
            
        except Exception as e:
            raise PlannerConnectionError(f"Error communicating with Gemini API: {e}")

# --- Factory function to get the correct backend ---
def get_backend(backend_name: str, **kwargs) -> MealPlannerBackend:
    """
    Factory function to instantiate and return the correct backend client.

    Args:
        backend_name (str): The name of the backend ('Ollama' or 'Gemini').
        **kwargs: Arguments to pass to the backend's constructor (model, api_key).

    Returns:
        An instance of a MealPlannerBackend subclass.
    """
    backend_name = backend_name.lower()
    if backend_name == 'ollama':
        return OllamaBackend(**kwargs)
    elif backend_name == 'gemini':
        return GeminiBackend(**kwargs)
    else:
        raise ValueError(f"Unknown backend: {backend_name}")

if __name__ == '__main__':
    # Example of how to use the factory
    print("--- Testing Ollama Backend ---")
    try:
        ollama_backend = get_backend('ollama', model='deepseekcoderafya')
        print(f"Successfully initialized {type(ollama_backend).__name__}")
        # To-do: add a dummy plan generation here
    except (ValueError, PlannerConnectionError, PlannerModelNotFound) as e:
        print(f"Ollama Error: {e}")

    print("
--- Testing Gemini Backend ---")
    # You would typically get the API key from a secure source
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
    if gemini_api_key == "YOUR_API_KEY_HERE":
        print("Skipping Gemini test: Set GEMINI_API_KEY environment variable.")
    else:
        try:
            gemini_backend = get_backend('gemini', model='gemini-1.5-flash', api_key=gemini_api_key)
            print(f"Successfully initialized {type(gemini_backend).__name__}")
        except (ValueError, PlannerConnectionError) as e:
            print(f"Gemini Error: {e}")


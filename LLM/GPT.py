from openai import OpenAI

class GPT:
    """
    A class for interacting with the OpenAI ChatGPT API.

    Attributes
    ----------
    client : OpenAI
        An instance of the OpenAI API client.
    model : str
        The model to be used for generating chat completions (default is "gpt-3.5-turbo").

    Methods
    -------
    chatcompletion(messages, temperature=0.3):
        Generates a response from the ChatGPT model based on the provided messages.
    """
    def __init__(self, model="gpt-3.5-turbo"):
        """
        Initializes the GPT class.

        Parameters
        ----------
        model : str, optional
            The name of the ChatGPT model to be used (default is "gpt-3.5-turbo").
        """
        self.client = OpenAI()
        self.model = model

    def chatcompletion(self, messages):
        """
        Generates a response from the ChatGPT model.

        Parameters
        ----------
        messages : list of dict
            A list of message dictionaries representing the conversation history. Each dictionary
            should have the keys "role" (e.g., "system", "user", or "assistant") and "content" (str).

        Returns
        -------
        str
            The generated response from the ChatGPT model.
        """

        completion = self.client.chat.completions.create(
        model=self.model,
        messages=messages
        )     

        return completion.choices[0].message.content
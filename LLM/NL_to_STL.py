from .GPT import *
from STL.STL_to_path import *
import os
from basics.logger import color_text

class NL_to_STL:
    """
    Class for converting natural language instructions to STL (Signal Temporal Logic) formulas
    and extracting relevant pecifications for motion planning.

    Attributes
    ----------
    objects : list
        List of objects referenced in the natural language instructions.
    N : int
        Maximum number of time steps for the STL formula.
    dt : float
        Time step size.
    print_instructions : bool
        Whether to print the system's instructions for debugging purposes.
    gpt : GPT
        Instance of the GPT class for interacting with ChatGPT.

    Methods
    -------
    get_specs(messages)
        Extracts the STL specification from the latest GPT response.
    gpt_conversation(...)
        Conducts a GPT-powered conversation to refine natural language into specifications.
    gpt_syntax_checker(spec)
        Checks and validates the syntax of an STL specification using GPT.
    load_chatgpt_instructions(filename)
        Loads instructions for GPT from a file.
    insert_instruction_variables(instructions)
        Replaces placeholders in instructions with specific variables.
    extract_spec(response)
        Extracts the STL specification from a GPT response.
    spec_accepted_check(response)
        Checks if a GPT response contains <accepted> or <rejected>.
    """

    def __init__(self, objects, N, dt, print_instructions=False, GPT_model="gpt-3.5-turbo"):
        """
        Initializes the NL_to_STL class.

        Parameters
        ----------
        objects : list
            List of objects referenced in the natural language instructions.
        N : int
            Maximum number of time steps for the STL formula.
        dt : float
            Time step size.
        print_instructions : bool, optional
            Whether to print the system's instructions for debugging (default is False).
        GPT_model : str, optional
            The GPT model to use for ChatGPT interaction (default is "gpt-3.5-turbo").
        """
        self.objects = objects
        self.dt = dt
        self.N = N
        self.print_instructions = print_instructions
        self.gpt = GPT(GPT_model)

    def get_specs(self, messages):
        """
        Extracts the STL specification from the latest GPT response.

        Parameters
        ----------
        messages : list of dict
            List of message dictionaries from the GPT conversation.

        Returns
        -------
        str
            Extracted STL specification.
        """
        print("Extracting the specification...")
        response = messages[-1]['content']
        spec = self.extract_spec(response)
        return spec

    def gpt_conversation(self, 
                         instructions_file, 
                         max_inputs=10, 
                         previous_messages=[], 
                         processing_feedback=False, 
                         status="active", 
                         automated_user=False, 
                         automated_user_input="",
                         ):
        """
        Conducts a GPT-powered conversation to refine natural language into STL specifications.

        Parameters
        ----------
        instructions_file : str
            Filename of the instructions file to load.
        max_inputs : int, optional
            Maximum number of user inputs allowed in the conversation (default is 10).
        previous_messages : list of dict, optional
            Previous conversation messages to continue from (default is an empty list).
        processing_feedback : bool, optional
            Whether the conversation is processing feedback (default is False).
        status : str, optional
            Status of the conversation (default is "active").
        automated_user : bool, optional
            Whether to simulate an automated user providing predefined input (default is False).
        automated_user_input : str, optional
            Input for the automated user (default is an empty string).

        Returns
        -------
        tuple
            Updated messages list and the final status of the conversation (active or exited).
        """
        if not previous_messages:
            instructions_template = self.load_chatgpt_instructions(instructions_file)
            instructions = self.insert_instruction_variables(instructions_template)
            if self.print_instructions:
                print("Instructions: ", instructions, "\n", "______________________________")
            messages = [{"role": "system", "content": instructions}]
        else:
            messages = previous_messages   

        if processing_feedback:
            print(color_text("Processing feedback...", 'yellow'))
            messages.append({
                "role": "system", 
                "content": "Please return a new specification directly, based on the feedback."
                })    
            response = self.gpt.chatcompletion(messages)
            messages.append({"role": "assistant", "content": response})
            print(color_text("Assistant:", 'cyan'), response)
        else:
            if not automated_user:
                print("Please specify the task. Type 'quit' to exit conversation and generate the final trajectory.")
                for _ in range(max_inputs):
                    user_input = input(color_text("User: ", 'orange'))

                    if user_input.lower() == 'quit':
                        print(color_text("Exited conversation", 'yellow'))
                        status = "exited"
                        break

                    messages.append({"role": "user", "content": user_input})
                    response = self.gpt.chatcompletion(messages)
                    messages.append({"role": "assistant", "content": response})
                    print(color_text("Assistant:", 'cyan'), response)

                    # check if < or > symbol is present in the response and exit conversation if detected
                    if '<' in response:
                        print("The final response was generated.")
                        break
            else:
                print(color_text("Automated user: ", 'orange'), automated_user_input)
                messages.append({"role": "user", "content": automated_user_input})
                for _ in range(max_inputs):
                    response = self.gpt.chatcompletion(messages)
                    messages.append({"role": "assistant", "content": response})
                    print(color_text("Assistant:", 'cyan'), response)

                    if '<' in response:
                            print("The final response was generated.")
                            break
                    else:
                        messages.append({"role": "system", "content": "Please provide the specification now."})
                        print("The final response was not generated correctly. Trying again...")

        return messages, status
    
    def gpt_syntax_checker(self, spec):
        """
        Validates and refines the syntax of an STL specification.

        Parameters
        ----------
        spec : str
            The STL specification to validate.

        Returns
        -------
        str
            Refined STL specification.
        """
        instructions_template = self.load_chatgpt_instructions('syntax_checker_instructions.txt')
        instructions = self.insert_instruction_variables(instructions_template)
        messages = [{"role": "system", "content": instructions}]
        messages.append({"role": "user", "content": f'Original specification: {spec}'})
        response = self.gpt.chatcompletion(messages)
        print(color_text("Syntax checker:", 'purple'), response)
        new_spec = self.extract_spec(response)
        return new_spec
    
    def load_chatgpt_instructions(self, filename):
        """
        Loads instructions for GPT from a file.

        Parameters
        ----------
        filename : str
            Name of the file containing instructions.

        Returns
        -------
        str
            Instructions loaded from the file.
        """
        current_path = os.path.dirname(os.path.abspath(__file__))
        folder = 'instructions'
        path = os.path.join(current_path, folder, filename)
        with open(path, 'r') as instructions_file:
            instructions = instructions_file.read()
        return instructions
    
    def insert_instruction_variables(self, instructions):
        """
        Replaces placeholders (objects and time horizon) in the instructions with specific variables.

        Parameters
        ----------
        instructions : str
            Instruction template containing placeholders.

        Returns
        -------
        str
            Instruction template with placeholders replaced.
        """
        # Attempt to replace OBJECTS placeholder
        if "OBJECTS" in instructions:
            instructions = instructions.replace("OBJECTS", str(self.objects))
        
        # Attempt to replace T_MAX placeholder
        if "T_MAX" in instructions:
            instructions = instructions.replace("T_MAX", str(self.N))
        
        return instructions
    
    def extract_spec(self, response):
        """
        Extracts the STL specification (between <...>) from a GPT response.

        Parameters
        ----------
        response : str
            GPT response containing the STL specification.

        Returns
        -------
        str
            Extracted STL specification.
        """
        last_spec = ""
        start = 0

        while True:
            start = response.find("<", start)
            if start == -1:
                break
            end = response.find(">", start)
            if end == -1:
                break
            last_spec = response[start + 1:end]  # Extract content between < and >
            start = end + 1  # Move forward to continue searching

        # Check if a specification was found; raise an error if not
        if not last_spec:
            raise ValueError("No specification found in the response.")

        # Clean and return the found specification
        return last_spec.replace("\n", " ")
    
    def spec_accepted_check(self, response):
        """
        Check if GPT response contains <accepted> or <rejected>.
        """
        if "<accepted>" in response:
            return True
        elif "<rejected>" in response:
            return False
        else:
            return None
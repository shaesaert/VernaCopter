# VernaCopter

**Author**: **Teun van de Laar** ([tavdlaar@gmail.com](mailto:tavdlaar@gmail.com)), **Jake Rap** ([j.e.w.rap@tue.nl](mailto:j.e.w.rap@tue.nl)), & **Sofie Haesaert**

![Blender_trajectory_cropped_2](https://github.com/user-attachments/assets/933817f1-721d-40bd-854a-4e9ebd1ba113)

This repository presents the code for VernaCopter, a framework for natural language-based drone control. The framework leverages large language models (LLMs) to translate task specifications in natural language into Signal Temporal Logic (STL) specifications. These specifications operate on user-defined objects and are used for trajectory optimization.

## Table of Contents
1. [Abstract](#abstract)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Configuration](#configuration)
5. [Authors and Acknowledgments](#authors-and-acknowledgments)
6. [Contact Information](#contact-information)

## Paper

The original paper can be found on [this webpage](https://www.arxiv.org/abs/2409.09536).

Abstract:
The ability to control robots was traditionally chiefly attributed to experts. However, the recent emergence of Large Language Models (LLMs) enables users to command robots using LLMs’ exceptional natural language processing abilities. Previous studies applied LLMs to convert tasks in natural language into robot controllers using a set of predefined high-level operations. However, this approach does not guarantee safety or optimality. This thesis introduces VernaCopter, a system that empowers non-technical users to control quadrocopters using natural language. Signal Temporal Logic (STL) functions as an intermediate representation of tasks specified in natural language. The LLM is responsible for task planning, whereas formal methods handle motion planning, addressing the abovementioned limitations. Automatic LLM-based syntax and semantics checkers are employed to improve the quality of STL specifications. The system’s performance was tested in experiments in varying scenarios, varying user involvement, and with and without automatic checkers. The experiments showed that including the user in conversation improves performance. Furthermore, the specific LLM used plays a significant role in the performance, while the checkers do not benefit the system due to frequent miscorrections.

## Installation

### Prerequisites

Before starting, ensure you have the following:
- Python 3.10 or higher.
- An OpenAI API key. If you don't have one, you can sign up and obtain it from [OpenAI](https://beta.openai.com/signup/).
- [Gurobi](https://support.gurobi.com/hc/en-us/articles/14799677517585-Getting-Started-with-Gurobi-Optimizer) installed and set up. Gurobi is free for academic use.

### Steps to Install

1. **Clone the Repository**:
Clone this repository and the stlpy repository
```bash
git clone https://github.com/shaesaert/VernaCopter.git
git clone https://github.com/shaesaert/stlpy.git

cd VernaCopter
```

2. **Create a virtual environment**:

```bash
conda create -n vernacopter_env python=3.10 -y

conda activate vernacopter_env
```



3. **Install the Dependencies**:
First go to the folder of stlpy and run
```bash 
pip install -e .
```
Then go to the folder of Vernacopter and run
```bash 
pip install -r requirements.txt
```

4. **Configure the OpenAI API Key (Set your OpenAI API key as an environment variable)**:

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

## Usage

### Running the default example

To test the system interactively, run:

```bash
python -m examples.default_example
```

### Running in Automatic Mode

For a one-shot example that runs without interaction:

```bash
python -m examples.one_shot_automatic
```

### Expected Output

The program will:

1. Prompt you to specify tasks in natural language (default example).
2. Generate and optimize a trajectory based on the STL specifications.
3. Display the drone's simulated behavior using PyBullet.

## Configuration

You can configure the following parameters in basics/setup.py:

- Maximum Acceleration: Adjust the drone's maximum allowed acceleration.
- Speed: Set the drone's top speed.
- Scenario Options: Define the objects and environment for task execution.

Other configuration options can be found in basics/setup.py

## Authors and Acknowledgments

- **Author 1** - *Initial work* - [Teun van de Laar](https://github.com/TeunvdL)
- **Author 2** - *Follow-up work* - [Sofie Haeseart](https://github.com/shaesaert)

## Contact Information

For any questions, please contact [tavdlaar@gmail.com](mailto:tavdlaar@gmail.com).

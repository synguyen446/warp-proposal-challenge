# Warp - Live Proposal Builder Challenge

## Installation
#### 1. Create a virtual environment
#### 2. Install dependencies
- No AI (Faster install)
```bash
pip install -r requirements.txt
```
- With AI that use pytorch cuda
```bash
pip install -r requirements_cuda.txt
```
## Run Application
Make sure you are in root directory: `warp-proposal-challenge/`
#### 1. Run with no AI or cloud AI
```bash
python -m solution.main_pipeline --no-ai
```
#### 2. Run with AI (Can only run when you install dependencies from requirements_cuda.txt)
```bash
python -m solution.main_pipeline
```
## Python UI
You can also run python UI with the following command
```bash
pythoon -m solution.ui path/to/folder/containing/proposals.json
```
<img width="529" height="166" alt="image" src="https://github.com/user-attachments/assets/e45760c0-0f6d-424f-a0a7-036d50c07126" />  

In the image would be:
```bash
pythoon -m solution.ui Downloads\warp-proposal-challenge\out\calls
```
The Representation will have the option to view the dashboard of any proposal.json and compare them after a change is made.

<img width="818" height="455" alt="image" src="https://github.com/user-attachments/assets/e3720967-5907-4dd0-bb42-c3fa723fc0aa" />


## Assessments
### 1. Which model provider you used and why
I chose ollama because it has lots of options to choose from. If I want efficiency and quick, I can choose llama3.2 (1B). If I want more accuracy, I can choose qwen2.5:7b. Also, the model is local so there is no limitation in term of cost and tokens.

### 2. Whether you read data/ directly or went through mock/server.py
I read data directly from data/*.csv

### 3. Your validate.py output, reported honestly
<img width="1090" height="241" alt="image" src="https://github.com/user-attachments/assets/a41f8996-fb52-43cf-bec0-39bd21e461dd" />

### 4. A "Decisions and tradeoffs" section: what you chose, what you cut, where your tool fails, and what you would do next with more time


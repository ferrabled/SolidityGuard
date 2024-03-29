# Solidity Guard

<img src="https://github.com/ferrabled/SolidityGuard/blob/main/SolidityGuard.png">


SolidityGuard is a Python tool that searches for vulnerabilities in the source code of a Solidity Smart contracts with static analysis by traversing its Abstract Syntax Tree (AST). It also leverages the OpenAI API to provide possible solutions and recommendations for those identified vulnerabilities. The execution finalizes with the generation of a report, identifying the vulnerabilities and warnings, if any.

- [Features](https://github.com/ferrabled/SolidityGuard#Feature) 
- [Detectors](https://github.com/ferrabled/SolidityGuard#Detectors)
- [Instalation](https://github.com/ferrabled/SolidityGuard#Instalation)
- [Usage](https://github.com/ferrabled/SolidityGuard#Usage)


<img src="https://github.com/ferrabled/SolidityGuard/blob/main/icon.png" width="150">


## Features

- Identify vulnerabilities in Solidity smart contracts.
- Connect to the OpenAI API to obtain recommendations and solutions.
- Provide recommendations for addressing the identified vulnerabilities.
- Offer best practices and coding patterns to improve smart contract security.


## Detectors
There are several detectors implemented:
- Reentrancy vulnerabilities
- Unchecked low level calls 
- selfdestructs not protected
- tx.origin usage
- possible overflows & underflows vulnerabilities

Some advices to the developer are given as well, as reminders to review the integrity and correctness of:
- insecure use of 'delegatecall'
- timestamps calls.
- possible denial of services findings, due to for and while loops.

Another functionality created is a require checker, that will recommend the use of a modifier when a require is found 3 or more times.


## Installation

### Using the Executable
If you're on Windows, you don't have to install any requirements, you can directly run the ".exe" executable  it has all the requirements already installed.
Just select if you want to use the AI recommender and the desired solidity smart contract to analyze.



### Using the Source code
1. Clone the repository:

```shell
git clone https://github.com/ferrabled/SolidityGuard
```

2. Install the required dependencies:
```shell
pip install -r requirements.txt
```

3. Set up the OpenAI API credentials:
If you were to use the AI bot, you need an OpenAI key for it to work.
Obtain one from the [OpenAI platform](https://platform.openai.com/account/api-keys) and set it into the secrets.json file.

```json
{
    "openai_api_key": "YOUR OPEN AI KEY"
}
```

4. Run Solidity Guard 
```python
python program.py
```



## Usage
Once you've executed the .exe file or ran the program with Python, you'll see a GUI.
Select if you want to use the AI Recommender and the desired solidity file to analyze. 
The program will start analyzing the source code and then open a report with the findings, if any.


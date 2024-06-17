# Easy Apply job crawler

This is a Python bot that seemless support Job applying for LinkedIn Easy Apply, Bumeran (AR) and Zonajobs (AR). You can setup your credentials and job query parameters and the bot will scan the activated websites and apply to jobs for you.

## 1. Setting up job platforms and bot configuration

Before you can start applying, you need credentials for each website and setup your profile. Once you have finished the setup you can configurate the bot.

Clone the git repo with:

    git clone https://github.com/notleanbarba/easy_apply_bot.git
    cd easy_apply_bot

Locate the file `config.toml.example`, rename it to `config.toml` and open it on a text editor

### Configuration options

The following are the available configuration variables:

| Domain | Variable | Type | Description |
| --- | --- | --- | --- |
| [activate] | linkedin | Boolean | Scan LinkedIn. |
| [activate] | bumeran | Boolean | Scan Bumeran. Only Argentina. |
| [activate] | zonajobs | Boolean | Scan Zonajobs. Only Argentina. |
| [linkedin] | use_top_applicant | Boolean | If true, the bot will search for the recommended jobs from LinkedIn. LinkedIn Premium is required. |
| [linkedin.resumes] | en, es | string | Is the resume file name that's uploaded to LinkedIn. You can setup one resume for each job description language |
| [linkedin] | blacklist | List[string] | Companies that you want to avoid |
| [bumeran, zonajobs] | jobs_to_apply | List[string] | A list of search queries you want to use. It will iterate for each option. |
| [bumeran, zonajobs] | city | string | The province that you want to use. Only provincies from Argentina. A validated list of provinces is available [here](#options-for-provincies-provincies). |
| [bumeran, zonajobs] | intended_salary | number | The monthly salary you want to send to the offer. ARS only. |
| [linkedin, bumeran, zonajobs] | user | string | Email or username used to login |
| [linkedin, bumeran, zonajobs] | password | string | Password of your account |

#### Options for provincies

|                     |
| ------------------- |
| Todo el país        |
| Capital Federal     |
| Buenos Aires        |
| Catamarca           |
| Chaco               |
| Chubut              |
| Corrientes          |
| Entre Ríos          |
| Formosa             |
| Jujuy               |
| La Pampa            |
| La Rioja            |
| Mendoza             |
| Misiones            |
| Neuquén             |
| Río Negro           |
| Salta               |
| San Juan            |
| San Luis            |
| Santa Cruz          |
| Santa Fe            |
| Santiago del Estero |
| Tierra del Fuego    |
| Tucumán             |

## 2. Creating virtual environment and installing dependencies

Once you have completed the [step 1](#1-setting-up-job-platforms-and-bot-configuration). You can install the virtual environment and the dependencies required by the bot. [^1][^2]

[^1]: Python-venv module is required for this step. Follow your distro documentation to install the module.
[^2]: Python 3.11 is recommended for this installation.

### 2.1 Create and activate virtual environment

Run the following command to create a virtual environment.

    python -m venv ./.venv

Then source the venv with the following command.

    source ./.venv/bin/activate

### 2.2 Install dependencies

Run this to install the required dependencies

    pip install -r requirements.txt

## 3. Run the bot

If everything went OK, now you should be able to start the bot. Simply run the following command and answer the required prompts. [^3]

    python main.py

[^3]: Remember to activate the virtual environment to start this command.

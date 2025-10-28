#!/usr/bin python3

import sys
import signal
import argparse
import configparser
#import pydevd_pycharm
from sources.browser import Browser
from sources.llm_provider import Provider
from sources.interaction import Interaction
from sources.agents import Agent, CoderAgent, CasualAgent, FileAgent, PlannerAgent, BrowserAgent , FacebookSearchAgent

import warnings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
warnings.filterwarnings("ignore")

config = configparser.ConfigParser()
config.read('config.ini')
#pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True, suspend=True)

def handleInterrupt(signum, frame):
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handler=handleInterrupt)

    if config.getboolean('MAIN', 'is_local'):
        provider = Provider(config["MAIN"]["provider_name"], config["MAIN"]["provider_model"], config["MAIN"]["provider_server_address"])
    else:
        provider = Provider(provider_name=config["MAIN"]["provider_name"],
                                   model=config["MAIN"]["provider_model"],
                                   server_address=config["MAIN"]["provider_server_address"])

    agents = [
        CasualAgent(model=config["MAIN"]["provider_model"],
                       name=config["MAIN"]["agent_name"],
                       prompt_path="prompts/casual_agent.txt",
                       provider=provider),
        CoderAgent(model=config["MAIN"]["provider_model"],
                       name="coder",
                       prompt_path="prompts/coder_agent.txt",
                       provider=provider),
        FileAgent(model=config["MAIN"]["provider_model"],
                       name="File Agent",
                       prompt_path="prompts/file_agent.txt",
                       provider=provider),
        BrowserAgent(model=config["MAIN"]["provider_model"],
                       name="Browser",
                       prompt_path="prompts/browser_agent.txt",
                       provider=provider),
        FacebookSearchAgent(
            model=config["MAIN"]["provider_model"],
            name="Facebook Search",
            prompt_path="prompts/facebook_search_agent.txt",
            provider=provider
        )
                      #  fb_email=config["MAIN"]["fb_email"],
                     #  fb_password=config["MAIN"]["fb_password"]


    ]

    interaction = Interaction(agents, tts_enabled=config.getboolean('MAIN', 'speak'),
                                      stt_enabled=config.getboolean('MAIN', 'listen'),
                                      recover_last_session=config.getboolean('MAIN', 'recover_last_session'))
    try:
        while interaction.is_active:
            interaction.get_user()
            interaction.think()
            interaction.show_answer()
    except Exception as e:
        if config.getboolean('MAIN', 'save_session'):
            interaction.save_session()
        raise e
    finally:
        if config.getboolean('MAIN', 'save_session'):
            interaction.save_session()


if __name__ == "__main__":
    main()
    shared_browser = Browser()

    # # Initialize the browser
    # browser = Browser()
    #
    # # Initialize the FacebookSearchAgent
    # provider = Provider(config["MAIN"]["provider_name"], config["MAIN"]["provider_model"], config["MAIN"]["provider_server_address"])
    #
    # agent =   FacebookSearchAgent(
    #     model=config["MAIN"]["provider_model"],
    #     name="Facebook Search",
    #     prompt_path="prompts/facebook_search_agent.txt",
    #     provider=provider
    # )
    #
    # # Run the agent with a user prompt
    # user_prompt = "search in facebook job opportunities"
    # answer, reasoning = agent.process(user_prompt, speech_module=None)
    #
    # # Print the results
    # print("Answer:", answer)
    # print("Reasoning:", reasoning)
    #
    # # Close the browser after execution
    # browser.close()
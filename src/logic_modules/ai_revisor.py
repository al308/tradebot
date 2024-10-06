# ai_revisor.py
import logging
import os

from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("tradebot")

# Set up Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")  # Read deployment name from .env


def revise_plan(plan):
    try:
        # Convert plan to a string format for the prompt
        plan_str = "\n".join(
            [f"{symbol}: {action[0]} {action[1]}" for symbol, action in plan.items()]
        )

        # Create a prompt for the AI model
        prompt = f"""
        You are a trading assistant. Review the following trading plan and suggest any necessary revisions for sanity check:
        
        {plan_str}
        
        Provide your revised plan in the same format.
        """

        # Call the Azure OpenAI API
        response = client.completions.create(
            model=deployment_name, prompt=prompt, max_tokens=150, temperature=0.5
        )

        # Parse the response
        revised_plan_str = response.choices[0].text.strip()
        revised_plan = {}
        for line in revised_plan_str.split("\n"):
            try:
                symbol, action, quantity = line.split()
                revised_plan[symbol] = (action, int(quantity))
            except ValueError as ve:
                logger.warning(f"Could not parse line '{line}': {ve}")
                continue  # Skip malformed lines

        logger.info(f"Revised Plan: {revised_plan}")
        return revised_plan

    except Exception as e:
        logger.error(f"Error revising plan: {e}")
        return plan  # Return the original plan if there's an error

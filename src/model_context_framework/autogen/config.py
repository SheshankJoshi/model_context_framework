import os
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

os.environ['AZURE_OPENAI_API_KEY'] = '39gcQzHx4OouFVZxRAb2lKE5akGB1J8OSGAj3BbAmxpcfHQORLcAJQQJ99ALACHrzpqXJ3w3AAABACOGJpy1'
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://oai-xnode-dev-001.openai.azure.com/'


mcp_model_client = AzureOpenAIChatCompletionClient(
        azure_endpoint="https://oai-xnode-uat-001.openai.azure.com/",
        model="gpt-4o",
        # model = "o1-2024-12-17",
        api_version='2025-01-01-preview',
        # api_version=
        azure_deployment='xnode-o1',
        api_key='Cnp4slzSzs5leIrhHfNjXPANvMK0k7iwtxtYsHOkthgwBmXozn93JQQJ99ALACHYHv6XJ3w3AAABACOGagx7')
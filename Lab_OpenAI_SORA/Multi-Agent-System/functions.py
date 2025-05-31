import requests
from typing import Any, Callable, Set, Dict, List, Optional
import json
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import uuid
import time
load_dotenv()

def use_video_generation_by_SORA(video_generation_prompt: str, n_seconds: int, height: int, width: int) -> str:
    """
    Generates a video by making a call to OpenAI Sora Video Generation model.
    
    :param video_generation_prompt (str): the detailed prompt/description according to which the video needs to be generated
    :param n_seconds (int): the length of the video to be generated (in seconds)
    :param height (int): the height of the video (in px)
    :param width (int): the width of the video (in px)
    :rtype: str
    
    """

    
    azure_openai_endpoint = os.getenv("SORA_MODEL_ENDPOINT")
    azure_openai_api_key = os.getenv("SORA_MODEL_API_KEY")
    sora_deployment_name = os.getenv("SORA_DEPLOYMENT_NAME")
    sora_api_version = os.getenv("SORA_API_VERSION")

    print("AZURE_OPENAI_ENDPOINT:", azure_openai_endpoint)
    print("SORA_DEPLOYMENT_NAME:", sora_deployment_name)
    print("SORA_API_VERSION:", sora_api_version)

    path = f'openai/v1/video/generations/jobs'
    params = f'?api-version={sora_api_version}'
    constructed_url = azure_openai_endpoint + path + params

    print("Constructed URL:", constructed_url)

    headers = {
        'Api-Key': azure_openai_api_key,
        'Content-Type': 'application/json',
    }

    body = {
        "prompt": video_generation_prompt,
        "n_seconds": n_seconds,
        "height": height,
        "width": width,
        "model": sora_deployment_name,
    }

    print("Request body:", body)

    job_response = requests.post(constructed_url, headers=headers, json=body)

    if not job_response.ok:
        print("API call failed!")
        print("Status code:", job_response.status_code)
        print("Response:", job_response.text)
        return "❌ Video generation failed."

    # ...rest of your code...
 
    else:
        print(json.dumps(job_response.json(), sort_keys=True, indent=4, separators=(',', ': ')))
        job_response = job_response.json()
        job_id = job_response.get("id")
        status = job_response.get("status")
        status_url = f"{azure_openai_endpoint}openai/v1/video/generations/jobs/{job_id}?api-version={sora_api_version}"

        print(f"⏳ Polling job status for ID: {job_id}")
        while status not in ["succeeded", "failed"]:
            time.sleep(5)
            job_response = requests.get(status_url, headers=headers).json()
            status = job_response.get("status")
            print(f"Status: {status}")

        if status == "succeeded":
            print(job_response)
            generations = job_response.get("generations", [])
            if generations:
                print(f"✅ Video generation succeeded.")

                generation_id = generations[0].get("id")
                video_url = f'{azure_openai_endpoint}openai/v1/video/generations/{generation_id}/content/video{params}'
                video_response = requests.get(video_url, headers=headers)
                if video_response.ok:
                    output_filename_prefix = "output" + str(uuid.uuid4())
                    output_filename = output_filename_prefix + ".mp4"
                    with open(output_filename, "wb") as file:
                        file.write(video_response.content)
                    return f'Video Generation succeeded and Generated video saved as "{output_filename}"'
            else:
                return "⚠️ Status is succeeded, but no generations were returned."
        elif status == "failed":
            return "❌ Video generation failed."


user_functions: Set[Callable[..., Any]] = {
    use_video_generation_by_SORA,
}


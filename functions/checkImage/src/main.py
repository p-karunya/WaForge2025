import os
from openai import OpenAI
from pydantic import BaseModel, Field
from appwrite.client import Client


def check_img(reqs, url):
    """
    Check if the image at the given path matches the prompt.
    """
    # Define response schema
    class ConfirmationOfEvent(BaseModel):
        TaskComplete: bool = Field(
            description="True if the task is completed in the image, False otherwise",
        )

    # Validate inputs
    if not reqs or not url:
        raise ValueError("Missing 'requirements' or 'image_url'")

    # Initialize OpenAI client
    client = OpenAI()

    # Call OpenAI GPT-4o using the correct .parse method
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Does this image meet the requirements of {reqs}? think critically and look for details."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                            }
                        },
                    ],
                }
            ],
            max_tokens=10,
            response_format=ConfirmationOfEvent,
        )
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {str(e)}")

    # Return the desired response format
    return {"taskCompleted": completion.choices[0].message.content.split(":")[1].replace("}", "").strip()}


def main(context):
    try:
        # Initialize Appwrite client
        client = (
            Client()
            .set_endpoint(os.environ["APPWRITE_FUNCTION_API_ENDPOINT"])
            .set_project(os.environ["APPWRITE_FUNCTION_PROJECT_ID"])
            .set_key(context.req.headers.get("x-appwrite-key"))
        )
        
        # Extract request data
        payload = context.req.query_string
        requirements = payload.split("&")[0].split("=")[1]
        image_url = payload.split("&")[1].split("=")[1]

        # Call the check_img function
        result = check_img(requirements, image_url.strip("'\""))

        

        # Return JSON response
        return context.res.json(result)

    except Exception as e:
        return context.res.json({"error": str(e)}, 500)

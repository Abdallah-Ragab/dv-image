import os
import requests
import logging
import time


HTTP_STATUS_VERBOSE = {
    200: "The request is successful",
    400: "Client side passed the wrong parameter. Please check if the parameter is missing or if the value is incorrect.",
    401: "Unauthorized API Key. Please check if the X-API-KEY is correct and if the service is enabled.",
    404: "The requested URL or resource does not exist. Please check if the URL or task_id is correct",
    413: "The uploaded file exceeded the allowed size. Please refer to the supported image size.",
    429: "The request frequency exceeds the QPS limit (the default QPS is 2). Please slow down the request rate or contact us to increase your QPS.",
    500: "Server side exception. Please contact the support."
}


class Client:
    API_KEY = os.environ.get("PICWISH_API_KEY")
    API_ENDPOINT = 'https://techhk.aoscdn.com/api/tasks/visual/segmentation'
    POLLING_INTERVAL = 2
    MAX_POLLS = 10

    logger = logging.getLogger(__name__)

    def create_cloud_async_task(self, image_url):
        headers = {"X-API-KEY": self.API_KEY}
        data = {"sync": "0", "image_url": image_url, 'format': "jpg", 'bg_color': "ffffff", 'crop': "1"}

        response = requests.post(self.API_ENDPOINT, headers=headers, data=data)
        task_id = None

        response_json = response.json()

        if 'status' in response_json and response_json['status'] == 200:
            result_status = 'failed'
            if 'data' in response_json:
                response_data = response_json['data']
                if 'task_id' in response_data:
                    task_id = response_data['task_id']
                    result_status = 'success'
            self.logger.info(f"Task creation {result_status}: {response_json}")
        else:
            self.logger.error(f"Task creation failed: [{response.status_code}]{response.text}")

        return task_id



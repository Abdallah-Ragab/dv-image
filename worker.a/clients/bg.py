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
    500: "Server side exception. Please contact the support.",
}

TASK_STATE_VERBOSE = {
    -8: "Processing timeout. The processing time is limited to 30 seconds.",
    -7: "Invalid image file. For example: corrupted image, incorrect format, etc.",
    -5: "Image exceeds size (Up to 15MB).",
    -3: "The server failed to download your file. Please check if the URL of your source image is available.",
    -2: "The task has been completed, but the result image upload OSS fails.",
    -1: "Task fails",
    0: "Too many requests. Your task is in the queue.",
    1: "Task succeeds",
    2: "Preparing",
    3: "Waiting",
    4: "Processing",
}


class Client:
    API_KEY = os.environ.get("PICWISH_API_KEY")
    API_ENDPOINT = "https://techhk.aoscdn.com/api/tasks/visual/segmentation"
    POLLING_INTERVAL = 2
    MAX_POLLS = 10

    logger = logging.getLogger(__name__)

    def create_cloud_async_task(self, image_url):
        headers = {"X-API-KEY": self.API_KEY}
        data = {
            "sync": "0",
            "image_url": image_url,
            "format": "jpg",
            "bg_color": "ffffff",
            "crop": "1",
        }

        response = requests.post(self.API_ENDPOINT, headers=headers, data=data)
        task_id = None

        response_json = response.json()

        if "status" in response_json and response_json["status"] == 200:
            result_status = "failed"
            if "data" in response_json:
                response_data = response_json["data"]
                if "task_id" in response_data:
                    task_id = response_data["task_id"]
                    result_status = "success"
            self.logger.info(f"Task creation {result_status}: {response_json}")
        else:
            self.logger.error(
                f"Task creation failed: [{response.status_code}]{response.text}"
            )

        return task_id

    def poll_task(self, task_id):
        headers = {"X-API-KEY": self.API_KEY}
        if not task_id:
            self.logger.error("Task ID is missing")
            return

        for _ in self.MAX_POLLS:
            time.sleep(self.POLLING_INTERVAL)
            response = requests.get(f"{self.API_ENDPOINT}/{task_id}", headers=headers)
            response_json = response.json()

            if (
                "status" in response_json
                and response_json["status"] == 200
                and "data" in response_json
            ):
                response_data = response_json["data"]
                if "state" in response_data:
                    task_state = int(response_data["state"])
                    if task_state >= 0:
                        self.logger.info(
                            f"Polling task#{task_id}: [{task_state}] {TASK_STATE_VERBOSE.get(task_state, 'unknown state')}"
                        )
                        if task_state == 1:
                            return response_data
                    else:
                        self.logger.error(
                            f"Polling task#{task_id}: [{task_state}] {TASK_STATE_VERBOSE.get(task_state, 'unknown state')}"
                        )
                        return response_data
                else:
                    self.logger.error(
                        f"Polling task#{task_id}: Task state is missing"
                    )
            else:
                self.logger.error(
                    f"Polling task#{task_id}: [failed request][{response.status_code}]{response.text}"
                )

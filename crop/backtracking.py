import time

# TODO: Image the contains that is not cropping the head (contains the head boundaries) should be valid even if the buffer is small. as the image can be expanded with white space (the background is later removed so it doesn't matter)

# Constraints Satisfaction Problem (CSP) Backtracking Algorithm


class BacktrackingCrop:
    CHUNKS = 30
    RATIO_TOLERANCE = 0.1
    CENTER_TOLERANCE = 0.05

    def __init__(self, image_info):
        self.info = image_info
        self.variables = [
            "x_min",
            "x_max",
            "y_min",
            "y_max",
        ]
        self.domains = {
            "x_min": range(0, self.info["width"], self.info["width"] // self.CHUNKS),
            "x_max": range(self.info["width"], 0, -self.info["width"] // self.CHUNKS),
            "y_min": range(0, self.info["height"], self.info["width"] // self.CHUNKS),
            "y_max": range(self.info["height"], 0, -self.info["width"] // self.CHUNKS),
        }

    def constraints(self, values):
        def check_x_min_max(values):
            if "x_min" in values and "x_max" in values:
                if values["x_min"] > values["x_max"]:
                    return False, "x_min must be less than x_max"
            return True, True

        def check_y_min_max(values):
            if "y_min" in values and "y_max" in values:
                if values["y_min"] > values["y_max"]:
                    return False, "y_min must be less than y_max"
            return True, True

        def check_x_max_min_width(values):
            if "x_max" in values and "x_min" in values:
                crop_width = values["x_max"] - values["x_min"]
                if crop_width > self.info["width"]:
                    return False, "Crop width must be less than or equal to image width"
            return True, True

        def check_y_max_min_height(values):
            if "y_max" in values and "y_min" in values:
                crop_height = values["y_max"] - values["y_min"]
                if crop_height > self.info["height"]:
                    return (
                        False,
                        "Crop height must be greater than or equal to image height",
                    )
            return True, True

        def check_eye_level(values):
            if "y_max" in values and "y_min" in values:
                eye_level = values["y_max"] - self.info["eye"]
                crop_height = values["y_max"] - values["y_min"]
                if eye_level < 0.56 * crop_height or eye_level > 0.69 * crop_height:
                    return (
                        False,
                        "eye level must be between 56% and 69% of the total cropped image height",
                    )
            return True, True

        def check_head_height(values):
            if "y_max" in values and "y_min" in values:
                head_height = self.info["chin"] - self.info["hair"]
                crop_height = values["y_max"] - values["y_min"]
                if head_height < 0.50 * crop_height or head_height > 0.69 * crop_height:
                    return (
                        False,
                        "head height must be between 50% and 69% of the total cropped image height",
                    )
            return True, True

        def check_crop_ratio(values):
            if "y_max" in values and "y_min" in values:
                crop_height = values["y_max"] - values["y_min"]
                crop_width = values["x_max"] - values["x_min"]
                diff = abs(crop_height - crop_width)
                if diff > self.RATIO_TOLERANCE * crop_height:
                    return False, "crop ratio must be 1:1"
            return True, True

        def check_x_centered(values):
            if "x_max" in values and "x_min" in values:
                crop_width = values["x_max"] - values["x_min"]
                x_min_to_center = self.info["nose"] - values["x_min"]
                x_max_to_center = values["x_max"] - self.info["nose"]
                diff = abs(x_min_to_center - x_max_to_center)
                if diff > self.CENTER_TOLERANCE * crop_width:
                    return False, "nose must be centered in the cropped image"
            return True, True

        checks = [
            check_x_min_max,
            check_x_max_min_width,
            check_x_centered,
            check_y_min_max,
            check_y_max_min_height,
            check_eye_level,
            check_head_height,
            check_crop_ratio,
        ]
        print(f"Trying : {values} ... ", end="")

        for check in checks:
            valid, result = check(values)
            if not valid:
                print(f"Failed: {result}")
                return valid, result
        print("Passed!")
        return True, values

    def backtracking(self):
        def backtrack(assignment):
            if len(assignment) == len(self.variables):
                return assignment

            var = next(var for var in self.variables if var not in assignment)
            for value in self.domains[var]:
                assignment[var] = value
                valid, returned = self.constraints(assignment)
                if valid:
                    result = backtrack(assignment)
                    if result is not None:
                        # print("Result found!")
                        return result
                del assignment[var]
            return None

        return backtrack({})

    def calculate(self):
        start = time.time()
        result = self.backtracking()
        stop = time.time()
        report = self.report(result, stop - start)
        print(f"Time taken: {stop - start}")
        if result is None:
            print("No solution found")
        else:
            print(
                f'W: {result["x_max"] - result["x_min"]}, H: {result["y_max"] - result["y_min"]}, X1: {result["x_min"]}, Y1: {result["y_min"]}, X2: {result["x_max"]}, Y2: {result["y_max"]}'
            )
        return report

    def report(self, result, time_taken):
        success = result is not None
        report = {
            "success": success,
            "time": time_taken,
        }
        if success:
            report.update(
                width = result["x_max"] - result["x_min"],
                height = result["y_max"] - result["y_min"],
                x_min = result["x_min"],
                y_min = result["y_min"],
                x_max = result["x_max"],
                y_max = result["y_max"],
                eye = self.info["eye"],
                nose = self.info["nose"],
                chin = self.info["chin"],
                hair = self.info["hair"],
                chunks = self.CHUNKS,
                ratio_tolerance = self.RATIO_TOLERANCE,
                center_tolerance = self.CENTER_TOLERANCE,
            )
        return report

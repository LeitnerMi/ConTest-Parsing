"""This class scans the input folder and looks for fitting data. There are no strict checks! It only looks for folder
structure. Having runtime errors will be common!"""

from jaeger_prometheus_joining.controlflow.ParseSettings import ParseSettings


class FilepathFinder:
    def __init__(self, settings: ParseSettings):
        self.settings: ParseSettings = settings

    def find_files(self):
        path_list = {}

        for service in self.settings.source.iterdir():
            if not service.is_dir():
                continue

            path_list[service.name] = {"monitoring": [], "traces": [], "logs": []}

            for category in service.iterdir():
                if not category.is_dir():
                    if (
                        category.name.lower().startswith("logs")
                        and category.suffix == ".txt"
                    ):
                        path_list[service.name]["logs"].append(category)

                folder_name = category.name.lower()
                # we may only process json files
                files = [x for x in category.glob("*.json") if x.stat().st_size > 100]

                # we may look for source data in a folder called monitor../trace../ts...
                if folder_name.startswith("monitor"):
                    # files = list(filter(lambda file: "container" in file.name, files))
                    # files = list(filter(lambda file: "container_network" in file.name or "container_memory_usage_bytes" in file.name or "container_cpu_usage" in file.name or "container_memory_working_set" in file.name, files))
                    # files = list(filter(lambda file: "container" in file.name, files))
                    path_list[service.name]["monitoring"].extend(files)

                if folder_name.startswith("ts") or folder_name.startswith("trace"):
                    path_list[service.name]["traces"].extend(files)

            if (
                len(path_list[service.name]["monitoring"]) == 0
                or len(path_list[service.name]["traces"]) == 0
            ):
                del path_list[service.name]

        if self.settings.test_mode:
            while len(path_list.keys()) > 2:
                path_list.popitem()

        return path_list

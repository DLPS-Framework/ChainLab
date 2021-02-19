#  Copyright 2020  ChainLab
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pandas as pd
import numpy as np


def readCSV(path, number_of_headers):
    try:
        data = pd.read_csv(path, header=number_of_headers, delim_whitespace=True, skipinitialspace=True)
        return data.to_numpy()
    except Exception as e:
        return []

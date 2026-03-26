# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from django.http import HttpResponse
from datetime import datetime


def home(request):
    return HttpResponse('Hello, World! from Boards app' + str(datetime.now()))

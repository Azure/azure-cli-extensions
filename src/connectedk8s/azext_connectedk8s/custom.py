# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.core.commands.client_factory import get_subscription_id
from azext_connectedk8s._client_factory import _graph_client_factory
from azext_connectedk8s._client_factory import cf_resource_groups
from azext_connectedk8s._client_factory import _resource_client_factory
from msrest.serialization import TZ_UTC
from dateutil.relativedelta import relativedelta
from knack.log import get_logger
from azure.cli.core.api import get_config_dir
from azure.cli.core.util import sdk_no_wait
from msrestazure.azure_exceptions import CloudError
from kubernetes import client, config
import kubernetes.client
from kubernetes.client.rest import ApiException
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from .vendored_sdks.models import ConnectedCluster, ConnectedClusterAADProfile, ConnectedClusterIdentity, LocationData

import os
import subprocess
from subprocess import Popen, PIPE
import json
import uuid
import datetime
import time
import base64
from Crypto.IO import PEM
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
from Crypto.Util.number import inverse
from pyasn1.codec.der.encoder import encode as der_encoder
from base64 import b64decode, b64encode

logger = get_logger(__name__)


def create_connectedk8s(cmd, client, resource_group_name, cluster_name,
                        location=None, kube_config=None, kube_context=None, no_wait=False,
                        location_data_name=None, location_data_country_or_region=None,
                        location_data_district=None, location_data_city=None):
    print("Ensure that you have the latest helm version installed before proceeding to avoid unexpected errors.")
    print("This operation might take a while...\n")


    # # test
    # keyPair = RSA.generate(4096)
    # pubKey = keyPair.publickey()
    # seq = asn1.DerSequence([pubKey.n, pubKey.e])
    # enc = seq.encode()
    # print(enc)
    # b64enc = b64encode(enc).decode('utf-8')
    # print(b64enc)
    # print(len(b64enc))
    # b64dec = b64decode(b64enc)
    # print(b64dec)
    # print(seq.decode(b64dec)[0])
    # return

    # //lower key is golang
    # pubKey = 'MIICCgKCAgEAtAzagFx+jXBVxkli47Onw1BOrhithUDdZSgZ/S/D1d0SVdjeIkFXcc6tqeYV8x923L0qMIWMyGwZUrwtVqfGakOvto3MlJsaUcQcXd5SuGifzbvusPFghuhB0iimvq307vQFe0+n6aRL3QEzi6pajehaEHjw43/BMvUOIkPxIbUtZH3xn3Ez3fvnTdH3hzaVlMI1cwDcqqJCvSkCHnCKZhqdCVdQKBDYQ2Yd3goqJUoHZECEwIx61C7qZJqNmqzNKsTtL4l7K4wgyshBhG1iUPqQ1sMuD1VxvW0RQzus0aknPfS5mgyfDFaasse5RiGC5u1j6VCg1MwdQrWgKXy3r7l8n8jinKqC8rPTDzcllq1RhgtnZ3rGW2Gpl0CYOaAV6wXGzG+yr0oEajLBHp9AEp4j64kD125kieXy1W71fd22o/hEVosdKzhNyLxVavtyi8VQS/bF9CBhVIVQ3zAnL9BO5GNXuoTOJn7GJN/AAJSFwJ2PILXLzttq9eW/wocPmrH4+nMCMU/9TBFcMrXnAGok2o9kTL1PvI65ZdG9oQ6GI+9rzejxqJjOXWYRXSWqZ6HerA3//sPPbjYAWtKNd/++ektO1915ALLyuCcUztck+9jfBXsrP5Nmqk8vHiqysmmwMpWoEsNZgcoTEZJYSxoZYoZyVgVIrWcrJDare78CAwEAAQ=='
    # pubKey = 'MIICCgKCAgEAynXnxoPiZhka0mD3i0d05WwBB1vtKQCeM4ffXaCOrC/FImLPC1Fw2/wAPI+qhObfXLrlWb7D4adQx+hiT35wWPbOJsY6O0+//hV38ZZPGSii+7oPmdVJrpyrbzF8Pg4EoFT1dy8kxnUiqEicG5v0E7bqmB6EsWYhPLNc3/x//JIN4+P1bd1Z41gh5t3lU173AfaWeIt/2SwzFjtgpmNGm9qxMU2IWzgnwZ2JSuUGIAjc1rzRDTt/oWjjmzS7KnXIrELGBuA5xkFOC+zmM3WW9JhKATE9YM+Vo1jN+GH4JRiOrFWOotUOrkqkRkxxwbaXopiDyx8j/vImc49b/r+9AIzSTnZxPifchsfzQ3nQlRIjzw1DbjkbxNxwtM4uNepuAYVwduMA76BzInVJxlb8z3LSx1szqBYVXhosV0DE4TRbgH2++oaZMywIGaqBwRg/XjOhJE7nU7XhQRayqVvRmOIUEi7K68GCfGqmUdC5Mt6lVDzUHtESxWSHyoZMVGKZAZmd2X8Ee2SBRVNNcm0kW9U5tzB8s1QGtZ0vNjlvujCoNBWBURkb4yURvzSJdFRfcK0EbwkONuBT/DmNdCTJ/hmFE1YJVdPyNXOWpdErWH2G3E+G+WacbRdzD+c6oKMwalVjvS8Of4LFWZRVCuzbSwcLf4vl4Q//Rl0CLsp2qR8CAwEAAQ=='
    # pubKey = 'LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlKS0FJQkFBS0NBZ0VBdEF6YWdGeCtqWEJWeGtsaTQ3T253MUJPcmhpdGhVRGRaU2daL1MvRDFkMFNWZGplCklrRlhjYzZ0cWVZVjh4OTIzTDBxTUlXTXlHd1pVcnd0VnFmR2FrT3Z0bzNNbEpzYVVjUWNYZDVTdUdpZnpidnUKc1BGZ2h1aEIwaWltdnEzMDd2UUZlMCtuNmFSTDNRRXppNnBhamVoYUVIanc0My9CTXZVT0lrUHhJYlV0WkgzeApuM0V6M2Z2blRkSDNoemFWbE1JMWN3RGNxcUpDdlNrQ0huQ0taaHFkQ1ZkUUtCRFlRMllkM2dvcUpVb0haRUNFCndJeDYxQzdxWkpxTm1xek5Lc1R0TDRsN0s0d2d5c2hCaEcxaVVQcVExc011RDFWeHZXMFJRenVzMGFrblBmUzUKbWd5ZkRGYWFzc2U1UmlHQzV1MWo2VkNnMU13ZFFyV2dLWHkzcjdsOG44amluS3FDOHJQVER6Y2xscTFSaGd0bgpaM3JHVzJHcGwwQ1lPYUFWNndYR3pHK3lyMG9FYWpMQkhwOUFFcDRqNjRrRDEyNWtpZVh5MVc3MWZkMjJvL2hFClZvc2RLemhOeUx4VmF2dHlpOFZRUy9iRjlDQmhWSVZRM3pBbkw5Qk81R05YdW9UT0puN0dKTi9BQUpTRndKMlAKSUxYTHp0dHE5ZVcvd29jUG1ySDQrbk1DTVUvOVRCRmNNclhuQUdvazJvOWtUTDFQdkk2NVpkRzlvUTZHSSs5cgp6ZWp4cUpqT1hXWVJYU1dxWjZIZXJBMy8vc1BQYmpZQVd0S05kLysrZWt0TzE5MTVBTEx5dUNjVXp0Y2srOWpmCkJYc3JQNU5tcWs4dkhpcXlzbW13TXBXb0VzTlpnY29URVpKWVN4b1pZb1p5VmdWSXJXY3JKRGFyZTc4Q0F3RUEKQVFLQ0FnQXBRSTZwZlVlemtVcmR3UCtxeXdWRGZ6bGZzeURDbUorQkowUjVHWUlGbEg2NGM1VkZoUElMamI2RgpZRVdrTEEvWU9IRWJwK1dmSUFGWFR1MFdYeDliUm9IU1VqL094cENycmtLUGtUb2pyVGo3OHJTWUR0MitXeVdGCmlMSFhtMVMwa08xV21PUVFhSWZITFpqSlJiRTB0VWs1WC9SVk0zYW8vYk9NejBOR3BWT3VwQnFCblBhMHhCdjEKWFFlWkQ3MEsxY3BZUEpqU2NaWFg4RGJma1lwc0pXblljNHhXZWJHTEU3RUJLQlFLOGlDcWJBdmViL0ZPZnlkTwpBSWswS0taalI3Wk9QM0ljZ3FFYXhQSVo3TlByV05WcGwxT015TmRqL3NMSFJEdHUyQkk1SkVLSUZKODJQUHQ1CnZiL3AzUkM0WnlpT2t0NGVrMXVhNXJFNUFDMjNiMlJaRFJsVVdrNEV5VDRDSWlCZDJsV3plazMzNUl4TDJOa1AKK0ZPcWRoTEtCUGtZZFg5c25lWGNqd29kR1NlN1NqQmJLM2RNQkpSa2FSQm9kSVJvQzl2ZWhDazdyK01WbjlEMApKeXlYMkZXZ1lyblQ4SWVqaGZrdzhLdFpPTUE3V1VNZTRic3Z6WU1SeGY1bUhieW5kQURCUmJBT1hIYklOWERrCkxFV3BYUFZQOXRYbjFGMHFmU1pJRWxNZWVBT0UvUit3dHFWb01CeC94WDJpcmVZY0JhT1NqS0VKZEpEdXJ4OTAKVExKRFRTbDNFYlcwTElHQjZvMmViTUs1Z3lNQ2FyTVNKK2paTGR6SXh4dDdSc0xVSjUwNk9VbVFsaVhFZFpabApoVFhEYm1ZTCtOM3FMOUJHUnlLeEs2QXZRMURQVm5XbXlvN0tSM2FaSXB3QjU3NlpBUUtDQVFFQTAyRkVxQzI4CmdHTFZFVWdHSFdUQ2oxQjJWdFJ6Z2pDZ2MzdVlMbkpQdml2OFo4cHVrMzc2cXBRQ21uUDYrV05DYlNuZnBiRzUKZ1VSTERNM3Y2b1VMcWR0bE0wYUduVzNsMXVtcjl3WlRicGxib09zWjE3ei9ObUJvUTUrK1pVOHFPekJCVHc2ZQord1JCYjNQQ3N5T0lRVkFFSEVSc1JsNWNhQk5Uc1A3SFlLME13c0FRTTltNFdpaW1TbkFLcDZiQzQrYmc0dUpaCk10YTVnR2puUFF6OG1kV1l1bWVWR2lOYk1qS2MrTEZOV1oxLzNBSS9hOTBTcHl0WGVOMjRwWHBySjRuMFRHaVEKd0FuNStpbzY5UDU4SWtDTHEyamJkVHBscmRVOWZGTGJrN25TK2VEanB6NDdxcWdnRlkyaTBCYVJvWHBId1Z4KwpGZWJBcWZqSUtVckpBUUtDQVFFQTJnNlB4ckNKbUlEUkFPZVNSbU04K1ZTcUlJVmc3RFpyVlo0b0dlL3NRYm1sCnlhTlA1VGtReHFUTUVSQzVQWDI5ZXprTnVVbHlucGw5YjU5RUNkNFNCandQY3doTXl5dzVLcDZpUHQxT2FrNjQKYjA0Z0oybkxYUmJ0R0NuOW5DVzBRQWRFMDNzZy84TUFpSWR5WUllTUx6dWRFM3RZVFVhZGF6dlpxZkY3dVNwdwpWYlRWVGs1bWp4alUyeTZab2xrRE50VkZkYTBDOC9PMUdXeG96Tkd2VDlQMXdHOEIxd2FDUUg0dWNUT2h4YlpQCkxsRGZFQ0FSWTNxckpQSEVLbXhFVmV6UlRUczI4dW43U3RJbU9Xek9TYUZZTEJuc0k5c2FjRHIrTzdMYzFHaW0KQ0xtQ25KSDBmOE53bmg4SnQ3WHRucCsvaHo4OXlsSHAvWmpaaFR1RXZ3S0NBUUVBcUZXYTFvL3R3UlJ6OTlveQp2Ry9FblZzSGt1aUh3Rk0zUkNCV05nN2t3RjdKR0dMV29uR0o4QlFFNnJtWVVjaWhXc3Z4QmtROXBkc2NKV3RQCk42V1NmMGR3RldDQnpaZDZaU2Nid3BKd0dQRGFUcEZMdUVvVHVGc1lUVnBHeHVrL2lYbEpXVXNjZ215R0s5cTEKWC9IWkRhSktVN1NOd1pCZDZLZ1RpeTJxMjZ1VU1QZkJMM21nWFhSbjBYbmVrbHEwYzhnbXFhaDJQbzFQbHhwegpwR1BXT2pBbSs3T0h3eFFMQ1RQVFhCM2VxcEpLQTR4cXMxeVFBVDc3M3c0N2dOUzN4dm9PNmxhUGg4K3FHblpOCkUxUWl5U2c3MGxxa0FueHFBd0NCZ2FOK3ArdGhQNHUvNEMwb1dTU2d3R2xXRW44V3BORDdtZG90c3dWYncwQ1QKTG9jWEFRS0NBUUE1VkFhOHlBRUUxU2tkd2NRVk9WWDRmeWZUTVAzUVhHWlB0aXI0MXJrWWRvUjl4Sy9tcGVBaApPWVpsSGk1MVdpK015KzB0djMrZzd0MnBrUWZFU0Z3WXc0V1VTcVJWN2lTQmJmOWQ0N1VRQWU0L1pSelMvOTkxCmMrZVZxTVNDWHU5S3ZoNThNeXp6MFFLODRrOVJ6WkV2Z2M3RUpuT0tyWHdKaTB5b2YxSjExaEIrbC9KVWlnd3cKcHVpZlQxc1k4YW9FcW9GK2RLUUlHeFNMd0pLMDlwUE91djByUUlRTlVpckFaZXd6MnMwM083MEpnajJDOGN0ZwppZ21neHVjNStBam5Sa0dvdWw2eDhvNGNsNjl3L1lnbWw0S2s1WlBOd1hicjlyYU1YM1ByYkMvcXIwc0ZldUg3CkRSajRtVlJtdGkvb3Vqc1NoYS9yRnlvYmdDbi8reXZsQW9JQkFGOXNLZk5QTmp2emg4Mm1ad2tLZDRtdk5QYnEKU2hGUW80c0FtQjVFWTZXamFESWIvWXJMRDhTdGhiSTc3YncwRGpjYzQzYmhQbTdrOUQ5ZktBNEd6TWxqRWVXNgpFY1pLamlrTzNjdmw1YTQyVUMydFRDNUhTalRaNzNQK2lzdkRMQ1pjcFFlajdlTTlYRnVXQitpd1Y2c0RHMElHClBLNHBNemRJUDVKeU5MQ0x3TzdGcEhWeWYwRUlMeDVqdkVjRnNsZmcxbEhZVzd5NWZNZkZFaUJEME92WGRTaG8KWkF4V2pSZDYxWGc3U1ZoMlRiM1JCNkVUbWtaWVBFZUF2UkFZei9FQXFrdnJ3L2hLZGJ5NnhRRXJWNnFGT2hLWgpTeVNsYWg0emJkYXBiS1ZlcEoxY0diWUxmQ0dqWUE4Q09veW9uSnJSbmxCOXdoVmhIcmszNjZYUUtuQT0KLS0tLS1FTkQgUlNBIFBSSVZBVEUgS0VZLS0tLS0='
    # pubKey = 'LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlKS0FJQkFBS0NBZ0VBNVgwelF6QnM3UkhPVTZsR0JqLzRsYjhkVzNUeFlLME5PWlA2SFZsRlB0aU1zRGIzCmdPQW1IdXpMdjNvUFZLL2U1am5maTdpTzBMUGdwOGM5RlpCV0Vlc0NLQ1ZXT05hWDF0V3JlV3QzbHI5ZmkrR0UKMnpwRnJSQ0VUSkdkUVA0bUVLQTNZYUVRQ2RmZEc2aW0rc3ZVVjBGT01aeEYxdE1TQWYrTGZoaFFXWnhxRFI5NQpOSnpDWjN3RTFwNlAwSnNYTEc3M04xam5iWktTUElPbVFCSzFDdExLNk42NFd5ZVJCUDhlL01vSW1WdVlWUkxKCnE0azFnbldOb0JOODVuWVJIS1J3NnpZZTNBVW0yaTE3MmNONXdsNWVDOEZNWVBMQmhwM0lvTDZlSVVEbU14OFEKc0JpSjRESVZNTWZYSlZJTG1hM0pTaDlsOVFORTB2MXFESCtZd0ZJWXBFNjk4N2s2RjVVUm9GbHhKN3Rkb0hucApuaXlmMkR3S0pFSWthb3RrbTlYTlB2d2ZKdDllelVxRmk5bVVkM2FHd3pOSk1TcHJ1QkxGNlpTUGYrSUc3ZG1mCis4R0tsMmNJNWxJU21QUmdNNU1sa0ZXbVQyMHRsMzlXaDRUbUhrMERPZFcxRUpqdzVIUFNCYTROdTQ1ek5JY2QKOWY1cmdyMnRaSnh4YnE3dlJzTmYzUXljOHBYbHV6ZitGM3ZBaGRhSGNtS2tBV09HY21XQTVwYmw5clRmUGV0bwpqWmFOd0ZXem1BMjhpcjVoTEpZdDdNcCsyQXE3Mnlsa243SysxalYvNEt4azQxY3BMcFpPckJNaGkrdGl4bC9uCldpUGxjYm14VXI2ZXY5Qm5uWGZKNytLVW1nV3VNeXlJNUZvenJ0RTlyZWRLZGVMeFNFZEpiYlc3UGVrQ0F3RUEKQVFLQ0FnRUFqclFoR1duV2drRHRUWWJZWFhDUU13WXB5a0paQ3VYeGNGbDlVWnkrZTRzTFNWU1U2ZFg0dm9nLwpWcTBmTldrN3NXeFJmei9meHhYajRGRDd3aG9EKzVab3UvQWp3cXBtdHhnZFRoNnV1ZFg5SXkyMGdPS21peXpYCktBbndnSWJKd3RMdVBVNTdlN040OGdjWTlxR2pSREwrM2Npd2dScTFldnFla21XcUtWOGpiMCtmL2tCd2Z3dFcKc3VMY3lUcDMyWkNUT0I2WG9zSmZIelE2UUdPaG9yNWJvUjFHQktFQkE5dGxPSXFsZUQvRjVUa09vUlZzYWRpUgpuZllnVitzWlR2ZE9wR1QrSVpFdWpNTjEzWDg1aXMxRnJBZWlhRExzZHJwTkZQQVR3dGZwamVhR2FRcUpTaG02CnBaL1BRSXpaVzlIK2RwSTV3M2NwNkEzZlVUQlRHaTgyeHU3VGFkZFB4NVl1T2JTeERnMmFZR1ZjbDJRZTZQSXoKbXhtc3Y3OGFnQlhtZnI3bEJWUGkvUUhxdWZqZXFCdkxpWmt4ODJDSndUdHpvUTM3RHdZWVBnZVl3d3FBMzJjTgpkL25wdVp3bE8xc01DMjl2b1ZRSlVMNE1ZTHJ5R3JEOVZpcllvaDh2dkl5cXlWQTR4T3p3NDFhZzlSdlhrNGx0CkczUU5PTWVMQzFCWlhvUUVRM0hmc21nZDJTMVpZMEw0b2hzWXRCbHdsNTJidU0zUXh3S081VWZQVEJQZFNRZkcKT2dCbjFJQjJZNmtDeGhmNFdDZ1FJbEYreDVQZTZtS2kvTi9raWNWUjhFZjh4dTkwb3VnUWF1aVA4S3FXa1lYKwpIWkJidkJheXl5Sy9HaUIwU2czRUNTalFNWG1RTHZWSCs2Y2ZxRjhCZHBHa014diszWkVDZ2dFQkFQWkF3b0dKCjVMalBkYmh6eUNCYjNoM2VpdzZzNi9wOUFPd0F4cVoyeFJxZzYrMmpKTDZURk1Nd0ZKdEpYeUV3anBoa2huNlUKemNRSEZFWGpZMGl3d3pjK3NiTVNCK0Jxc0RJWk1uaEUrT21HeW53Y3c4K2VyMWExcGVTclFqeThmd0ZFTXlMKwpwalk4bi8zYVhNZ1Q1ODBkODdjNVdRN0Q3Z0EyY2s4bTJ5a201V0F3WkVmUHVIQXQ3WFA0ZnQrN0VOZzJFeWRWCjBjdUdrdzR0WUttYXN5OUFrRlFLZWMyRXJueHBheGxNdktYT2pWOW5rQml6a3Z4NHZwSnBTNXB0WTdHL0dldUEKV0tiTmNZT2xqWXd1VVNmMUs2dk1QUDdXckRDYlU3emJReGsxd3QreDdkelZiQ05lTXhGWmdDYTh0bnRqSjAwUgo3T01NcnZNTmhFM1NBRjBDZ2dFQkFPNlNreG1lWGQ3a3F4dlg4Zmp0M3dkWThOK1RPb3IrNis5V2xEaElmck91CnFzOVVQaUFtYVc3bm8wb2JYYWE5cTIzczFXS3BYZE15eTY2Tkdpdk9ySzNhTGw2VkxETXFMa0Q1Rkx6d3d4QmQKbWJWOUtMRk42REVXSnFPQUdwYlBvM1hJa1RETGRBM214OVd2d2s3V0tKSzYyOUUwUEY0OWppbkFhWXFBc0ROQwpzeEVIU2N3M0xCTks4SGs1TjdtUGtlWlhVZ0VHU2tQZ1ZOaWdxcXY1QmpRbkI5c0VyUnBVM2EyeStCY0lCL3laCnpyYkpyem5IVElRUDJhajhFQ0R5T0lGcmo3QStWMmZXWVMxOVZnR051NnhJdmtJakcrdzdSdStabWZzYVpHOFcKV25zVlM0UHdMSFV0M2FvUlIvd21XbWN2Y1Y2VWVsdmo0cS9GNlNRT1N2MENnZ0VBZWd6SzJxMWZvWUdobFJROQpvbHdtRUtQV1JDWE1wOUFBL3ZlN2ZaSHNTekJxL3RNWFNTVlk2dzBQaVkrcUNLY3FaYm1kTjJ2Rk9GMVIzUG5BCm9heUtkUDByMGRjajlFU3NvNGY5amNLUnBCemNpdnN1eWQ2YWhOMXZKWkVFT1ZvcmtKTWV6VDl0WGdCYVE5VlEKbXhIU2w4VTZvQnRhV29rZGt4bHBPblhGdGZYRFJoTjJBR21odm1mbEFzK3RBbktTL0xhQWM4U0RRTjZvVUNTSgpma1pnZlJFQTk4WmhiRTFRdGZVQjBmNUltZDF3RUZNaUJqd3FvOXVzaUtDTGlqU2hidDJLbVVCNXIrS3ZXbEpaCmY1c05Pa0szckdTRDdzS3pnVHZiR3dXSmtoc2xSUDNKS09UV3ZnallRc2NiVHhmRlVnNW8wamdLTXRaOGQ1YkIKZGxpWk9RS0NBUUFMVjlTK3B4VDNnQS9TcHhYT0xDRXFqRVFIblV4dlIyZVlYWmwyZzV2aWx5OXY1Q1dBQ2RPQgpmbW41SUF2MzNaVEZDVG1zRXpsdXpUOTU4U09KYWE0MEplZUdmN2syUlk4bGI3Sll1V25NNFdacGhxWGtxRHVkCitkdWtjbmJSTE5Zc3gzaC94V3lqTEpIYnl4dUYvQkM1eVVDaVZjVjVCWnc0eC9rOHFKbTRGamZGVzM5YXdsVEsKSmdvQStZTjR3eWJBdU80aE5sZFptdFR0NTlXMWo0V0gvVU1XV3NhUU5mREVUWG9XUGorQzl4MG8rN1hsSFdDNQo5cmIybmVWMmE0M2NPV3ovaURkSHJKMjZOL2RhNDQ1RXhzQ2xERjVMZ1JZQ1ZsOUgzUjFoV3NLNmoyeWp2VXVmCjFxcHZaNXJ3bGpJK0xiZEtNKzBOYVd4aHh4c3FwN05SQW9JQkFCck0rY3Bua3A0MEdwbGhIaGo3RU5pYWtOMjkKNVZIK1p0WkFGd0d5TmJQUmhUMkprN2VxcW92UjZrYTR0TjdNZDBhY0ROdFRmcmVqVjdaV3hNckF4OTRhVWF4ZwpLVUlIL2dSa1IzbzR1dGlXNzFNQ1JBRlpRVUoxRE83V2RSUHdYalZXdkRldHNtZGdxQ3l0QkdtTWJucUNxbWNoCkQyd3U4MGNQei9ROWg3U1pIWFNXbHFsRmpaZ2ZISjJlTUlhbmxQY0c5akRvdnEwYUxoNUV6a1pMY1VvSGpEOE4KMzAxRzVuK1IwZ1doQ0xhVGUxcHlodENHK3BXNUswOFNjaG5NZ3BtV2g0aU5GNndCRHd6L2FnSW1Obm9TN1E3Uwo1bmg0Zng2cnhnYmFNUW1hclpCMFR3eVJRK3RiUVdDVHkybUcvaDVDSDZleER5SlMwaW9sY29Ud1F4Yz0KLS0tLS1FTkQgUlNBIFBSSVZBVEUgS0VZLS0tLS0K'
    # print(len(pubKey))
    # keyDER = b64decode(pubKey) 
    # seq = asn1.DerSequence()
    # decoded = seq.decode(keyDER)
    # print(len(seq))
    # print(seq[0])
    # return 

    # key_pair = RSA.generate(4096)
    # privKey_DER = key_pair.exportKey(format='DER')
    # enc_privkey = b64encode(privKey_DER).decode('utf-8')
    # print(enc_privkey)
    # print(len(enc_privkey))
    # return
    # pubKey = keyPair.publickey()
    # der_serialisation = der_encoder(pubKey)
    # print(der_serialisation)
    # return
    # encoder = asn1.Encoder()
    # encoder.start()
    # encoder.write('1.2.3', asn1.ObjectIdentifier)
    # print(encoder.output())

    # return
    # pubKeyPEM = pubKey.exportKey(format='DER')
    # #print(pubKeyPEM.decode('utf-8'))
    # print(base64.standard_b64encode(pubKeyPEM).decode('utf-8'))
    # privKeyPEM = keyPair.exportKey(format='DER')
    # private_key_pem = PEM.encode(privKeyPEM, "RSA PRIVATE KEY")
    # print (private_key_pem)
    # return

    # Checking location data info
    if location_data_name is None:
        if ((location_data_country_or_region is not None) or (location_data_district is not None) or (location_data_city is not None)):
            raise CLIError("--location-data-name is required when providing location data info.")

    # Setting subscription id
    subscription_id = get_subscription_id(cmd.cli_ctx) 

    # Fetching Tenant Id
    graph_client = _graph_client_factory(cmd.cli_ctx)
    onboarding_tenant_id = graph_client.config.tenant_id

    # Setting kubeconfig
    if kube_config is None:
        kube_config = os.getenv('KUBECONFIG')
        if kube_config is None:
            kube_config = os.path.join(os.path.expanduser('~'), '.kube', 'config')

    # Removing quotes from kubeconfig path
    if (kube_config.startswith("'") or kube_config.startswith('"')):
        kube_config = kube_config[1:]
    if (kube_config.endswith("'") or kube_config.endswith('"')):
        kube_config = kube_config[:-1]

    # Loading the kubeconfig file in kubernetes client configuration
    configuration = kubernetes.client.Configuration()
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context, client_configuration=configuration)
    except Exception as e:
        raise CLIError("Problem loading the kubeconfig file." + str(e))

    # Checking the connection to kubernetes cluster. This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters if the user had not logged in.
    api_instance = kubernetes.client.NetworkingV1Api(kubernetes.client.ApiClient(configuration))
    try:
        api_response = api_instance.get_api_resources()
    except ApiException as e:
        print("Exception when calling NetworkingV1Api->get_api_resources: %s\n" % e)
        raise CLIError("If you are using AAD Enabled cluster, check if you have logged in to the cluster properly and try again")
    
    # Checking helm installation
    cmd_helm_installed = ["helm", "--kubeconfig", kube_config, "--debug"]
    if kube_context:
        cmd_helm_installed.extend(["--kube-context", kube_context])
    try:
        response_helm_installed = subprocess.Popen(cmd_helm_installed, stdout=PIPE, stderr=PIPE)
        output_helm_installed, error_helm_installed = response_helm_installed.communicate()
        if response_helm_installed.returncode != 0:
            if "unknown flag" in error_helm_installed.decode("ascii"):
                raise CLIError("Please install the latest version of helm")
            raise CLIError(error_helm_installed.decode("ascii"))
    except FileNotFoundError:
        raise CLIError("Helm is not installed or requires elevated permissions. Please ensure that you have the latest version of helm installed on your machine.")
    except subprocess.CalledProcessError as e2:
        e2.output = e2.output.decode("ascii")
        print(e2.output)

    # Check helm version
    cmd_helm_version = ["helm", "version", "--short", "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_version.extend(["--kube-context", kube_context])
    response_helm_version = subprocess.Popen(cmd_helm_version, stdout=PIPE, stderr=PIPE)
    output_helm_version, error_helm_version = response_helm_version.communicate()
    if response_helm_version.returncode != 0:
        raise CLIError("Unable to determine helm version: " + error_helm_version.decode("ascii"))
    else:
        if "v2" in output_helm_version.decode("ascii"):
            raise CLIError("Please install the latest version of helm and then try again")
    
    # Validate location
    resourceClient = _resource_client_factory(cmd.cli_ctx, subscription_id=subscription_id)
    if location is None:
        try:
            location = resourceClient.resource_groups.get(resource_group_name).location
        except:
            raise CLIError("The provided resource group does not exist. Please provide location to create the Resource Group")

    rp_locations = []
    providerDetails = resourceClient.providers.get('Microsoft.Kubernetes')
    for resourceTypes in providerDetails.resource_types:
        if resourceTypes.resource_type == 'connectedClusters':
            rp_locations = [location.replace(" ", "").lower() for location in resourceTypes.locations]
            if location.lower() not in rp_locations:
                raise CLIError("The connected cluster resource creation is supported only in the following locations: " + ', '.join(map(str, rp_locations)) + ". Please use the --location flag to specify right location.")
            break

    # Check Release Existance
    release_namespace = get_release_namespace(kube_config, kube_context) 
    if release_namespace is not None:
        # Loading config map
        api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
        try:
            configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
        except ApiException as e:
            raise CLIError("Exception when calling CoreV1Api->read_namespaced_config_map: %s\n" % e)
        configmap_resource_group_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if connected_cluster_exists(client, configmap_resource_group_name, configmap_cluster_name):
            if (configmap_resource_group_name.lower() == resource_group_name.lower() and configmap_cluster_name.lower() == cluster_name.lower()):
                # Re-put connected cluster
                public_key = client.get(configmap_resource_group_name, configmap_cluster_name).agent_public_key_certificate
                cc = generate_request_payload(configuration, location, public_key, location_data_name, location_data_city, location_data_district, location_data_country_or_region)
                try:
                    return sdk_no_wait(no_wait, client.create, resource_group_name=resource_group_name, cluster_name=cluster_name, connected_cluster=cc)
                except CloudError as ex:
                    raise CLIError(ex)
            else:
                raise CLIError("The kubernetes cluster you are trying to onboard is already onboarded to the resource group '{}' with resource name '{}'.".format(configmap_resource_group_name, configmap_cluster_name))
        else:
            # Cleanup agents and continue with put
            delete_arc_agents(release_namespace, kube_config, kube_context, configuration)
    else:
        if connected_cluster_exists(client, resource_group_name, cluster_name):
            raise CLIError("The connected cluster resource already exists and correspods to a different kubernetes cluster. To onboard this kubernetes cluster to azure, please provide a different resource name or resource group name.")
    
    # Resource group Creation
    if (resource_group_exists(cmd.cli_ctx, resource_group_name, subscription_id) is False):
        resource_group_params = {'location': location}
        try:
            resourceClient.resource_groups.create_or_update(resource_group_name, resource_group_params)
        except Exception as e:
            raise CLIError("Resource Group Creation Failed." + str(e.message))  
    
    # # Adding helm repo
    # cmd_helm_repo = ["helm", "repo", "add", "azurearcfork8s", "https://azurearcfork8s.azurecr.io/helm/v1/repo", "--kubeconfig", kube_config]
    # if kube_context:
    #     cmd_helm_repo.extend(["--kube-context", kube_context])
    # response_helm_repo = subprocess.Popen(cmd_helm_repo, stdout=PIPE, stderr=PIPE)
    # output_helm_repo, error_helm_repo = response_helm_repo.communicate()
    # if response_helm_repo.returncode != 0:
    #     raise CLIError("Helm unable to add repository: " + error_helm_repo.decode("ascii"))

    # Generate public-private key pair
    #key_pair = RSA.generate(4096)
    #public_key = get_public_key(key_pair)
    #private_key_pem = get_private_key(key_pair)
    #print(private_key_pem)
    public_key = 'MIICCgKCAgEAvxiLRytUYzAHxhiXXqxlnFECIlRD6Y6LixDpO1QcB/GH8TU/KY1xK0P3hgH2TArtBmaQ/OO6dS+BZhrKTfj8qrlQN+Kx2hE+0PpjndtKc1mmwjzRF8NqycAnS7obJ4wcV30yyADKOyE1JVmuyik4B+BMqPg1i0bIpKhR6ZLE3CfKaFNm/X2FLi4/8ap/EpcHnVvwIoqIiKAZedjP9i8z9TC3vGml09klwfeu98cGQjQBLCrKR0WK8ZNpjcNYnfawLniLzJj2B524oj6ihOJyOjqR1Hm5O+kCOT4wkOfwD9NYE46P+Db0VnsUG+xMmlqUJUNv60VXL6psr0MbV4WZKYE2G9inhyC3q2l6wj4Brg2OHgtkO57rhTALz8T7850svGmOqGt17mbdQRrUZDHsQ5NeLQ/nsr93zOt5i9qsK5fP0a81igmNpEg4xe1hgJqPMfuaw930UDpwe74gBWI6+MvO22iXkfvD8Rz+ZVbu0+0XHaNKrU7WuQ2TwV5VAOJApFpxdGKDVPfQYvkGPM8CH3rVX3Dphjfu/iDnN3UocLS9gVmN5PYW39/lfPJ9KA7Z+pSQQY7u6jlAwZJMNOUcuBzhW2Q+ys1j+q1rJXQ+6NKQHsUF+Fg4h0613f7yqjTKaAx6DtwacPZHp5yvXBB7l2X8lIZL6fES47Y3iKmk2zkCAwEAAQ=='
    private_key_pem = 'LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlKS1FJQkFBS0NBZ0VBdnhpTFJ5dFVZekFIeGhpWFhxeGxuRkVDSWxSRDZZNkxpeERwTzFRY0IvR0g4VFUvCktZMXhLMFAzaGdIMlRBcnRCbWFRL09PNmRTK0JaaHJLVGZqOHFybFFOK0t4MmhFKzBQcGpuZHRLYzFtbXdqelIKRjhOcXljQW5TN29iSjR3Y1YzMHl5QURLT3lFMUpWbXV5aWs0QitCTXFQZzFpMGJJcEtoUjZaTEUzQ2ZLYUZObQovWDJGTGk0LzhhcC9FcGNIblZ2d0lvcUlpS0FaZWRqUDlpOHo5VEMzdkdtbDA5a2x3ZmV1OThjR1FqUUJMQ3JLClIwV0s4Wk5wamNOWW5mYXdMbmlMekpqMkI1MjRvajZpaE9KeU9qcVIxSG01TytrQ09UNHdrT2Z3RDlOWUU0NlAKK0RiMFZuc1VHK3hNbWxxVUpVTnY2MFZYTDZwc3IwTWJWNFdaS1lFMkc5aW5oeUMzcTJsNndqNEJyZzJPSGd0awpPNTdyaFRBTHo4VDc4NTBzdkdtT3FHdDE3bWJkUVJyVVpESHNRNU5lTFEvbnNyOTN6T3Q1aTlxc0s1ZlAwYTgxCmlnbU5wRWc0eGUxaGdKcVBNZnVhdzkzMFVEcHdlNzRnQldJNitNdk8yMmlYa2Z2RDhSeitaVmJ1MCswWEhhTksKclU3V3VRMlR3VjVWQU9KQXBGcHhkR0tEVlBmUVl2a0dQTThDSDNyVlgzRHBoamZ1L2lEbk4zVW9jTFM5Z1ZtTgo1UFlXMzkvbGZQSjlLQTdaK3BTUVFZN3U2amxBd1pKTU5PVWN1QnpoVzJRK3lzMWorcTFySlhRKzZOS1FIc1VGCitGZzRoMDYxM2Y3eXFqVEthQXg2RHR3YWNQWkhwNXl2WEJCN2wyWDhsSVpMNmZFUzQ3WTNpS21rMnprQ0F3RUEKQVFLQ0FnRUFyRjROTXpMSU9YZVhhMzIrKzZ4eE11QjNGbFAvdGVuWHdLYU9XZTl5SVZBaG1OYTRsRmg2bmRYKwpyS2VVYTk3bkVZRHVnczArNEhqck5SZ3hKc2ZSMElTNjhNM1FNcXlmaG94ejBtMTg2RE1Ua2R5ZGxkdTB0U3BYCng1eWs1YlVoMDJDZ3Izclc3eUx5OXkrLzA2WCtYa3habVlmWmREbHl2ZUw5ajd2TlNlK3lTUXdCdCtEQ2duZEIKUWxEUnNnajgyMW1VYnZPYVYvSmhTR0RpcEdMTGNQeHluc2FFeDJQMUJOTE94YnlGenExdDZWTG5oZ1lhWC9EaApvdmR6TlhqUVRmcDV6eUNodXhqdTg1bWZxbEUvUzNxTkU2U0FDcVFRVjJYYkZMbkE5ZVZpYXJHSzl3OUtzYjd1CjBva0FSN0l3TXJSemZUbmNmS2d5eEp1NVMrYTcwUDA1RUtPd3lSYVNsb3Y0T1Jib3Qzc3ZQZVFRL3VpME85RGEKTllKMmtFY2dYUGRiQk9pMW1vYnJqTzl5Zm5EbDg5SXBRanM5N0FsS2RUWDJLcVlNYXFsUjI5Ylk3RnpyTGwregpHSSt1VEM3aW5kZjA3WkpTM0ZOOFNWQkdkZFVrM0orNTZDUkx4cWlVYlI3Mm1iMjVPZnhJL0dOVm9LOW5yZlFRClM4ckF1eURxa1hoNGNyK1hCVm1SQy9IOFY0dkx5d0dZRXpEa3BqaytJT3ppT05JbnBqZSs3RHhERi9rYWpLTDUKNE5remd0dG5nNURDV2k1MnU2bXZQeDhCcEY2ZGs0N0FpZ0I0aitIVENreE9WSDFadDZQSEEvWHlPVytMdzRqVQpDUHNCaVcwU01kbGVaSy9EOUJOWEFWM0tlTTFVUmtVZWJuZHlTZFA1TVVmZWRNTHppd0VDZ2dFQkFQUk94MFRZCllueVhjSTR3c0hIcWM4MzFpUjRnS2RXbUFkMzAxY2RFWW9hNW9QbUlEY1AxS1RoYlBuWGtMVFEzUnBKaGNJd3MKblFGRlUzWWdhbFo2YzdYUFVlcWpDbnJFK3A2TG04VnhydU9YUUgzNHM0aEd3b00wS1lONGo1MVpSeVRxNjVwdwo0N1VVRjVLOEhqM3E4UlEyS0JTaytwL2NYb3hKVElFZEpOKzZqWjIyT2hrQVhIRXRUeHhZRW54RDA2TWFzRVRZCkVBMTBkbEgzaFI2enI3ZGRtZU0zQzArQ2VmL0ZIYUJOcDU4TVI5alg5ZDZJeHhVVStUT3VvQXQvSUoyZU4xdTgKQmFFNkRnYzVjamNudW54OWV1YkFuQWVpY1pDcUwyc1dyd09nSXgwbVdkbjNYZkg1a3RCRTVyYlpaVjcrYlpRMQpQclFmTzVHYmJWVDRwbkVDZ2dFQkFNZzkwbkJweHdIZ1g5MFdhTXRkTVBiSlhhVXFmUmRzNzhmU1hvM0F4VHJLCkZUWWQ2MFA3dGdmcHZ4dTgvaVpuaHgySHJacyswUlNEU2t2Ui9MSlJ2cFEvY2FOcDdIL1lYbDN0ZHVySTU2WUQKMlcrZjMrTVNGeC9yMktQc2VPWEJzMHVGVURpaDg3SEFtaFQyQjZUbUJnRlcvZFlCejJIaCs4M2p3c3NZdlhqTgppSnhRRHBkUkFqM0VzOTE1MWhEd0xEMlNiR2c5REhrd3ZIQXgzcVdlSUgvd0Q4OVBjWjZyY2xVWUdnU1NHZFR5Cm9CNStNU295cWJ3cHZETVFSckxiV0hvQkpjZEgyS2lhdGQ2bmE0OUdyTVpxTUdBUEJkRHFIc1BLTm1nNi9qaUoKbHo2VGdXVTMvZW1Xem5sNkF1czNMZElSMHRaRDhiMUg0L2hlanF6SU5Va0NnZ0VCQU9GZDZxU3ZsK3FuS01XQwpWTUpCTFNMSlpmdk1YOHNlb0lwSDJRMUJJRUozNnU5RmVxMVI4dnh4NzJTQllOSFNTOStzMDAzN3VibjZZY3VPCmk0bkszQUxUaFJXVjRZenZPT0lZbDFIRVZUak54a2h1cSs4Q2wxekJPYXAyQk1WNkhnOElSdDdwVktVdUs3REkKcUgwbHhjNkhSdUlFYnM0WlUzN0YvelQ3MVpBdFg0WWxHK01FV2tKdE1aVk1DWUZvY0VyOXk2MDJRMWltSHAvdQpYWGE4KzFPRG5QbmxSU0hMa3c5R250WEp6TjhEVFNQVDFKTzhTU3BCZHNFZVRiVk5TS0VkMnFOZEJ6UjdnWVZZCmtPd2dVZitWSVZMTVN5TWZ6dk5NaXdHV28wd001VmQya1Z4b3ZOa0RDVlBtdTQzaGJZbjcyc25sZERwa3RXYlUKb2o3SVFZRUNnZ0VBY0c2MkFFU0VaenRTMkZMQzJKMGs1d3k5dGdXYlkxSFplTHRZT0FPck9vMUpSNitZNy8wZgpnbVh1MW1aUjFjSi9qVWNuWlducC83aVFPTzVaRXM3dlVWSW1QbmsxUDd0L2tRSEtxWjNRNDloNWVFR3VkbE1zCkJOSnFPL0NGR1l5ZlhhSW5Id1ZnVGNnMU85dkJBd2ZkQzFlTEEyVFV5c01XbmM1ckM1cUNtSmZmUXRWNHUrSFMKZmxnNkhmdFJCUVcxOFlTTHRpUEJJek1JTzM3azR0MWNwamxteHlKMlMzODhuU2NCUk51OEFXT1NJRXorMGhETQpXVWlkMFpZci9EVkpBb2d1YkN5ZExGNWlDL2k1WGlOeTA1M0FOODkzbG93K1pmVGVnN3ZNRG5iREkzR3pUK0FXCmc5Z1hhd0hsTGFrMzR5SDYzakFjUmdsZHFaRitUdW5EY1FLQ0FRQTBWK3M1WTFGTXREVGNPeHdTYjdiS2JGYUQKWnBwbVVORHJ0bUNPYnErUkJZakhpSnZWSXhVTytyS1NEQ3Vqc1FvbWpwWFZVcHppVkJrYnpVVVhKcHo3b2hnMAo3RUlZQjZodUtHQ0ZUQklERmtNbTRFRGlzUXJQL090RG92anppQkhadHdaUkJ2YzIrNlBiQU9Xa1RuTEltUnZyCnhZOTlrM2hPUWcxakZhaGd1WXJZazBoaElZZGxncHJ5VFpiRDdVL3ovcGg5NnRYMWgvTlFOMnJZMVNiN0x5UFEKR1FBbEFSbSsrbmRkZ2o1cEZxZ1hCc2ZCc2VndlE5dXQzWThZMTlFa2FiM3FXR0JhZFA5QUkvTXVkMXBEUDVrMwpJU1B1MDN1WW1zb0VZUEtBY3hZNHM3YVNuTjlicXNOS2UwYXVkRWRiSnJCS0pBNkxJeHV2M0NyWmQ1OGgKLS0tLS1FTkQgUlNBIFBSSVZBVEUgS0VZLS0tLS0K'

    # Test Helm Install
    chart_path = os.getenv('HELMCHART')
    cmd_helm_install = ["helm", "install", "azure-arc", chart_path, "--set", "global.subscriptionId={}".format(subscription_id), "--set", "global.resourceGroupName={}".format(resource_group_name), "--set", "global.resourceName={}".format(cluster_name), "--set", "global.location={}".format(location), "--set", "global.tenantId={}".format(onboarding_tenant_id), "--set", "global.connectPrivateKey={}".format(private_key_pem), "--set", "systemDefaultValues.spnOnboarding=false", "--kubeconfig", kube_config, "--output", "json"]
    if kube_context:
        cmd_helm_install.extend(["--kube-context", kube_context])
    response_helm_install = subprocess.Popen(cmd_helm_install, stdout=PIPE, stderr=PIPE)
    output_helm_install, error_helm_install = response_helm_install.communicate()
    if response_helm_install.returncode != 0:
        raise CLIError("Unable to install helm release: " + error_helm_install.decode("ascii"))

    # # Install agents
    # cmd_helm_install = ["helm", "install", "azure-arc", "azurearcfork8s/azure-arc-k8sagents", "--set", "global.subscriptionId={}".format(subscription_id), "--set", "global.resourceGroupName={}".format(resource_group_name), "--set", "global.resourceName={}".format(cluster_name), "--set", "global.location={}".format(location), "--set", "global.tenantId={}".format(onboarding_tenant_id), "--set", "global.connectPrivateKey={}".format(private_key_pem), "--set", "systemDefaultValues.spnOnboarding=false", "--kubeconfig", kube_config, "--output", "json"]
    # if kube_context:
    #     cmd_helm_install.extend(["--kube-context", kube_context])
    # response_helm_install = subprocess.Popen(cmd_helm_install, stdout=PIPE, stderr=PIPE)
    # output_helm_install, error_helm_install = response_helm_install.communicate()
    # if response_helm_install.returncode != 0:
    #     raise CLIError("Unable to install helm release: " + error_helm_install.decode("ascii"))

    # Create connected cluster resource
    cc = generate_request_payload(configuration, location, public_key, location_data_name, location_data_city, location_data_district, location_data_country_or_region)
    try:
        put_cc_response = sdk_no_wait(no_wait, client.create, resource_group_name=resource_group_name, cluster_name=cluster_name, connected_cluster=cc)
        if no_wait:
            return put_cc_response
    except CloudError as ex:
        raise CLIError(ex)

    return put_cc_response


def resource_group_exists(ctx, resource_group_name, subscription_id=None):
    groups = cf_resource_groups(ctx, subscription_id=subscription_id)
    try:
        rg = groups.get(resource_group_name)
        return True
    except:
        return False

def connected_cluster_exists(client, resource_group_name, cluster_name):
    try:
        client.get(resource_group_name, cluster_name)
    except Exception as ex:
        if (('was not found' in str(ex)) or ('could not be found' in str(ex))):
            return False
        else:
            raise CLIError("Unable to determine if the connected cluster resource exists. " + str(ex))
    return True


def get_public_key(key_pair):
    pubKey = key_pair.publickey()
    seq = asn1.DerSequence([pubKey.n, pubKey.e])
    enc = seq.encode()
    return b64encode(enc).decode('utf-8')


def get_private_key(key_pair):
    seq = asn1.DerSequence([0, key_pair.n, key_pair.e, key_pair.d, key_pair.p, key_pair.q, key_pair.d % (key_pair.p-1), key_pair.d % (key_pair.q-1), inverse(key_pair.q, key_pair.p)])
    privKey_DER = seq.encode()
    #privKey_DER = key_pair.exportKey(format='DER')
    #print(b64encode(privKey_DER).decode('utf-8'))
    return PEM.encode(privKey_DER, "RSA PRIVATE KEY")


def get_node_count(configuration):
    api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
    try:
        api_response = api_instance.list_node()
        return len(api_response.items)
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_node: %s\n" % e)


def get_server_version(configuration):
    api_instance = kubernetes.client.VersionApi(kubernetes.client.ApiClient(configuration))
    try:
        api_response = api_instance.get_code()
        return api_response.git_version
    except ApiException as e:
        print("Exception when calling VersionApi->get_code: %s\n" % e)


def get_agent_version(configuration):
    api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
    try:
        api_response = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
        return api_response.data["AZURE_ARC_AGENT_VERSION"]
    except ApiException as e:
        print("Exception when calling CoreV1Api->read_namespaced_config_map: %s\n" % e)


def generate_request_payload(configuration, location, public_key, location_data_name, location_data_city, location_data_district, location_data_country_or_region):
    # Fetch cluster info
    total_node_count = get_node_count(configuration)
    kubernetes_version = get_server_version(configuration)
    azure_arc_agent_version = get_agent_version(configuration)

    # Create connected cluster resource object
    aad_profile = ConnectedClusterAADProfile(
        tenant_id="",
        client_app_id="",
        server_app_id=""
    )
    identity = ConnectedClusterIdentity(
        type="SystemAssigned"
    )
    location_data = LocationData(
        name=location_data_name,
        city=location_data_city,
        district=location_data_district,
        country_or_region=location_data_country_or_region
    )
    cc = ConnectedCluster(
        location=location,
        identity=identity,
        agent_public_key_certificate=public_key,
        aad_profile=aad_profile,
        kubernetes_version=kubernetes_version,
        total_node_count=total_node_count,
        agent_version=azure_arc_agent_version,
    )
    if location_data_name:
        cc.location_data=location_data
    return cc


def get_pod_names(api_instance, namespace):
    pod_list = []
    timeout = time.time() + 60
    while(not pod_list):
        try:
            api_response = api_instance.list_namespaced_pod(namespace)
            for pod in api_response.items:
                pod_list.append(pod.metadata.name)
        except ApiException as e:
            print("Exception when calling get pods: %s\n" % e)
            pod_list = []
            time.sleep(5)
        if time.time()>timeout:
            raise CLIError("")
    return pod_list



def check_pod_status(api_instance, namespace, podname):
    connect_agent_state = None
    timeout = time.time() + 300
    found_running = 0
    while connect_agent_state is None:
        if(time.time()>timeout):
            break
        try:
            api_response = api_instance.list_namespaced_pod(namespace)
            #print(api_response.items)
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
        for pod in api_response.items:
            if pod.metadata.name.startswith('connect-agent'):
                for container_status in pod.status.container_statuses:
                    if container_status.name == 'connect-agent':
                        connect_agent_state = container_status.state.running
                        if connect_agent_state is not None:
                            found_running = found_running + 1
                            time.sleep(3)
                        break
                break
        if found_running > 5:
            break
        else:
            connect_agent_state = None
    if connect_agent_state is None:
        raise CLIError("There was a problem with connect-agent deployment. Please run 'kubectl -n azure-arc logs -l app.kubernetes.io/component=connect-agent -c connect-agent' to debug the error.")


def get_connectedk8s(cmd, client, resource_group_name, cluster_name):
    return client.get(resource_group_name, cluster_name)


def list_connectedk8s(cmd, client, resource_group_name=None):
    if resource_group_name is None:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def delete_connectedk8s(cmd, client, resource_group_name, cluster_name, kube_config=None, kube_context=None):
    print("Ensure that you have the latest helm version installed before proceeding to avoid unexpected errors.")
    print("This operation might take a while ...\n")
    
    # ARM delete Connected Cluster Resource
    client.delete_cluster(resource_group_name, cluster_name)

    # Setting kubeconfig
    if kube_config is None:
        kube_config = os.getenv('KUBECONFIG')
        if kube_config is None:
            kube_config = os.path.join(os.path.expanduser('~'), '.kube', 'config')

    # Loading the kubeconfig file in kubernetes client configuration
    configuration = kubernetes.client.Configuration()
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context, client_configuration=configuration)
    except Exception as e:
        print("Problem loading the kubeconfig file.")
        raise CLIError(e)

    # Checking the connection to kubernetes cluster. This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters if the user had not logged in.
    api_instance = kubernetes.client.NetworkingV1Api(kubernetes.client.ApiClient(configuration))
    try:
        api_response = api_instance.get_api_resources()
    except ApiException as e:
        print("Exception when calling NetworkingV1Api->get_api_resources: %s\n" % e)
        raise CLIError("If you are using AAD Enabled cluster, check if you have logged in to the cluster properly and try again")

    # Checking helm installation
    cmd_helm_installed = ["helm", "--kubeconfig", kube_config, "--debug"]
    if kube_context:
        cmd_helm_installed.extend(["--kube-context", kube_context])
    try:
        response_helm_installed = subprocess.Popen(cmd_helm_installed, stdout=PIPE, stderr=PIPE)
        output_helm_installed, error_helm_installed = response_helm_installed.communicate()
        if response_helm_installed.returncode != 0:
            if "unknown flag" in error_helm_installed.decode("ascii"):
                raise CLIError("Please install the latest version of helm")
            raise CLIError(error_helm_installed.decode("ascii"))
    except FileNotFoundError:
        raise CLIError("Helm is not installed or requires elevated permissions. Please ensure that you have the latest version of helm installed on your machine.")
    except subprocess.CalledProcessError as e2:
        e2.output = e2.output.decode("ascii")
        print(e2.output)

    # Check helm version
    cmd_helm_version = ["helm", "version", "--short", "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_version.extend(["--kube-context", kube_context])
    response_helm_version = subprocess.Popen(cmd_helm_version, stdout=PIPE, stderr=PIPE)
    output_helm_version, error_helm_version = response_helm_version.communicate()
    if response_helm_version.returncode != 0:
        raise CLIError("Unable to determine helm version: " + error_helm_version.decode("ascii"))
    else:
        if "v2" in output_helm_version.decode("ascii"):
            raise CLIError("Please install the latest version of helm and then try again")

    # Check Release Existance
    release_namespace = get_release_namespace(kube_config, kube_context)
    if release_namespace is None:
        return 

    # Loading config map
    api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
    namespace = 'azure-arc'
    try:
        api_response = api_instance.list_namespaced_config_map(namespace)
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_namespaced_config_map: %s\n" % e)
    for configmap in api_response.items:
        if configmap.metadata.name == 'azure-clusterconfig':
            if (configmap.data["AZURE_RESOURCE_GROUP"].lower() == resource_group_name.lower() and configmap.data["AZURE_RESOURCE_NAME"].lower() == cluster_name.lower()):
                break
            else:
                raise CLIError("The kube config does not correspond to the connected cluster resource provided. Agents installed on this cluster correspond to the resource group name '{}' and resource name '{}'.".format(configmap.data["AZURE_RESOURCE_GROUP"], configmap.data["AZURE_RESOURCE_NAME"]))

    # Deleting the azure-arc agents
    delete_arc_agents(release_namespace, kube_config, kube_context, configuration)


def get_release_namespace(kube_config, kube_context):
    cmd_helm_release = ["helm", "list", "-a", "--all-namespaces", "--output", "json", "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_release.extend(["--kube-context", kube_context])
    response_helm_release = subprocess.Popen(cmd_helm_release, stdout=PIPE, stderr=PIPE)
    output_helm_release, error_helm_release = response_helm_release.communicate()
    if response_helm_release.returncode != 0:
        raise CLIError("Helm list release failed: " + error_helm_release.decode("ascii"))
    else:
        output_helm_release = output_helm_release.decode("ascii")
        output_helm_release = json.loads(output_helm_release)
        for release in output_helm_release:
            if release['name'] == 'azure-arc':
                return release['namespace']
    return None


def delete_arc_agents(release_namespace, kube_config, kube_context, configuration):
    cmd_helm_delete = ["helm", "delete", "azure-arc", "--namespace", release_namespace, "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_delete.extend(["--kube-context", kube_context])
    response_helm_delete = subprocess.Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
    output_helm_delete, error_helm_delete = response_helm_delete.communicate()
    if response_helm_delete.returncode != 0:
        raise CLIError("Error occured while cleaning up arc agents. Helm release deletion failed: " + error_helm_delete.decode("ascii"))
    ensure_namespace_cleanup(configuration)


def ensure_namespace_cleanup(configuration):
    api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
    timeout = time.time() + 120
    while(True):
        if time.time()>timeout:
            logger.warning("Namespace 'azure-arc' still in terminating state")
            return
        try:
            api_response = api_instance.list_namespace(field_selector='metadata.name=azure-arc')
            if len(api_response.items) == 0:
                return
            else:
                time.sleep(5)
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)


def update_connectedk8s(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance


def _is_guid(guid):
    try:
        uuid.UUID(guid)
        return True
    except ValueError:
        return False


def _error_caused_by_role_assignment_exists(ex):
    return getattr(ex, 'status_code', None) == 409 and 'role assignment already exists' in ex.message

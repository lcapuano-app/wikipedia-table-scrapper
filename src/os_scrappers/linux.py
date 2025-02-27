

from src.os_scrappers.awslinux import version_info_awslinux
from src.os_scrappers.centOS import version_info_centOS
from src.os_scrappers.ubuntu import version_info_ubuntu


def version_info_linux():
    centos =  version_info_centOS()
    ubuntu = version_info_ubuntu()
    al = version_info_awslinux()
    # res = {
    #     "centos": centos,
    #     "ubuntu": ubuntu,
    #     "al2023": al["al2023"],
    #     "al2": al["al2"],
    # }
    res = []
    res.extend(centos)
    res.extend(ubuntu)
    res.extend(al)

    return res
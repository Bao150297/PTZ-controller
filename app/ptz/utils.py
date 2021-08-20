# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-10 13:34:04
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-18 14:38:51

import os
import sys

__all__ = ["e_verbose"]

def e_verbose(e, logger=None, prefix=""):
    """ Get more details about the exception 
    Args:
        - e: catched Exception (except Exception as e)
        - logger: logger instance. If not provide, only print to screen
        - prefix: additional infomation needed to be added to the message
    Return: print/log exception with additional details   
    """
    exc_type, _, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    msg  = prefix + ". " if prefix else ""
    msg += "Error: \n\tType: %s\n\tFile name: %s\n\tLine number: %s\n\tContent: %s" %(exc_type, fname, str(exc_tb.tb_lineno), e)
    if logger:
        logger.error(msg)
    else:
        print(msg)


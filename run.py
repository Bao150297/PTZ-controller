# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-20 09:21:34
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-20 09:58:58

from app import app

# start flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
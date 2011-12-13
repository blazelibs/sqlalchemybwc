import os
from jenkinsutils import BuildHelper

package = 'SQLAlchemyBWC'
type = 'build'

bh = BuildHelper(package, type)

# delete & re-create the venv
bh.venv_create()

## install package w/ setuptools develop command
bh.setuppy_develop()

## run tests
bh.vepycall('nosetests', 'sqlalchemybwc_ta', '--with-xunit', '--blazeweb-package=sqlalchemybwc_ta')

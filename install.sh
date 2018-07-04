cd ./ob-core
python setup.py sdist
pip install ./dist/ob-core-0.1.tar.gz

cd ../ob-time
python setup.py sdist
pip install ./dist/ob-time-0.1.tar.gz

cd ../ob-math
python setup.py sdist
pip install ./dist/ob-math-0.1.tar.gz

cd ../ob-astro
python setup.py bdist_wheel
pip install ./dist/ob_astro-0.1-cp27-cp27mu-linux_x86_64.whl

cd ../
python setup.py sdist
pip install ./dist/ouroboros-0.1.tar.gz

cd ./ob-core
python setup.py sdist
pip install ./dist/ob-core-0.1.tar.gz

cd ../ob-time
python setup.py sdist
pip install ./dist/ob-time-0.1.tar.gz

cd ../ob-math
python setup.py sdist
pip install ./dist/ob-math-0.1.tar.gz

cd ../ob-orbit
python setup.py sdist
pip install ./dist/ob-orbit-0.1.tar.gz

cd ../ob-web
python setup.py sdist
pip install ./dist/ob-web-0.1.tar.gz

cd ..
python setup.py sdist
pip install ./dist/ouroboros-0.1.tar.gz
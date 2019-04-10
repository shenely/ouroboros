python setup.py sdist
pip install ./dist/ouroboros-0.1.tar.gz

cd ./ob-time
python setup.py sdist
pip install ./dist/ob-time-0.1.tar.gz

cd ../ob-math
python setup.py sdist
pip install ./dist/ob-math-0.1.tar.gz

cd ../ob-astro
python setup.py bdist_wheel
pip install ./dist/ob_astro-0.1-cp35-cp35m-linux_x86_64.whl

#cd ../ob-data
#python setup.py sdist
#pip install ./dist/ob-data-0.1.tar.gz

#cd ../ob-sat
#python setup.py sdist
#pip install ./dist/ob-sat-0.1.tar.gz

cd ..

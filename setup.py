from setuptools import find_packages, setup

package_name = 'catch_them_all'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='parsa07',
    maintainer_email='parsa07@todo.todo',
    description='Autonomous turtle catcher using P control',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'spawner_node = catch_them_all.spawner_node:main',
            'controller_node = catch_them_all.controller_node:main',
        ],
    },
)

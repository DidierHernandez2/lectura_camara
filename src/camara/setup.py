from setuptools import find_packages, setup

package_name = 'camara'

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
    maintainer='darhf',
    maintainer_email='didier.hernandez1972@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_publisher = camara.simple_publisher:main',
            'simple_subscriber = camara.simple_subscriber:main',

            'camera_publisher = camara.camera_publisher:main',
            'camera_subscriber = camara.camera_subscriber:main',
	    'color_detector      = camara.camera_color_detector:main',
	    'traffic_light       = camara.traffic_light:main',
        ],
    },
)

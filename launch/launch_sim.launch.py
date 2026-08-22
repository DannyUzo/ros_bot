# import os

# from ament_index_python.packages import get_package_share_directory

# from launch import LaunchDescription
# from launch.actions import IncludeLaunchDescription
# from launch.launch_description_sources import PythonLaunchDescriptionSource
# from launch_ros.actions import Node

# def generate_launch_description():

#     package_name = 'ros_bot'

#     # 1. Robot State Publisher
#     rsp = IncludeLaunchDescription(
#         PythonLaunchDescriptionSource([os.path.join(
#             get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
#         )]), launch_arguments={'use_sim_time': 'true'}.items()
#     )

#     # 2. Modern Gazebo Sim
#     gazebo = IncludeLaunchDescription(
#         PythonLaunchDescriptionSource([os.path.join(
#             get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
#         )]),
#         launch_arguments={'gz_args': 'empty.sdf -r'}.items()
#     )

#     # 3. Modern Gazebo Spawner
#     spawn_entity = Node(
#         package='ros_gz_sim',
#         executable='create',
#         arguments=[
#             '-topic', 'robot_description',
#             '-name', 'ros_bot',
#             '-z', '0.1'
#         ],
#         output='screen'
#     )

#     return LaunchDescription([
#         rsp,
#         gazebo,
#         spawn_entity,
#     ])

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    package_name = 'ros_bot'

    # 0. Global Environment Override for RViz Rendering
    qt_env = SetEnvironmentVariable('QT_ENABLE_HIGHDPI_SCALING', '0')

    # 1. Robot State Publisher
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 2. Modern Gazebo Sim (Using Custom World)
    world_path = os.path.join(get_package_share_directory(package_name), 'worlds', 'custom_empty.sdf')
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
        )]),
        launch_arguments={'gz_args': f'{world_path} -r'}.items()
    )

    # 3. Modern Gazebo Spawner
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'ros_bot',
            '-z', '0.1'
        ],
        output='screen'
    )

    # 4. Message Bridge (Namespaced TF Remapping)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/model/ros_bot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/depth_image/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        ],
        remappings=[
            ('/model/ros_bot/tf', '/tf'),
        ],
        output='screen'
    )

    # 5. RViz2 Visualizer
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        qt_env,
        rsp,
        gazebo,
        spawn_entity,
        bridge,
        rviz,
    ])
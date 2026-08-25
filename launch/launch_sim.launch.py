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
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node

def generate_launch_description():

    package_name = 'ros_bot'

    # 0. Global Environment Configurations for RViz and Gazebo Plugin Paths
    qt_env = SetEnvironmentVariable('QT_ENABLE_HIGHDPI_SCALING', '0')

    # Safely append paths rather than overriding to prevent dropping internal Gazebo links
    append_gz_sim_plugin_path = AppendEnvironmentVariable(
        name='GZ_SIM_SYSTEM_PLUGIN_PATH',
        value='/opt/ros/lyrical/lib'
    )
    
    append_gazebo_plugin_path = AppendEnvironmentVariable(
        name='GAZEBO_PLUGIN_PATH',
        value='/opt/ros/lyrical/lib'
    )

    controllers_file_path = os.path.join(
        get_package_share_directory(package_name),
        'config',
        'my_controllers.yaml'
    )

    # 1. Robot State Publisher
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 2. Modern Gazebo Sim (Using Custom World)
    world_path = os.path.join(get_package_share_directory(package_name), 'worlds', 'custom_empty.sdf')
    gazebo_params_path = os.path.join(get_package_share_directory(package_name), 'config', 'gazebo_params.yaml')

    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
        )]),
        launch_arguments={'gz_args': f'{world_path} -r', 'params_file': gazebo_params_path}.items()
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
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
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

    # 6. ROS 2 Control Spawner Nodes
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "-p", controllers_file_path],
        parameters=[{'use_sim_time': True}],
        output="screen"
    )

    diff_cont_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont", "-p", controllers_file_path],
        parameters=[{'use_sim_time': True}],
        remappings=[
            ('/diff_cont/cmd_vel', '/cmd_vel'), # Route global cmd_vel into the controller
            ('/diff_cont/odom', '/odom'),       # Route the controller odom to global odom
        ],
        output="screen"
    )

    # 7. Ordered Event Handlers to Prevent Race Conditions
    delay_joint_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )

    delay_diff_cont = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[diff_cont_spawner],
        )
    )

    return LaunchDescription([
        append_gz_sim_plugin_path,
        append_gazebo_plugin_path,
        qt_env,
        rsp,
        gazebo,
        spawn_entity,
        delay_joint_broadcaster,
        delay_diff_cont,
        bridge,
        rviz,
    ])

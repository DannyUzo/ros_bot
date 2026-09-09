## Robot Package Template
Hi, I'm currently learning ROS2 and I see you're interested also. I've converted my tutorials into a DIY course for us all. The learning curve is high and hope you have ubuntu setup....its only execution from here. 

Here's an Abstract of everything in this repo:
--- TO DO. 
For more detailed guides and documentation, check the AMTES Blog (link)

For Ubuntu 26.04 and ROS Lyrical run Rviz using QT_ENABLE_HIGHDPI_SCALING=0 rviz2
To launch Gazebo use the command ros2 launch ros_gz_sim gz_sim.launch.py gz_args:="empty.sdf -r"

To run Gazebo Simulations we would need to run three commands, the launch file with sim_time parameter, gazebo and the Node spawner, but making a change to the code would require us running those commands all over again. So as Engineers, we have to do come up with a much more efficient method. We write a script to run all executables in a single file `launch_sim.launch.py`

ros2_control, Odometry

To run teleop, run this: ros2 run teleop_twist_keyboard teleop_twist_keyboard

Run the bot with `ros2 launch ros_bot launch_sim.launch.py`

Build with `colcon build --symlink-install`

This is a GitHub template. You can make your own copy by clicking the green "Use this template" button.

For the camera frame note that the coordinate system is different from ROS body standard under the name camera_link_optical and must be rotated.
However, this is now obsolete modern Gazebo builds and sensors aren't. 

To run teleop on Ros2 Control `ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diff_cont/cmd_vel -p stamped:=true`

To run slam toolbox `ros2 launch slam_toolbox online_async_launch.py params_file:=./config/mapper_params_online_async.yaml use_sim_time:=true`

Problems Faced:
--I mistakenly saved the robot in the custom world so I had to go edit the file my self. 

--LiDAR visualization in Gazebo remained at the map origin instead of tracking a moving robot, run gz model -m ros_bot -l lidar_frame to relink the sensor or a delay/re-order the launch file. 

-- I used a c++ // style comment in the xml, xml can't parse // so it choke the compilation. 

--This was the worst one yet, I encountered a known, active upstream bug in the ROS 2 Lyrical / Gazebo stack (tracked under ros2_control Issue #3401 and Issue #805). Pulling the upstream fix quickly wiped
my tears away.

It is recommended that you keep the repo/package name the same, but if you do change it, ensure you do a "Find all" using your IDE (or the built-in GitHub IDE by hitting the `.` key) and rename all instances of `ros_bot` to whatever your project's name is.

Note that each directory currently has at least one file in it to ensure that git tracks the files (and, consequently, that a fresh clone has direcctories present for CMake to find). These example files can be removed if required (and the directories can be removed if `CMakeLists.txt` is adjusted accordingly).
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
import xacro

def generate_launch_description():
    # Get the path to the xacro file
    xacro_file = os.path.join(get_package_share_directory('senton_description'), 'urdf', 'senton.urdf.xacro')

    # Process the xacro file to generate the URDF
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = {'robot_description': robot_description_config.toxml()}

    # Create a Node action for RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        
    )
    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # Joint State Publisher GUI
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )

    return LaunchDescription([
    robot_state_publisher_node,
    joint_state_publisher_gui_node,
    rviz_node
])
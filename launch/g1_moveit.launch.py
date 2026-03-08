import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    # Load the MoveIt configuration (SRDF, kinematics, limits, etc.)
    moveit_config = MoveItConfigsBuilder("g1_29dof", package_name="g1_dual_arm_moveit_config").to_moveit_configs()

    # Get the absolute path to the RViz config
    rviz_config_file = os.path.join(
        get_package_share_directory("g1_dual_arm_moveit_config"),
        "config",
        "moveit.rviz"
    )

    # 1. The Math Engine (MoveGroup)
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            {"use_sim_time": False},
        ],
    )

    # 2. The Visualizer (RViz)
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[
            # --- THE FIX: Pass the URDF and SRDF to RViz ---
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
        ],
    )

    # 3. The 3D Transformer (Robot State Publisher)
    rsp_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[moveit_config.robot_description],
    )

    return LaunchDescription([move_group_node, rviz_node, rsp_node])
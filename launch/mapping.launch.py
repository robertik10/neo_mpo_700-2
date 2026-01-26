# Copyright 2025 Neobotix GmbH.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Pradheep Padmanabhan, Adarsh Karan K P
# Co-Author: Darby Lim

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    LogInfo,
    RegisterEventHandler,
)
from launch.conditions import IfCondition
from launch.events import matches_action
from launch.substitutions import AndSubstitution, LaunchConfiguration, NotSubstitution
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition

# HINT added for project
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    # HINT added for project
    robot_namespace = LaunchConfiguration("robot_namespace")

    autostart = LaunchConfiguration("autostart")
    use_lifecycle_manager = LaunchConfiguration("use_lifecycle_manager")
    use_sim_time = LaunchConfiguration("use_sim_time")
    slam_params_file = LaunchConfiguration("slam_params_file")

    # HINT added for project
    declare_robot_namespace_cmd = DeclareLaunchArgument(
        "robot_namespace", default_value="", description="Top-level namespace"
    )

    declare_autostart_cmd = DeclareLaunchArgument(
        "autostart",
        default_value="True",
        description="Automatically startup the slamtoolbox. "
        "Ignored when use_lifecycle_manager is true.",
    )
    declare_use_lifecycle_manager = DeclareLaunchArgument(
        "use_lifecycle_manager",
        default_value="False",
        description="Enable bond connection during node activation",
    )
    declare_use_sim_time_argument = DeclareLaunchArgument(
        "use_sim_time", default_value="False", description="Use simulation/Gazebo clock"
    )
    declare_slam_params_file_cmd = DeclareLaunchArgument(
        "slam_params_file",
        default_value=os.path.join(
            get_package_share_directory("neo_mpo_700-2"),
            "configs/navigation",
            "mapping.yaml",
        ),
        description="Full path to the ROS2 parameters file to use for the slam_toolbox node",
    )

    # HINT added for project
    configured_params = RewrittenYaml(
        source_file=slam_params_file,
        root_key=robot_namespace,
        param_rewrites={
            # "odom_frame": [robot_namespace, "/odom"],
            # "base_frame": [robot_namespace, "/base_footprint"],
            # "map_frame": "/map",
        },
        convert_types=True,
    )

    start_sync_slam_toolbox_node = LifecycleNode(
        parameters=[
            # HINT changed for project
            # slam_params_file,
            configured_params,
            {
                "use_lifecycle_manager": use_lifecycle_manager,
                "use_sim_time": use_sim_time,
            },
        ],
        package="slam_toolbox",
        executable="sync_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        namespace=robot_namespace,
    )

    configure_event = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(start_sync_slam_toolbox_node),
            transition_id=Transition.TRANSITION_CONFIGURE,
        ),
        condition=IfCondition(
            AndSubstitution(autostart, NotSubstitution(use_lifecycle_manager))
        ),
    )

    activate_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=start_sync_slam_toolbox_node,
            start_state="configuring",
            goal_state="inactive",
            entities=[
                LogInfo(msg="[LifecycleLaunch] Slamtoolbox node is activating."),
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(
                            start_sync_slam_toolbox_node
                        ),
                        transition_id=Transition.TRANSITION_ACTIVATE,
                    )
                ),
            ],
        ),
        condition=IfCondition(
            AndSubstitution(autostart, NotSubstitution(use_lifecycle_manager))
        ),
    )

    ld = LaunchDescription()

    # HINT added for project
    ld.add_action(declare_robot_namespace_cmd)
    ld.add_action(declare_autostart_cmd)
    ld.add_action(declare_use_lifecycle_manager)
    ld.add_action(declare_use_sim_time_argument)
    ld.add_action(declare_slam_params_file_cmd)
    ld.add_action(start_sync_slam_toolbox_node)
    ld.add_action(configure_event)
    ld.add_action(activate_event)

    return ld

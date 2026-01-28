from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.descriptions import ParameterValue

def generate_launch_description():
    namespace = LaunchConfiguration('namespace', default='')

    frame_id_1 = ParameterValue(
        PythonExpression([
            "'lidar_1_link' if '", namespace, "' == '' else '", namespace, "/lidar_1_link'"
        ]),
        value_type=str
    )
    frame_id_2 = ParameterValue(
        PythonExpression([
            "'lidar_2_link' if '", namespace, "' == '' else '", namespace, "/lidar_2_link'"
        ]),
        value_type=str
    )
    
    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value=''),
        GroupAction([
            PushRosNamespace(namespace),
            Node(
                package="sick_safetyscanners2",
                executable="sick_safetyscanners2_node",
                name="sick_safetyscanners2_node",
                output="screen",
                emulate_tty=True,
                parameters=[
                    {"frame_id": frame_id_1,
                    "sensor_ip": "192.168.1.30",
                    "host_ip": "192.168.1.10",
                    "interface_ip": "0.0.0.0",
                    "host_udp_port": 6060,
                    "channel": 0,
                    "channel_enabled": True,
                    "skip": 1,
                    "angle_start": -1.48,
                    "angle_end": 1.48,
                    "time_offset": -0.07,
                    "general_system_state": True,
                    "derived_settings": True,
                    "measurement_data": True,
                    "intrusion_data": True,
                    "application_io_data": True,
                    "use_persistent_config": False,
                    "min_intensities": 0.0}
                ],
                remappings=[
                    ('scan', 'lidar_1/scan_filtered'),
                ]
            ), Node(
                package="sick_safetyscanners2",
                executable="sick_safetyscanners2_node",
                name="sick_safetyscanners2_node1",
                output="screen",
                emulate_tty=True,
                parameters=[
                    {"frame_id": frame_id_2,
                    "sensor_ip": "192.168.1.31",
                    "host_ip": "192.168.1.10",
                    "interface_ip": "0.0.0.0",
                    "host_udp_port": 6061,
                    "channel": 0,
                    "channel_enabled": True,
                    "skip": 1,
                    "angle_start": -1.48,
                    "angle_end": 1.48,
                    "time_offset": -0.07,
                    "general_system_state": True,
                    "derived_settings": True,
                    "measurement_data": True,
                    "intrusion_data": True,
                    "application_io_data": True,
                    "use_persistent_config": False,
                    "min_intensities": 0.0}
                ],
                remappings=[
                    ('scan', 'lidar_2/scan_filtered'),
                ]
            )
        ])
    ])
